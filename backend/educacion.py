"""
M2 — Educacion Vial Personalizada
Sprint 2 — Lecciones + Quizzes + Sistema de Progreso
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import generar_leccion, generar_quiz
from typing import Optional
import asyncio

router = APIRouter()

CATEGORIAS = [
    {
        "id": 1,
        "nombre": "Normativa LOTTTSV y Velocidades",
        "descripcion": "Velocidades maximas, senales de transito, licencias, infracciones y SOAT",
        "icono": "📋",
        "insignia_id": 2,
        "insignia_nombre": "Experto LOTTTSV",
        "puntos_insignia": 100
    },
    {
        "id": 2,
        "nombre": "Conduccion Segura",
        "descripcion": "Tecnicas de frenado, curvas, adelantamiento, distancia de seguimiento",
        "icono": "🏍️",
        "insignia_id": None,
        "insignia_nombre": "Conductor Seguro",
        "puntos_insignia": 75
    },
    {
        "id": 3,
        "nombre": "Conduccion en Lluvia",
        "descripcion": "Tecnicas especificas para piso mojado, aquaplaning, visibilidad bajo lluvia",
        "icono": "🌧️",
        "insignia_id": 3,
        "insignia_nombre": "Conductor de Lluvia",
        "puntos_insignia": 75
    },
    {
        "id": 4,
        "nombre": "Equipamiento de Seguridad",
        "descripcion": "Cascos certificados, chaquetas CE, guantes, botas y protecciones",
        "icono": "🪖",
        "insignia_id": 9,
        "insignia_nombre": "Seguridad Total",
        "puntos_insignia": 90
    },
    {
        "id": 5,
        "nombre": "Mantenimiento Preventivo",
        "descripcion": "Revision FINE-C, llantas, cadena, frenos, niveles de aceite",
        "icono": "🔧",
        "insignia_id": None,
        "insignia_nombre": "Mecanico Basico",
        "puntos_insignia": 60
    }
]


@router.get("/categorias", summary="Lista las 5 categorias de educacion vial")
def listar_categorias(db: Session = Depends(get_db)):
    return {
        "total": len(CATEGORIAS),
        "categorias": CATEGORIAS,
        "mensaje": "Completa cada categoria para desbloquear insignias y subir de nivel"
    }


@router.post("/leccion", summary="Genera una leccion personalizada con Claude API")
async def obtener_leccion(
    datos: dict = Body(..., example={
        "categoria": "Normativa LOTTTSV y Velocidades",
        "perfil": {
            "nombre": "Carlos",
            "tipo_uso": "delivery",
            "anos_experiencia": 2,
            "moto_actual": "Honda CB100",
            "zona": "Guayas",
            "nivel": "basico"
        }
    }),
    db: Session = Depends(get_db)
):
    categoria = datos.get("categoria", CATEGORIAS[0]["nombre"])
    perfil    = datos.get("perfil", {})
    nivel     = perfil.get("nivel", "basico")

    leccion = await generar_leccion(categoria, perfil, nivel)

    return {
        "categoria":  categoria,
        "nivel":      nivel,
        "perfil":     perfil.get("tipo_uso", "urbano"),
        "leccion":    leccion,
        "modo_ia":    "claude_api" if not leccion.get("modo") else "mock"
    }


@router.post("/quiz", summary="Genera un quiz de 10 preguntas con Claude API")
async def obtener_quiz(
    datos: dict = Body(..., example={
        "categoria": "Normativa LOTTTSV y Velocidades",
        "perfil": {
            "tipo_uso": "delivery",
            "anos_experiencia": 2,
            "nivel": "basico"
        },
        "n_preguntas": 10
    })
):
    categoria   = datos.get("categoria", CATEGORIAS[0]["nombre"])
    perfil      = datos.get("perfil", {})
    n_preguntas = datos.get("n_preguntas", 10)

    preguntas = await generar_quiz(categoria, perfil, n=n_preguntas)

    return {
        "categoria":       categoria,
        "perfil":          perfil.get("tipo_uso", "urbano"),
        "total_preguntas": len(preguntas),
        "quiz":            preguntas,
        "instrucciones":   "Responde cada pregunta. Al finalizar se calcula tu puntaje y retroalimentacion personalizada."
    }


@router.post("/progreso", summary="Registra el progreso de una evaluacion")
def registrar_progreso(
    datos: dict = Body(..., example={
        "usuario_id": "uuid-del-usuario",
        "pregunta_id": 1,
        "respuesta_dada": "50 km/h",
        "correcta": True,
        "tiempo_seg": 12,
        "categoria": "Normativa LOTTTSV y Velocidades"
    }),
    db: Session = Depends(get_db)
):
    usuario_id = datos.get("usuario_id")
    correcta   = datos.get("correcta", False)
    puntos     = 20 if correcta else 0

    try:
        # Registrar evaluacion
        db.execute(text("""
            INSERT INTO historial_evaluaciones
                (usuario_id, pregunta_id, respuesta_dada, correcta, tiempo_seg)
            VALUES (:uid, :pid, :resp, :correcta, :tiempo)
        """), {
            "uid":      usuario_id,
            "pid":      datos.get("pregunta_id", 1),
            "resp":     datos.get("respuesta_dada", ""),
            "correcta": correcta,
            "tiempo":   datos.get("tiempo_seg", 0)
        })

        # Actualizar puntos del usuario
        if puntos > 0:
            db.execute(text("""
                UPDATE usuarios SET puntos_acumulados = puntos_acumulados + :pts WHERE id = :uid
            """), {"pts": puntos, "uid": usuario_id})

        db.commit()

        # Verificar si merece insignia (>= 70% en la categoria)
        stats = db.execute(text("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN h.correcta THEN 1 ELSE 0 END) AS correctas
            FROM historial_evaluaciones h
            JOIN preguntas_viales p ON h.pregunta_id = p.id
            JOIN categorias_pregunta c ON p.categoria_id = c.id
            WHERE h.usuario_id = :uid
              AND LOWER(c.nombre) LIKE LOWER(:cat)
        """), {"uid": usuario_id, "cat": f"%{datos.get('categoria','')[:15]}%"}).mappings().first()

        insignia_desbloqueada = None
        if stats and stats["total"] >= 5:
            pct = 100 * stats["correctas"] / stats["total"]
            if pct >= 70:
                cat_nombre = datos.get("categoria", "")
                for cat in CATEGORIAS:
                    if cat["nombre"] == cat_nombre and cat["insignia_nombre"]:
                        insignia_desbloqueada = {
                            "nombre":  cat["insignia_nombre"],
                            "puntos":  cat["puntos_insignia"],
                            "mensaje": f"Felicitaciones! Desbloqueaste la insignia {cat['insignia_nombre']}"
                        }
                        # Dar los puntos de la insignia
                        db.execute(text("""
                            UPDATE usuarios SET puntos_acumulados = puntos_acumulados + :pts WHERE id = :uid
                        """), {"pts": cat["puntos_insignia"], "uid": usuario_id})
                        db.commit()
                        break

        return {
            "registrado":            True,
            "correcta":              correcta,
            "puntos_ganados":        puntos,
            "insignia_desbloqueada": insignia_desbloqueada,
            "retroalimentacion":     "Correcto!" if correcta else "Incorrecto. Revisa la leccion para reforzar este tema."
        }

    except Exception as e:
        db.rollback()
        return {"error": str(e), "registrado": False}


@router.get("/progreso/{usuario_id}", summary="Progreso del usuario por categoria")
def ver_progreso(usuario_id: str, db: Session = Depends(get_db)):
    progreso_cats = []
    for cat in CATEGORIAS:
        stats = db.execute(text("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN h.correcta THEN 1 ELSE 0 END) AS correctas
            FROM historial_evaluaciones h
            JOIN preguntas_viales p ON h.pregunta_id = p.id
            JOIN categorias_pregunta c ON p.categoria_id = c.id
            WHERE h.usuario_id = :uid
              AND LOWER(c.nombre) LIKE LOWER(:cat)
        """), {"uid": usuario_id, "cat": f"%{cat['nombre'][:15]}%"}).mappings().first()

        total     = stats["total"] if stats else 0
        correctas = stats["correctas"] if stats else 0
        pct       = round(100 * correctas / total, 1) if total > 0 else 0

        progreso_cats.append({
            "categoria":      cat["nombre"],
            "icono":          cat["icono"],
            "total_resp":     total,
            "correctas":      correctas,
            "pct_acierto":    pct,
            "insignia_logro": pct >= 70,
            "insignia_nombre":cat["insignia_nombre"]
        })

    return {"usuario_id": usuario_id, "progreso_por_categoria": progreso_cats}
