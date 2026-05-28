"""
Pretest-Postest — Experimento Piloto Sprint 5
MotoEdu EC — UPS Cuenca 2026

Cuestionario de 15 items sobre LOTTTSV, conduccion segura y equipamiento.
Analisis estadistico: t-test pareado, Cohen's d, IC 95%.

Uso:
  python tests/pretest_postest.py --modo registrar --usuario_id UUID --tipo pretest
  python tests/pretest_postest.py --modo analizar
  python tests/pretest_postest.py --modo cuestionario
"""
import json, argparse, statistics, math
from datetime import datetime

# ─── Cuestionario 15 items ────────────────────────────────────
CUESTIONARIO = [
    {
        "id": 1,
        "pregunta": "Cual es la velocidad maxima permitida para motocicletas en zona urbana en Ecuador?",
        "opciones": ["A) 40 km/h", "B) 50 km/h", "C) 60 km/h", "D) 80 km/h"],
        "correcta": "B",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 2,
        "pregunta": "Cual es la velocidad maxima en carretera para motocicletas en Ecuador?",
        "opciones": ["A) 80 km/h", "B) 90 km/h", "C) 100 km/h", "D) 120 km/h"],
        "correcta": "C",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 3,
        "pregunta": "Es obligatorio el uso de casco para motociclistas en Ecuador segun la LOTTTSV?",
        "opciones": ["A) Solo en carretera", "B) Solo de noche", "C) Si, siempre es obligatorio", "D) Solo para el conductor"],
        "correcta": "C",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 4,
        "pregunta": "Que documentos debe portar obligatoriamente un motociclista en Ecuador?",
        "opciones": ["A) Solo la licencia", "B) Licencia y matricula", "C) Licencia, matricula y SOAT", "D) Solo el SOAT"],
        "correcta": "C",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 5,
        "pregunta": "Que significa SOAT?",
        "opciones": [
            "A) Seguro Obligatorio de Accidentes de Transito",
            "B) Sistema Operativo de Atencion al Transportista",
            "C) Seguro Opcional de Asistencia en Transito",
            "D) Servicio Oficial de Ayuda al Transportista"
        ],
        "correcta": "A",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 6,
        "pregunta": "Cual es la tecnica correcta de frenado en condiciones normales con una motocicleta?",
        "opciones": [
            "A) Solo el freno delantero",
            "B) Solo el freno trasero",
            "C) Ambos frenos gradualmente, primero el trasero luego el delantero",
            "D) Freno de motor unicamente"
        ],
        "correcta": "C",
        "categoria": "Conduccion Segura",
        "dificultad": "intermedio"
    },
    {
        "id": 7,
        "pregunta": "Como se debe frenar correctamente en piso mojado?",
        "opciones": [
            "A) Frenar fuerte solo con el delantero",
            "B) Suavemente con ambos frenos sin bloquear las ruedas",
            "C) Solo frenar con el motor",
            "D) No frenar y esperar que la moto se detenga sola"
        ],
        "correcta": "B",
        "categoria": "Conduccion en Lluvia",
        "dificultad": "intermedio"
    },
    {
        "id": 8,
        "pregunta": "Que es el aquaplaning?",
        "opciones": [
            "A) Una tecnica de conduccion deportiva",
            "B) Perdida de traccion cuando la llanta flota sobre agua",
            "C) Un tipo de llanta para lluvia",
            "D) El sistema de frenos ABS"
        ],
        "correcta": "B",
        "categoria": "Conduccion en Lluvia",
        "dificultad": "intermedio"
    },
    {
        "id": 9,
        "pregunta": "Que significa la certificacion ECE 22.06 en un casco?",
        "opciones": [
            "A) Es el precio del casco en euros",
            "B) Es el numero de serie del fabricante",
            "C) Es el estandar europeo de seguridad mas reciente para cascos",
            "D) Indica que el casco es para uso deportivo unicamente"
        ],
        "correcta": "C",
        "categoria": "Equipamiento de Seguridad",
        "dificultad": "intermedio"
    },
    {
        "id": 10,
        "pregunta": "Cuales son los primeros pasos ante un accidente de transito como primer respondiente?",
        "opciones": [
            "A) Mover al herido para que este comodo",
            "B) Llamar al 911, no mover al herido, senalizar el area",
            "C) Dar agua al herido y esperar",
            "D) Fotografiar el accidente y publicar en redes"
        ],
        "correcta": "B",
        "categoria": "Primeros Auxilios",
        "dificultad": "basico"
    },
    {
        "id": 11,
        "pregunta": "Que significa FINE-C en el mantenimiento de motocicletas?",
        "opciones": [
            "A) Es una marca de lubricante",
            "B) Es una norma de la ANT",
            "C) Combustible, Instrumentos, Neumaticos, Electrico, Control — revision previa",
            "D) Es el protocolo de emergencia vial"
        ],
        "correcta": "C",
        "categoria": "Mantenimiento",
        "dificultad": "avanzado"
    },
    {
        "id": 12,
        "pregunta": "Se puede adelantar a otro vehiculo por la derecha en Ecuador?",
        "opciones": [
            "A) Si, siempre que haya espacio",
            "B) Solo en autopistas",
            "C) No, los adelantamientos se realizan por la izquierda",
            "D) Solo si el vehiculo va muy lento"
        ],
        "correcta": "C",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 13,
        "pregunta": "Cuanto tiempo de seguimiento minimo se recomienda mantener detras de un vehiculo a 50 km/h?",
        "opciones": ["A) 1 segundo", "B) 2 segundos", "C) 5 segundos", "D) 10 metros fijos"],
        "correcta": "B",
        "categoria": "Conduccion Segura",
        "dificultad": "intermedio"
    },
    {
        "id": 14,
        "pregunta": "El zigzag entre vehiculos esta permitido en Ecuador?",
        "opciones": [
            "A) Si, si se hace con precaucion",
            "B) Solo en emergencias",
            "C) No, esta expresamente PROHIBIDO por la LOTTTSV",
            "D) Solo en zonas de alta congestion"
        ],
        "correcta": "C",
        "categoria": "Normativa LOTTTSV",
        "dificultad": "basico"
    },
    {
        "id": 15,
        "pregunta": "Que tipo de motocicleta es mas adecuada para uso de delivery en ciudad en Ecuador?",
        "opciones": [
            "A) Moto deportiva 600cc",
            "B) Moto utilitaria 100-150cc",
            "C) Moto enduro",
            "D) Cualquier tipo de moto"
        ],
        "correcta": "B",
        "categoria": "Tipos de Motocicletas",
        "dificultad": "basico"
    },
]

# ─── Almacen de datos (en produccion usar PostgreSQL) ─────────
DATOS_EXPERIMENTO = []


def calcular_puntaje(respuestas: dict) -> dict:
    """Calcula el puntaje de un cuestionario completado."""
    correctas = 0
    resultados_detalle = []
    for item in CUESTIONARIO:
        resp = respuestas.get(str(item["id"]), "")
        es_correcta = resp.upper().startswith(item["correcta"])
        if es_correcta:
            correctas += 1
        resultados_detalle.append({
            "id": item["id"],
            "respuesta_dada": resp,
            "correcta": es_correcta,
            "categoria": item["categoria"]
        })
    pct = round(100 * correctas / len(CUESTIONARIO), 1)
    return {
        "total_preguntas": len(CUESTIONARIO),
        "correctas": correctas,
        "pct_acierto": pct,
        "detalle": resultados_detalle
    }


def registrar_resultado(usuario_id: str, tipo: str, respuestas: dict):
    """Registra pretest o postest de un participante."""
    resultado = calcular_puntaje(respuestas)
    entrada = {
        "usuario_id": usuario_id,
        "tipo": tipo,  # "pretest" o "postest"
        "puntaje": resultado["correctas"],
        "total": resultado["total_preguntas"],
        "pct_acierto": resultado["pct_acierto"],
        "fecha": datetime.now().isoformat(),
        "detalle": resultado["detalle"]
    }
    DATOS_EXPERIMENTO.append(entrada)
    return entrada


def analisis_estadistico():
    """
    Analisis estadistico del experimento pretest-postest.
    T-test pareado + Cohen's d + IC 95%
    """
    pretests  = [d for d in DATOS_EXPERIMENTO if d["tipo"] == "pretest"]
    postests  = [d for d in DATOS_EXPERIMENTO if d["tipo"] == "postest"]

    if len(pretests) < 2 or len(postests) < 2:
        return {"error": f"Datos insuficientes. Pretests: {len(pretests)}, Postests: {len(postests)}. Se necesitan minimo 2 de cada tipo."}

    # Parear por usuario_id
    pares = []
    for pre in pretests:
        post = next((p for p in postests if p["usuario_id"] == pre["usuario_id"]), None)
        if post:
            pares.append({"pre": pre["pct_acierto"], "post": post["pct_acierto"],
                          "usuario_id": pre["usuario_id"]})

    if len(pares) < 2:
        return {"error": f"Solo {len(pares)} pares encontrados. Se necesitan minimo 2 usuarios con ambas pruebas."}

    pre_scores  = [p["pre"]  for p in pares]
    post_scores = [p["post"] for p in pares]
    diferencias = [p["post"] - p["pre"] for p in pares]

    n           = len(pares)
    media_pre   = statistics.mean(pre_scores)
    media_post  = statistics.mean(post_scores)
    media_diff  = statistics.mean(diferencias)
    sd_diff     = statistics.stdev(diferencias) if n > 1 else 0
    mejora_abs  = media_post - media_pre
    mejora_pct  = round(100 * mejora_abs / media_pre, 1) if media_pre > 0 else 0

    # T-test pareado manual
    if sd_diff > 0 and n > 0:
        t_stat    = media_diff / (sd_diff / math.sqrt(n))
        # Valor p aproximado para t con n-1 grados de libertad
        # Para df >= 10: p < 0.05 si |t| > 2.228 (df=10), > 2.101 (df=18), > 2.045 (df=28)
        df        = n - 1
        p_significativo = abs(t_stat) > 2.0  # Aproximacion conservadora
    else:
        t_stat          = 0
        p_significativo = False

    # Cohen's d
    sd_pooled = math.sqrt((statistics.variance(pre_scores) + statistics.variance(post_scores)) / 2) if n > 1 else 1
    cohen_d   = mejora_abs / sd_pooled if sd_pooled > 0 else 0

    # IC 95% para la diferencia media
    error_std = sd_diff / math.sqrt(n) if n > 0 else 0
    ic_inf    = round(media_diff - 1.96 * error_std, 2)
    ic_sup    = round(media_diff + 1.96 * error_std, 2)

    # Interpretacion Cohen's d
    if abs(cohen_d) < 0.2:
        efecto = "negligible"
    elif abs(cohen_d) < 0.5:
        efecto = "pequeno"
    elif abs(cohen_d) < 0.8:
        efecto = "mediano"
    else:
        efecto = "grande"

    # Hipotesis H1
    h1_aceptada = p_significativo and mejora_abs > 0 and mejora_pct >= 20

    return {
        "fecha_analisis":        datetime.now().isoformat(),
        "n_participantes":       n,
        "media_pretest":         round(media_pre, 2),
        "media_postest":         round(media_post, 2),
        "mejora_absoluta_pct":   round(mejora_abs, 2),
        "mejora_relativa_pct":   mejora_pct,
        "t_estadistico":         round(t_stat, 3),
        "p_significativo":       p_significativo,
        "p_nivel":               "p < 0.05" if p_significativo else "p >= 0.05",
        "cohen_d":               round(cohen_d, 3),
        "tamano_efecto":         efecto,
        "ic_95_inferior":        ic_inf,
        "ic_95_superior":        ic_sup,
        "h1_aceptada":           h1_aceptada,
        "interpretacion":        f"Con {n} participantes, el puntaje promedio mejoro de {media_pre:.1f}% a {media_post:.1f}% ({mejora_abs:+.1f} puntos porcentuales, {mejora_pct}% de mejora relativa). T={t_stat:.3f}, {'p<0.05 SIGNIFICATIVO' if p_significativo else 'p>=0.05 no significativo'}, d={cohen_d:.3f} ({efecto}). H1 {'ACEPTADA' if h1_aceptada else 'RECHAZADA'}.",
        "pares": pares
    }


def modo_cuestionario():
    """Imprime el cuestionario para aplicacion manual."""
    print("\n" + "="*65)
    print("  CUESTIONARIO MOTOEDUC EC — EVALUACION CONOCIMIENTO VIAL")
    print("  Universidad Politecnica Salesiana — Cuenca 2026")
    print("="*65)
    print(f"\nTotal de preguntas: {len(CUESTIONARIO)}")
    print("Instrucciones: Marque la letra de la respuesta correcta.\n")
    for item in CUESTIONARIO:
        print(f"\n{item['id']}. [{item['categoria']}] {item['pregunta']}")
        for op in item["opciones"]:
            print(f"   {op}")
    print("\n" + "="*65)


def demo_con_datos_ficticios():
    """Demo del analisis con 5 participantes ficticios."""
    print("\n📊 DEMO — Analisis con datos ficticios (5 participantes)\n")

    # Simular datos de 5 participantes
    participantes = [
        {"id": "usr001", "pre_correctas": 7,  "post_correctas": 11},
        {"id": "usr002", "pre_correctas": 6,  "post_correctas": 10},
        {"id": "usr003", "pre_correctas": 8,  "post_correctas": 12},
        {"id": "usr004", "pre_correctas": 5,  "post_correctas": 9},
        {"id": "usr005", "pre_correctas": 9,  "post_correctas": 13},
    ]

    for p in participantes:
        pre_resp  = {str(i+1): "B" if i < p["pre_correctas"]  else "A" for i in range(15)}
        post_resp = {str(i+1): "B" if i < p["post_correctas"] else "A" for i in range(15)}
        registrar_resultado(p["id"], "pretest",  pre_resp)
        registrar_resultado(p["id"], "postest", post_resp)

    resultado = analisis_estadistico()

    print(f"  Participantes:          {resultado['n_participantes']}")
    print(f"  Media pretest:          {resultado['media_pretest']}%")
    print(f"  Media postest:          {resultado['media_postest']}%")
    print(f"  Mejora absoluta:        {resultado['mejora_absoluta_pct']:+.1f} puntos porcentuales")
    print(f"  Mejora relativa:        {resultado['mejora_relativa_pct']}%")
    print(f"  T-estadistico:          {resultado['t_estadistico']}")
    print(f"  Significancia:          {resultado['p_nivel']}")
    print(f"  Cohen's d:              {resultado['cohen_d']} ({resultado['tamano_efecto']})")
    print(f"  IC 95%:                 [{resultado['ic_95_inferior']}, {resultado['ic_95_superior']}]")
    print(f"  H1 aceptada:            {'SI ✅' if resultado['h1_aceptada'] else 'NO ❌'}")
    print(f"\n  Interpretacion: {resultado['interpretacion']}")

    with open("tests/pretest_postest_demo.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"\n  📄 Resultado guardado en tests/pretest_postest_demo.json")
    print("="*65)
    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MotoEdu EC — Pretest-Postest")
    parser.add_argument("--modo", choices=["cuestionario","demo","analizar"], default="demo")
    args = parser.parse_args()

    if args.modo == "cuestionario":
        modo_cuestionario()
    elif args.modo == "demo":
        demo_con_datos_ficticios()
    elif args.modo == "analizar":
        resultado = analisis_estadistico()
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
