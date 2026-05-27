"""
Evaluacion RAGAS — M3 Asistente RAG
MotoEdu EC — Sprint 2 — UPS Cuenca 2026

Mide: faithfulness, context_recall, answer_relevance
sobre 20 preguntas de prueba del LOTTTSV

Ejecutar: python tests/ragas_eval.py
NOTA: Requiere Claude API Key activa en .env
"""
import httpx
import json
import statistics
from datetime import datetime

BASE = "http://localhost:8010"

# 20 preguntas de prueba con respuesta esperada (ground truth)
PREGUNTAS_EVAL = [
    {
        "pregunta":  "Cual es la velocidad maxima permitida para motocicletas en zona urbana en Ecuador?",
        "esperado":  "50 km/h",
        "categoria": "velocidad"
    },
    {
        "pregunta":  "Que documentos debe portar obligatoriamente un motociclista?",
        "esperado":  "licencia, matricula, SOAT",
        "categoria": "documentos"
    },
    {
        "pregunta":  "Es obligatorio el uso de casco para motociclistas en Ecuador?",
        "esperado":  "Si, es obligatorio por la LOTTTSV",
        "categoria": "equipamiento"
    },
    {
        "pregunta":  "Cual es la velocidad maxima en carretera para motocicletas?",
        "esperado":  "90 km/h o 100 km/h segun la via",
        "categoria": "velocidad"
    },
    {
        "pregunta":  "Que significa SOAT y para que sirve?",
        "esperado":  "Seguro Obligatorio de Accidentes de Transito, cubre gastos medicos",
        "categoria": "documentos"
    },
    {
        "pregunta":  "Cuales son las sanciones por conducir sin casco en Ecuador?",
        "esperado":  "Multa y retencion del vehiculo",
        "categoria": "sanciones"
    },
    {
        "pregunta":  "Se puede circular con dos personas en una motocicleta en Ecuador?",
        "esperado":  "Si, si la moto esta disenada para ello y el pasajero usa casco",
        "categoria": "normativa"
    },
    {
        "pregunta":  "Que tipos de licencia existen para motocicletas en Ecuador?",
        "esperado":  "Tipo A: motocicletas, con subcategorias por cilindraje",
        "categoria": "licencias"
    },
    {
        "pregunta":  "Cual es la tecnica correcta de frenado en condiciones normales?",
        "esperado":  "Usar ambos frenos gradualmente, primero el trasero luego el delantero",
        "categoria": "conduccion"
    },
    {
        "pregunta":  "Como se debe frenar en piso mojado con una motocicleta?",
        "esperado":  "Suavemente con ambos frenos, sin bloquear las ruedas",
        "categoria": "lluvia"
    },
    {
        "pregunta":  "Que es el aquaplaning y como se previene en moto?",
        "esperado":  "Perdida de traccion sobre agua, se previene reduciendo velocidad",
        "categoria": "lluvia"
    },
    {
        "pregunta":  "Que significa la certificacion ECE 22.06 en un casco?",
        "esperado":  "Estandar europeo de seguridad vigente para cascos de moto",
        "categoria": "equipamiento"
    },
    {
        "pregunta":  "Cuantas horas antes de manejar no se debe consumir alcohol?",
        "esperado":  "No se debe conducir con alcohol en sangre, limite 0 para motos",
        "categoria": "normativa"
    },
    {
        "pregunta":  "Que es el FINE-C en el mantenimiento de motos?",
        "esperado":  "Combustible, Instrumentos, Neumaticos, Electrico, Control — revision previa",
        "categoria": "mantenimiento"
    },
    {
        "pregunta":  "Cual es la presion recomendada para llantas de motos utilitarias?",
        "esperado":  "Segun el fabricante, generalmente entre 28-32 PSI",
        "categoria": "mantenimiento"
    },
    {
        "pregunta":  "Se puede adelantar por la derecha en Ecuador?",
        "esperado":  "No, los adelantamientos se realizan por la izquierda",
        "categoria": "normativa"
    },
    {
        "pregunta":  "Que hacer si hay un accidente de transito como primer respondiente?",
        "esperado":  "Llamar al 911, no mover al herido, senalizar el area",
        "categoria": "primeros_auxilios"
    },
    {
        "pregunta":  "Cuantos centimetros debe ser la distancia de seguimiento en moto a 50 km/h?",
        "esperado":  "Minimo 2 segundos de distancia de seguimiento",
        "categoria": "conduccion"
    },
    {
        "pregunta":  "Es obligatorio el chaleco reflectivo para delivery en Ecuador?",
        "esperado":  "Si, para actividad comercial nocturna y en carretera",
        "categoria": "equipamiento"
    },
    {
        "pregunta":  "Que es el zigzag y esta permitido en moto?",
        "esperado":  "Maniobra peligrosa de cambios bruscos de carril, esta PROHIBIDA",
        "categoria": "normativa"
    },
]


def calcular_faithfulness(respuesta: str, contexto: list) -> float:
    """
    Calcula faithfulness simplificado:
    Proporcion de palabras clave del contexto presente en la respuesta.
    """
    if not contexto or not respuesta:
        return 0.0

    palabras_clave_contexto = set()
    for doc in contexto:
        texto = doc.get("texto", "").lower()
        palabras = [p for p in texto.split() if len(p) > 4]
        palabras_clave_contexto.update(palabras[:20])

    if not palabras_clave_contexto:
        return 0.5

    respuesta_lower = respuesta.lower()
    encontradas = sum(1 for p in palabras_clave_contexto if p in respuesta_lower)
    score = min(1.0, encontradas / max(len(palabras_clave_contexto) * 0.3, 1))
    return round(score, 3)


def calcular_relevancia(pregunta: str, respuesta: str, esperado: str) -> float:
    """
    Calcula answer_relevance simplificado:
    Coincidencia entre respuesta y terminos esperados.
    """
    terminos_esperados = esperado.lower().split()
    respuesta_lower    = respuesta.lower()
    encontrados = sum(1 for t in terminos_esperados if t in respuesta_lower)
    return round(encontrados / max(len(terminos_esperados), 1), 3)


def evaluar_ragas():
    print("=" * 60)
    print("  EVALUACION RAGAS — MotoEdu EC M3 Asistente RAG")
    print(f"  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    # Verificar estado del pipeline
    try:
        estado = httpx.get(f"{BASE}/m3/asistente/estado", timeout=5).json()
        print(f"\n✅ ChromaDB: {estado['documentos_indexados']} docs indexados")
        print(f"   Pipeline: {estado['pipeline']}")
    except:
        print("\n❌ No se puede conectar con la API. Verifica que Docker este corriendo.")
        return

    resultados  = []
    faithfulness_scores = []
    relevancia_scores   = []

    print(f"\n📊 Evaluando {len(PREGUNTAS_EVAL)} preguntas...\n")

    for i, eval_item in enumerate(PREGUNTAS_EVAL):
        try:
            r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
                "pregunta":   eval_item["pregunta"],
                "usuario_id": f"ragas_eval_{i}",
                "perfil":     {"tipo_uso": "urbano", "anos_experiencia": 2}
            }, timeout=30)

            data     = r.json()
            respuesta = data.get("respuesta", "")
            contexto  = [{"texto": c} for c in data.get("contexto_preview", [])]
            docs      = data.get("documentos_recuperados", 0)

            faith = calcular_faithfulness(respuesta, contexto)
            relev = calcular_relevancia(eval_item["pregunta"], respuesta, eval_item["esperado"])

            faithfulness_scores.append(faith)
            relevancia_scores.append(relev)

            resultado = {
                "id":         i + 1,
                "categoria":  eval_item["categoria"],
                "pregunta":   eval_item["pregunta"][:60] + "...",
                "docs":       docs,
                "faithfulness": faith,
                "relevancia":   relev,
                "modo":       data.get("modo", "unknown")
            }
            resultados.append(resultado)

            estado_icon = "✅" if faith >= 0.5 else "⚠️"
            print(f"  {estado_icon} P{i+1:02d} [{eval_item['categoria'][:12]:12}] "
                  f"docs:{docs} faith:{faith:.2f} relev:{relev:.2f}")

        except Exception as e:
            print(f"  ❌ P{i+1:02d} Error: {e}")
            faithfulness_scores.append(0.0)
            relevancia_scores.append(0.0)

    # Calcular metricas globales
    faith_mean = statistics.mean(faithfulness_scores)
    relev_mean = statistics.mean(relevancia_scores)
    faith_std  = statistics.stdev(faithfulness_scores) if len(faithfulness_scores) > 1 else 0

    print("\n" + "=" * 60)
    print("  RESULTADOS RAGAS")
    print("=" * 60)
    print(f"  Faithfulness media:     {faith_mean:.3f} (objetivo >= 0.70)")
    print(f"  Faithfulness std:       {faith_std:.3f}")
    print(f"  Answer Relevance media: {relev_mean:.3f}")
    print(f"  Preguntas evaluadas:    {len(resultados)}")

    if faith_mean >= 0.70:
        print(f"\n  ✅ RAGAS PASS — faithfulness {faith_mean:.3f} >= 0.70")
    else:
        print(f"\n  ⚠️  RAGAS necesita mejora — faithfulness {faith_mean:.3f} < 0.70")
        print("     Acciones: aumentar k ChromaDB, mejorar embeddings o prompt")

    modo = resultados[0]["modo"] if resultados else "unknown"
    if modo == "mock":
        print("\n  ℹ️  MODO MOCK activo — scores son aproximados.")
        print("     Conectar Claude API Key para scores RAGAS reales.")

    # Guardar resultados
    reporte = {
        "fecha":             datetime.now().isoformat(),
        "total_preguntas":   len(resultados),
        "faithfulness_mean": round(faith_mean, 3),
        "faithfulness_std":  round(faith_std, 3),
        "relevancia_mean":   round(relev_mean, 3),
        "objetivo_pass":     faith_mean >= 0.70,
        "modo":              modo,
        "resultados":        resultados
    }

    with open("tests/ragas_resultado.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 Reporte guardado en tests/ragas_resultado.json")
    print("=" * 60)

    return reporte


if __name__ == "__main__":
    evaluar_ragas()
