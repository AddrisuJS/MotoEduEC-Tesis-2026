"""
M3 — Asistente Experto RAG
Sprint 2 — Pipeline ChromaDB + Claude API + historial conversacion
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import asistente_rag
import httpx, math, time

router = APIRouter()

CHROMA_BASE = "http://chromadb:8000"
TENANT      = "default_tenant"
DATABASE    = "default_database"
COL_NAME    = "motoeduc_knowledge"

# Historial en memoria — en produccion usar Redis
historial_sesiones: dict = {}


import hashlib, unicodedata

def _normalizar_texto(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return "".join(c if c.isalnum() else " " for c in t)

def _embed(text: str, dim: int = 256) -> list:
    """Embedding deterministico (MD5 estable entre procesos) — identico al de seed_tesis.py."""
    vec = [0.0] * dim
    palabras = [w for w in _normalizar_texto(text).split() if len(w) > 2]
    for i, w in enumerate(palabras):
        vec[int(hashlib.md5(w.encode()).hexdigest(), 16) % dim] += 1.0
        if i + 1 < len(palabras):
            big = w + "_" + palabras[i + 1]
            vec[int(hashlib.md5(big.encode()).hexdigest(), 16) % dim] += 0.5
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def buscar_chromadb(pregunta: str, n: int = 5) -> list:
    """Busca los n documentos mas similares en ChromaDB."""
    try:
        # Obtener ID de la coleccion
        r = httpx.get(
            f"{CHROMA_BASE}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{COL_NAME}",
            timeout=5
        )
        if r.status_code != 200:
            return []
        col_id = r.json()["id"]

        # Buscar por similitud
        r = httpx.post(
            f"{CHROMA_BASE}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{col_id}/query",
            json={
                "query_embeddings": [_embed(pregunta)],
                "n_results":        n,
                "include":          ["documents", "metadatas", "distances"]
            },
            timeout=10
        )

        if r.status_code != 200:
            return []

        data    = r.json()
        docs    = data.get("documents",  [[]])[0]
        metas   = data.get("metadatas",  [[]])[0]
        dists   = data.get("distances",  [[]])[0]

        return [
            {
                "texto":      doc,
                "fuente":     meta.get("fuente", "LOTTTSV"),
                "categoria":  meta.get("categoria", "General"),
                "dificultad": meta.get("dificultad", "basico"),
                "relevancia": round(1 - dist, 3)
            }
            for doc, meta, dist in zip(docs, metas, dists)
        ]

    except Exception as e:
        print(f"ChromaDB error: {e}")
        return []


def buscar_historia_relevante(pregunta: str, db: Session) -> dict | None:
    """Busca en el muro de historias reales (encuesta E1) si alguna coincide
    tematicamente con la pregunta del usuario (por palabra clave en 'tema').
    Devuelve la mas reciente que matchee (incluida su imagen si tiene), o None."""
    try:
        filas = db.execute(text(
            "SELECT nombre, ciudad, historia, tema, imagen_url FROM contribuciones_historia "
            "WHERE estado='aprobada' AND tema IS NOT NULL ORDER BY fecha_envio DESC")
        ).fetchall()
    except Exception:
        return None
    pregunta_norm = pregunta.lower()
    for nombre, ciudad, historia, tema, imagen_url in filas:
        if tema and tema.lower() in pregunta_norm:
            return {"nombre": nombre, "ciudad": ciudad, "historia": historia, "tema": tema, "imagen_url": imagen_url}
    return None


@router.post("/consultar", summary="Consulta al asistente RAG sobre normativa vial ecuatoriana")
async def consultar_asistente(
    datos: dict = Body(..., example={
        "pregunta":    "Cual es la velocidad maxima permitida para motos en zona urbana en Ecuador?",
        "usuario_id":  "uuid-del-usuario",
        "perfil": {
            "nombre":           "Carlos",
            "tipo_uso":         "delivery",
            "anos_experiencia": 2,
            "moto_actual":      "Honda CB100",
            "zona":             "Guayas",
            "nivel":            "basico"
        }
    }),
    db: Session = Depends(get_db)
):
    t0         = time.perf_counter()
    pregunta   = datos.get("pregunta", "")
    usuario_id = datos.get("usuario_id", "anonimo")
    perfil     = datos.get("perfil", {})

    if not pregunta.strip():
        return {"error": "La pregunta no puede estar vacia"}

    # Recuperar historial de la sesion (ultimas 6 interacciones)
    historial = historial_sesiones.get(usuario_id, [])

    # Buscar contexto relevante en ChromaDB
    contexto = buscar_chromadb(pregunta, n=15)  # k ajustado empiricamente (barrido_k): codo de la curva recall/costo

    # Si la pregunta coincide tematicamente con una historia real de la
    # encuesta E1, se agrega como contexto adicional -una anecdota real que
    # ilustra la norma-, ademas del contexto normativo recuperado.
    historia_rel = buscar_historia_relevante(pregunta, db)
    if historia_rel:
        contexto.append({
            "texto": f"Testimonio real de un motociclista de {historia_rel['ciudad']}: {historia_rel['historia']}",
            "fuente": "Muro de historias (encuesta E1)"
        })

    # Generar respuesta con Claude API (o mock)
    respuesta_data = await asistente_rag(pregunta, perfil, contexto, historial)

    # Actualizar historial (maximo 12 mensajes = 6 turnos)
    historial.append({"role": "user",      "content": pregunta})
    historial.append({"role": "assistant", "content": respuesta_data["respuesta"]})
    historial_sesiones[usuario_id] = historial[-12:]

    # Contar la consulta de verdad (para la insignia "Consultor RAG"), no un
    # proxy de actividad general. Aditivo: crea la fila si el usuario aun no
    # tiene arcade_stats (participante que solo usa el asistente, sin jugar).
    # Se omite si usuario_id no es un ID valido (ej. "anonimo").
    if str(usuario_id).isdigit():
        try:
            r_count = db.execute(text("""
                INSERT INTO arcade_stats (usuario_id, consultas_asistente)
                VALUES (:uid, 1)
                ON CONFLICT (usuario_id) DO UPDATE
                SET consultas_asistente = arcade_stats.consultas_asistente + 1
                RETURNING consultas_asistente
            """), {"uid": int(usuario_id)}).fetchone()
            # Insignia "Consultor RAG" (id=10): 10 consultas reales, no un proxy
            if r_count and r_count[0] >= 10:
                db.execute(text("""
                    INSERT INTO insignias_usuario (usuario_id, insignia_id)
                    VALUES (:uid, 10) ON CONFLICT (usuario_id, insignia_id) DO NOTHING
                """), {"uid": int(usuario_id)})
            db.commit()
        except Exception:
            db.rollback()  # no bloquear la respuesta al usuario si esto falla

    latencia_ms = int((time.perf_counter() - t0) * 1000)

    # ── Registro de la sesion (M12) ────────────────────────────────────
    # Aditivo y tolerante a fallos: si algo falla aqui, la respuesta al
    # usuario NO se ve afectada. Es telemetria, no parte del servicio.
    try:
        db.execute(text("""
            INSERT INTO sesiones_chat
                (usuario_auth_id, pregunta, respuesta, fuentes_rag, tokens_usados,
                 latencia_ms, documentos_recuperados, modo, fecha)
            VALUES (:uid, :preg, :resp, :fuentes, :tok, :lat, :docs, :modo, NOW())
        """), {
            "uid":     int(usuario_id) if str(usuario_id).isdigit() else None,
            "preg":    pregunta,
            "resp":    respuesta_data["respuesta"],
            "fuentes": [str(f) for f in (respuesta_data.get("fuentes") or [])],
            "tok":     respuesta_data.get("tokens_usados", 0),
            "lat":     latencia_ms,
            "docs":    len(contexto),
            "modo":    respuesta_data.get("modo", "claude_api"),
        })
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[M12] No se pudo registrar la sesion: {e}")

    return {
        "pregunta":               pregunta,
        "respuesta":              respuesta_data["respuesta"],
        "fuentes":                respuesta_data["fuentes"],
        "documentos_recuperados": len(contexto),
        "contexto_preview":       [c["texto"][:100] for c in contexto[:2]],
        "tokens_usados":          respuesta_data.get("tokens_usados", 0),
        "latencia_ms":            latencia_ms,
        "turno_conversacion":     len(historial_sesiones.get(usuario_id, [])) // 2,
        "modo":                   respuesta_data.get("modo", "claude_api"),
        "historia_relacionada":   historia_rel  # None si no hubo match; si hay, incluye imagen_url
    }


@router.get("/historial/{usuario_id}", summary="Obtiene el historial de conversacion")
def ver_historial(usuario_id: str):
    historial = historial_sesiones.get(usuario_id, [])
    return {
        "usuario_id": usuario_id,
        "turnos":     len(historial) // 2,
        "historial":  historial
    }


@router.delete("/historial/{usuario_id}", summary="Limpia el historial de conversacion")
def limpiar_historial(usuario_id: str):
    historial_sesiones.pop(usuario_id, None)
    return {"mensaje": f"Historial limpiado para usuario {usuario_id}"}


@router.get("/estado", summary="Estado del pipeline RAG")
def estado_rag():
    """Verifica la conectividad con ChromaDB."""
    try:
        r = httpx.get(f"{CHROMA_BASE}/api/v2/heartbeat", timeout=3)
        chroma_ok = r.status_code == 200
    except:
        chroma_ok = False

    # Contar documentos
    doc_count = 0
    try:
        r = httpx.get(
            f"{CHROMA_BASE}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{COL_NAME}",
            timeout=3
        )
        if r.status_code == 200:
            col_id = r.json()["id"]
            r2 = httpx.get(
                f"{CHROMA_BASE}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{col_id}/count",
                timeout=3
            )
            doc_count = int(r2.text) if r2.status_code == 200 else 0
    except:
        pass

    return {
        "chromadb_conectado":    chroma_ok,
        "coleccion":             COL_NAME,
        "documentos_indexados":  doc_count,
        "sesiones_activas":      len(historial_sesiones),
        "pipeline":              "ChromaDB (hash-embed) + Claude API",
        "estado":                "operativo" if chroma_ok else "sin conexion a ChromaDB"
    }
