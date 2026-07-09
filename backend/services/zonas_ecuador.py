"""
Contexto geográfico para personalización de prompts — MotoEdu EC
Genera un bloque de contexto local (vías, clima, riesgos conocidos) según
la ciudad/provincia del usuario, para que Claude use ejemplos familiares.

Uso:
    from services.zonas_ecuador import contexto_geografico
    bloque = contexto_geografico(ciudad="Cuenca", provincia="Azuay")
    # → inyectar `bloque` en el system prompt de M2 (lecciones) y M3 (asistente)

UPS Cuenca 2026
"""

ZONAS = {
    # ─── SIERRA SUR ──────────────────────────────────────────────
    "azuay": {
        "region": "Sierra sur",
        "ciudades": "Cuenca, Gualaceo, Paute, Chordeleg, Girón, Sígsig",
        "contexto": (
            "Vías urbanas de referencia en Cuenca: Av. de las Américas (Circunvalación), "
            "Av. Solano, Av. 12 de Abril junto al río Tomebamba, Av. Ordóñez Lasso, "
            "Av. González Suárez y el Control Sur. "
            "Carreteras conocidas: vía Cuenca–Molleturo–Naranjal por el Parque Nacional El Cajas "
            "(neblina densa, lluvia y temperaturas bajo 5°C a más de 4.000 msnm — riesgo alto para motociclistas), "
            "vía rápida Cuenca–Azogues–Biblián (autopista con vientos cruzados), "
            "vía Cuenca–Gualaceo–Chordeleg (curvas de montaña muy transitadas los fines de semana), "
            "vía a Girón y la ruta al valle de Yunguilla (descenso pronunciado con cambio brusco de clima frío a cálido), "
            "y la vía al Sígsig. "
            "Riesgos locales típicos: neblina matinal en Turi y el Cajas, lluvia vespertina casi diaria, "
            "adoquín y piedra resbalosa en el Centro Histórico de Cuenca, y el rocío que deja las vías "
            "mojadas en las madrugadas de la Sierra."
        ),
    },
    "pichincha": {
        "region": "Sierra norte",
        "ciudades": "Quito, Machachi (Mejía), Cayambe, Sangolquí",
        "contexto": (
            "Vías urbanas de referencia en Quito: Av. Simón Bolívar (curvas, pendientes y alto flujo de "
            "carga pesada — una de las vías más peligrosas para motos), Av. Occidental (Mariscal Sucre), "
            "Ruta Viva hacia los valles, Av. General Rumiñahui hacia Sangolquí y la Panamericana Norte y Sur. "
            "Para el cantón Mejía/Machachi: la Panamericana Sur y el ingreso a la vía Alóag–Santo Domingo "
            "(neblina espesa, lluvia y tráfico pesado de tráilers — extremar precaución). "
            "Riesgos locales típicos: lluvia y granizo por las tardes, pendientes pronunciadas con pavimento "
            "mojado, altitud sobre 2.800 msnm que reduce potencia del motor, y neblina en los pasos altos "
            "como el sector de Jambelí y el páramo de Mejía."
        ),
    },
    # ─── COSTA ───────────────────────────────────────────────────
    "guayas": {
        "region": "Costa",
        "ciudades": "Guayaquil, Milagro, Durán, Daule, Samborondón",
        "contexto": (
            "Vías urbanas de referencia en Guayaquil: Av. Francisco de Orellana, Vía a la Costa, "
            "Av. Perimetral, Vía a Daule, y los puentes de la Unidad Nacional hacia Durán y Samborondón. "
            "Para Milagro: la vía Durán–Yaguachi–Milagro y la vía Milagro–Naranjito (rectas largas donde "
            "el exceso de velocidad es la principal causa de siniestros, y cruce frecuente de cañeros y "
            "vehículos agrícolas en época de zafra). "
            "Riesgos locales típicos: lluvias torrenciales de diciembre a mayo (estación invernal) con "
            "calles anegadas y aquaplaning, calor sobre 32°C que fatiga y deshidrata al conductor, "
            "asfalto que 'suda' aceite con las primeras lluvias, y alto flujo de motos de delivery."
        ),
    },
    "el_oro": {
        "region": "Costa sur / frontera",
        "ciudades": "Machala, Huaquillas, Pasaje, Santa Rosa",
        "contexto": (
            "Vías de referencia: la Panamericana en el tramo Machala–Huaquillas (recta, calurosa y de alto "
            "tráfico comercial hacia la frontera con Perú), la vía Machala–Pasaje y la ruta Pasaje–Girón–Cuenca "
            "(ascenso de la Costa a la Sierra con cambio drástico de clima: de calor a neblina y frío en pocos km). "
            "Riesgos locales típicos en Huaquillas y la zona fronteriza: tráfico intenso de comercio, "
            "triciclos y motos de carga, lluvias intensas en invierno, calor extremo que exige hidratación, "
            "y polvo en vías secundarias de las camaroneras y bananeras."
        ),
    },
    "los_rios": {
        "region": "Costa interior",
        "ciudades": "Babahoyo, Quevedo, Ventanas, Vinces",
        "contexto": (
            "Vías de referencia: la troncal Babahoyo–Quevedo (recta con alto flujo de carga agrícola), "
            "la vía Babahoyo–Guayaquil y la Quevedo–Santo Domingo. "
            "Riesgos locales típicos: es una de las provincias más lluviosas del país — inundaciones y "
            "calles anegadas en invierno, aquaplaning frecuente, cruce de maquinaria agrícola y "
            "animales en la vía, y neblina baja al amanecer sobre los ríos."
        ),
    },
    # ─── GENÉRICOS DE RESPALDO ───────────────────────────────────
    "sierra": {
        "region": "Sierra",
        "ciudades": "Cuenca, Loja, Ambato, Riobamba, Ibarra",
        "contexto": (
            "Contexto general de Sierra: curvas de montaña, neblina en pasos altos, lluvia vespertina, "
            "pavimento frío y húmedo en las mañanas, altitud que reduce la potencia del motor, y "
            "descensos largos donde se recalientan los frenos."
        ),
    },
    "costa": {
        "region": "Costa",
        "ciudades": "Guayaquil, Machala, Manta, Portoviejo",
        "contexto": (
            "Contexto general de Costa: calor y humedad que fatigan al conductor, lluvias torrenciales en "
            "invierno (diciembre–mayo) con riesgo de aquaplaning, rectas largas que invitan al exceso de "
            "velocidad, y alto volumen de motos de trabajo y delivery."
        ),
    },
    "amazonia": {
        "region": "Amazonía",
        "ciudades": "Tena, Puyo, Macas, Nueva Loja",
        "contexto": (
            "Contexto general de Amazonía: lluvia intensa casi todo el año, derrumbes y deslaves en las "
            "vías de acceso, vegetación que reduce visibilidad, puentes angostos y pavimento "
            "permanentemente húmedo."
        ),
    },
}

# Alias ciudad → clave de provincia/región
CIUDAD_A_ZONA = {
    "cuenca": "azuay", "gualaceo": "azuay", "paute": "azuay", "chordeleg": "azuay",
    "giron": "azuay", "sigsig": "azuay", "azuay": "azuay",
    "quito": "pichincha", "distrito metropolitano de quito": "pichincha",
    "mejia": "pichincha", "machachi": "pichincha", "sangolqui": "pichincha", "pichincha": "pichincha",
    "guayaquil": "guayas", "milagro": "guayas", "duran": "guayas", "daule": "guayas",
    "samborondon": "guayas", "guayas": "guayas",
    "machala": "el_oro", "huaquillas": "el_oro", "pasaje": "el_oro", "santa rosa": "el_oro",
    "el oro": "el_oro",
    "babahoyo": "los_rios", "quevedo": "los_rios", "ventanas": "los_rios", "vinces": "los_rios",
    "los rios": "los_rios",
}


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    t = texto.strip().lower()
    for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
        t = t.replace(a, b)
    return t


def contexto_geografico(ciudad: str = "", provincia: str = "", zona: str = "") -> str:
    """
    Devuelve un bloque de texto para inyectar en el system prompt.
    Prioridad: ciudad > provincia > zona (Sierra/Costa/Amazonía) > Sierra por defecto.
    """
    clave = (
        CIUDAD_A_ZONA.get(_normalizar(ciudad))
        or CIUDAD_A_ZONA.get(_normalizar(provincia))
        or _normalizar(zona) if _normalizar(zona) in ZONAS else None
    )
    z = ZONAS.get(clave) or ZONAS.get(_normalizar(zona)) or ZONAS["sierra"]

    lugar = ciudad.strip().title() if ciudad and ciudad.strip() else z["ciudades"].split(",")[0]

    return (
        f"\n\nCONTEXTO GEOGRÁFICO DEL USUARIO — región {z['region']}, ubicación: {lugar}.\n"
        f"{z['contexto']}\n"
        f"INSTRUCCIÓN: Usa ejemplos de estas vías, clima y riesgos LOCALES para que el usuario se sienta "
        f"identificado. NO uses Quito como ejemplo por defecto salvo que el usuario esté en Quito. "
        f"Menciona lugares de su zona de forma natural cuando sea relevante para la lección o respuesta."
    )
