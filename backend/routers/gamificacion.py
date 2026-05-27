"""M7 — Gamificación Edutainment"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter()

INSIGNIAS = [
    {"id":1,"nombre":"Primera Leccion","descripcion":"Completa tu primera leccion educativa","puntos":50,"icono":"🎯"},
    {"id":2,"nombre":"Experto LOTTTSV","descripcion":"Aprueba la evaluacion de normativa con 100%","puntos":100,"icono":"📋"},
    {"id":3,"nombre":"Conductor de Lluvia","descripcion":"Completa el modulo de conduccion en lluvia","puntos":75,"icono":"🌧️"},
    {"id":4,"nombre":"Equipado","descripcion":"Revisa todo el catalogo de equipamiento","puntos":60,"icono":"🪖"},
    {"id":5,"nombre":"Motero Historico","descripcion":"Lee 3 narrativas de historia motera","puntos":80,"icono":"🏍️"},
    {"id":6,"nombre":"Quiz Master","descripcion":"Responde correctamente 50 preguntas","puntos":150,"icono":"⭐"},
    {"id":7,"nombre":"Perfil Completo","descripcion":"Completa todos los campos de tu perfil","puntos":40,"icono":"👤"},
    {"id":8,"nombre":"Recomendacion Inteligente","descripcion":"Usa el recomendador de motos","puntos":60,"icono":"🤖"},
    {"id":9,"nombre":"Seguridad Total","descripcion":"Completa el modulo de equipamiento","puntos":90,"icono":"🛡️"},
    {"id":10,"nombre":"Consultor RAG","descripcion":"Realiza 10 consultas al asistente experto","puntos":120,"icono":"💬"},
    {"id":11,"nombre":"Nivel Intermedio","descripcion":"Alcanza el nivel intermedio de conocimiento","puntos":200,"icono":"🥈"},
    {"id":12,"nombre":"Experto Vial","descripcion":"Completa todos los modulos educativos","puntos":500,"icono":"🏆"},
]

NIVELES = [
    {"nivel":1,"nombre":"Principiante","puntos_min":0,"puntos_max":199},
    {"nivel":2,"nombre":"Basico","puntos_min":200,"puntos_max":499},
    {"nivel":3,"nombre":"Intermedio","puntos_min":500,"puntos_max":999},
    {"nivel":4,"nombre":"Avanzado","puntos_min":1000,"puntos_max":1999},
    {"nivel":5,"nombre":"Experto Vial","puntos_min":2000,"puntos_max":99999},
]

@router.get("/insignias", summary="Lista las 12 insignias disponibles")
def listar_insignias():
    return {"total": len(INSIGNIAS), "insignias": INSIGNIAS}


@router.get("/niveles", summary="Lista los 5 niveles de competencia")
def listar_niveles():
    return {"niveles": NIVELES}


@router.get("/dashboard/{usuario_id}", summary="Dashboard de progreso del usuario")
def dashboard_usuario(usuario_id: str, db: Session = Depends(get_db)):
    usuario = db.execute(text(
        "SELECT * FROM usuarios WHERE id = :id"
    ), {"id": usuario_id}).mappings().first()

    if not usuario:
        return {"error": "Usuario no encontrado"}

    puntos = dict(usuario).get("puntos_acumulados", 0)
    nivel_actual = next((n for n in reversed(NIVELES) if puntos >= n["puntos_min"]), NIVELES[0])
    nivel_sig = next((n for n in NIVELES if n["puntos_min"] > puntos), None)

    historial = db.execute(text("""
        SELECT COUNT(*) AS total, SUM(CASE WHEN correcta THEN 1 ELSE 0 END) AS correctas
        FROM historial_evaluaciones WHERE usuario_id = :uid
    """), {"uid": usuario_id}).mappings().first()

    stats = dict(historial) if historial else {"total":0,"correctas":0}
    pct = round(100*stats["correctas"]/stats["total"],1) if stats["total"] else 0

    return {
        "usuario": dict(usuario),
        "puntos": puntos,
        "nivel_actual": nivel_actual,
        "nivel_siguiente": nivel_sig,
        "puntos_para_siguiente": (nivel_sig["puntos_min"] - puntos) if nivel_sig else 0,
        "evaluaciones": stats,
        "pct_acierto": pct,
        "insignias_disponibles": len(INSIGNIAS),
    }


@router.post("/otorgar-insignia", summary="Otorga una insignia al usuario")
def otorgar_insignia(datos: dict = Body(...), db: Session = Depends(get_db)):
    try:
        insignia = next((i for i in INSIGNIAS if i["id"] == datos.get("insignia_id")), None)
        if not insignia:
            return {"error": "Insignia no encontrada"}
        db.execute(text("""
            UPDATE usuarios SET puntos_acumulados = puntos_acumulados + :puntos WHERE id = :uid
        """), {"puntos": insignia["puntos"], "uid": datos.get("usuario_id")})
        db.commit()
        return {"insignia": insignia, "puntos_ganados": insignia["puntos"], "mensaje": f"Insignia {insignia['icono']} {insignia['nombre']} otorgada"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
