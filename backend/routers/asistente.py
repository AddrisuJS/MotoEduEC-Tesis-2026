"""M3 — Asistente Experto RAG"""
from fastapi import APIRouter, Body
from services.claude_service import asistente_rag
import httpx

router = APIRouter()

CHROMA_BASE = "http://chromadb:8000"
COLLECTION  = "motoeduc_knowledge"
TENANT      = "default_tenant"
DATABASE    = "default_database"
historial_sesiones = {}  # En produccion usar Redis


def buscar_chromadb(pregunta: str, n: int = 5) -> list:
    """Busca documentos relevantes en ChromaDB."""
    try:
        # Obtener ID de coleccion
        col_url = f"{CHROMA_BASE}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{COLLECTION}"
        r = httpx.get(col_url, timeout=5)
        if r.status_code != 200:
            return []
        col_id = r.json()["id"]

        # Buscar por texto (embedding simple)
        query_url = f"{CHROMA_BASE}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{col_id}/query"
        import math
        def embed(text, dim=64):
            vec = [0.0]*dim
            for w in text.lower().split():
                vec[hash(w)%dim] += 1.0
            norm = math.sqrt(sum(x*x for x in vec)) or 1.0
            return [x/norm for x in vec]

        r = httpx.post(query_url, json={
            "query_embeddings": [embed(pregunta)],
            "n_results": n,
            "include": ["documents","metadatas"]
        }, timeout=10)

        if r.status_code == 200:
            data = r.json()
            docs = data.get("documents", [[]])[0]
            metas = data.get("metadatas", [[]])[0]
            return [
                {"texto": doc, "fuente": meta.get("fuente","LOTTTSV"), "categoria": meta.get("categoria","")}
                for doc, meta in zip(docs, metas)
            ]
    except Exception as e:
        print(f"ChromaDB error: {e}")
    return []


@router.post("/consultar", summary="Consulta al asistente RAG sobre normativa vial")
async def consultar_asistente(
    datos: dict = Body(..., example={
        "pregunta": "Cual es la velocidad maxima en zona urbana para motos?",
        "usuario_id": "uuid-del-usuario",
        "perfil": {"tipo_uso": "urbano", "anos_experiencia": 2}
    })
):
    pregunta   = datos.get("pregunta", "")
    usuario_id = datos.get("usuario_id", "anonimo")
    perfil     = datos.get("perfil", {})

    # Recuperar historial de la sesion
    historial = historial_sesiones.get(usuario_id, [])

    # Buscar contexto en ChromaDB
    contexto = buscar_chromadb(pregunta)

    # Llamar al asistente (mock o Claude API)
    respuesta = await asistente_rag(pregunta, perfil, contexto, historial)

    # Actualizar historial (ultimas 6 interacciones)
    historial.append({"role": "user", "content": pregunta})
    historial.append({"role": "assistant", "content": respuesta["respuesta"]})
    historial_sesiones[usuario_id] = historial[-12:]

    return {
        "pregunta": pregunta,
        "respuesta": respuesta["respuesta"],
        "fuentes": respuesta["fuentes"],
        "documentos_recuperados": len(contexto),
        "tokens_usados": respuesta.get("tokens_usados", 0)
    }


@router.delete("/historial/{usuario_id}", summary="Limpia el historial de conversacion")
def limpiar_historial(usuario_id: str):
    historial_sesiones.pop(usuario_id, None)
    return {"mensaje": f"Historial de {usuario_id} limpiado"}
