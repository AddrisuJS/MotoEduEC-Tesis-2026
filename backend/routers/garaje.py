"""
GARAJE VIRTUAL — MotoEdu EC
Piezas y equipo que se desbloquean con XP, rachas y partidas del Arcade.
El desbloqueo se calcula en vivo desde arcade_stats: cero mantenimiento.
Sprint 5 — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter(prefix="/m8/garaje", tags=["M8 — Garaje Virtual"])


@router.get("/{usuario_id}")
def garaje(usuario_id: int, db: Session = Depends(get_db)):
    st = db.execute(text("""
        SELECT COALESCE(xp_total,0), COALESCE(racha_maxima,0), COALESCE(partidas,0)
        FROM arcade_stats WHERE usuario_id=:u
    """), {"u": usuario_id}).fetchone()
    xp, racha, partidas = (st[0], st[1], st[2]) if st else (0, 0, 0)
    progreso = {"xp": xp, "racha": racha, "partidas": partidas}

    items = db.execute(text("""
        SELECT id, nombre, icono, tipo, requisito_tipo, requisito_valor, descripcion, rareza
        FROM garaje_items ORDER BY requisito_tipo, requisito_valor
    """)).fetchall()

    salida, desbloqueados = [], 0
    for it in items:
        actual = progreso[it[4]]
        ok = actual >= it[5]
        desbloqueados += 1 if ok else 0
        salida.append({
            "id": it[0], "nombre": it[1], "icono": it[2], "tipo": it[3],
            "requisito_tipo": it[4], "requisito_valor": it[5],
            "descripcion": it[6], "rareza": it[7] or "comun", "desbloqueado": ok,
            "progreso_actual": min(actual, it[5]),
            "falta": max(0, it[5] - actual),
        })

    return {"stats": progreso,
            "desbloqueados": desbloqueados, "total": len(salida),
            "equipo": [i for i in salida if i["tipo"] == "equipo"],
            "moto":   [i for i in salida if i["tipo"] == "moto"]}
