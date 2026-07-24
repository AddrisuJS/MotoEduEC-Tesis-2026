"""
M10 â€” ADMINISTRACION DE GRUPOS DEL EXPERIMENTO
Permite al investigador (rol='admin') asignar cada participante al grupo
de INTERVENCION (usa la plataforma completa) o de CONTROL (solo pretest
y postest), desde la propia plataforma y no a mano en la base de datos.

Cada cambio se registra en piloto_grupo_log: quien lo hizo, cuando y por
que. Esa bitacora es la evidencia de la asignacion para el capitulo de
metodologia.

Prefijo: /m10/admin
"""
from typing import List, Optional
import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

# âš ï¸ AJUSTA ESTA LINEA para que sea igual a la de tus otros routers
# (mira el import de get_db en routers/experimento.py y copia el mismo).
try:
    from models.database import get_db
except ImportError:  # pragma: no cover
    from models.database import get_db

router = APIRouter(prefix="/m10/admin", tags=["M10 Administracion"])

GRUPOS_VALIDOS = ("intervencion", "control")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ utilidades â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _exigir_admin(db: Session, admin_id: int) -> dict:
    """Verifica que quien pide la accion sea el investigador."""
    row = db.execute(
        text("SELECT id, nombre, rol FROM usuarios_auth WHERE id = :i"),
        {"i": admin_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario administrador no encontrado")
    if row["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo el investigador puede asignar grupos")
    return dict(row)


def _cambiar_grupo(db: Session, usuario_id: int, grupo: str, admin_id: int,
                   motivo: Optional[str], confirmar: bool) -> dict:
    actual = db.execute(
        text("""SELECT u.id, u.nombre, u.grupo, u.rol,
                       (SELECT COUNT(*) FROM piloto_evaluaciones e
                         WHERE e.usuario_id = u.id) AS evaluaciones
                  FROM usuarios_auth u WHERE u.id = :i"""),
        {"i": usuario_id},
    ).mappings().first()

    if not actual:
        raise HTTPException(status_code=404, detail=f"Participante {usuario_id} no existe")
    if actual["rol"] == "admin":
        raise HTTPException(status_code=400, detail="El investigador no forma parte de ningun grupo")

    # Candado metodologico: si ya rindio evaluaciones, cambiarlo de grupo
    # contamina el experimento. Se permite, pero exige confirmacion explicita.
    if actual["evaluaciones"] > 0 and not confirmar:
        raise HTTPException(
            status_code=409,
            detail=(f"{actual['nombre']} ya tiene {actual['evaluaciones']} evaluacion(es) "
                    f"registrada(s). Cambiar su grupo ahora afecta la validez del "
                    f"experimento. Reenvia con confirmar=true si aun asi deseas hacerlo."),
        )

    if actual["grupo"] == grupo:
        return {"usuario_id": usuario_id, "nombre": actual["nombre"],
                "grupo": grupo, "cambio": False, "mensaje": "Ya estaba en ese grupo"}

    db.execute(
        text("""UPDATE usuarios_auth
                   SET grupo = :g, grupo_asignado_en = NOW()
                 WHERE id = :i"""),
        {"g": grupo, "i": usuario_id},
    )
    db.execute(
        text("""INSERT INTO piloto_grupo_log
                    (usuario_id, grupo_anterior, grupo_nuevo, cambiado_por, motivo)
                VALUES (:u, :ga, :gn, :por, :m)"""),
        {"u": usuario_id, "ga": actual["grupo"], "gn": grupo,
         "por": admin_id, "m": motivo},
    )
    return {"usuario_id": usuario_id, "nombre": actual["nombre"],
            "grupo_anterior": actual["grupo"], "grupo": grupo,
            "cambio": True, "mensaje": f"{actual['nombre']} movido a {grupo}"}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ esquemas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class CambioGrupo(BaseModel):
    grupo: str = Field(..., description="intervencion | control")
    admin_id: int
    motivo: Optional[str] = None
    confirmar: bool = False


class CambioMasivo(BaseModel):
    usuario_ids: List[int]
    grupo: str
    admin_id: int
    motivo: Optional[str] = None
    confirmar: bool = False


class Aleatorizar(BaseModel):
    admin_id: int
    semilla: Optional[int] = None
    solo_sin_evaluaciones: bool = True


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@router.get("/participantes", summary="Lista de participantes con su grupo y avance")
def listar_participantes(admin_id: int, db: Session = Depends(get_db)):
    _exigir_admin(db, admin_id)
    filas = db.execute(text("""
        SELECT u.id, u.nombre, u.email, u.grupo, u.tipo_uso, u.creado_en,
               pre.score AS pretest_score, pre.total AS pretest_total,
               pre.creado_en AS pretest_fecha,
               pos.score AS postest_score, pos.total AS postest_total,
               pos.creado_en AS postest_fecha
          FROM usuarios_auth u
          LEFT JOIN piloto_evaluaciones pre
                 ON pre.usuario_id = u.id AND pre.fase = 'pretest'
          LEFT JOIN piloto_evaluaciones pos
                 ON pos.usuario_id = u.id AND pos.fase = 'postest'
         WHERE u.rol <> 'admin'
         ORDER BY u.id
    """)).mappings().all()

    participantes = []
    for f in filas:
        d = dict(f)
        d["pretest_hecho"] = d["pretest_score"] is not None
        d["postest_hecho"] = d["postest_score"] is not None
        d["bloqueado"] = d["pretest_hecho"] or d["postest_hecho"]
        participantes.append(d)

    resumen = {
        "total": len(participantes),
        "intervencion": sum(1 for p in participantes if p["grupo"] == "intervencion"),
        "control": sum(1 for p in participantes if p["grupo"] == "control"),
        "pretest_completados": sum(1 for p in participantes if p["pretest_hecho"]),
        "postest_completados": sum(1 for p in participantes if p["postest_hecho"]),
    }
    return {"resumen": resumen, "participantes": participantes}


@router.patch("/participantes/{usuario_id}/grupo", summary="Cambiar el grupo de un participante")
def cambiar_grupo(usuario_id: int, body: CambioGrupo, db: Session = Depends(get_db)):
    if body.grupo not in GRUPOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"grupo debe ser uno de {GRUPOS_VALIDOS}")
    _exigir_admin(db, body.admin_id)
    r = _cambiar_grupo(db, usuario_id, body.grupo, body.admin_id, body.motivo, body.confirmar)
    db.commit()
    return r


@router.post("/participantes/grupo-masivo", summary="Asignar el mismo grupo a varios participantes")
def grupo_masivo(body: CambioMasivo, db: Session = Depends(get_db)):
    if body.grupo not in GRUPOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"grupo debe ser uno de {GRUPOS_VALIDOS}")
    _exigir_admin(db, body.admin_id)
    resultados, errores = [], []
    for uid in body.usuario_ids:
        try:
            resultados.append(_cambiar_grupo(db, uid, body.grupo, body.admin_id,
                                             body.motivo, body.confirmar))
        except HTTPException as e:
            errores.append({"usuario_id": uid, "error": e.detail})
    db.commit()
    return {"aplicados": len(resultados), "resultados": resultados, "errores": errores}


@router.post("/participantes/aleatorizar", summary="Asignacion aleatoria 50/50 (asignacion al azar)")
def aleatorizar(body: Aleatorizar, db: Session = Depends(get_db)):
    """Reparte al azar mitad y mitad. Por defecto SOLO toca a quienes aun no
    han rendido ninguna evaluacion, para no contaminar datos ya recogidos.
    La semilla queda registrada en el motivo: eso hace la asignacion
    reproducible y auditable."""
    _exigir_admin(db, body.admin_id)
    cond = "AND NOT EXISTS (SELECT 1 FROM piloto_evaluaciones e WHERE e.usuario_id = u.id)" \
        if body.solo_sin_evaluaciones else ""
    ids = [r["id"] for r in db.execute(text(
        f"SELECT u.id FROM usuarios_auth u WHERE u.rol <> 'admin' {cond} ORDER BY u.id"
    )).mappings().all()]

    if not ids:
        return {"asignados": 0, "mensaje": "No hay participantes elegibles para aleatorizar"}

    semilla = body.semilla if body.semilla is not None else random.randint(1, 999999)
    rnd = random.Random(semilla)
    rnd.shuffle(ids)
    mitad = len(ids) // 2
    plan = {uid: ("intervencion" if i < mitad else "control") for i, uid in enumerate(ids)}

    motivo = f"Asignacion aleatoria (semilla={semilla})"
    for uid, g in plan.items():
        _cambiar_grupo(db, uid, g, body.admin_id, motivo, confirmar=True)
    db.commit()
    return {"asignados": len(plan), "semilla": semilla,
            "intervencion": sum(1 for g in plan.values() if g == "intervencion"),
            "control": sum(1 for g in plan.values() if g == "control"),
            "detalle": plan}


@router.get("/bitacora", summary="Historial de cambios de grupo")
def bitacora(admin_id: int, db: Session = Depends(get_db)):
    _exigir_admin(db, admin_id)
    filas = db.execute(text("""
        SELECT l.id, l.usuario_id, u.nombre, l.grupo_anterior, l.grupo_nuevo,
               l.motivo, l.creado_en, a.nombre AS cambiado_por
          FROM piloto_grupo_log l
          JOIN usuarios_auth u ON u.id = l.usuario_id
          LEFT JOIN usuarios_auth a ON a.id = l.cambiado_por
         ORDER BY l.creado_en DESC LIMIT 200
    """)).mappings().all()
    return {"total": len(filas), "movimientos": [dict(f) for f in filas]}

