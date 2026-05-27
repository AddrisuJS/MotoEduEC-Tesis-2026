"""M2 — Educación Vial Personalizada"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import generar_leccion, generar_quiz
from typing import Optional
import asyncio

router = APIRouter()

CATEGORIAS = [
    "Normativa LOTTTSV y velocidades",
    "Conduccion segura y tecnicas de frenado",
    "Conduccion en lluvia y condiciones adversas",
    "Equipamiento de seguridad obligatorio",
    "Mantenimiento preventivo de la motocicleta",
]

@router.get("/categorias", summary="Lista las 5 categorias de educacion vial")
def listar_categorias():
    return {"categorias": CATEGORIAS, "total": len(CATEGORIAS)}


@router.post("/leccion", summary="Genera una leccion personalizada con IA")
async def obtener_leccion(
    datos: dict,
    db: Session = Depends(get_db)
):
    categoria = datos.get("categoria", CATEGORIAS[0])
    perfil = datos.get("perfil", {})
    nivel = datos.get("nivel", "basico")
    leccion = await generar_leccion(categoria, perfil, nivel)
    return {"categoria": categoria, "nivel": nivel, "leccion": leccion}


@router.post("/quiz", summary="Genera quiz de 10 preguntas con IA")
async def obtener_quiz(datos: dict):
    categoria = datos.get("categoria", CATEGORIAS[0])
    perfil = datos.get("perfil", {})
    preguntas = await generar_quiz(categoria, perfil, n=10)
    return {"categoria": categoria, "total_preguntas": len(preguntas), "quiz": preguntas}


@router.post("/progreso", summary="Registra el progreso de una leccion")
def registrar_progreso(datos: dict, db: Session = Depends(get_db)):
    try:
        db.execute(text("""
            INSERT INTO historial_evaluaciones (usuario_id, pregunta_id, respuesta_dada, correcta, tiempo_seg)
            VALUES (:uid, :pid, :resp, :correcta, :tiempo)
        """), {
            "uid": datos.get("usuario_id"),
            "pid": datos.get("pregunta_id", 1),
            "resp": datos.get("respuesta"),
            "correcta": datos.get("correcta", False),
            "tiempo": datos.get("tiempo_seg", 0)
        })
        db.commit()
        puntos = 20 if datos.get("correcta") else 0
        return {"mensaje": "Progreso registrado", "puntos_ganados": puntos}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
