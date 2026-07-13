"""
M9 — EXPERIMENTO MotoEdu EC
Pretest → 3 dias de intervencion → Postest, todo dentro de la app.
La calificacion ocurre EN EL SERVIDOR: el frontend nunca recibe las
respuestas correctas, para no contaminar el postest.
Sprint 5 — UPS Cuenca 2026
"""
import json
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter(prefix="/m9/experimento", tags=["M9 — Experimento Piloto"])

DIAS_INTERVENCION = 3   # dias entre pretest y desbloqueo del postest
TOTAL_PREGUNTAS   = 15


def _evaluaciones(usuario_id: int, db: Session) -> dict:
    rows = db.execute(text("""
        SELECT fase, score, total, creado_en FROM piloto_evaluaciones WHERE usuario_id=:u
    """), {"u": usuario_id}).fetchall()
    return {r[0]: {"score": r[1], "total": r[2], "fecha": r[3]} for r in rows}


@router.get("/estado/{usuario_id}")
def estado(usuario_id: int, db: Session = Depends(get_db)):
    """Estado del participante en el experimento: que fase le toca."""
    ev = _evaluaciones(usuario_id, db)
    pre, post = ev.get("pretest"), ev.get("postest")

    postest_disponible, dias_restantes, fecha_desbloqueo = False, None, None
    if pre and not post:
        desbloqueo = pre["fecha"] + timedelta(days=DIAS_INTERVENCION)
        fecha_desbloqueo = desbloqueo.strftime("%d/%m/%Y")
        postest_disponible = datetime.now() >= desbloqueo
        if not postest_disponible:
            dias_restantes = max(0, (desbloqueo - datetime.now()).days + 1)

    resultado = {
        "pretest_hecho": pre is not None,
        "postest_hecho": post is not None,
        "postest_disponible": postest_disponible,
        "dias_restantes": dias_restantes,
        "fecha_desbloqueo": fecha_desbloqueo,
        "fase_actual": ("completado" if post else
                        "postest" if postest_disponible else
                        "intervencion" if pre else "pretest"),
    }
    if post:  # solo al completar todo se revelan los scores
        mejora = round((post["score"] - pre["score"]) / max(pre["score"], 1) * 100, 1)
        resultado["resultados"] = {
            "pretest": pre["score"], "postest": post["score"],
            "total": post["total"], "mejora_pct": mejora,
        }
    return resultado


@router.get("/preguntas")
def preguntas(db: Session = Depends(get_db)):
    """Las 15 preguntas congeladas del piloto. SIN el campo de respuesta correcta."""
    rows = db.execute(text("""
        SELECT pp.orden, pv.id, pv.pregunta, pv.respuesta_correcta,
               pv.opcion_b, pv.opcion_c, pv.opcion_d, c.nombre
        FROM piloto_preguntas pp
        JOIN preguntas_viales pv ON pv.id = pp.pregunta_id
        LEFT JOIN categorias_pregunta c ON c.id = pv.categoria_id
        ORDER BY pp.orden
    """)).fetchall()
    if len(rows) < TOTAL_PREGUNTAS:
        raise HTTPException(503, f"Solo hay {len(rows)} preguntas del piloto — correr la migracion M9")
    salida = []
    for r in rows:
        opciones = [o for o in [r[3], r[4], r[5], r[6]] if o]
        random.shuffle(opciones)
        salida.append({"orden": r[0], "pregunta_id": r[1], "pregunta": r[2],
                       "opciones": opciones, "categoria": r[7] or "General"})
    return {"total": len(salida), "preguntas": salida}


class RespuestaIn(BaseModel):
    pregunta_id: int
    respuesta: str


class EnvioIn(BaseModel):
    usuario_id: int
    fase: str                       # 'pretest' | 'postest'
    respuestas: list[RespuestaIn]


@router.post("/enviar")
def enviar(datos: EnvioIn, db: Session = Depends(get_db)):
    """Recibe las 15 respuestas, califica en servidor y registra la fase."""
    if datos.fase not in ("pretest", "postest"):
        raise HTTPException(400, "Fase invalida")

    ev = _evaluaciones(datos.usuario_id, db)
    if datos.fase in ev:
        raise HTTPException(409, f"El {datos.fase} ya fue registrado — no se puede repetir")
    if datos.fase == "postest":
        pre = ev.get("pretest")
        if not pre:
            raise HTTPException(409, "Primero debe completar el pretest")
        if datetime.now() < pre["fecha"] + timedelta(days=DIAS_INTERVENCION):
            raise HTTPException(423, f"El postest se desbloquea {DIAS_INTERVENCION} dias despues del pretest")
    if len(datos.respuestas) != TOTAL_PREGUNTAS:
        raise HTTPException(400, f"Se esperan {TOTAL_PREGUNTAS} respuestas")

    correctas_map = {r[0]: r[1] for r in db.execute(text("""
        SELECT pv.id, pv.respuesta_correcta
        FROM piloto_preguntas pp JOIN preguntas_viales pv ON pv.id = pp.pregunta_id
    """)).fetchall()}

    score, detalles = 0, []
    for resp in datos.respuestas:
        correcta_txt = correctas_map.get(resp.pregunta_id)
        if correcta_txt is None:
            raise HTTPException(400, f"Pregunta {resp.pregunta_id} no pertenece al piloto")
        es_correcta = resp.respuesta.strip() == correcta_txt.strip()
        score += 1 if es_correcta else 0
        detalles.append({"pregunta_id": resp.pregunta_id,
                         "respuesta": resp.respuesta, "correcta": es_correcta})

    db.execute(text("""
        INSERT INTO piloto_evaluaciones (usuario_id, fase, score, total, detalles)
        VALUES (:u, :f, :s, :t, :d)
    """), {"u": datos.usuario_id, "f": datos.fase, "s": score,
           "t": TOTAL_PREGUNTAS, "d": json.dumps(detalles)})
    db.commit()

    if datos.fase == "pretest":
        # CRITICO: no revelar el score ni las correctas — evita contaminar el postest
        return {"ok": True, "fase": "pretest", "mensaje":
                "Evaluacion inicial registrada. Ahora aprende con la app durante "
                f"{DIAS_INTERVENCION} dias: lecciones, asistente y arcade. El postest se "
                "desbloqueara automaticamente."}

    pre = _evaluaciones(datos.usuario_id, db)["pretest"]
    mejora = round((score - pre["score"]) / max(pre["score"], 1) * 100, 1)
    return {"ok": True, "fase": "postest",
            "pretest": pre["score"], "postest": score, "total": TOTAL_PREGUNTAS,
            "mejora_pct": mejora}


@router.get("/resultados")
def resultados_agregados(db: Session = Depends(get_db)):
    """Pares pretest-postest para el analisis estadistico (uso del investigador)."""
    rows = db.execute(text("""
        SELECT u.id, u.nombre,
               MAX(CASE WHEN e.fase='pretest' THEN e.score END) AS pre,
               MAX(CASE WHEN e.fase='postest' THEN e.score END) AS post,
               MAX(CASE WHEN e.fase='pretest' THEN e.creado_en END) AS fecha_pre,
               MAX(CASE WHEN e.fase='postest' THEN e.creado_en END) AS fecha_post
        FROM piloto_evaluaciones e JOIN usuarios_auth u ON u.id = e.usuario_id
        GROUP BY u.id, u.nombre ORDER BY u.id
    """)).fetchall()
    pares = [{"usuario_id": r[0], "nombre": r[1], "pretest": r[2], "postest": r[3],
              "fecha_pretest": str(r[4]) if r[4] else None,
              "fecha_postest": str(r[5]) if r[5] else None,
              "completo": r[2] is not None and r[3] is not None} for r in rows]
    completos = [p for p in pares if p["completo"]]
    return {"participantes": len(pares), "completos": len(completos), "pares": pares}
