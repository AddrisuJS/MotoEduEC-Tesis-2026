"""M5 — Recomendador de Llantas"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter()

MAPA_LLANTAS = {
    ("utilitaria","ciudad"):     "Carretera (Road)",
    ("utilitaria","carretera"):  "Carretera (Road)",
    ("deportivo","carretera"):   "Carretera (Road)",
    ("touring","carretera"):     "Trail/Adventure",
    ("aventura","offroad"):      "Off-road/Enduro",
    ("enduro","offroad"):        "Off-road/Enduro",
    ("utilitaria","lluvia"):     "Lluvia/Rain",
    ("scooter","ciudad"):        "Scooter",
}

@router.post("/recomendar", summary="Recomienda llantas segun perfil y uso")
def recomendar_llantas(
    datos: dict = Body(..., example={
        "tipo_moto":"utilitaria","uso":"ciudad","clima":"lluvia","gama":"media"
    }),
    db: Session = Depends(get_db)
):
    tipo = datos.get("tipo_moto","utilitaria").lower()
    uso  = datos.get("uso","ciudad").lower()
    gama = datos.get("gama","media")
    tipo_llanta = MAPA_LLANTAS.get((tipo,uso), "Trail/Adventure")

    result = db.execute(text("""
        SELECT l.id, ml.nombre AS marca, ml.gama, tl.nombre AS tipo,
               l.modelo, l.medida_ejemplo, l.precio_min_usd, l.precio_max_usd, l.descripcion
        FROM llantas l
        JOIN marcas_llanta ml ON l.marca_id = ml.id
        JOIN tipos_llanta tl ON l.tipo_id = tl.id
        WHERE tl.nombre = :tipo_llanta AND ml.gama = :gama
        ORDER BY l.precio_min_usd ASC LIMIT 5
    """), {"tipo_llanta": tipo_llanta, "gama": gama}).mappings().all()

    return {
        "tipo_moto": tipo, "uso": uso,
        "tipo_llanta_recomendada": tipo_llanta,
        "gama": gama,
        "opciones": [dict(r) for r in result],
        "alerta_ia": f"Para uso {uso} bajo condiciones de {datos.get('clima','seco')}, verifica siempre la presion segun el fabricante."
    }
