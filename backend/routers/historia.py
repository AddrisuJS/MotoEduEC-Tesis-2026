"""
M6 — Historia del Motociclismo Ecuatoriano
Sprint 3 — Con contribuciones en PostgreSQL
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import generar_historia

router = APIRouter()

TEMAS_HISTORIA = [
    {"id":1,"tema":"Los inicios del motociclismo en Ecuador (1900-1970)","epoca":"1900-1970"},
    {"id":2,"tema":"La llegada de las marcas japonesas y la masificacion (1970-2000)","epoca":"1970-2000"},
    {"id":3,"tema":"El boom del delivery y la era digital (2000-2020)","epoca":"2000-2020"},
    {"id":4,"tema":"El record historico de 2025: 274.729 motos vendidas","epoca":"2020-2026"},
    {"id":5,"tema":"La Federacion Ecuatoriana de Motociclismo y el deporte","epoca":"2000-2026"},
    {"id":6,"tema":"La cultura motera ecuatoriana: clubes, rodadas y comunidad","epoca":"1990-2026"},
]


@router.get("/temas", summary="Lista los 6 temas de historia motera")
def listar_temas():
    return {"temas": TEMAS_HISTORIA}


@router.get("/{tema_id}", summary="Genera narrativa de un tema historico con Claude API")
async def obtener_historia(tema_id: int):
    tema_info = next((t for t in TEMAS_HISTORIA if t["id"] == tema_id), None)
    if not tema_info:
        return {"error": "Tema no encontrado"}
    narrativa = await generar_historia(tema_info["tema"])
    return {"tema": tema_info, "contenido": narrativa}


@router.post("/contribuir", summary="Envia una contribucion de historia comunitaria")
def contribuir_historia(
    datos: dict = Body(..., example={
        "nombre":   "El Lobo de Cuenca",
        "ciudad":   "Cuenca",
        "anio":     "1995",
        "historia": "Mi primera moto fue una Honda CB100..."
    }),
    db: Session = Depends(get_db)
):
    if not datos.get("historia", "").strip():
        return {"error": "La historia no puede estar vacia"}

    try:
        result = db.execute(text("""
            INSERT INTO contribuciones_historia (nombre, ciudad, anio, historia, estado)
            VALUES (:nombre, :ciudad, :anio, :historia, 'pendiente_revision')
            RETURNING id
        """), {
            "nombre":   datos.get("nombre", "Anonimo"),
            "ciudad":   datos.get("ciudad", "Ecuador"),
            "anio":     datos.get("anio", ""),
            "historia": datos.get("historia", "")
        })
        nuevo_id = result.fetchone()[0]
        db.commit()

        total = db.execute(text("SELECT COUNT(*) FROM contribuciones_historia")).scalar()

        return {
            "mensaje":              "Historia recibida exitosamente. Sera revisada y publicada pronto.",
            "id":                   nuevo_id,
            "estado":               "pendiente_revision",
            "total_contribuciones": total
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e), "mensaje": "Error al guardar la historia"}


@router.get("/contribuciones/lista", summary="Lista las contribuciones comunitarias")
def listar_contribuciones(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT id, nombre, ciudad, anio,
               LEFT(historia, 100) || '...' AS preview,
               estado, fecha_envio
        FROM contribuciones_historia
        ORDER BY fecha_envio DESC
    """)).mappings().all()
    return {
        "total":          len(result),
        "contribuciones": [dict(r) for r in result]
    }