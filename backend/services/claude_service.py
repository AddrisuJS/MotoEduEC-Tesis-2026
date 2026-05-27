"""
Servicio Claude API — MotoEdu EC Tesis
Wrapper central para todas las llamadas a Claude API.
Cuando CLAUDE_API_KEY esté disponible, reemplaza las respuestas mock.
"""
import os
from typing import Optional

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL_SONNET = "claude-sonnet-4-20250514"
CLAUDE_MODEL_HAIKU  = "claude-haiku-4-5-20251001"
USE_MOCK = not CLAUDE_API_KEY or CLAUDE_API_KEY.startswith("sk-ant-XXX")


async def generar_leccion(
    categoria: str,
    perfil: dict,
    nivel: str = "basico"
) -> dict:
    """
    M2 — Genera una lección educativa personalizada.
    Cuando Claude API esté disponible, reemplaza el mock.
    """
    if USE_MOCK:
        return _mock_leccion(categoria, perfil, nivel)

    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    system_prompt = _system_prompt_base() + _perfil_prompt(perfil)
    task_prompt = f"""
    Genera una lección educativa sobre "{categoria}" para un motociclista con perfil:
    - Tipo de uso: {perfil.get('tipo_uso', 'urbano')}
    - Experiencia: {perfil.get('anos_experiencia', 1)} años
    - Nivel objetivo: {nivel}
    
    La lección debe tener:
    1. Título atractivo
    2. Introducción de 2 párrafos
    3. 3 puntos clave numerados
    4. Ejemplo práctico ecuatoriano
    5. Tip de seguridad final
    
    Responde en JSON con campos: titulo, introduccion, puntos_clave, ejemplo, tip_seguridad
    """

    response = client.messages.create(
        model=CLAUDE_MODEL_HAIKU,
        max_tokens=1000,
        messages=[{"role": "user", "content": task_prompt}],
        system=system_prompt
    )
    import json
    text = response.content[0].text
    try:
        return json.loads(text)
    except:
        return {"titulo": categoria, "contenido": text, "tipo": "generado"}


async def generar_quiz(categoria: str, perfil: dict, n: int = 10) -> list:
    """M2 — Genera quiz de N preguntas personalizado."""
    if USE_MOCK:
        return _mock_quiz(categoria, n)

    import anthropic, json
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    system_prompt = _system_prompt_base() + _perfil_prompt(perfil)
    task_prompt = f"""
    Genera {n} preguntas de opción múltiple sobre "{categoria}" para el reglamento LOTTTSV ecuatoriano.
    Perfil del motociclista: {perfil.get('tipo_uso', 'urbano')}, {perfil.get('anos_experiencia', 1)} años de experiencia.
    
    Responde en JSON array con objetos:
    {{
        "pregunta": "...",
        "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
        "correcta": "A",
        "explicacion": "..."
    }}
    Solo JSON, sin texto adicional.
    """
    response = client.messages.create(
        model=CLAUDE_MODEL_HAIKU,
        max_tokens=2000,
        messages=[{"role": "user", "content": task_prompt}],
        system=system_prompt
    )
    try:
        return json.loads(response.content[0].text)
    except:
        return _mock_quiz(categoria, n)


async def asistente_rag(
    pregunta: str,
    perfil: dict,
    contexto_chromadb: list,
    historial: list
) -> dict:
    """
    M3 — Asistente RAG con ChromaDB + Claude API.
    contexto_chromadb: documentos recuperados de ChromaDB.
    """
    if USE_MOCK:
        return _mock_rag(pregunta, contexto_chromadb)

    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    contexto_str = "\n\n".join([
        f"[Fuente: {d.get('fuente','LOTTTSV')}]\n{d.get('texto','')}"
        for d in contexto_chromadb
    ])

    system_prompt = _system_prompt_base() + _perfil_prompt(perfil) + f"""
    
    CONTEXTO DE LA BASE DE CONOCIMIENTO (LOTTTSV y catálogo):
    {contexto_str}
    
    INSTRUCCIÓN: Responde usando únicamente la información del contexto anterior.
    Cita el artículo o fuente específica al final de tu respuesta.
    Si la información no está en el contexto, indícalo claramente.
    """

    messages = historial[-6:] + [{"role": "user", "content": pregunta}]

    response = client.messages.create(
        model=CLAUDE_MODEL_SONNET,
        max_tokens=1000,
        messages=messages,
        system=system_prompt
    )

    return {
        "respuesta": response.content[0].text,
        "fuentes": [d.get("fuente", "LOTTTSV") for d in contexto_chromadb],
        "tokens_usados": response.usage.input_tokens + response.usage.output_tokens
    }


async def recomendar_moto(perfil: dict, catalogo: list) -> dict:
    """M4 — Recomienda motos con justificación en lenguaje natural."""
    if USE_MOCK:
        return _mock_recomendacion_moto(perfil, catalogo)

    import anthropic, json
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    catalogo_str = "\n".join([
        f"- {m['marca']} {m['modelo']} ({m['anio']}): {m['cilindrada_cc']}cc, ${m['precio_usd']}, {m['uso_recomendado']}"
        for m in catalogo[:20]
    ])

    task_prompt = f"""
    Analiza el perfil del motociclista y recomienda exactamente 3 motos del catálogo.
    
    PERFIL:
    - Tipo de uso: {perfil.get('tipo_uso')}
    - Años de experiencia: {perfil.get('anos_experiencia')}
    - Presupuesto máximo: ${perfil.get('presupuesto_max', 5000)}
    - Zona geográfica: {perfil.get('zona', 'Sierra')}
    
    CATÁLOGO DISPONIBLE:
    {catalogo_str}
    
    Responde en JSON:
    {{
        "recomendaciones": [
            {{"moto": "Marca Modelo", "justificacion": "...", "ventaja_principal": "...", "precio_usd": 0}},
            ...
        ],
        "razonamiento_general": "..."
    }}
    """

    response = client.messages.create(
        model=CLAUDE_MODEL_HAIKU,
        max_tokens=1000,
        messages=[{"role": "user", "content": task_prompt}],
        system=_system_prompt_base()
    )
    try:
        return json.loads(response.content[0].text)
    except:
        return _mock_recomendacion_moto(perfil, catalogo)


async def generar_historia(tema: str) -> dict:
    """M6 — Genera narrativa cultural del motociclismo ecuatoriano."""
    if USE_MOCK:
        return _mock_historia(tema)

    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    task_prompt = f"""
    Genera una narrativa cultural sobre "{tema}" en la historia del motociclismo ecuatoriano.
    Incluye datos reales: AEADE, ANT, Federación Ecuatoriana de Motociclismo.
    
    Responde en JSON:
    {{
        "titulo": "...",
        "narrativa": "3 párrafos de narrativa cultural",
        "datos_clave": ["dato 1", "dato 2", "dato 3"],
        "epoca": "..."
    }}
    """
    response = client.messages.create(
        model=CLAUDE_MODEL_HAIKU,
        max_tokens=800,
        messages=[{"role": "user", "content": task_prompt}],
        system=_system_prompt_base()
    )
    import json
    try:
        return json.loads(response.content[0].text)
    except:
        return _mock_historia(tema)


# ─── System Prompts ───────────────────────────────────────────

def _system_prompt_base() -> str:
    return """Eres MotoEdu EC, el asistente experto en educación vial para motociclistas ecuatorianos.
Tu misión es educar, informar y orientar a los motociclistas del Ecuador para reducir la siniestralidad vial.

RESTRICCIONES:
- Solo hablas sobre temas de motociclismo, seguridad vial, LOTTTSV y cultura motera ecuatoriana.
- Nunca inventes información. Si no sabes, dilo claramente.
- Siempre cita la fuente (artículo del reglamento, estadística, etc.).
- Usa lenguaje claro y accesible, sin tecnicismos innecesarios.
- Respeta el contexto ecuatoriano (leyes, marcas disponibles, geografía).
"""


def _perfil_prompt(perfil: dict) -> str:
    if not perfil:
        return ""
    return f"""
PERFIL DEL MOTOCICLISTA:
- Nombre: {perfil.get('nombre', 'Motociclista')}
- Tipo de uso: {perfil.get('tipo_uso', 'urbano')}
- Años de experiencia: {perfil.get('anos_experiencia', 1)}
- Moto actual: {perfil.get('moto_actual', 'No especificada')}
- Zona geográfica: {perfil.get('zona', 'Sierra')}
- Nivel de conocimiento: {perfil.get('nivel', 'basico')}

Adapta SIEMPRE el contenido a este perfil específico.
"""


# ─── Respuestas Mock (sin Claude API) ────────────────────────

def _mock_leccion(categoria: str, perfil: dict, nivel: str) -> dict:
    return {
        "titulo": f"Lección: {categoria}",
        "introduccion": f"Esta lección sobre {categoria} está diseñada para motociclistas con perfil {perfil.get('tipo_uso', 'urbano')}. [MODO MOCK — conectar Claude API para contenido personalizado]",
        "puntos_clave": [
            f"Punto 1 sobre {categoria} según la LOTTTSV",
            f"Punto 2 — aplicación práctica en Ecuador",
            f"Punto 3 — estadísticas de la ANT Ecuador"
        ],
        "ejemplo": f"Ejemplo práctico de {categoria} en Cuenca, Ecuador.",
        "tip_seguridad": "Recuerda siempre usar casco certificado ECE 22.06.",
        "modo": "mock — integrar Claude API"
    }


def _mock_quiz(categoria: str, n: int) -> list:
    return [
        {
            "pregunta": f"Pregunta {i+1} sobre {categoria} (MOCK)",
            "opciones": ["A) Opción A", "B) Opción B", "C) Opción C", "D) Opción D"],
            "correcta": "A",
            "explicacion": "Explicación de la respuesta correcta. [Conectar Claude API para quizzes reales]"
        }
        for i in range(n)
    ]


def _mock_rag(pregunta: str, contexto: list) -> dict:
    return {
        "respuesta": f"[MODO MOCK] Respuesta a: '{pregunta}'. Conectar Claude API para respuestas reales basadas en la LOTTTSV.",
        "fuentes": ["LOTTTSV — Art. XXX"],
        "tokens_usados": 0,
        "modo": "mock"
    }


def _mock_recomendacion_moto(perfil: dict, catalogo: list) -> dict:
    motos = catalogo[:3] if catalogo else []
    return {
        "recomendaciones": [
            {
                "moto": f"{m.get('marca','')} {m.get('modelo','')}",
                "justificacion": f"Recomendada para perfil {perfil.get('tipo_uso','urbano')} [MOCK]",
                "ventaja_principal": "Bajo consumo y alta durabilidad",
                "precio_usd": m.get('precio_usd', 0)
            }
            for m in motos
        ],
        "razonamiento_general": "[MODO MOCK] Conectar Claude API para recomendaciones personalizadas.",
        "modo": "mock"
    }


def _mock_historia(tema: str) -> dict:
    return {
        "titulo": f"Historia: {tema}",
        "narrativa": f"[MODO MOCK] Narrativa cultural sobre {tema} en el motociclismo ecuatoriano. Conectar Claude API para contenido generado por IA.",
        "datos_clave": ["274.729 motos vendidas en 2025", "28.4% del parque vehicular", "685 fallecidos en 2024"],
        "epoca": "2020-2026",
        "modo": "mock"
    }
