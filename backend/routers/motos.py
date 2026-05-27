"""
M4 — Recomendador de Motocicletas
Sprint 2 — Con catalogo real + Claude API mock
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends, Body, Query
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
    tipo_uso   = perfil.get("tipo_uso", "urbano").lower()
    precio_max = perfil.get("presupuesto_max", 5000)

    tipos = TIPO_POR_PERFIL.get(tipo_uso, ["Utilitaria", "Naked/Street"])
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
