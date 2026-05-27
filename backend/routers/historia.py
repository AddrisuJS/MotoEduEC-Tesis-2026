"""M6 — Historia del Motociclismo Ecuatoriano"""
from fastapi import APIRouter
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

@router.get("/temas", summary="Lista los temas de historia motera")
def listar_temas():
    return {"temas": TEMAS_HISTORIA}


@router.get("/{tema_id}", summary="Genera narrativa de un tema historico con IA")
async def obtener_historia(tema_id: int):
    tema_info = next((t for t in TEMAS_HISTORIA if t["id"] == tema_id), None)
    if not tema_info:
        return {"error": "Tema no encontrado"}
    narrativa = await generar_historia(tema_info["tema"])
    return {"tema": tema_info, "contenido": narrativa}
