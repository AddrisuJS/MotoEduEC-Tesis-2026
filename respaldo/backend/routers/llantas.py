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
