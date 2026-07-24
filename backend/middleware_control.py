"""
GUARDIA DEL EXPERIMENTO — bloqueo del grupo CONTROL a nivel de API.

El bloqueo del frontend (useAuth) solo evita la navegacion: un participante
de control podria llamar los endpoints de juego directamente desde el
navegador o con curl, y contaminar sus propios datos. Este middleware lo
impide en el servidor, que es donde el bloqueo realmente cuenta para la
validez del cuasi-experimento.

Instalacion en backend/main.py (2 lineas, despues de crear `app`):

    from middleware_control import instalar_guardia_control
    instalar_guardia_control(app)

Si algo falla al importar la base, el middleware se desactiva solo y la API
sigue funcionando normalmente (nunca tumba el servidor).
"""
import json
import re
from typing import Optional

from starlette.responses import JSONResponse

# Prefijos que SOLO puede usar el grupo intervencion.
# Evaluacion (/m9), perfil (/m1) y auth quedan libres a proposito: el
# control tambien rinde pretest y postest.
RUTAS_BLOQUEADAS = (
    "/m8/arcade",
    "/m8/duelos",
    "/m8/ruta",
    "/m7/gamificacion",
    "/m2/educacion",
    "/m3/asistente",
    "/garaje",
)

_NUM = re.compile(r"/(\d+)(?:/|$)")


def _id_de_la_ruta(path: str) -> Optional[int]:
    """Toma el ultimo segmento numerico del path: /m8/arcade/stats/233 -> 233"""
    encontrados = _NUM.findall(path)
    return int(encontrados[-1]) if encontrados else None


def instalar_guardia_control(app) -> bool:
    try:
        from models.database import SessionLocal
        from sqlalchemy import text
    except Exception as e:  # pragma: no cover
        print(f"[GuardiaControl] DESACTIVADA (no se pudo importar la BD): {e}")
        return False

    @app.middleware("http")
    async def guardia_control(request, call_next):
        path = request.url.path

        if not any(path.startswith(p) for p in RUTAS_BLOQUEADAS):
            return await call_next(request)

        # 1) id en el path  2) id en la query  3) id en el cuerpo JSON
        uid = _id_de_la_ruta(path)

        if uid is None:
            for k in ("usuario_id", "user_id", "retador_id", "id"):
                v = request.query_params.get(k)
                if v and v.isdigit():
                    uid = int(v)
                    break

        if uid is None and request.method in ("POST", "PUT", "PATCH"):
            cuerpo = await request.body()

            # Reinyectar el cuerpo para que el endpoint lo pueda leer
            async def receive():
                return {"type": "http.request", "body": cuerpo, "more_body": False}
            request._receive = receive

            if cuerpo:
                try:
                    datos = json.loads(cuerpo)
                    if isinstance(datos, dict):
                        for k in ("usuario_id", "user_id", "retador_id"):
                            if isinstance(datos.get(k), int):
                                uid = datos[k]
                                break
                except Exception:
                    pass

        # Si no se puede identificar al usuario, se deja pasar: este guardia
        # protege la integridad del experimento, no es un control de acceso.
        if uid is None:
            return await call_next(request)

        db = SessionLocal()
        try:
            fila = db.execute(
                text("SELECT grupo, rol FROM usuarios_auth WHERE id = :i"),
                {"i": uid},
            ).mappings().first()
        except Exception:
            fila = None
        finally:
            db.close()

        if fila and fila["grupo"] == "control" and fila["rol"] != "admin":
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Tu participacion en el estudio consiste unicamente "
                              "en la evaluacion inicial y la final. Los modulos de "
                              "aprendizaje y juego no estan habilitados para tu grupo.",
                    "grupo": "control",
                },
            )

        return await call_next(request)

    print(f"[GuardiaControl] ACTIVA sobre {len(RUTAS_BLOQUEADAS)} prefijos")
    return True
