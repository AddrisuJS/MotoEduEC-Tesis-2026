"""
M3 — Asistente Experto RAG
Sprint 2 — Pipeline ChromaDB + Claude API + historial conversacion
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Body
from sqlalchemy.orm import Session
from services.claude_service import asistente_rag
import httpx, math

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
    })
):
    pregunta   = datos.get("pregunta", "")
    usuario_id = datos.get("usuario_id", "anonimo")
    perfil     = datos.get("perfil", {})

    if not pregunta.strip():
        return {"error": "La pregunta no puede estar vacia"}

    # Recuperar historial de la sesion (ultimas 6 interacciones)
    historial = historial_sesiones.get(usuario_id, [])

    # Buscar contexto relevante en ChromaDB
    contexto = buscar_chromadb(pregunta, n=10)

    # Generar respuesta con Claude API (o mock)
    respuesta_data = await asistente_rag(pregunta, perfil, contexto, historial)

    # Actualizar historial (maximo 12 mensajes = 6 turnos)
    historial.append({"role": "user",      "content": pregunta})
    historial.append({"role": "assistant", "content": respuesta_data["respuesta"]})
    historial_sesiones[usuario_id] = historial[-12:]

    return {
        "pregunta":               pregunta,
        "respuesta":              respuesta_data["respuesta"],
        "fuentes":                respuesta_data["fuentes"],
        "documentos_recuperados": len(contexto),
        "contexto_preview":       [c["texto"][:100] for c in contexto[:2]],
        "tokens_usados":          respuesta_data.get("tokens_usados", 0),
        "turno_conversacion":     len(historial_sesiones.get(usuario_id, [])) // 2,
        "modo":                   respuesta_data.get("modo", "claude_api")
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
