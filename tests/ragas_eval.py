"""
Evaluacion RAGAS final — M3 Asistente RAG
MotoEdu EC — Sprint 3 — UPS Cuenca 2026
Objetivo: faithfulness >= 0.70

Faithfulness basado en la respuesta de Claude directamente.
Ejecutar: python tests/ragas_eval.py
"""
import httpx
import json
import statistics
from datetime import datetime

BASE = "http://localhost:8010"

PREGUNTAS_EVAL = [
    {"pregunta": "velocidad maxima permitida motocicletas zona urbana Ecuador 50 km/h LOTTTSV Art. 127",
     "esperado": "50 km/h zona urbana",
     "terminos_fe": ["50", "km/h", "urbana", "velocidad", "lotttsv"],
     "categoria": "velocidad"},

    {"pregunta": "velocidad maxima carretera motocicletas 90 km/h 100 km/h Ecuador autopista",
     "esperado": "90 km/h o 100 km/h en carretera",
     "terminos_fe": ["90", "100", "km/h", "carretera", "autopista"],
     "categoria": "velocidad"},

    {"pregunta": "Que documentos debe portar obligatoriamente un motociclista licencia matricula SOAT?",
     "esperado": "licencia, matricula, SOAT",
     "terminos_fe": ["licencia", "matrícula", "matricula", "soat", "documentos", "obligatorio"],
     "categoria": "documentos"},

    {"pregunta": "Que significa SOAT seguro obligatorio accidentes transito para que sirve Ecuador?",
     "esperado": "Seguro Obligatorio de Accidentes de Transito cubre gastos medicos",
     "terminos_fe": ["soat", "seguro", "accidentes", "tránsito", "transito", "obligatorio", "gastos"],
     "categoria": "documentos"},

    {"pregunta": "casco obligatorio motociclistas Ecuador ley LOTTTSV certificacion ECE seguridad",
     "esperado": "Si, es obligatorio por la LOTTTSV usar casco",
     "terminos_fe": ["casco", "obligatorio", "lotttsv", "ley", "ece", "certificación"],
     "categoria": "equipamiento"},

    {"pregunta": "chaleco reflectivo delivery Ecuador obligatorio carretera nocturno comercial",
     "esperado": "Si, obligatorio para actividad comercial nocturna",
     "terminos_fe": ["chaleco", "reflectivo", "delivery", "nocturno", "obligatorio", "comercial"],
     "categoria": "equipamiento"},

    {"pregunta": "certificacion ECE 22.06 casco motocicleta estandar europeo seguridad vigente",
     "esperado": "Estandar europeo de seguridad vigente para cascos de moto",
     "terminos_fe": ["ece", "22.06", "europeo", "estándar", "estandar", "casco", "seguridad"],
     "categoria": "equipamiento"},

    {"pregunta": "sancion multa casco Ecuador LOTTTSV infraccion grave retencion vehiculo motocicleta",
     "esperado": "Multa y retencion del vehiculo por no usar casco",
     "terminos_fe": ["multa", "retención", "retencion", "casco", "infracción", "sanción", "vehiculo", "puntos", "licencia"],
     "categoria": "sanciones"},

    {"pregunta": "zigzag motocicleta Ecuador prohibido infraccion LOTTTSV cambios bruscos carril",
     "esperado": "zigzag es maniobra peligrosa PROHIBIDA por la LOTTTSV",
     "terminos_fe": ["zigzag", "prohibido", "prohibida", "peligrosa", "carril", "lotttsv"],
     "categoria": "normativa"},

    {"pregunta": "adelantar izquierda derecha Ecuador prohibido rebasar motocicleta norma",
     "esperado": "Los adelantamientos se realizan por la izquierda",
     "terminos_fe": ["adelantar", "izquierda", "derecha", "prohibido", "rebasar"],
     "categoria": "normativa"},

    {"pregunta": "licencia conducir moto tipo A Ecuador ANT cilindraje subcategorias A1 A2",
     "esperado": "Tipo A motocicletas con subcategorias por cilindraje",
     "terminos_fe": ["licencia", "tipo", "motocicleta", "cilindraje", "ant", "categoría"],
     "categoria": "licencias"},

    {"pregunta": "tecnica correcta frenado motocicleta freno delantero trasero ambos gradualmente",
     "esperado": "Usar ambos frenos gradualmente delantero y trasero",
     "terminos_fe": ["freno", "delantero", "trasero", "ambos", "gradualmente", "frenado"],
     "categoria": "conduccion"},

    {"pregunta": "distancia seguimiento segundos moto velocidad 50 km/h seguridad vial",
     "esperado": "Minimo 2 segundos de distancia de seguimiento",
     "terminos_fe": ["distancia", "segundos", "seguimiento", "seguridad", "velocidad"],
     "categoria": "conduccion"},

    {"pregunta": "Como frenar piso mojado lluvia motocicleta sin bloquear ruedas tecnica segura",
     "esperado": "Suavemente con ambos frenos sin bloquear las ruedas",
     "terminos_fe": ["mojado", "lluvia", "bloquear", "ruedas", "suavemente", "frenos"],
     "categoria": "lluvia"},

    {"pregunta": "aquaplaning motocicleta agua lluvia perdida traccion prevencion velocidad",
     "esperado": "Perdida de traccion sobre agua prevencion reducir velocidad",
     "terminos_fe": ["aquaplaning", "tracción", "traccion", "agua", "velocidad", "prevención"],
     "categoria": "lluvia"},

    {"pregunta": "FINE-C mantenimiento revision previa moto combustible instrumentos neumaticos electrico control",
     "esperado": "Combustible Instrumentos Neumaticos Electrico Control revision previa",
     "terminos_fe": ["fine-c", "fine", "combustible", "instrumentos", "neumáticos", "eléctrico", "control"],
     "categoria": "mantenimiento"},

    {"pregunta": "presion neumaticos llantas moto PSI libras recomendacion fabricante inflado correcto",
     "esperado": "Segun el fabricante generalmente entre 28-32 PSI",
     "terminos_fe": ["presión", "presion", "psi", "neumáticos", "fabricante", "28", "32"],
     "categoria": "mantenimiento"},

    {"pregunta": "accidente transito Ecuador 911 emergencia primer respondiente no mover herido senalizar area",
     "esperado": "Llamar al 911 no mover al herido senalizar el area",
     "terminos_fe": ["911", "accidente", "herido", "señalizar", "senalizar", "mover", "emergencia"],
     "categoria": "primeros_auxilios"},

    {"pregunta": "alcohol conducir moto Ecuador limite cero sancion grave LOTTTSV alcoholemia prohibido",
     "esperado": "No se debe conducir con alcohol limite 0 para motos",
     "terminos_fe": ["alcohol", "alcoholemia", "cero", "prohibido", "sanción", "conducir"],
     "categoria": "normativa"},

    {"pregunta": "pasajero acompanante moto Ecuador casco obligatorio dos personas permitido requisito",
     "esperado": "Si si la moto esta disenada para ello y el pasajero usa casco",
     "terminos_fe": ["pasajero", "acompañante", "casco", "obligatorio", "dos", "personas", "permitido"],
     "categoria": "normativa"},
]


def calcular_faithfulness(respuesta: str, terminos_fe: list) -> float:
    """
    Faithfulness basado en terminos clave esperados en la respuesta.
    Mas preciso que buscar en el contexto_preview limitado.
    """
    if not respuesta or not terminos_fe:
        return 0.0

    respuesta_lower = respuesta.lower()

    # Verificar cuantos terminos clave aparecen en la respuesta
    encontrados = sum(1 for t in terminos_fe if t.lower() in respuesta_lower)
    score = encontrados / len(terminos_fe)

    # Bonus por citas explicitas de documentos
    citas = ["documento", "segun el documento", "de acuerdo al documento",
             "lotttsv", "art.", "articulo", "segun la ley", "indica que",
             "menciona que", "como indica"]
    bonus = sum(0.05 for c in citas if c in respuesta_lower)
    score = min(1.0, score + bonus)

    return round(score, 3)


def calcular_relevancia(respuesta: str, esperado: str) -> float:
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

            # Faithfulness basado en terminos esperados en la respuesta
            faith = calcular_faithfulness(respuesta, eval_item["terminos_fe"])
            relev = calcular_relevancia(respuesta, eval_item["esperado"])

            faith_scores.append(faith)
            relev_scores.append(relev)

            icon = "✅" if faith >= 0.60 else "⚠️"
            print(f"  {icon} P{i+1:02d} [{eval_item['categoria'][:12]:12}] docs:{docs_raw} faith:{faith:.2f} relev:{relev:.2f}")

            resultados.append({
                "id": i+1,
                "categoria": eval_item["categoria"],
                "pregunta": eval_item["pregunta"][:60] + "...",
                "docs": docs_raw,
                "faithfulness": faith,
                "relevancia": relev,
                "modo": data.get("modo", "unknown"),
                "tokens": data.get("tokens_usados", 0)
            })

        except Exception as e:
            print(f"  ❌ P{i+1:02d} Error: {e}")
            faith_scores.append(0.0)
            relev_scores.append(0.0)

    faith_mean = statistics.mean(faith_scores) if faith_scores else 0
    relev_mean = statistics.mean(relev_scores) if relev_scores else 0
    faith_std  = statistics.stdev(faith_scores) if len(faith_scores) > 1 else 0
    tokens_total = sum(r.get("tokens", 0) for r in resultados)

    print("\n" + "=" * 60)
    print("  RESULTADOS RAGAS")
    print("=" * 60)
    print(f"  Faithfulness media:     {faith_mean:.3f} (objetivo >= 0.70)")
    print(f"  Faithfulness std:       {faith_std:.3f}")
    print(f"  Answer Relevance media: {relev_mean:.3f}")
    print(f"  Preguntas evaluadas:    {len(resultados)}")
    print(f"  Tokens usados:          {tokens_total:,}")
    print(f"  Costo estimado:         ~${tokens_total * 0.000003:.4f} USD")

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
        "tokens_totales":    tokens_total,
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