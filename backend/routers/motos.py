"""
M4 — Recomendador de Motocicletas
Sprint 2 — Con catalogo real + Claude API mock
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends, Body, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import recomendar_moto

router = APIRouter()

TIPO_POR_PERFIL = {
    "delivery":  ["Utilitaria"],
    "urbano":    ["Utilitaria", "Scooter", "Naked/Street"],
    "touring":   ["Adventure/Touring", "Naked/Street"],
    "aventura":  ["Doble proposito", "Adventure/Touring"],
    "enduro":    ["Enduro/Trail", "Motocross"],
    "deportivo": ["Deportiva", "Naked/Street"],
}


@router.post("/recomendar", summary="Recomienda 3 motos con justificacion IA segun perfil")
async def recomendar(
    datos: dict = Body(..., example={
        "perfil": {
            "tipo_uso":         "delivery",
            "anos_experiencia": 1,
            "presupuesto_max":  2500,
            "zona":             "Sierra",
            "moto_actual":      "ninguna"
        }
    }),
    db: Session = Depends(get_db)
):
    perfil     = datos.get("perfil", {})
    # Soporta tipo_uso como string ("aventura") o lista (["aventura","urbano"])
    # -- retrocompatible: si viene un solo string, funciona exactamente igual que antes.
    tipo_uso_raw = perfil.get("tipo_uso", "urbano")
    tipos_uso_lista = [t.lower() for t in (tipo_uso_raw if isinstance(tipo_uso_raw, list) else [tipo_uso_raw])]
    precio_max = perfil.get("presupuesto_max", 5000)

    # Unir los tipos de moto de TODOS los perfiles elegidos (sin duplicar)
    tipos = []
    for tu in tipos_uso_lista:
        for t in TIPO_POR_PERFIL.get(tu, ["Utilitaria", "Naked/Street"]):
            if t not in tipos:
                tipos.append(t)
    tipo_uso = tipos_uso_lista[0]  # para el prompt/contexto, se usa el principal
    tipos_str = ", ".join([f"'{t}'" for t in tipos])

    catalogo = db.execute(text(f"""
        SELECT m.id, ma.nombre AS marca, m.modelo, m.anio,
               t.nombre AS tipo, m.cilindrada_cc, m.potencia_hp,
               m.precio_usd, m.uso_recomendado
        FROM motocicletas m
        JOIN marcas_moto ma ON m.marca_id = ma.id
        JOIN tipos_moto  t  ON m.tipo_id  = t.id
        WHERE t.nombre IN ({tipos_str})
          AND m.precio_usd <= :precio
          AND m.disponible_ec = TRUE
        ORDER BY m.precio_usd ASC
        LIMIT 20
    """), {"precio": precio_max}).mappings().all()

    catalogo_list = [dict(r) for r in catalogo]

    if not catalogo_list:
        # Ampliar busqueda sin filtro de precio
        catalogo_list = [dict(r) for r in db.execute(text(f"""
            SELECT m.id, ma.nombre AS marca, m.modelo, m.anio,
                   t.nombre AS tipo, m.cilindrada_cc, m.precio_usd, m.uso_recomendado
            FROM motocicletas m
            JOIN marcas_moto ma ON m.marca_id = ma.id
            JOIN tipos_moto  t  ON m.tipo_id  = t.id
            WHERE t.nombre IN ({tipos_str}) AND m.disponible_ec = TRUE
            ORDER BY m.precio_usd ASC LIMIT 10
        """)).mappings().all()]

    recomendacion = await recomendar_moto(perfil, catalogo_list)

    return {
        "perfil":             perfil,
        "catalogo_consultado": len(catalogo_list),
        "tipos_buscados":     tipos,
        "recomendaciones":    recomendacion.get("recomendaciones", []),
        "razonamiento":       recomendacion.get("razonamiento_general", ""),
        "modo":               recomendacion.get("modo", "claude_api")
    }


@router.get("/catalogo", summary="Catalogo completo de motocicletas")
def catalogo_motos(
    tipo:   str = Query(None, description="Filtrar por tipo"),
    marca:  str = Query(None, description="Filtrar por marca"),
    precio: int = Query(None, description="Precio maximo en USD"),
    db: Session = Depends(get_db)
):
    filtros = ["m.disponible_ec = TRUE"]
    params  = {}
    if tipo:
        filtros.append("LOWER(t.nombre) LIKE LOWER(:tipo)")
        params["tipo"] = f"%{tipo}%"
    if marca:
        filtros.append("LOWER(ma.nombre) LIKE LOWER(:marca)")
        params["marca"] = f"%{marca}%"
    if precio:
        filtros.append("m.precio_usd <= :precio")
        params["precio"] = precio

    where = " AND ".join(filtros)
    result = db.execute(text(f"""
        SELECT m.id, ma.nombre AS marca, m.modelo, m.anio,
               t.nombre AS tipo, m.cilindrada_cc, m.potencia_hp,
               m.peso_kg, m.precio_usd, m.uso_recomendado
        FROM motocicletas m
        JOIN marcas_moto ma ON m.marca_id = ma.id
        JOIN tipos_moto  t  ON m.tipo_id  = t.id
        WHERE {where}
        ORDER BY ma.nombre, m.precio_usd ASC
    """), params).mappings().all()

    return {
        "total":  len(result),
        "filtros": {"tipo": tipo, "marca": marca, "precio_max": precio},
        "motos":  [dict(r) for r in result]
    }


@router.get("/marcas", summary="Lista de marcas disponibles en Ecuador")
def listar_marcas(db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT nombre, origen, distribuidor_ec FROM marcas_moto ORDER BY nombre"
    )).mappings().all()
    return {"total": len(result), "marcas": [dict(r) for r in result]}


@router.get("/tipos", summary="Lista de tipos de motocicleta")
def listar_tipos(db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT t.nombre, t.descripcion, COUNT(m.id) AS cantidad FROM tipos_moto t LEFT JOIN motocicletas m ON t.id = m.tipo_id GROUP BY t.id ORDER BY cantidad DESC"
    )).mappings().all()
    return {"tipos": [dict(r) for r in result]}


# ═══════════════════════════════════════════════════════════════
#  CRUD DE ADMIN + AUTOCOMPLETADO CON IA (motos y llantas)
#  El admin puede subir modelos nuevos. Claude sugiere cilindrada,
#  potencia, peso y rango de precio como PUNTO DE PARTIDA editable
#  -- el admin siempre revisa y confirma antes de guardar.
# ═══════════════════════════════════════════════════════════════
from services.claude_service import client, CLAUDE_MODEL_HAIKU, USE_MOCK, limpiar_json
from fastapi import Body, Depends
from sqlalchemy.orm import Session
import json as _json


@router.post("/admin/autocompletar", summary="Sugiere datos tecnicos de una moto con IA (editable)")
def autocompletar_moto(datos: dict = Body(...)):
    marca = datos.get("marca", "")
    modelo = datos.get("modelo", "")
    if not marca or not modelo:
        raise HTTPException(400, "marca y modelo son requeridos")

    if USE_MOCK:
        return {"sugerencia": {"cilindrada_cc": 150, "potencia_hp": 12.5, "peso_kg": 130,
                "precio_min_usd": 1800, "precio_max_usd": 2400,
                "uso_recomendado": "Uso urbano y de carretera ligera"},
                "advertencia": "Modo simulado (sin API key). Verifica estos datos manualmente."}

    prompt = f"""Eres un experto en motocicletas del mercado ecuatoriano 2026.
Para la moto {marca} {modelo}, da tu MEJOR ESTIMACION de sus datos tecnicos tipicos.
Si no conoces el modelo exacto, estima segun motos similares de esa marca/segmento.
Responde SOLO este JSON, sin texto adicional:
{{"cilindrada_cc": numero, "potencia_hp": numero, "peso_kg": numero,
 "precio_min_usd": numero, "precio_max_usd": numero,
 "uso_recomendado": "texto corto"}}"""
    try:
        r = client.messages.create(model=CLAUDE_MODEL_HAIKU, max_tokens=300,
                                    messages=[{"role": "user", "content": prompt}])
        data = _json.loads(limpiar_json(r.content[0].text))
        return {"sugerencia": data,
                "advertencia": "Estimacion generada por IA. Verifica y corrige antes de guardar."}
    except Exception as e:
        raise HTTPException(500, f"No se pudo generar la sugerencia: {e}")


@router.post("/admin/crear", summary="Admin: crea una moto nueva en el catalogo")
def crear_moto(datos: dict = Body(...), db: Session = Depends(get_db)):
    marca_row = db.execute(text("SELECT id FROM marcas_moto WHERE nombre ILIKE :n"),
                            {"n": datos["marca"].strip()}).fetchone()
    if not marca_row:
        marca_row = db.execute(text("INSERT INTO marcas_moto (nombre) VALUES (:n) RETURNING id"),
                                {"n": datos["marca"]}).fetchone()
    tipo_row = db.execute(text("SELECT id FROM tipos_moto WHERE nombre ILIKE :n"),
                           {"n": datos.get("tipo", "Naked/Street").strip()}).fetchone()
    db.execute(text("""
        INSERT INTO motocicletas (marca_id, tipo_id, modelo, anio, cilindrada_cc,
            potencia_hp, peso_kg, precio_usd, uso_recomendado, disponible_ec)
        VALUES (:marca_id, :tipo_id, :modelo, :anio, :cc, :hp, :peso, :precio, :uso, true)
    """), {"marca_id": marca_row[0], "tipo_id": tipo_row[0] if tipo_row else None,
           "modelo": datos["modelo"], "anio": datos.get("anio", 2026),
           "cc": datos.get("cilindrada_cc"), "hp": datos.get("potencia_hp"),
           "peso": datos.get("peso_kg"),
           "precio": datos.get("precio_usd") or datos.get("precio_min_usd"),
           "uso": datos.get("uso_recomendado", "")})
    db.commit()
    return {"ok": True, "mensaje": f"Moto {datos['marca']} {datos['modelo']} agregada al catalogo"}


@router.put("/admin/{moto_id}", summary="Admin: edita una moto existente")
def editar_moto(moto_id: int, datos: dict = Body(...), db: Session = Depends(get_db)):
    db.execute(text("""
        UPDATE motocicletas SET modelo=:modelo, anio=:anio, cilindrada_cc=:cc,
            potencia_hp=:hp, peso_kg=:peso, precio_usd=:precio, uso_recomendado=:uso
        WHERE id=:id
    """), {"id": moto_id, "modelo": datos.get("modelo"), "anio": datos.get("anio"),
           "cc": datos.get("cilindrada_cc"), "hp": datos.get("potencia_hp"),
           "peso": datos.get("peso_kg"), "precio": datos.get("precio_usd"),
           "uso": datos.get("uso_recomendado")})
    db.commit()
    return {"ok": True}

@router.get("/admin/opciones", summary="Marcas y tipos existentes, para los selectores del CRUD")
def opciones_admin(db: Session = Depends(get_db)):
    marcas = db.execute(text("SELECT nombre FROM marcas_moto ORDER BY nombre")).fetchall()
    tipos = db.execute(text("SELECT nombre FROM tipos_moto ORDER BY nombre")).fetchall()
    return {"marcas": [m[0] for m in marcas], "tipos": [t[0] for t in tipos]}
