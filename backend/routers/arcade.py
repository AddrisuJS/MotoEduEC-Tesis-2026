"""
M8 — ARCADE MotoEdu EC
Duelo Relampago (quiz contrarreloj) + Desafio del Dia + Rachas + Top
Usa el banco de preguntas_viales (600) — cero costo de API.
Sprint 5 — UPS Cuenca 2026
"""
import random
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter(prefix="/m8/arcade", tags=["M8 — Arcade"])

PUNTOS_ACIERTO = 100      # base por respuesta correcta
BONUS_MAX = 150           # bonus máximo por velocidad (seg_restantes * 10)
MULTIPLICADOR_DESAFIO = 2 # el desafío del día paga doble


def _fila_a_pregunta(row) -> dict:
    """Convierte una fila de preguntas_viales en pregunta con opciones barajadas."""
    opciones = [o for o in [row[2], row[3], row[4], row[5]] if o]
    random.shuffle(opciones)
    return {
        "id": row[0],
        "pregunta": row[1],
        "opciones": opciones,
        "correcta": row[2],          # texto de la opción correcta
        "explicacion": row[6] or "",
        "categoria": row[7] or "General",
    }


@router.get("/quiz")
def quiz_relampago(n: int = 10, db: Session = Depends(get_db)):
    """Duelo Relámpago: n preguntas aleatorias del banco de 600."""
    rows = db.execute(text("""
        SELECT p.id, p.pregunta, p.respuesta_correcta, p.opcion_b, p.opcion_c, p.opcion_d,
               p.explicacion, c.nombre
        FROM preguntas_viales p
        LEFT JOIN categorias_pregunta c ON c.id = p.categoria_id
        WHERE p.activa = TRUE
        ORDER BY RANDOM() LIMIT :n
    """), {"n": min(max(n, 5), 20)}).fetchall()
    if not rows:
        raise HTTPException(503, "No hay preguntas en el banco")
    return {"modo": "relampago", "segundos_por_pregunta": 15,
            "preguntas": [_fila_a_pregunta(r) for r in rows]}


@router.get("/desafio")
def desafio_del_dia(usuario_id: int = 0, db: Session = Depends(get_db)):
    """Primer desafío del día: pregunta fija para todos, x2 XP.
    Si ya lo jugó hoy: Ronda Extra con 3 preguntas aleatorias a XP normal."""
    total = db.execute(text("SELECT COUNT(*) FROM preguntas_viales WHERE activa = TRUE")).scalar()
    if not total:
        raise HTTPException(503, "No hay preguntas en el banco")

    ya_jugado = False
    if usuario_id:
        ya_jugado = db.execute(text("""
            SELECT COUNT(*) FROM arcade_partidas
            WHERE usuario_id=:u AND modo='desafio' AND jugada_en::date = CURRENT_DATE
        """), {"u": usuario_id}).scalar() > 0

    if ya_jugado:
        rows = db.execute(text("""
            SELECT p.id, p.pregunta, p.respuesta_correcta, p.opcion_b, p.opcion_c, p.opcion_d,
                   p.explicacion, c.nombre
            FROM preguntas_viales p
            LEFT JOIN categorias_pregunta c ON c.id = p.categoria_id
            WHERE p.activa = TRUE ORDER BY RANDOM() LIMIT 3
        """)).fetchall()
        return {"modo": "relampago", "ronda_extra": True, "multiplicador": 1,
                "segundos_por_pregunta": 15,
                "preguntas": [_fila_a_pregunta(r) for r in rows]}

    offset = date.today().toordinal() % total
    row = db.execute(text("""
        SELECT p.id, p.pregunta, p.respuesta_correcta, p.opcion_b, p.opcion_c, p.opcion_d,
               p.explicacion, c.nombre
        FROM preguntas_viales p
        LEFT JOIN categorias_pregunta c ON c.id = p.categoria_id
        WHERE p.activa = TRUE ORDER BY p.id OFFSET :o LIMIT 1
    """), {"o": offset}).fetchone()
    return {"modo": "desafio", "ronda_extra": False, "fecha": str(date.today()),
            "multiplicador": MULTIPLICADOR_DESAFIO, "segundos_por_pregunta": 20,
            "preguntas": [_fila_a_pregunta(row)]}

class PartidaIn(BaseModel):
    usuario_id: int
    modo: str = "relampago"          # 'relampago' | 'desafio'
    aciertos: int
    total: int
    segundos_restantes_suma: int = 0 # suma de segundos sobrantes en aciertos


@router.post("/finalizar")
def finalizar_partida(datos: PartidaIn, db: Session = Depends(get_db)):
    """Registra la partida, calcula puntos, actualiza XP y racha, devuelve posición."""
    if datos.aciertos > datos.total or datos.total <= 0:
        raise HTTPException(400, "Datos de partida inválidos")

    bonus = min(datos.segundos_restantes_suma * 10, BONUS_MAX * max(datos.aciertos, 1))
    puntos = datos.aciertos * PUNTOS_ACIERTO + bonus
    if datos.modo == "desafio":
        puntos *= MULTIPLICADOR_DESAFIO

    # ── Racha: mismo día mantiene, día seguido suma, salto reinicia ──
    hoy = date.today()
    st = db.execute(text(
        "SELECT racha_actual, racha_maxima, ultima_fecha FROM arcade_stats WHERE usuario_id=:u"
    ), {"u": datos.usuario_id}).fetchone()

    if st is None:
        racha, racha_max = 1, 1
        db.execute(text("""
            INSERT INTO arcade_stats (usuario_id, xp_total, partidas, aciertos_total,
                                      racha_actual, racha_maxima, ultima_fecha)
            VALUES (:u, :xp, 1, :ac, 1, 1, :hoy)
        """), {"u": datos.usuario_id, "xp": puntos, "ac": datos.aciertos, "hoy": hoy})
    else:
        racha_prev, racha_max, ultima = st
        if ultima == hoy:
            racha = racha_prev
        elif ultima == hoy - timedelta(days=1):
            racha = racha_prev + 1
        else:
            racha = 1
        racha_max = max(racha_max or 0, racha)
        db.execute(text("""
            UPDATE arcade_stats
            SET xp_total = xp_total + :xp, partidas = partidas + 1,
                aciertos_total = aciertos_total + :ac,
                racha_actual = :r, racha_maxima = :rm, ultima_fecha = :hoy
            WHERE usuario_id = :u
        """), {"xp": puntos, "ac": datos.aciertos, "r": racha, "rm": racha_max,
               "hoy": hoy, "u": datos.usuario_id})

    db.execute(text("""
        INSERT INTO arcade_partidas (usuario_id, modo, puntos, aciertos, total)
        VALUES (:u, :m, :p, :a, :t)
    """), {"u": datos.usuario_id, "m": datos.modo, "p": puntos,
           "a": datos.aciertos, "t": datos.total})
    db.commit()

    xp_total = db.execute(text(
        "SELECT xp_total FROM arcade_stats WHERE usuario_id=:u"), {"u": datos.usuario_id}).scalar()
    posicion = db.execute(text(
        "SELECT COUNT(*)+1 FROM arcade_stats WHERE xp_total > :xp"), {"xp": xp_total}).scalar()

    return {"ok": True, "puntos_partida": puntos, "bonus_velocidad": bonus,
            "xp_total": xp_total, "racha_actual": racha, "racha_maxima": racha_max,
            "posicion_ranking": posicion}


@router.get("/top")
def leaderboard(limite: int = 20, db: Session = Depends(get_db)):
    """Top de XP con nombre, racha y partidas."""
    rows = db.execute(text("""
        SELECT u.id, u.nombre, s.xp_total, s.racha_actual, s.partidas, s.aciertos_total
        FROM arcade_stats s JOIN usuarios_auth u ON u.id = s.usuario_id
        ORDER BY s.xp_total DESC, s.aciertos_total DESC
        LIMIT :l
    """), {"l": min(limite, 50)}).fetchall()
    return {"top": [
        {"posicion": i + 1, "usuario_id": r[0], "nombre": r[1], "xp": r[2],
         "racha": r[3], "partidas": r[4], "aciertos": r[5]}
        for i, r in enumerate(rows)
    ]}


@router.get("/stats/{usuario_id}")
def stats_usuario(usuario_id: int, db: Session = Depends(get_db)):
    st = db.execute(text("""
        SELECT xp_total, partidas, aciertos_total, racha_actual, racha_maxima, ultima_fecha
        FROM arcade_stats WHERE usuario_id=:u
    """), {"u": usuario_id}).fetchone()
    if st is None:
        return {"xp_total": 0, "partidas": 0, "aciertos_total": 0,
                "racha_actual": 0, "racha_maxima": 0, "posicion": None,
                "racha_en_riesgo": False}
    posicion = db.execute(text(
        "SELECT COUNT(*)+1 FROM arcade_stats WHERE xp_total > :xp"), {"xp": st[0]}).scalar()
    en_riesgo = st[5] is not None and st[5] < date.today() and st[3] > 0
    return {"xp_total": st[0], "partidas": st[1], "aciertos_total": st[2],
            "racha_actual": st[3], "racha_maxima": st[4],
            "posicion": posicion, "racha_en_riesgo": en_riesgo}
