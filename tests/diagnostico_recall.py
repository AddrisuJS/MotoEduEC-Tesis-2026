"""
DIAGNOSTICO DE CONTEXT RECALL — MotoEdu EC
===========================================
Responde la pregunta que RAGAS no responde por si sola:

  Cuando context recall es bajo, ¿de quien es la culpa?

  (a) CORPUS GAP      -> el termino NO existe en ninguno de los 200 documentos.
                         El recuperador hizo su trabajo; no hay nada que traer.
                         Se corrige AMPLIANDO EL CORPUS.

  (b) RETRIEVAL MISS  -> el termino SI existe en el corpus, pero no aparecio en
                         los 10 documentos recuperados.
                         Se corrige AJUSTANDO LA RECUPERACION (embedding, k,
                         expansion de consulta).

Optimizar sin este diagnostico es adivinar. Este script mide antes de tocar.

Uso:
    python tests/diagnostico_recall.py

Requiere: la API arriba (localhost:8010) y PostgreSQL (localhost:5434).
Costo: ~0.40 USD (una consulta al asistente por pregunta del dataset).
"""
import json
import unicodedata
from datetime import datetime

import httpx
import psycopg2

BASE = "http://localhost:8010"
PG = dict(host="localhost", port=5434, dbname="motoeduc_tesis",
          user="motoeduc_user", password="MotoEduC_2026$")


def normalizar(t: str) -> str:
    """Misma normalizacion que el embedding: minusculas y sin tildes."""
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def cargar_corpus() -> str:
    """Reconstruye el corpus exactamente como lo indexa seed_tesis.py:
    'Pregunta: {pregunta} Respuesta: {respuesta_correcta}. {explicacion}'
    """
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    cur.execute("""
        SELECT pregunta, respuesta_correcta, COALESCE(explicacion, '')
        FROM preguntas_viales
        WHERE activa = TRUE
    """)
    docs = [f"Pregunta: {p} Respuesta: {r}. {e}" for p, r, e in cur.fetchall()]
    cur.close()
    conn.close()
    print(f"  Corpus cargado: {len(docs)} documentos desde PostgreSQL")
    return normalizar(" ".join(docs))


def cargar_dataset() -> list:
    """Importa el dataset de evaluacion del script RAGAS."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ragas_eval_50 import PREGUNTAS_EVAL
    return PREGUNTAS_EVAL


def diagnosticar():
    print("=" * 70)
    print("  DIAGNOSTICO DE CONTEXT RECALL")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 70)
    print()

    corpus = cargar_corpus()
    dataset = cargar_dataset()
    print(f"  Dataset: {len(dataset)} preguntas de evaluacion")
    print()

    hits = 0
    corpus_gaps = []
    retrieval_misses = []
    total_terminos = 0
    detalle = []

    print("  Evaluando (esto consume Claude API)...\n")

    for i, item in enumerate(dataset):
        try:
            r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
                "pregunta": item["pregunta"],
                "usuario_id": f"diag_recall_{i}",
                "perfil": {"tipo_uso": "urbano", "anos_experiencia": 2, "zona": "Sierra"},
                "incluir_contexto": True
            }, timeout=45)
            recuperado = normalizar(" ".join(r.json().get("contexto_completo") or []))
        except Exception as e:
            print(f"  ❌ P{i+1:02d} error: {e}")
            continue

        gaps_p, misses_p, hits_p = [], [], []

        for termino in item["terminos_fe"]:
            total_terminos += 1
            t_norm = normalizar(termino)

            if t_norm in recuperado:
                hits += 1
                hits_p.append(termino)
            elif t_norm in corpus:
                # Existe en el corpus pero el recuperador no lo trajo
                retrieval_misses.append((i + 1, termino, item["categoria"]))
                misses_p.append(termino)
            else:
                # No existe en ningun documento del corpus
                corpus_gaps.append((i + 1, termino, item["categoria"]))
                gaps_p.append(termino)

        n = len(item["terminos_fe"])
        recall_p = len(hits_p) / n if n else 0
        icono = "✅" if recall_p >= 0.7 else ("⚠️" if recall_p >= 0.4 else "❌")
        etiqueta = ""
        if gaps_p and not misses_p:
            etiqueta = "  <- CORPUS GAP puro"
        elif misses_p and not gaps_p:
            etiqueta = "  <- RETRIEVAL MISS puro"

        print(f"  {icono} P{i+1:02d} [{item['categoria'][:14]:14}] recall:{recall_p:.2f}"
              f"  hits:{len(hits_p)} gap:{len(gaps_p)} miss:{len(misses_p)}{etiqueta}")

        detalle.append({
            "id": i + 1, "categoria": item["categoria"],
            "recall": round(recall_p, 3),
            "hits": hits_p, "corpus_gap": gaps_p, "retrieval_miss": misses_p
        })

    # ─── Resumen ───
    n_gap = len(corpus_gaps)
    n_miss = len(retrieval_misses)
    fallos = n_gap + n_miss

    print()
    print("=" * 70)
    print("  ANATOMIA DEL RECALL")
    print("=" * 70)
    print(f"  Terminos evaluados:        {total_terminos}")
    print(f"  Recuperados correctamente: {hits}  ({hits/total_terminos*100:.1f}%)")
    print(f"  Fallos:                    {fallos}  ({fallos/total_terminos*100:.1f}%)")
    print()
    if fallos:
        print(f"  De los {fallos} fallos:")
        print(f"    CORPUS GAP     {n_gap:3}  ({n_gap/fallos*100:.1f}%)  el termino no existe en el corpus")
        print(f"    RETRIEVAL MISS {n_miss:3}  ({n_miss/fallos*100:.1f}%)  esta en el corpus pero no se recupero")
    print()

    # ─── Veredicto ───
    print("=" * 70)
    print("  VEREDICTO")
    print("=" * 70)
    if fallos == 0:
        print("  Recall perfecto.")
    elif n_gap > n_miss:
        techo = (hits + n_miss) / total_terminos
        print(f"  El cuello de botella es la COBERTURA DEL CORPUS ({n_gap/fallos*100:.0f}% de los fallos).")
        print(f"  Afinar la recuperacion no puede superar un techo de {techo:.3f},")
        print(f"  porque {n_gap} terminos no existen en ningun documento.")
        print(f"  Accion: ampliar el corpus en las categorias senaladas abajo.")
    else:
        print(f"  El cuello de botella es la RECUPERACION ({n_miss/fallos*100:.0f}% de los fallos).")
        print(f"  La informacion esta en el corpus pero no llega al top-10.")
        print(f"  Accion: expansion de consulta, subir k, o revisar el embedding.")

    # ─── Categorias mas afectadas por gap de corpus ───
    if corpus_gaps:
        print()
        print("  Categorias con vacios de corpus:")
        por_cat = {}
        for _, termino, cat in corpus_gaps:
            por_cat.setdefault(cat, []).append(termino)
        for cat, terms in sorted(por_cat.items(), key=lambda x: -len(x[1])):
            muestra = ", ".join(sorted(set(terms))[:6])
            print(f"    {cat[:22]:22} {len(terms):3} terminos  ej: {muestra}")

    if retrieval_misses:
        print()
        print("  Terminos que existen pero no se recuperan (top 10):")
        por_term = {}
        for _, termino, _ in retrieval_misses:
            por_term[termino] = por_term.get(termino, 0) + 1
        for termino, n in sorted(por_term.items(), key=lambda x: -x[1])[:10]:
            print(f"    {termino[:28]:28} x{n}")

    reporte = {
        "fecha": datetime.now().isoformat(),
        "terminos_evaluados": total_terminos,
        "hits": hits,
        "recall_global": round(hits / total_terminos, 3) if total_terminos else 0,
        "corpus_gap": n_gap,
        "retrieval_miss": n_miss,
        "pct_fallos_por_corpus": round(n_gap / fallos * 100, 1) if fallos else 0,
        "pct_fallos_por_recuperacion": round(n_miss / fallos * 100, 1) if fallos else 0,
        "techo_alcanzable_afinando_recuperacion": round((hits + n_miss) / total_terminos, 3) if total_terminos else 0,
        "detalle": detalle
    }
    with open("tests/diagnostico_recall.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print()
    print("  📄 Reporte guardado en tests/diagnostico_recall.json")
    print("=" * 70)
    return reporte


if __name__ == "__main__":
    diagnosticar()
