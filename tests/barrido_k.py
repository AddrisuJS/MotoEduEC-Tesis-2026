"""
BARRIDO DEL PARAMETRO k — MotoEdu EC
=====================================
Ajusta empiricamente el numero de documentos que el recuperador entrega al
generador. Es una de las acciones de mejora declaradas en la metodologia del
proyecto (Sprint 4: "ajuste de chunk size, k de recuperacion y prompt de
sintesis").

COSTO: 0.00 USD. No invoca a Claude.
Usa el endpoint /m3/asistente/recuperar, que solo consulta ChromaDB. Medir la
recuperacion de forma aislada del generador permite optimizarla sin gastar
tokens y sin que la variabilidad del LLM contamine la medida.

Que reporta para cada k:
  - context recall (fraccion de terminos esperados presentes en el contexto)
  - retrieval miss (terminos que estan en el corpus pero no se recuperaron)
  - el costo de contexto (documentos por consulta = tokens que paga el prompt)

Uso:
    python tests/barrido_k.py
"""
import json
import unicodedata
from datetime import datetime

import httpx

BASE = "http://localhost:8010"
VALORES_K = [5, 10, 15, 20, 30]


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def cargar_dataset():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ragas_eval_50 import PREGUNTAS_EVAL
    return PREGUNTAS_EVAL


def evaluar_k(dataset, k):
    hits = total = 0
    chars = 0
    for item in dataset:
        try:
            r = httpx.post(f"{BASE}/m3/asistente/recuperar",
                           json={"pregunta": item["pregunta"], "k": k}, timeout=20)
            docs = r.json().get("documentos", [])
        except Exception:
            docs = []
        ctx = normalizar(" ".join(docs))
        chars += len(ctx)
        for t in item["terminos_fe"]:
            total += 1
            if normalizar(t) in ctx:
                hits += 1
    return (hits / total if total else 0), total - hits, chars / len(dataset)


def main():
    print("=" * 70)
    print("  BARRIDO DEL PARAMETRO k — recuperacion aislada")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}   costo: 0.00 USD")
    print("=" * 70)
    print()

    try:
        est = httpx.get(f"{BASE}/m3/asistente/estado", timeout=5).json()
        print(f"  ChromaDB: {est.get('documentos_indexados')} docs")
        print(f"  Embedding: {est.get('embedding_version', '?')}")
        print(f"  Terminos IDF: {est.get('idf_terminos', '?')}")
    except Exception as e:
        print(f"  ❌ API no responde: {e}")
        return

    dataset = cargar_dataset()
    print(f"  Dataset: {len(dataset)} preguntas")
    print()

    print(f"  {'k':>4} {'recall':>9} {'miss':>7} {'ctx/consulta':>14} {'':>6}")
    print("  " + "-" * 46)

    resultados = []
    base_recall = None
    for k in VALORES_K:
        recall, miss, chars = evaluar_k(dataset, k)
        if base_recall is None:
            base_recall = recall
        resultados.append({"k": k, "recall": round(recall, 4), "miss": miss,
                           "chars_promedio": int(chars)})
        marca = "  <- actual" if k == 10 else ""
        print(f"  {k:>4} {recall:9.3f} {miss:7} {int(chars):11} ch{marca}")

    print()
    print("=" * 70)
    print("  ANALISIS")
    print("=" * 70)

    mejor = max(resultados, key=lambda x: x["recall"])
    actual = next(r for r in resultados if r["k"] == 10)

    print(f"  k actual (10):  recall {actual['recall']:.3f}  contexto {actual['chars_promedio']} ch")
    print(f"  mejor k ({mejor['k']}):    recall {mejor['recall']:.3f}  contexto {mejor['chars_promedio']} ch")
    print()

    if mejor["k"] == 10:
        print("  k=10 ya es el optimo del rango probado. No cambiar.")
    else:
        d_recall = mejor["recall"] - actual["recall"]
        d_ctx = (mejor["chars_promedio"] / actual["chars_promedio"] - 1) * 100
        print(f"  Subir k de 10 a {mejor['k']}:")
        print(f"    recall   {d_recall:+.3f}  ({d_recall/actual['recall']*100:+.1f}%)")
        print(f"    contexto {d_ctx:+.1f}% mas largo -> mas tokens por consulta")
        print()
        print("  El intercambio: mas contexto sube el recall, pero encarece cada")
        print("  consulta y puede diluir la atencion del generador entre documentos")
        print("  menos relevantes. Verificar con ragas_eval_50.py que faithfulness")
        print("  no caiga antes de adoptar el cambio.")

    print()
    print("  Rendimientos marginales por escalon:")
    for i in range(1, len(resultados)):
        prev, cur = resultados[i-1], resultados[i]
        d = cur["recall"] - prev["recall"]
        print(f"    k {prev['k']:>2} -> {cur['k']:<2}  recall {d:+.3f}")

    with open("tests/barrido_k.json", "w", encoding="utf-8") as f:
        json.dump({"fecha": datetime.now().isoformat(), "resultados": resultados}, f, indent=2)
    print()
    print("  📄 tests/barrido_k.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
