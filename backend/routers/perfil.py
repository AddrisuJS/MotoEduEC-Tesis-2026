"""M1 — Perfil Inteligente del Motociclista"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
import uuid

router = APIRouter()

PERFILES = {
    "delivery":          {"nombre":"Delivery","velocidad_tipica":60,"riesgo":"ALTO","motos":["Honda CB100","Bajaj Boxer 150","Shineray XY150"]},
    "urbano":            {"nombre":"Urbano Diario","velocidad_tipica":50,"riesgo":"MEDIO","motos":["Honda CB1 Star","Yamaha YBR125","Bajaj NS160"]},
    "touring":           {"nombre":"Touring","velocidad_tipica":100,"riesgo":"MEDIO","motos":["Yamaha Tenere 700","KTM 390 Adventure","Royal Enfield Himalayan 450"]},
    "aventura":          {"nombre":"Aventura Off-road","velocidad_tipica":80,"riesgo":"MEDIO","motos":["KTM EXC 300","Yamaha XTZ250","Honda CRF300L"]},
    "enduro":            {"nombre":"Enduro","velocidad_tipica":90,"riesgo":"ALTO","motos":["KTM EXC 300","Honda CRF450R","Yamaha YZ"]},
    "deportivo":         {"nombre":"Deportivo","velocidad_tipica":150,"riesgo":"ALTO","motos":["Kawasaki Ninja 400","Yamaha R3","KTM RC 390"]},
}

@router.post("/crear", summary="Crea el perfil del motociclista (onboarding)")
def crear_perfil(
    datos: dict = Body(..., example={
        "nombre": "Juan Perez",
        "tipo_uso": "delivery",
        "anos_experiencia": 2,
        "moto_actual": "Honda CB100",
        "zona": "Sierra",
        "presupuesto_max": 3000,
        "objetivos": ["mejorar seguridad", "conocer normativa"]
    }),
    db: Session = Depends(get_db)
):
    tipo_uso = datos.get("tipo_uso", "urbano").lower()
    perfil_info = PERFILES.get(tipo_uso, PERFILES["urbano"])

    # Determinar nivel segun experiencia
    anos = datos.get("anos_experiencia", 0)
    nivel = "basico" if anos < 2 else "intermedio" if anos < 5 else "avanzado"

    usuario_id = str(uuid.uuid4())

    try:
        db.execute(text("""
            INSERT INTO usuarios (id, nombre, email, provincia, tipo_moto, anos_experiencia, nivel)
            VALUES (:id, :nombre, :email, :provincia, :tipo_moto, :anos, :nivel)
            ON CONFLICT DO NOTHING
        """), {
            "id": usuario_id,
            "nombre": datos.get("nombre", "Motociclista"),
            "email": datos.get("email", f"{usuario_id[:8]}@motoedu.ec"),
            "provincia": datos.get("zona", "Azuay"),
            "tipo_moto": datos.get("tipo_uso", "urbano"),
            "anos": anos,
            "nivel": nivel
        })
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error guardando usuario: {e}")

    return {
        "usuario_id": usuario_id,
        "perfil_asignado": perfil_info["nombre"],
        "nivel": nivel,
        "tipo_uso": tipo_uso,
        "motos_tipicas": perfil_info["motos"],
        "nivel_riesgo": perfil_info["riesgo"],
        "mensaje": f"Bienvenido {datos.get('nombre','Motociclista')} — perfil {perfil_info['nombre']} configurado",
        "siguiente_paso": "/m2/educacion/lecciones"
    }


@router.get("/{usuario_id}", summary="Obtiene el perfil de un usuario")
def obtener_perfil(usuario_id: str, db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT * FROM usuarios WHERE id = :id"
    ), {"id": usuario_id}).mappings().first()
    if not result:
        return {"error": "Usuario no encontrado"}
    return dict(result)


@router.get("/", summary="Lista todos los perfiles disponibles")
def listar_perfiles():
    return {"perfiles": PERFILES}
