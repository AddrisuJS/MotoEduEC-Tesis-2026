"""
M6 — Historia del Motociclismo Ecuatoriano
Sprint 3 — Con endpoint de contribuciones comunitarias
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Body
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

# Almacen en memoria para contribuciones (en produccion usar PostgreSQL)
contribuciones_store = []


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
        "historia": "Mi primera moto fue una Honda CB100 que compre con mis ahorros de 3 meses..."
    })
):
    """
    Los motociclistas pueden contribuir sus propias historias.
    En Sprint 3 se almacena en memoria. En produccion va a PostgreSQL.
    """
    if not datos.get("historia", "").strip():
        return {"error": "La historia no puede estar vacia"}

    contribucion = {
        "id":       len(contribuciones_store) + 1,
        "nombre":   datos.get("nombre", "Anonimo"),
        "ciudad":   datos.get("ciudad", "Ecuador"),
        "anio":     datos.get("anio", ""),
        "historia": datos.get("historia", ""),
        "estado":   "pendiente_revision"
    }
    contribuciones_store.append(contribucion)

    return {
        "mensaje":    "Historia recibida exitosamente. Sera revisada y publicada pronto.",
        "id":         contribucion["id"],
        "estado":     "pendiente_revision",
        "total_contribuciones": len(contribuciones_store)
    }


@router.get("/contribuciones/lista", summary="Lista las contribuciones comunitarias")
def listar_contribuciones():
    return {
        "total": len(contribuciones_store),
        "contribuciones": [
            {
                "id":      c["id"],
                "nombre":  c["nombre"],
                "ciudad":  c["ciudad"],
                "anio":    c["anio"],
                "preview": c["historia"][:100] + "..." if len(c["historia"]) > 100 else c["historia"],
                "estado":  c["estado"]
            }
            for c in contribuciones_store
        ]
    }
