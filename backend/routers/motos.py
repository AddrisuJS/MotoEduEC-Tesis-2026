"""M4 — Recomendador de Motocicletas"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import recomendar_moto

router = APIRouter()

@router.post("/recomendar", summary="Recomienda 3 motos segun perfil con IA")
async def recomendar(
    datos: dict = Body(..., example={
        "perfil": {"tipo_uso":"delivery","anos_experiencia":1,"presupuesto_max":2500,"zona":"Sierra"}
    }),
    db: Session = Depends(get_db)
):
    perfil = datos.get("perfil", {})
    precio_max = perfil.get("presupuesto_max", 5000)
    tipo = perfil.get("tipo_uso", "urbano")

    tipo_map = {
        "delivery": ["Utilitaria"],
        "urbano": ["Utilitaria","Scooter","Naked/Street"],
        "touring": ["Adventure/Touring","Naked/Street"],
        "aventura": ["Doble proposito","Adventure/Touring"],
        "enduro": ["Enduro/Trail","Motocross"],
        "deportivo": ["Deportiva","Naked/Street"],
    }
    tipos = tipo_map.get(tipo, ["Utilitaria"])
    tipos_str = ", ".join([f"'{t}'" for t in tipos])

    catalogo = db.execute(text(f"""
        SELECT m.id, ma.nombre AS marca, m.modelo, m.anio,
               m.cilindrada_cc, m.precio_usd, m.uso_recomendado
        FROM motocicletas m
        JOIN marcas_moto ma ON m.marca_id = ma.id
        JOIN tipos_moto t ON m.tipo_id = t.id
        WHERE t.nombre IN ({tipos_str})
          AND m.precio_usd <= :precio AND m.disponible_ec = TRUE
        ORDER BY m.precio_usd ASC LIMIT 20
    """), {"precio": precio_max}).mappings().all()

    catalogo_list = [dict(r) for r in catalogo]
    recomendacion = await recomendar_moto(perfil, catalogo_list)
    return {"perfil": perfil, "catalogo_consultado": len(catalogo_list), **recomendacion}


@router.get("/catalogo", summary="Lista el catalogo completo de motos")
def catalogo_motos(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM v_motos_completo")).mappings().all()
    return {"total": len(result), "motos": [dict(r) for r in result]}
