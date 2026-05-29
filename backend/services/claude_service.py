"""
Claude Service — MotoEdu EC
Wrapper para Claude API con modo mock automatico
Sprint 3 — Prompt mejorado para RAGAS >= 0.70
UPS Cuenca 2026
"""
import os
import json
import anthropic

CLAUDE_API_KEY      = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL_SONNET = "claude-sonnet-4-5"
CLAUDE_MODEL_HAIKU  = "claude-haiku-4-5-20251001"
USE_MOCK            = not CLAUDE_API_KEY.startswith("sk-ant")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if not USE_MOCK else None

print(f"[Claude Service] Modo: {'CLAUDE API REAL' if not USE_MOCK else 'MOCK'}")


# ─── M2 — Generar Leccion ────────────────────────────────────

async def generar_leccion(categoria: str, perfil: dict, nivel: str) -> dict:
    if USE_MOCK:
        return {
            "titulo": f"{categoria}",
            "introduccion": f"[MODO MOCK] Leccion sobre {categoria} para perfil {perfil.get('tipo_uso','urbano')}. Conectar Claude API para contenido real.",
            "puntos_clave": [
                f"Punto clave 1 sobre {categoria}",
                f"Punto clave 2 sobre {categoria}",
                f"Punto clave 3 sobre {categoria}"
            ],
            "ejemplo": f"Ejemplo practico de {categoria} en Ecuador.",
            "tip_seguridad": f"Tip de seguridad relacionado con {categoria}.",
            "modo": "mock"
        }

    tipo_uso = perfil.get("tipo_uso", "urbano")
    zona     = perfil.get("zona", "Sierra")
    moto     = perfil.get("moto_actual", "motocicleta")
    nombre   = perfil.get("nombre", "Motociclista")

    prompt = f"""Eres MotoEdu EC, experto en educacion vial para motociclistas ecuatorianos.

Genera una leccion educativa sobre "{categoria}" personalizada para:
- Nombre: {nombre}
- Perfil: {tipo_uso}
- Moto: {moto}
- Zona: {zona}
- Nivel: {nivel}

Responde SOLO con un JSON valido con esta estructura exacta:
{{
  "titulo": "titulo atractivo y personalizado",
  "introduccion": "2-3 parrafos introductorios con contexto ecuatoriano",
  "puntos_clave": ["punto 1 con detalle", "punto 2", "punto 3", "punto 4"],
  "ejemplo": "ejemplo practico real en Ecuador para este perfil",
  "tip_seguridad": "consejo de seguridad especifico y accionable"
}}

Menciona articulos de la LOTTTSV cuando aplique. Usa ejemplos de ciudades ecuatorianas."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        # Limpiar markdown si viene con backticks
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        return json.loads(texto.strip())
    except Exception as e:
        return {
            "titulo": categoria,
            "introduccion": f"Leccion sobre {categoria} para motociclistas {tipo_uso} en Ecuador.",
            "puntos_clave": ["Respetar velocidades maximas", "Usar equipamiento completo", "Conocer la LOTTTSV"],
            "ejemplo": f"Ejemplo para {tipo_uso} en {zona}.",
            "tip_seguridad": "Siempre usa casco certificado ECE 22.06.",
            "error": str(e)
        }


# ─── M2 — Generar Quiz ───────────────────────────────────────

async def generar_quiz(categoria: str, perfil: dict, n: int = 10) -> list:
    if USE_MOCK:
        preguntas = []
        for i in range(n):
            preguntas.append({
                "pregunta":  f"[MOCK] Pregunta {i+1} sobre {categoria}",
                "opciones":  ["A) Opcion correcta", "B) Opcion incorrecta", "C) Opcion incorrecta", "D) Opcion incorrecta"],
                "correcta":  "A",
                "explicacion": f"Explicacion de la pregunta {i+1}."
            })
        return preguntas

    tipo_uso = perfil.get("tipo_uso", "urbano")

    prompt = f"""Genera exactamente {n} preguntas de opcion multiple sobre "{categoria}" para motociclistas ecuatorianos con perfil {tipo_uso}.

Responde SOLO con un JSON array valido:
[
  {{
    "pregunta": "texto de la pregunta",
    "opciones": ["A) opcion", "B) opcion", "C) opcion", "D) opcion"],
    "correcta": "A",
    "explicacion": "por que es correcta, citando la LOTTTSV si aplica"
  }}
]

Genera exactamente {n} preguntas. Las preguntas deben ser sobre la normativa ecuatoriana LOTTTSV."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        preguntas = json.loads(texto.strip())
        return preguntas[:n]
    except Exception as e:
        return [{"pregunta": f"Error generando quiz: {e}", "opciones": ["A) Error"], "correcta": "A", "explicacion": ""}]


# ─── M3 — Asistente RAG ──────────────────────────────────────

async def asistente_rag(pregunta: str, perfil: dict, contexto_chromadb: list, historial: list) -> dict:
    if USE_MOCK:
        return {
            "respuesta": f"[MODO MOCK] Respuesta a: '{pregunta}'. Conectar Claude API para respuestas reales basadas en la LOTTTSV.",
            "fuentes":   ["LOTTTSV — Art. XXX"],
            "tokens_usados": 0,
            "modo": "mock"
        }

    tipo_uso = perfil.get("tipo_uso", "urbano")
    zona     = perfil.get("zona", "Sierra")
    anos     = perfil.get("anos_experiencia", 1)

    # Construir contexto de ChromaDB con numeracion clara
    if contexto_chromadb:
        contexto_texto = "\n\n".join([
            f"[DOCUMENTO {i+1}] Fuente: {doc.get('fuente', 'LOTTTSV')} | Categoria: {doc.get('categoria', 'General')}\n{doc.get('texto', '')}"
            for i, doc in enumerate(contexto_chromadb)
        ])
    else:
        contexto_texto = "No se encontraron documentos relevantes en la base de conocimiento."

    system_prompt = f"""Eres MotoEdu EC, asistente experto en educacion vial para motociclistas ecuatorianos.

PERFIL DEL USUARIO:
- Tipo de uso: {tipo_uso}
- Zona geografica: {zona}
- Anos de experiencia: {anos}

DOCUMENTOS RECUPERADOS DE LA BASE DE CONOCIMIENTO:
{contexto_texto}

INSTRUCCIONES CRITICAS:
1. Responde UNICAMENTE usando la informacion de los documentos anteriores
2. Cita EXPLICITAMENTE los documentos usando frases como "Segun el Documento X", "De acuerdo al Documento Y", "Como indica el Documento Z"
3. Si la informacion esta en los documentos, DEBES citarla textualmente o parafraseada con referencia
4. Menciona los articulos de la LOTTTSV cuando aparezcan en los documentos
5. Si la informacion NO esta en los documentos, di: "Esta informacion no esta disponible en mi base de conocimiento actual"
6. Personaliza la respuesta para un motociclista {tipo_uso} en {zona}
7. Sé concreto, claro y usa ejemplos del contexto ecuatoriano"""

    messages = historial[-6:] + [{"role": "user", "content": pregunta}]

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_SONNET,
            max_tokens=1000,
            messages=messages,
            system=system_prompt
        )
        return {
            "respuesta":    response.content[0].text,
            "fuentes":      list(set([d.get("fuente", "LOTTTSV") for d in contexto_chromadb])),
            "tokens_usados": response.usage.input_tokens + response.usage.output_tokens,
            "modo":         "claude_api"
        }
    except Exception as e:
        return {
            "respuesta":    f"Error en Claude API: {str(e)}",
            "fuentes":      [],
            "tokens_usados": 0,
            "modo":         "error"
        }


# ─── M4 — Recomendar Moto ────────────────────────────────────

async def recomendar_moto(perfil: dict, catalogo: list) -> dict:
    if USE_MOCK:
        top3 = catalogo[:3]
        return {
            "recomendaciones": [
                {
                    "moto":             f"{m.get('marca','')} {m.get('modelo','')}",
                    "justificacion":    f"Recomendada para perfil {perfil.get('tipo_uso','urbano')} [MOCK]",
                    "ventaja_principal": "Bajo consumo y alta durabilidad",
                    "precio_usd":        m.get("precio_usd", 0)
                }
                for m in top3
            ],
            "razonamiento_general": "[MODO MOCK] Conectar Claude API para recomendaciones personalizadas.",
            "modo": "mock"
        }

    tipo_uso   = perfil.get("tipo_uso", "urbano")
    zona       = perfil.get("zona", "Sierra")
    anos       = perfil.get("anos_experiencia", 1)
    presupuesto = perfil.get("presupuesto_max", 5000)

    catalogo_texto = "\n".join([
        f"- {m.get('marca')} {m.get('modelo')} ({m.get('anio')}): {m.get('cilindrada_cc')}cc, {m.get('potencia_hp')}HP, ${m.get('precio_usd')}, {m.get('uso_recomendado')}"
        for m in catalogo[:15]
    ])

    prompt = f"""Eres un experto en motocicletas del mercado ecuatoriano.

PERFIL DEL USUARIO:
- Tipo de uso: {tipo_uso}
- Zona: {zona}
- Anos de experiencia: {anos}
- Presupuesto maximo: ${presupuesto} USD

CATALOGO DISPONIBLE EN ECUADOR:
{catalogo_texto}

Recomienda las 3 mejores motos del catalogo para este perfil.
Responde SOLO con JSON valido:
{{
  "recomendaciones": [
    {{
      "moto": "Marca Modelo",
      "justificacion": "explicacion detallada de 2-3 oraciones mencionando zona, experiencia y uso",
      "ventaja_principal": "ventaja clave en una frase",
      "precio_usd": 0000
    }}
  ],
  "razonamiento_general": "explicacion general de por que estas 3 motos son las mejores para este perfil"
}}"""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        data = json.loads(texto.strip())
        data["modo"] = "claude_api"
        return data
    except Exception as e:
        top3 = catalogo[:3]
        return {
            "recomendaciones": [
                {
                    "moto":             f"{m.get('marca','')} {m.get('modelo','')}",
                    "justificacion":    f"Recomendada para perfil {tipo_uso} en {zona}.",
                    "ventaja_principal": "Disponible en Ecuador",
                    "precio_usd":        m.get("precio_usd", 0)
                }
                for m in top3
            ],
            "razonamiento_general": f"Error: {str(e)}",
            "modo": "error"
        }


# ─── M6 — Historia ───────────────────────────────────────────

async def generar_historia(tema: str) -> dict:
    if USE_MOCK:
        return {
            "titulo":     tema,
            "narrativa":  f"[MODO MOCK] Narrativa sobre: {tema}. Conectar Claude API para narrativas reales.",
            "datos_clave": ["Dato 1", "Dato 2", "Dato 3"],
            "modo":       "mock"
        }

    prompt = f"""Eres un historiador especializado en el motociclismo ecuatoriano.

Escribe una narrativa historica sobre: "{tema}"

Responde SOLO con JSON valido:
{{
  "titulo": "titulo atractivo del tema",
  "narrativa": "narrativa de 3-4 parrafos con hechos verificados sobre Ecuador",
  "datos_clave": ["dato estadistico 1", "dato historico 2", "hecho relevante 3"]
}}

Usa datos reales de Ecuador: AEADE, ANT, Federacion Ecuatoriana de Motociclismo."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        data = json.loads(texto.strip())
        data["modo"] = "claude_api"
        return data
    except Exception as e:
        return {
            "titulo":     tema,
            "narrativa":  f"El motociclismo en Ecuador tiene una rica historia desde principios del siglo XX.",
            "datos_clave": ["274.729 motos vendidas en 2025", "685 fallecidos en 2024", "Record historico de ventas"],
            "modo":       "error",
            "error":      str(e)
        }