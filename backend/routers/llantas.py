"""
M5 — Recomendador de Llantas
Sprint 2 — Con catalogo real de 16 llantas
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter()

# Mapa tipo_moto + uso → tipo de llanta recomendada
MAPA = {
    ("utilitaria",  "ciudad"):    "Carretera (Road)",
    ("utilitaria",  "lluvia"):    "Lluvia/Rain",
    ("utilitaria",  "carretera"): "Carretera (Road)",
    ("scooter",     "ciudad"):    "Scooter",
    ("scooter",     "lluvia"):    "Lluvia/Rain",
    ("naked",       "ciudad"):    "Carretera (Road)",
    ("naked",       "carretera"): "Carretera (Road)",
    ("deportiva",   "carretera"): "Sport",
    ("deportiva",   "ciudad"):    "Carretera (Road)",
    ("touring",     "carretera"): "Trail/Adventure",
    ("touring",     "lluvia"):    "Lluvia/Rain",
    ("aventura",    "offroad"):   "Off-road/Enduro",
    ("aventura",    "carretera"): "Trail/Adventure",
    ("enduro",      "offroad"):   "Off-road/Enduro",
    ("doble",       "offroad"):   "Trail/Adventure",
    ("doble",       "carretera"): "Trail/Adventure",
}

ALERTAS = {
    "Sport":           "Las llantas sport son para clima SECO. En lluvia reduce velocidad y aumenta distancia de frenado.",
    "Off-road/Enduro": "No usar en asfalto a alta velocidad — el taco se desgasta rapidamente y pierde agarre.",
    "Lluvia/Rain":     "Las llantas de lluvia rinden mejor por debajo de 80 km/h. En seco se desgastan mas rapido.",
    "Scooter":         "Verifica siempre la presion recomendada por el fabricante — los scooters son muy sensibles a la presion.",
    "Carretera (Road)":"Ideal para uso mixto ciudad/carretera. Verificar presion cada 2 semanas.",
    "Trail/Adventure": "Excelente versatilidad. En off-road severo considera una llanta mas especializada.",
}


@router.post("/recomendar", summary="Recomienda llantas segun perfil, moto y condiciones")
def recomendar_llantas(
    datos: dict = Body(..., example={
        "tipo_moto": "utilitaria",
        "uso":       "ciudad",
        "clima":     "lluvia",
        "gama":      "media",
        "presupuesto_max": 80
    }),
    db: Session = Depends(get_db)
):
    tipo_moto = datos.get("tipo_moto", "utilitaria").lower()
    uso       = datos.get("uso",       "ciudad").lower()
    clima     = datos.get("clima",     "seco").lower()
    gama      = datos.get("gama",      "media").lower()
    precio_max= datos.get("presupuesto_max", 200)

    # Ajustar uso segun clima
    uso_efectivo = "lluvia" if "lluv" in clima or "mojado" in clima else uso

    # Buscar tipo de llanta recomendado
    tipo_llanta = None
    for (tm, u), tl in MAPA.items():
        if tm in tipo_moto and u in uso_efectivo:
            tipo_llanta = tl
            break
    if not tipo_llanta:
        tipo_llanta = "Carretera (Road)"

    result = db.execute(text("""
        SELECT l.id, ml.nombre AS marca, ml.gama, tl.nombre AS tipo,
               l.modelo, l.medida_ejemplo,
               l.precio_min_usd, l.precio_max_usd
        FROM llantas l
        JOIN marcas_llanta ml ON l.marca_id = ml.id
        JOIN tipos_llanta  tl ON l.tipo_id  = tl.id
        WHERE tl.nombre = :tipo
          AND LOWER(ml.gama) = LOWER(:gama)
          AND l.precio_max_usd <= :precio
        ORDER BY l.precio_min_usd ASC
        LIMIT 5
    """), {"tipo": tipo_llanta, "gama": gama, "precio": precio_max}).mappings().all()

    # Si no hay resultados con esa gama, buscar sin filtro de gama
    if not result:
        result = db.execute(text("""
            SELECT l.id, ml.nombre AS marca, ml.gama, tl.nombre AS tipo,
                   l.modelo, l.medida_ejemplo,
                   l.precio_min_usd, l.precio_max_usd
            FROM llantas l
            JOIN marcas_llanta ml ON l.marca_id = ml.id
            JOIN tipos_llanta  tl ON l.tipo_id  = tl.id
            WHERE tl.nombre = :tipo
            ORDER BY l.precio_min_usd ASC
            LIMIT 5
        """), {"tipo": tipo_llanta}).mappings().all()

    alerta = ALERTAS.get(tipo_llanta, "Verifica siempre la presion recomendada por el fabricante.")

    return {
        "tipo_moto":              tipo_moto,
        "uso":                    uso,
        "clima":                  clima,
        "tipo_llanta_recomendada": tipo_llanta,
        "gama":                   gama,
        "alerta_seguridad":       alerta,
        "opciones":               [dict(r) for r in result],
        "consejo":                f"Para tu moto tipo {tipo_moto} en uso {uso_efectivo}, la llanta {tipo_llanta} es la mas adecuada."
    }


@router.get("/catalogo", summary="Catalogo completo de llantas")
def catalogo_llantas(
    tipo: str = Query(None),
    gama: str = Query(None),
    db: Session = Depends(get_db)
):
    filtros = ["1=1"]
    params  = {}
    if tipo:
        filtros.append("LOWER(tl.nombre) LIKE LOWER(:tipo)")
        params["tipo"] = f"%{tipo}%"
    if gama:
        filtros.append("LOWER(ml.gama) = LOWER(:gama)")
        params["gama"] = gama

    where = " AND ".join(filtros)
    result = db.execute(text(f"""
        SELECT l.id, ml.nombre AS marca, ml.gama, tl.nombre AS tipo,
               l.modelo, l.medida_ejemplo,
               l.precio_min_usd, l.precio_max_usd
        FROM llantas l
        JOIN marcas_llanta ml ON l.marca_id = ml.id
        JOIN tipos_llanta  tl ON l.tipo_id  = tl.id
        WHERE {where}
        ORDER BY ml.gama, l.precio_min_usd ASC
    """), params).mappings().all()

    return {"total": len(result), "llantas": [dict(r) for r in result]}


@router.get("/tipos", summary="Tipos de llanta disponibles")
def tipos_llanta(db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT nombre, terreno_ideal, clima_ideal FROM tipos_llanta ORDER BY nombre"
    )).mappings().all()
    return {"tipos": [dict(r) for r in result]}


# ═══════════════════════════════════════════════════════════════
#  ADMIN: autocompletado con IA + crear/editar llanta
# ═══════════════════════════════════════════════════════════════
from fastapi import HTTPException
from services.claude_service import client, CLAUDE_MODEL_HAIKU, USE_MOCK, limpiar_json
import json as _json


@router.post("/admin/autocompletar", summary="Sugiere datos tecnicos de una llanta con IA (editable)")
def autocompletar_llanta(datos: dict = Body(...)):
    marca = datos.get("marca", ""); modelo = datos.get("modelo", "")
    if not marca or not modelo:
        raise HTTPException(400, "marca y modelo son requeridos")
    if USE_MOCK:
        return {"sugerencia": {"medida_ejemplo": "110/70-17", "precio_min_usd": 45, "precio_max_usd": 90,
                "terreno_ideal": "Asfalto urbano", "clima_ideal": "Seco y humedo"},
                "advertencia": "Modo simulado (sin API key). Verifica estos datos manualmente."}
    prompt = f"""Eres un experto en llantas de motocicleta del mercado ecuatoriano 2026.
Para la llanta {marca} {modelo}, da tu MEJOR ESTIMACION de sus datos tipicos.
Responde SOLO este JSON, sin texto adicional:
{{"medida_ejemplo": "ej 110/70-17", "precio_min_usd": numero, "precio_max_usd": numero,
 "terreno_ideal": "texto corto", "clima_ideal": "texto corto"}}"""
    try:
        r = client.messages.create(model=CLAUDE_MODEL_HAIKU, max_tokens=250,
                                    messages=[{"role": "user", "content": prompt}])
        data = _json.loads(limpiar_json(r.content[0].text))
        return {"sugerencia": data, "advertencia": "Estimacion generada por IA. Verifica y corrige antes de guardar."}
    except Exception as e:
        raise HTTPException(500, f"No se pudo generar la sugerencia: {e}")


@router.post("/admin/crear", summary="Admin: crea una llanta nueva en el catalogo")
def crear_llanta(datos: dict = Body(...), db: Session = Depends(get_db)):
    marca_row = db.execute(text("SELECT id FROM marcas_llanta WHERE nombre ILIKE :n"), {"n": datos["marca"].strip()}).fetchone()
    if not marca_row:
        marca_row = db.execute(text("INSERT INTO marcas_llanta (nombre) VALUES (:n) RETURNING id"),
                                {"n": datos["marca"]}).fetchone()
    tipo_row = db.execute(text("SELECT id FROM tipos_llanta WHERE nombre ILIKE :n"),
                           {"n": datos.get("tipo", "Carretera (Road)").strip()}).fetchone()
    db.execute(text("""
        INSERT INTO llantas (marca_id, tipo_id, modelo, medida_ejemplo, precio_min_usd, precio_max_usd, descripcion)
        VALUES (:marca_id, :tipo_id, :modelo, :medida, :pmin, :pmax, :desc)
    """), {"marca_id": marca_row[0], "tipo_id": tipo_row[0] if tipo_row else None,
           "modelo": datos["modelo"], "medida": datos.get("medida_ejemplo", ""),
           "pmin": datos.get("precio_min_usd"), "pmax": datos.get("precio_max_usd"),
           "desc": datos.get("descripcion", "")})
    db.commit()
    return {"ok": True, "mensaje": f"Llanta {datos['marca']} {datos['modelo']} agregada al catalogo"}


@router.put("/admin/{llanta_id}", summary="Admin: edita una llanta existente")
def editar_llanta(llanta_id: int, datos: dict = Body(...), db: Session = Depends(get_db)):
    db.execute(text("""
        UPDATE llantas SET modelo=:modelo, medida_ejemplo=:medida, precio_min_usd=:pmin,
            precio_max_usd=:pmax, descripcion=:desc WHERE id=:id
    """), {"id": llanta_id, "modelo": datos.get("modelo"), "medida": datos.get("medida_ejemplo"),
           "pmin": datos.get("precio_min_usd"), "pmax": datos.get("precio_max_usd"),
           "desc": datos.get("descripcion")})
    db.commit()
    return {"ok": True}

@router.get("/admin/opciones", summary="Marcas y tipos existentes, para los selectores del CRUD")
def opciones_admin_llantas(db: Session = Depends(get_db)):
    marcas = db.execute(text("SELECT nombre FROM marcas_llanta ORDER BY nombre")).fetchall()
    tipos = db.execute(text("SELECT nombre FROM tipos_llanta ORDER BY nombre")).fetchall()
    return {"marcas": [m[0] for m in marcas], "tipos": [t[0] for t in tipos]}
