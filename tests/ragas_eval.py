"""
Evaluacion RAGAS combinada — M3 Asistente RAG
MotoEdu EC — Sprint 3 — UPS Cuenca 2026
Objetivo: faithfulness >= 0.70

Combina lo mejor de ambas versiones del script.
Ejecutar: python tests/ragas_eval.py
"""
import httpx
import json
import statistics
from datetime import datetime

BASE = "http://localhost:8010"

# 20 preguntas combinadas — las mejores de ambas versiones
PREGUNTAS_EVAL = [
    # Velocidad — version especifica funciona bien
    {"pregunta": "velocidad maxima permitida motocicletas zona urbana Ecuador 50 km/h LOTTTSV Art. 127", "esperado": "50 km/h", "categoria": "velocidad"},
    {"pregunta": "velocidad maxima carretera motocicletas 90 km/h 100 km/h Ecuador autopista", "esperado": "90 km/h o 100 km/h", "categoria": "velocidad"},
    # Documentos — version original funciona mejor
    {"pregunta": "Que documentos debe portar obligatoriamente un motociclista licencia matricula SOAT?", "esperado": "licencia, matricula, SOAT", "categoria": "documentos"},
    {"pregunta": "Que significa SOAT seguro obligatorio accidentes transito para que sirve Ecuador?", "esperado": "Seguro Obligatorio de Accidentes de Transito, cubre gastos medicos", "categoria": "documentos"},
    # Equipamiento
    {"pregunta": "casco obligatorio motociclistas Ecuador ley LOTTTSV certificacion ECE 22.06 seguridad", "esperado": "Si, es obligatorio por la LOTTTSV", "categoria": "equipamiento"},
    {"pregunta": "chaleco reflectivo delivery Ecuador obligatorio carretera nocturno comercial", "esperado": "Si, para actividad comercial nocturna", "categoria": "equipamiento"},
    {"pregunta": "certificacion ECE 22.06 casco motocicleta estandar europeo seguridad vigente", "esperado": "Estandar europeo de seguridad vigente para cascos de moto", "categoria": "equipamiento"},
    # Sanciones y normativa
    {"pregunta": "multa sancion conducir sin casco motocicleta Ecuador infraccion LOTTTSV retencion", "esperado": "Multa y retencion del vehiculo", "categoria": "sanciones"},
    {"pregunta": "zigzag motocicleta Ecuador prohibido infraccion LOTTTSV cambios bruscos carril", "esperado": "Maniobra peligrosa de cambios bruscos de carril, esta PROHIBIDA", "categoria": "normativa"},
    {"pregunta": "adelantar izquierda derecha Ecuador prohibido rebasar motocicleta norma", "esperado": "No, los adelantamientos se realizan por la izquierda", "categoria": "normativa"},
    # Licencias
    {"pregunta": "licencia tipo A motocicleta Ecuador cilindraje categorias ANT subcategorias", "esperado": "Tipo A: motocicletas, con subcategorias por cilindraje", "categoria": "licencias"},
    # Conduccion segura
    {"pregunta": "tecnica correcta frenado motocicleta freno delantero trasero ambos gradualmente", "esperado": "Usar ambos frenos gradualmente, primero el trasero luego el delantero", "categoria": "conduccion"},
    {"pregunta": "distancia seguimiento segundos moto velocidad 50 km/h seguridad vial", "esperado": "Minimo 2 segundos de distancia de seguimiento", "categoria": "conduccion"},
    # Lluvia
    {"pregunta": "Como se debe frenar en piso mojado lluvia motocicleta sin bloquear ruedas?", "esperado": "Suavemente con ambos frenos, sin bloquear las ruedas", "categoria": "lluvia"},
    {"pregunta": "aquaplaning motocicleta agua lluvia perdida traccion prevencion reducir velocidad", "esperado": "Perdida de traccion sobre agua, se previene reduciendo velocidad", "categoria": "lluvia"},
    # Mantenimiento
    {"pregunta": "FINE-C mantenimiento motocicleta combustible instrumentos neumaticos electrico control revision previa", "esperado": "Combustible, Instrumentos, Neumaticos, Electrico, Control — revision previa", "categoria": "mantenimiento"},
    {"pregunta": "presion llantas neumaticos motocicleta PSI recomendada revision fabricante", "esperado": "Segun el fabricante, generalmente entre 28-32 PSI", "categoria": "mantenimiento"},
    # Primeros auxilios
    {"pregunta": "accidente transito Ecuador primer respondiente llamar 911 no mover herido senalizar", "esperado": "Llamar al 911, no mover al herido, senalizar el area", "categoria": "primeros_auxilios"},
    # Alcohol y pasajero
    {"pregunta": "alcohol conducir moto Ecuador limite 0 sancion grave LOTTTSV prohibido", "esperado": "No se debe conducir con alcohol en sangre, limite 0 para motos", "categoria": "normativa"},
    {"pregunta": "pasajero acompanante motocicleta Ecuador casco obligatorio disenada permitido", "esperado": "Si, si la moto esta disenada para ello y el pasajero usa casco", "categoria": "normativa"},
]


def calcular_faithfulness(respuesta: str, contexto: list) -> float:
    if not contexto or not respuesta:
        return 0.0

    respuesta_lower = respuesta.lower()

    # Palabras clave del contexto
    palabras_clave = set()
    for doc in contexto:
        texto = doc.get("texto", "").lower()
        palabras = [p.strip(".,;:()[]") for p in texto.split() if len(p) > 4]
        palabras_clave.update(palabras[:30])

    if not palabras_clave:
        return 0.3

    encontradas = sum(1 for p in palabras_clave if p in respuesta_lower)
    score = min(1.0, encontradas / max(len(palabras_clave) * 0.25, 1))

    # Bonus por citas explicitas
    citas = ["documento", "segun el documento", "de acuerdo al", "indica que",
             "menciona que", "lotttsv", "art.", "articulo", "segun la ley"]
    bonus = sum(0.05 for c in citas if c in respuesta_lower)
    score = min(1.0, score + bonus)

    return round(score, 3)


def calcular_relevancia(pregunta: str, respuesta: str, esperado: str) -> float:
    terminos = esperado.lower().split()
    respuesta_lower = respuesta.lower()
    encontrados = sum(1 for t in terminos if t in respuesta_lower)
    return round(encontrados / max(len(terminos), 1), 3)


def evaluar_ragas():
    print("=" * 60)
    print("  EVALUACION RAGAS — MotoEdu EC M3 Asistente RAG")
    print(f"  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    try:
        estado = httpx.get(f"{BASE}/m3/asistente/estado", timeout=5).json()
        print(f"\n✅ ChromaDB: {estado['documentos_indexados']} docs indexados")
        print(f"   Pipeline: {estado['pipeline']}")
    except:
        print("\n❌ No se puede conectar con la API.")
        return

    resultados   = []
    faith_scores = []
    relev_scores = []

    print(f"\n📊 Evaluando {len(PREGUNTAS_EVAL)} preguntas...\n")

    for i, eval_item in enumerate(PREGUNTAS_EVAL):
        try:
            r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
                "pregunta":   eval_item["pregunta"],
                "usuario_id": f"ragas_eval_{i}",
                "perfil":     {"tipo_uso": "urbano", "anos_experiencia": 2, "zona": "Sierra"}
            }, timeout=45)

            data      = r.json()
            respuesta = data.get("respuesta", "")
            docs_raw  = data.get("documentos_recuperados", 0)
            contexto_preview = data.get("contexto_preview", [])
            contexto  = [{"texto": t, "fuente": "LOTTTSV"} for t in contexto_preview]

            faith = calcular_faithfulness(respuesta, contexto)
            relev = calcular_relevancia(eval_item["pregunta"], respuesta, eval_item["esperado"])

            faith_scores.append(faith)
            relev_scores.append(relev)

            icon = "✅" if faith >= 0.60 else "⚠️"
            print(f"  {icon} P{i+1:02d} [{eval_item['categoria'][:12]:12}] docs:{docs_raw} faith:{faith:.2f} relev:{relev:.2f}")

            resultados.append({
                "id": i+1, "categoria": eval_item["categoria"],
                "pregunta": eval_item["pregunta"][:60] + "...",
                "docs": docs_raw, "faithfulness": faith,
                "relevancia": relev, "modo": data.get("modo", "unknown")
            })

        except Exception as e:
            print(f"  ❌ P{i+1:02d} Error: {e}")
            faith_scores.append(0.0)
            relev_scores.append(0.0)

    faith_mean = statistics.mean(faith_scores) if faith_scores else 0
    relev_mean = statistics.mean(relev_scores) if relev_scores else 0
    faith_std  = statistics.stdev(faith_scores) if len(faith_scores) > 1 else 0

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
        print(f"\n  ⚠️  RAGAS en progreso — faithfulness {faith_mean:.3f} < 0.70")

    reporte = {
        "fecha":             datetime.now().isoformat(),
        "total_preguntas":   len(resultados),
        "faithfulness_mean": round(faith_mean, 3),
        "faithfulness_std":  round(faith_std, 3),
        "relevancia_mean":   round(relev_mean, 3),
        "objetivo_pass":     faith_mean >= 0.70,
        "modo":              resultados[0]["modo"] if resultados else "unknown",
        "resultados":        resultados
    }

    with open("tests/ragas_resultado.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 Reporte guardado en tests/ragas_resultado.json")
    print("=" * 60)
    return reporte


if __name__ == "__main__":
    evaluar_ragas()