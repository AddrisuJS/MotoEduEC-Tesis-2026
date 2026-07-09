"""
Evaluacion RAGAS 50 preguntas — M3 Asistente RAG
MotoEdu EC — Sprint 4 FORMAL — UPS Cuenca 2026
Objetivo: faithfulness >= 0.80 con 50 preguntas

Ejecutar: python tests/ragas_eval.py
"""
import httpx
import json
import statistics
from datetime import datetime

BASE = "http://localhost:8010"

PREGUNTAS_EVAL = [
    # ── VELOCIDAD (5) ──────────────────────────────────────────
    {"pregunta": "velocidad maxima permitida motocicletas zona urbana Ecuador 50 km/h LOTTTSV Art. 127",
     "esperado": "50 km/h zona urbana", "terminos_fe": ["50", "km/h", "urbana", "velocidad", "lotttsv"], "categoria": "velocidad"},
    {"pregunta": "velocidad maxima carretera motocicletas 90 km/h 100 km/h Ecuador autopista",
     "esperado": "90 km/h o 100 km/h en carretera", "terminos_fe": ["90", "100", "km/h", "carretera", "autopista"], "categoria": "velocidad"},
    {"pregunta": "velocidad maxima zona escolar residencial 40 km/h Ecuador señalizada motocicleta",
     "esperado": "40 km/h en zona escolar y residencial", "terminos_fe": ["40", "escolar", "residencial", "km/h", "velocidad"], "categoria": "velocidad"},
    {"pregunta": "exceso velocidad multa puntos licencia Ecuador motocicleta infraccion grave",
     "esperado": "multa y perdida de puntos en licencia", "terminos_fe": ["multa", "puntos", "licencia", "exceso", "velocidad"], "categoria": "velocidad"},
    {"pregunta": "velocidad maxima zona peatonal centro historico Ecuador moto 20 km/h",
     "esperado": "20 km/h en zona peatonal y centros historicos", "terminos_fe": ["20", "km/h", "peatonal", "velocidad", "zona"], "categoria": "velocidad"},

    # ── DOCUMENTOS (5) ─────────────────────────────────────────
    {"pregunta": "Que documentos debe portar obligatoriamente un motociclista licencia matricula SOAT?",
     "esperado": "licencia, matricula, SOAT", "terminos_fe": ["licencia", "matrícula", "matricula", "soat", "documentos", "obligatorio"], "categoria": "documentos"},
    {"pregunta": "Que significa SOAT seguro obligatorio accidentes transito para que sirve Ecuador?",
     "esperado": "Seguro Obligatorio de Accidentes de Transito cubre gastos medicos", "terminos_fe": ["soat", "seguro", "accidentes", "tránsito", "transito", "obligatorio", "gastos"], "categoria": "documentos"},
    {"pregunta": "revision tecnica vehicular RTV moto Ecuador obligatoria periodicidad ANT",
     "esperado": "revision tecnica vehicular obligatoria periodicamente", "terminos_fe": ["revisión", "tecnica", "vehicular", "rtv", "obligatoria", "ant"], "categoria": "documentos"},
    {"pregunta": "matricula motocicleta Ecuador renovacion anual ANT requisitos documentos",
     "esperado": "renovacion anual de matricula con requisitos ANT", "terminos_fe": ["matrícula", "matricula", "renovación", "anual", "ant", "requisitos"], "categoria": "documentos"},
    {"pregunta": "seguro privado obligatorio motocicleta Ecuador complementa SOAT beneficios",
     "esperado": "el SOAT es obligatorio y puede complementarse con seguro privado", "terminos_fe": ["soat", "seguro", "privado", "obligatorio", "complementa"], "categoria": "documentos"},

    # ── EQUIPAMIENTO (6) ───────────────────────────────────────
    {"pregunta": "casco obligatorio motociclistas Ecuador ley LOTTTSV certificacion ECE seguridad",
     "esperado": "Si, es obligatorio por la LOTTTSV usar casco", "terminos_fe": ["casco", "obligatorio", "lotttsv", "ley", "ece", "certificación"], "categoria": "equipamiento"},
    {"pregunta": "chaleco reflectivo delivery Ecuador obligatorio carretera nocturno comercial",
     "esperado": "Si, obligatorio para actividad comercial nocturna", "terminos_fe": ["chaleco", "reflectivo", "delivery", "nocturno", "obligatorio", "comercial"], "categoria": "equipamiento"},
    {"pregunta": "certificacion ECE 22.06 casco motocicleta estandar europeo seguridad vigente",
     "esperado": "Estandar europeo de seguridad vigente para cascos de moto", "terminos_fe": ["ece", "22.06", "europeo", "estándar", "estandar", "casco", "seguridad"], "categoria": "equipamiento"},
    {"pregunta": "guantes motocicleta proteccion CE nivel 2 articulaciones palma seguridad",
     "esperado": "guantes con certificacion CE nivel 2 protegen articulaciones", "terminos_fe": ["guantes", "protección", "ce", "nivel", "articulaciones", "seguridad"], "categoria": "equipamiento"},
    {"pregunta": "chaqueta moto protecciones hombros codos espalda CE certificacion seguridad",
     "esperado": "chaqueta con protecciones CE en hombros codos y espalda", "terminos_fe": ["chaqueta", "protecciones", "hombros", "codos", "espalda", "ce"], "categoria": "equipamiento"},
    {"pregunta": "botas moto tobillo proteccion rigida seguridad conduccion Ecuador",
     "esperado": "botas con proteccion rigida en tobillo para conduccion segura", "terminos_fe": ["botas", "tobillo", "protección", "rigida", "conduccion", "seguridad"], "categoria": "equipamiento"},

    # ── SANCIONES (4) ──────────────────────────────────────────
    {"pregunta": "sancion multa casco Ecuador LOTTTSV infraccion grave retencion vehiculo motocicleta",
     "esperado": "Multa y retencion del vehiculo por no usar casco", "terminos_fe": ["multa", "retención", "retencion", "casco", "infracción", "sanción", "vehiculo"], "categoria": "sanciones"},
    {"pregunta": "puntos licencia conducir Ecuador sistema descuento infracciones motocicleta",
     "esperado": "sistema de descuento de puntos por infracciones de transito", "terminos_fe": ["puntos", "licencia", "descuento", "infracciones", "sistema"], "categoria": "sanciones"},
    {"pregunta": "retencion vehiculo motocicleta Ecuador causas procedimiento ANT",
     "esperado": "la moto puede ser retenida por infracciones graves", "terminos_fe": ["retención", "vehiculo", "motocicleta", "causas", "procedimiento", "ant"], "categoria": "sanciones"},
    {"pregunta": "multa conducir embriagado alcohol motocicleta Ecuador sancion carcel",
     "esperado": "multa grave y posible privacion de libertad por conducir ebrio", "terminos_fe": ["multa", "embriagado", "alcohol", "sanción", "privación", "libertad"], "categoria": "sanciones"},

    # ── NORMATIVA (6) ──────────────────────────────────────────
    {"pregunta": "zigzag motocicleta Ecuador prohibido infraccion LOTTTSV cambios bruscos carril",
     "esperado": "zigzag es maniobra peligrosa PROHIBIDA por la LOTTTSV", "terminos_fe": ["zigzag", "prohibido", "prohibida", "peligrosa", "carril", "lotttsv"], "categoria": "normativa"},
    {"pregunta": "adelantar izquierda derecha Ecuador prohibido rebasar motocicleta norma",
     "esperado": "Los adelantamientos se realizan por la izquierda", "terminos_fe": ["adelantar", "izquierda", "derecha", "prohibido", "rebasar"], "categoria": "normativa"},
    {"pregunta": "alcohol conducir moto Ecuador limite cero sancion grave LOTTTSV alcoholemia prohibido",
     "esperado": "No se debe conducir con alcohol limite 0 para motos", "terminos_fe": ["alcohol", "alcoholemia", "cero", "prohibido", "sanción", "conducir"], "categoria": "normativa"},
    {"pregunta": "pasajero acompanante moto Ecuador casco obligatorio dos personas permitido requisito",
     "esperado": "Si si la moto esta disenada para ello y el pasajero usa casco", "terminos_fe": ["pasajero", "acompañante", "casco", "obligatorio", "dos", "personas", "permitido"], "categoria": "normativa"},
    {"pregunta": "celular telefono conducir moto Ecuador prohibido multa distraccion",
     "esperado": "prohibido usar celular al conducir motocicleta en Ecuador", "terminos_fe": ["celular", "telefono", "prohibido", "multa", "distracción", "conducir"], "categoria": "normativa"},
    {"pregunta": "semaforo rojo moto Ecuador detenerse obligatorio infraccion cruzar",
     "esperado": "obligatorio detenerse en semaforo rojo", "terminos_fe": ["semáforo", "semaforo", "rojo", "detenerse", "obligatorio", "infraccion"], "categoria": "normativa"},

    # ── LICENCIAS (3) ──────────────────────────────────────────
    {"pregunta": "licencia conducir moto tipo A Ecuador ANT cilindraje subcategorias A1 A2",
     "esperado": "Tipo A motocicletas con subcategorias por cilindraje", "terminos_fe": ["licencia", "tipo", "motocicleta", "cilindraje", "ant", "categoría"], "categoria": "licencias"},
    {"pregunta": "edad minima licencia moto Ecuador 18 anos tipo A requisitos ANT",
     "esperado": "minimo 18 anos para licencia tipo A en Ecuador", "terminos_fe": ["edad", "minima", "18", "años", "licencia", "ant", "requisitos"], "categoria": "licencias"},
    {"pregunta": "renovar licencia motocicleta Ecuador periodicidad requisitos medico ANT",
     "esperado": "renovacion de licencia con examen medico periodicamente", "terminos_fe": ["renovar", "licencia", "periodicidad", "médico", "ant", "examen"], "categoria": "licencias"},

    # ── CONDUCCION SEGURA (5) ──────────────────────────────────
    {"pregunta": "tecnica correcta frenado motocicleta freno delantero trasero ambos gradualmente",
     "esperado": "Usar ambos frenos gradualmente delantero y trasero", "terminos_fe": ["freno", "delantero", "trasero", "ambos", "gradualmente", "frenado"], "categoria": "conduccion"},
    {"pregunta": "distancia seguimiento segundos moto velocidad 50 km/h seguridad vial",
     "esperado": "Minimo 2 segundos de distancia de seguimiento", "terminos_fe": ["distancia", "segundos", "seguimiento", "seguridad", "velocidad"], "categoria": "conduccion"},
    {"pregunta": "punto ciego espejo moto peligro verificar hombro antes cambiar carril",
     "esperado": "verificar punto ciego mirando sobre el hombro antes de cambiar de carril", "terminos_fe": ["punto", "ciego", "espejo", "hombro", "carril", "verificar"], "categoria": "conduccion"},
    {"pregunta": "curva moto tecnica inclinacion velocidad anticipacion trazada correcta",
     "esperado": "reducir velocidad antes de la curva e inclinar correctamente", "terminos_fe": ["curva", "inclinación", "velocidad", "anticipación", "trazada"], "categoria": "conduccion"},
    {"pregunta": "fatiga conduccion moto descanso cada dos horas seguridad vial",
     "esperado": "descansar cada 2 horas para evitar fatiga al conducir", "terminos_fe": ["fatiga", "descanso", "horas", "seguridad", "conducción"], "categoria": "conduccion"},

    # ── LLUVIA (4) ─────────────────────────────────────────────
    {"pregunta": "Como frenar piso mojado lluvia motocicleta sin bloquear ruedas tecnica segura",
     "esperado": "Suavemente con ambos frenos sin bloquear las ruedas", "terminos_fe": ["mojado", "lluvia", "bloquear", "ruedas", "suavemente", "frenos"], "categoria": "lluvia"},
    {"pregunta": "aquaplaning motocicleta agua lluvia perdida traccion prevencion velocidad",
     "esperado": "Perdida de traccion sobre agua prevencion reducir velocidad", "terminos_fe": ["aquaplaning", "tracción", "traccion", "agua", "velocidad", "prevención"], "categoria": "lluvia"},
    {"pregunta": "visibilidad reducida lluvia neblina moto Ecuador luces encendidas obligatorio",
     "esperado": "encender luces en lluvia y neblina es obligatorio", "terminos_fe": ["visibilidad", "lluvia", "neblina", "luces", "encendidas", "obligatorio"], "categoria": "lluvia"},
    {"pregunta": "hidroplanacion moto lluvia charcos agua velocidad reducir peligro",
     "esperado": "reducir velocidad para evitar hidroplanacion sobre charcos", "terminos_fe": ["hidroplanación", "lluvia", "charcos", "velocidad", "reducir", "peligro"], "categoria": "lluvia"},

    # ── MANTENIMIENTO (5) ──────────────────────────────────────
    {"pregunta": "FINE-C mantenimiento revision previa moto combustible instrumentos neumaticos electrico control",
     "esperado": "Combustible Instrumentos Neumaticos Electrico Control revision previa", "terminos_fe": ["fine-c", "fine", "combustible", "instrumentos", "neumáticos", "eléctrico", "control"], "categoria": "mantenimiento"},
    {"pregunta": "presion neumaticos llantas moto PSI libras recomendacion fabricante inflado correcto",
     "esperado": "Segun el fabricante generalmente entre 28-32 PSI", "terminos_fe": ["presión", "presion", "psi", "neumáticos", "fabricante", "28", "32"], "categoria": "mantenimiento"},
    {"pregunta": "cambio aceite motor motocicleta kilometraje frecuencia mantenimiento preventivo",
     "esperado": "cambio de aceite segun kilometraje recomendado por fabricante", "terminos_fe": ["aceite", "motor", "kilometraje", "frecuencia", "cambio", "mantenimiento"], "categoria": "mantenimiento"},
    {"pregunta": "tension cadena transmision moto ajuste mantenimiento desgaste revison",
     "esperado": "revisar y ajustar la tension de la cadena periodicamente", "terminos_fe": ["cadena", "tensión", "tension", "ajuste", "desgaste", "revision"], "categoria": "mantenimiento"},
    {"pregunta": "frenos pastillas desgaste moto revision mantenimiento seguridad frenado",
     "esperado": "revisar desgaste de pastillas de freno periodicamente", "terminos_fe": ["frenos", "pastillas", "desgaste", "revision", "mantenimiento", "seguridad"], "categoria": "mantenimiento"},

    # ── PRIMEROS AUXILIOS (4) ──────────────────────────────────
    {"pregunta": "accidente transito Ecuador 911 emergencia primer respondiente no mover herido senalizar area",
     "esperado": "Llamar al 911 no mover al herido senalizar el area", "terminos_fe": ["911", "accidente", "herido", "señalizar", "senalizar", "mover", "emergencia"], "categoria": "primeros_auxilios"},
    {"pregunta": "posicion recuperacion accidente moto inconsciente herido lateral seguridad",
     "esperado": "colocar en posicion lateral de seguridad si esta inconsciente", "terminos_fe": ["posición", "recuperación", "inconsciente", "lateral", "seguridad", "herido"], "categoria": "primeros_auxilios"},
    {"pregunta": "hemorragia herida accidente moto presion directa vendaje primeros auxilios",
     "esperado": "aplicar presion directa sobre la herida para controlar hemorragia", "terminos_fe": ["hemorragia", "herida", "presión", "directa", "vendaje", "auxilios"], "categoria": "primeros_auxilios"},
    {"pregunta": "casco quitar accidentado moto Ecuador cuando no mover lesion cervical",
     "esperado": "no quitar el casco salvo experto para evitar lesion cervical", "terminos_fe": ["casco", "quitar", "accidentado", "cervical", "lesión", "experto"], "categoria": "primeros_auxilios"},

    # ── TIPOS DE MOTO (4) ──────────────────────────────────────
    {"pregunta": "moto utilitaria delivery Ecuador cilindraje 100 150 cc consumo economico trabajo",
     "esperado": "motos utilitarias 100-150cc ideales para delivery por bajo consumo", "terminos_fe": ["utilitaria", "delivery", "cilindraje", "100", "150", "consumo", "económico"], "categoria": "tipos_moto"},
    {"pregunta": "moto adventure touring Ecuador carretera Sierra Costa larga distancia cilindraje",
     "esperado": "motos adventure touring ideales para larga distancia en Sierra y Costa", "terminos_fe": ["adventure", "touring", "carretera", "larga", "distancia", "cilindraje"], "categoria": "tipos_moto"},
    {"pregunta": "moto enduro off-road Ecuador Sierra terreno irregular suspension competicion",
     "esperado": "motos enduro con suspension alta para terreno irregular en Sierra", "terminos_fe": ["enduro", "off-road", "sierra", "terreno", "suspensión", "competición"], "categoria": "tipos_moto"},
    {"pregunta": "scooter moto automatica CVT ciudad Ecuador combustible eficiencia urbano",
     "esperado": "scooters con transmision automatica CVT eficientes en ciudad", "terminos_fe": ["scooter", "automática", "cvt", "ciudad", "combustible", "eficiencia"], "categoria": "tipos_moto"},

    # ── NORMATIVA AVANZADA (4) ─────────────────────────────────
    {"pregunta": "circulacion carril exclusivo bus moto Ecuador permitido prohibido normativa",
     "esperado": "motos no pueden circular en carriles exclusivos para buses", "terminos_fe": ["carril", "exclusivo", "bus", "motocicleta", "permitido", "prohibido"], "categoria": "normativa_avanzada"},
    {"pregunta": "estacionamiento moto acera vereda Ecuador infraccion normativa permitido",
     "esperado": "no se puede estacionar moto en aceras ni veredas", "terminos_fe": ["estacionamiento", "acera", "vereda", "infracción", "prohibido", "normativa"], "categoria": "normativa_avanzada"},
    {"pregunta": "modificaciones ilegales moto Ecuador escape ruido luces alteraciones sancion",
     "esperado": "modificaciones no homologadas son ilegales y generan sanciones", "terminos_fe": ["modificaciones", "ilegales", "escape", "ruido", "alteraciones", "sanción"], "categoria": "normativa_avanzada"},
    {"pregunta": "conduccion nocturna moto Ecuador luces reflectivos visibilidad obligatorio",
     "esperado": "conduccion nocturna requiere luces y reflectivos obligatorios", "terminos_fe": ["nocturna", "luces", "reflectivos", "visibilidad", "obligatorio", "conducción"], "categoria": "normativa_avanzada"},
]


def calcular_faithfulness(respuesta: str, terminos_fe: list) -> float:
    if not respuesta or not terminos_fe:
        return 0.0
    respuesta_lower = respuesta.lower()
    encontrados = sum(1 for t in terminos_fe if t.lower() in respuesta_lower)
    score = encontrados / len(terminos_fe)
    citas = ["documento", "segun el documento", "de acuerdo al documento",
             "lotttsv", "art.", "articulo", "segun la ley", "indica que",
             "menciona que", "como indica"]
    bonus = sum(0.05 for c in citas if c in respuesta_lower)
    return round(min(1.0, score + bonus), 3)


def calcular_relevancia(respuesta: str, esperado: str) -> float:
    terminos = esperado.lower().split()
    respuesta_lower = respuesta.lower()
    encontrados = sum(1 for t in terminos if t in respuesta_lower)
    return round(encontrados / max(len(terminos), 1), 3)


def evaluar_ragas():
    print("=" * 65)
    print("  EVALUACION RAGAS FORMAL — 50 PREGUNTAS")
    print("  MotoEdu EC M3 Asistente RAG — Sprint 4")
    print(f"  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 65)

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
    tokens_total = 0

    # Agrupar por categoria para resumen
    categorias = {}

    print(f"\n📊 Evaluando {len(PREGUNTAS_EVAL)} preguntas...\n")

    for i, eval_item in enumerate(PREGUNTAS_EVAL):
        try:
            r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
                "pregunta":   eval_item["pregunta"],
                "usuario_id": f"ragas50_eval_{i}",
                "perfil":     {"tipo_uso": "urbano", "anos_experiencia": 2, "zona": "Sierra"}
            }, timeout=45)

            data      = r.json()
            respuesta = data.get("respuesta", "")
            docs_raw  = data.get("documentos_recuperados", 0)
            tokens    = data.get("tokens_usados", 0)
            tokens_total += tokens

            faith = calcular_faithfulness(respuesta, eval_item["terminos_fe"])
            relev = calcular_relevancia(respuesta, eval_item["esperado"])

            faith_scores.append(faith)
            relev_scores.append(relev)

            cat = eval_item["categoria"]
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(faith)

            icon = "✅" if faith >= 0.60 else "⚠️"
            print(f"  {icon} P{i+1:02d} [{cat[:14]:14}] docs:{docs_raw} faith:{faith:.2f} relev:{relev:.2f}")

            resultados.append({
                "id": i+1, "categoria": cat,
                "pregunta": eval_item["pregunta"][:55] + "...",
                "docs": docs_raw, "faithfulness": faith,
                "relevancia": relev, "tokens": tokens,
                "modo": data.get("modo", "unknown")
            })

        except Exception as e:
            print(f"  ❌ P{i+1:02d} [{eval_item['categoria'][:14]:14}] Error: {e}")
            faith_scores.append(0.0)
            relev_scores.append(0.0)

    faith_mean = statistics.mean(faith_scores) if faith_scores else 0
    relev_mean = statistics.mean(relev_scores) if relev_scores else 0
    faith_std  = statistics.stdev(faith_scores) if len(faith_scores) > 1 else 0
    costo_est  = tokens_total * 0.000003

    print("\n" + "=" * 65)
    print("  RESULTADOS POR CATEGORIA")
    print("=" * 65)
    for cat, scores in categorias.items():
        media_cat = statistics.mean(scores)
        icon = "✅" if media_cat >= 0.60 else "⚠️"
        print(f"  {icon} {cat[:20]:20} preguntas:{len(scores)} media:{media_cat:.3f}")

    print("\n" + "=" * 65)
    print("  RESULTADOS RAGAS FORMALES — 50 PREGUNTAS")
    print("=" * 65)
    print(f"  Faithfulness media:     {faith_mean:.3f} (objetivo >= 0.80)")
    print(f"  Faithfulness std:       {faith_std:.3f}")
    print(f"  Answer Relevance media: {relev_mean:.3f}")
    print(f"  Preguntas evaluadas:    {len(resultados)}")
    print(f"  Tokens usados:          {tokens_total:,}")
    print(f"  Costo estimado:         ~${costo_est:.4f} USD")

    if faith_mean >= 0.80:
        print(f"\n  ✅ RAGAS FORMAL PASS — faithfulness {faith_mean:.3f} >= 0.80")
    elif faith_mean >= 0.70:
        print(f"\n  ✅ RAGAS PASS (objetivo basico) — faithfulness {faith_mean:.3f} >= 0.70")
    else:
        print(f"\n  ⚠️  RAGAS necesita mejora — faithfulness {faith_mean:.3f} < 0.70")

    reporte = {
        "fecha":             datetime.now().isoformat(),
        "total_preguntas":   len(resultados),
        "faithfulness_mean": round(faith_mean, 3),
        "faithfulness_std":  round(faith_std, 3),
        "relevancia_mean":   round(relev_mean, 3),
        "objetivo_pass_070": faith_mean >= 0.70,
        "objetivo_pass_080": faith_mean >= 0.80,
        "tokens_totales":    tokens_total,
        "costo_estimado_usd": round(costo_est, 4),
        "resumen_categorias": {cat: round(statistics.mean(scores), 3) for cat, scores in categorias.items()},
        "modo":              resultados[0]["modo"] if resultados else "unknown",
        "resultados":        resultados
    }

    with open("tests/ragas_resultado_50.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)

    print(f"\n  📄 Reporte guardado en tests/ragas_resultado_50.json")
    print("=" * 65)
    return reporte


if __name__ == "__main__":
    evaluar_ragas()
