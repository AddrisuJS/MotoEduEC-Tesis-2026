"""
M13 — ESTADO DEL PERFIL (M1)

PROBLEMA QUE RESUELVE
El asistente de onboarding (/perfil) vuelve a mostrarse cada vez que el
usuario inicia sesion, aunque ya lo haya completado. La causa es que la
comprobacion depende de localStorage ("motoeduc_usuario_id" y
"motoeduc_perfil"), y cerrarSesion() borra ambas claves. Al volver a
entrar, el navegador no tiene rastro del perfil y el asistente arranca
de cero.

SOLUCION
Consultar al servidor, que es la unica fuente de verdad. Este endpoint
responde si el usuario ya tiene perfil registrado en la tabla usuarios.

Router SEPARADO: no modifica perfil.py.
Prefijo: /m13/perfil
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.database import get_db

router = APIRouter(prefix="/m13/perfil", tags=["M13 Estado del perfil"])


@router.get("/estado/{usuario_auth_id}", summary="Indica si el usuario ya completo el onboarding")
def estado(usuario_auth_id: int, db: Session = Depends(get_db)):
    """Cruza usuarios_auth con usuarios (perfil M1) por correo electronico."""
    auth = db.execute(
        text("SELECT id, nombre, email FROM usuarios_auth WHERE id = :i"),
        {"i": usuario_auth_id},
    ).mappings().first()
    if not auth:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    perfil = db.execute(text("""
        SELECT id, nombre, provincia, tipo_moto, anos_experiencia, nivel, created_at
          FROM usuarios WHERE LOWER(email) = LOWER(:e)
         ORDER BY created_at DESC LIMIT 1
    """), {"e": auth["email"]}).mappings().first()

    if not perfil:
        return {"tiene_perfil": False, "perfil_completo": False,
                "usuario_auth_id": usuario_auth_id,
                "fase": "sin_perfil", "siguiente_paso": "/perfil"}

    p = dict(perfil)
    # Completo = tiene los campos que el onboarding recoge
    completo = all(p.get(k) not in (None, "") for k in
                   ("tipo_moto", "anos_experiencia", "nivel"))

    # ── Adonde enviar al usuario ───────────────────────────────────────
    # Enviar siempre a /evaluacion seria incorrecto: quien ya la rindio
    # llegaria a una pantalla sin nada que hacer. El destino depende de
    # la fase del experimento en que se encuentra y de su grupo.
    fases = {r["fase"] for r in db.execute(
        text("SELECT fase FROM piloto_evaluaciones WHERE usuario_id = :i"),
        {"i": usuario_auth_id}).mappings().all()}

    grupo = db.execute(text("SELECT COALESCE(grupo,'intervencion') FROM usuarios_auth WHERE id = :i"),
                       {"i": usuario_auth_id}).scalar()

    if not completo:
        fase, destino = "perfil_incompleto", "/perfil"
    elif "pretest" not in fases:
        fase, destino = "pendiente_pretest", "/evaluacion"
    elif "postest" not in fases:
        # En intervencion toca aprender; el control solo espera el postest
        fase = "en_intervencion"
        destino = "/educacion" if grupo == "intervencion" else "/evaluacion"
    else:
        fase, destino = "completado", "/mis-evaluaciones"

    return {
        "tiene_perfil": True,
        "perfil_completo": completo,
        "usuario_auth_id": usuario_auth_id,
        "perfil_id": str(p["id"]),
        "perfil": {k: (str(v) if k == "id" else v) for k, v in p.items()},
        "grupo": grupo,
        "pretest_hecho": "pretest" in fases,
        "postest_hecho": "postest" in fases,
        "fase": fase,
        "siguiente_paso": destino,
    }


class Vinculo(BaseModel):
    usuario_auth_id: int
    perfil_id: str


@router.post("/vincular", summary="Vincula un perfil recien creado con la cuenta del usuario")
def vincular(body: Vinculo, db: Session = Depends(get_db)):
    """El onboarding crea el perfil en la tabla usuarios SIN correo, por lo
    que queda huerfano: no se puede saber a que cuenta pertenece y el
    asistente vuelve a mostrarse en cada inicio de sesion.

    Este endpoint escribe el correo y el nombre de la cuenta autenticada
    sobre el perfil recien creado, cerrando el vinculo.

    Es aditivo: no modifica perfil.py ni el endpoint de creacion.
    """
    auth = db.execute(
        text("SELECT id, nombre, email FROM usuarios_auth WHERE id = :i"),
        {"i": body.usuario_auth_id},
    ).mappings().first()
    if not auth:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    r = db.execute(text("""
        UPDATE usuarios
           SET email  = :e,
               nombre = CASE WHEN nombre IS NULL OR nombre = '' OR nombre = 'Motociclista'
                             THEN :n ELSE nombre END
         WHERE id::text = :pid
        RETURNING id
    """), {"e": auth["email"], "n": auth["nombre"], "pid": body.perfil_id}).fetchone()

    if not r:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    db.commit()
    return {"ok": True, "usuario_auth_id": body.usuario_auth_id,
            "perfil_id": body.perfil_id, "email": auth["email"]}
