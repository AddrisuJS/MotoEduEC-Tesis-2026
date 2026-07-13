"""
DUELOS 1v1 — MotoEdu EC
Reta a otro motociclista: ambos responden LAS MISMAS 5 preguntas
(congeladas al crear el duelo). Gana quien haga más puntos.
Premios: ganador +200 XP, perdedor +50 XP, empate +100 XP c/u.
Sprint 5 — UPS Cuenca 2026
"""
import json
import random
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter(prefix="/m8/duelos", tags=["M8 — Duelos 1v1"])

XP_GANADOR, XP_PERDEDOR, XP_EMPATE = 200, 50, 100
PREGUNTAS_POR_DUELO = 5


def _sumar_xp(usuario_id: int, xp: int, db: Session):
    """Suma XP al arcade_stats (crea la fila si no existe, sin tocar la racha)."""
    existe = db.execute(text("SELECT 1 FROM arcade_stats WHERE usuario_id=:u"),
                        {"u": usuario_id}).fetchone()
    if existe:
        db.execute(text("UPDATE arcade_stats SET xp_total = xp_total + :x WHERE usuario_id=:u"),
                   {"x": xp, "u": usuario_id})
    else:
        db.execute(text("""
            INSERT INTO arcade_stats (usuario_id, xp_total, partidas, aciertos_total,
                                      racha_actual, racha_maxima, ultima_fecha)
            VALUES (:u, :x, 0, 0, 0, 0, :hoy)
        """), {"u": usuario_id, "x": xp, "hoy": date.today()})


def _preguntas_por_ids(ids: list, db: Session) -> list:
    rows = db.execute(text("""
        SELECT p.id, p.pregunta, p.respuesta_correcta, p.opcion_b, p.opcion_c, p.opcion_d,
               p.explicacion, c.nombre
        FROM preguntas_viales p
        LEFT JOIN categorias_pregunta c ON c.id = p.categoria_id
        WHERE p.id = ANY(:ids)
    """), {"ids": ids}).fetchall()
    orden = {pid: i for i, pid in enumerate(ids)}
    rows = sorted(rows, key=lambda r: orden.get(r[0], 99))
    salida = []
    for r in rows:
        opciones = [o for o in [r[2], r[3], r[4], r[5]] if o]
        random.shuffle(opciones)
        salida.append({"id": r[0], "pregunta": r[1], "opciones": opciones,
                       "correcta": r[2], "explicacion": r[6] or "", "categoria": r[7] or "General"})
    return salida


@router.get("/rivales/{usuario_id}")
def rivales(usuario_id: int, db: Session = Depends(get_db)):
    """Participantes disponibles para retar, con su XP para elegir víctima."""
    rows = db.execute(text("""
        SELECT u.id, u.nombre, COALESCE(s.xp_total,0)
        FROM usuarios_auth u
        LEFT JOIN arcade_stats s ON s.usuario_id = u.id
        WHERE u.rol = 'participante' AND u.id != :u
        ORDER BY s.xp_total DESC NULLS LAST
    """), {"u": usuario_id}).fetchall()
    return {"rivales": [{"id": r[0], "nombre": r[1], "xp": r[2]} for r in rows]}


class CrearIn(BaseModel):
    retador_id: int
    rival_id: int


@router.post("/crear")
def crear(datos: CrearIn, db: Session = Depends(get_db)):
    """Crea el duelo con 5 preguntas congeladas. El retador juega de inmediato."""
    if datos.retador_id == datos.rival_id:
        raise HTTPException(400, "No puedes retarte a ti mismo")
    abierto = db.execute(text("""
        SELECT id FROM duelos
        WHERE retador_id=:a AND rival_id=:b AND estado != 'completado'
    """), {"a": datos.retador_id, "b": datos.rival_id}).fetchone()
    if abierto:
        raise HTTPException(409, "Ya tienes un duelo abierto con este rival")

    ids = [r[0] for r in db.execute(text(
        "SELECT id FROM preguntas_viales WHERE activa=TRUE ORDER BY RANDOM() LIMIT :n"
    ), {"n": PREGUNTAS_POR_DUELO}).fetchall()]
    row = db.execute(text("""
        INSERT INTO duelos (retador_id, rival_id, pregunta_ids, estado)
        VALUES (:a, :b, :p, 'pendiente') RETURNING id
    """), {"a": datos.retador_id, "b": datos.rival_id, "p": json.dumps(ids)}).fetchone()
    db.commit()
    return {"ok": True, "duelo_id": row[0]}


@router.get("/mis-duelos/{usuario_id}")
def mis_duelos(usuario_id: int, db: Session = Depends(get_db)):
    """Duelos del usuario: por jugar, esperando al otro, e historial con W/L."""
    rows = db.execute(text("""
        SELECT d.id, d.retador_id, r1.nombre, d.rival_id, r2.nombre,
               d.puntos_retador, d.puntos_rival, d.estado, d.ganador_id, d.creado_en
        FROM duelos d
        JOIN usuarios_auth r1 ON r1.id = d.retador_id
        JOIN usuarios_auth r2 ON r2.id = d.rival_id
        WHERE d.retador_id=:u OR d.rival_id=:u
        ORDER BY d.creado_en DESC LIMIT 30
    """), {"u": usuario_id}).fetchall()
    duelos = []
    for r in rows:
        soy_retador = r[1] == usuario_id
        mi_punto = r[5] if soy_retador else r[6]
        duelos.append({
            "id": r[0], "oponente": r[4] if soy_retador else r[2],
            "estado": r[7],
            "me_toca_jugar": (r[7] != "completado") and (mi_punto is None),
            "mis_puntos": mi_punto,
            "puntos_oponente": r[6] if soy_retador else r[5],
            "resultado": None if r[7] != "completado" else
                         ("empate" if r[8] is None else ("gane" if r[8] == usuario_id else "perdi")),
            "fecha": str(r[9])[:16],
        })
    return {"duelos": duelos,
            "pendientes": sum(1 for d in duelos if d["me_toca_jugar"])}


@router.get("/{duelo_id}/preguntas")
def preguntas_duelo(duelo_id: int, db: Session = Depends(get_db)):
    d = db.execute(text("SELECT pregunta_ids, estado FROM duelos WHERE id=:d"),
                   {"d": duelo_id}).fetchone()
    if not d:
        raise HTTPException(404, "Duelo no existe")
    if d[1] == "completado":
        raise HTTPException(409, "Este duelo ya terminó")
    ids = d[0] if isinstance(d[0], list) else json.loads(d[0])
    return {"segundos_por_pregunta": 15, "preguntas": _preguntas_por_ids(ids, db)}


class JugarIn(BaseModel):
    usuario_id: int
    aciertos: int
    segundos_restantes_suma: int = 0


@router.post("/{duelo_id}/jugar")
def jugar(duelo_id: int, datos: JugarIn, db: Session = Depends(get_db)):
    d = db.execute(text("""
        SELECT retador_id, rival_id, puntos_retador, puntos_rival, estado
        FROM duelos WHERE id=:d
    """), {"d": duelo_id}).fetchone()
    if not d:
        raise HTTPException(404, "Duelo no existe")
    if d[4] == "completado":
        raise HTTPException(409, "Este duelo ya terminó")

    soy_retador = datos.usuario_id == d[0]
    soy_rival   = datos.usuario_id == d[1]
    if not (soy_retador or soy_rival):
        raise HTTPException(403, "No eres parte de este duelo")
    if (soy_retador and d[2] is not None) or (soy_rival and d[3] is not None):
        raise HTTPException(409, "Ya jugaste este duelo")

    puntos = datos.aciertos * 100 + min(datos.segundos_restantes_suma * 10, 500)
    campo_p = "puntos_retador" if soy_retador else "puntos_rival"
    campo_a = "aciertos_retador" if soy_retador else "aciertos_rival"
    db.execute(text(f"UPDATE duelos SET {campo_p}=:p, {campo_a}=:a WHERE id=:d"),
               {"p": puntos, "a": datos.aciertos, "d": duelo_id})

    otro = d[3] if soy_retador else d[2]
    if otro is None:
        db.execute(text("UPDATE duelos SET estado='esperando_rival' WHERE id=:d"), {"d": duelo_id})
        db.commit()
        return {"ok": True, "puntos": puntos, "estado": "esperando_rival",
                "mensaje": "¡Jugado! Ahora le toca a tu rival. Te avisamos el resultado en Mis Duelos."}

    # Ambos jugaron → resolver
    p_ret = puntos if soy_retador else d[2]
    p_riv = puntos if soy_rival else d[3]
    if p_ret > p_riv:
        ganador, perdedor = d[0], d[1]
    elif p_riv > p_ret:
        ganador, perdedor = d[1], d[0]
    else:
        ganador = None

    if ganador:
        _sumar_xp(ganador, XP_GANADOR, db)
        _sumar_xp(perdedor, XP_PERDEDOR, db)
    else:
        _sumar_xp(d[0], XP_EMPATE, db)
        _sumar_xp(d[1], XP_EMPATE, db)

    db.execute(text("""
        UPDATE duelos SET estado='completado', ganador_id=:g, resuelto_en=NOW() WHERE id=:d
    """), {"g": ganador, "d": duelo_id})
    db.commit()

    mi_resultado = "empate" if ganador is None else ("gane" if ganador == datos.usuario_id else "perdi")
    return {"ok": True, "puntos": puntos, "estado": "completado",
            "resultado": mi_resultado,
            "xp_ganado": XP_EMPATE if ganador is None else (XP_GANADOR if mi_resultado == "gane" else XP_PERDEDOR),
            "puntos_retador": p_ret, "puntos_rival": p_riv}
