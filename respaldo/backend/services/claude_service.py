"""
Claude Service — MotoEdu EC
Wrapper para Claude API con modo mock automatico
Sprint 3 — Prompt mejorado para RAGAS >= 0.70
Parser JSON robusto para evitar errores de truncamiento
UPS Cuenca 2026
"""
import os
import json
import re
import anthropic

CLAUDE_API_KEY      = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_MODEL_SONNET = "claude-sonnet-4-5"
CLAUDE_MODEL_HAIKU  = "claude-haiku-4-5-20251001"
USE_MOCK            = not CLAUDE_API_KEY.startswith("sk-ant")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if not USE_MOCK else None

print(f"[Claude Service] Modo: {'CLAUDE API REAL' if not USE_MOCK else 'MOCK'}")


def limpiar_json(texto: str) -> str:
    """Limpia el texto de Claude para obtener JSON valido."""
    texto = texto.strip()
    # Remover markdown backticks
    if "```" in texto:
        partes = texto.split("```")
        for parte in partes:
            parte = parte.strip()
            if parte.startswith("json"):
                parte = parte[4:].strip()
            if parte.startswith("{") or parte.startswith("["):
                texto = parte
                break
    # Extraer el JSON entre { } o [ ]
    if texto.startswith("{"):
        # Encontrar el ultimo } que cierra el JSON
        nivel = 0
        pos_fin = -1
        for i, c in enumerate(texto):
            if c == "{":
                nivel += 1
            elif c == "}":
                nivel -= 1
                if nivel == 0:
                    pos_fin = i
                    break
        if pos_fin > 0:
            texto = texto[:pos_fin+1]
    elif texto.startswith("["):
        nivel = 0
        pos_fin = -1
        for i, c in enumerate(texto):
            if c == "[":
                nivel += 1
            elif c == "]":
                nivel -= 1
                if nivel == 0:
                    pos_fin = i
                    break
        if pos_fin > 0:
            texto = texto[:pos_fin+1]
    return texto.strip()


def parsear_json_seguro(texto: str) -> dict:
    """Intenta parsear JSON con multiples estrategias."""
    # Estrategia 1: directo
    try:
        return json.loads(texto)
    except:
        pass
    # Estrategia 2: limpiar y reintentar
    try:
        return json.loads(limpiar_json(texto))
    except:
        pass
    # Estrategia 3: extraer campos manualmente con regex
    resultado = {}
    for campo in ["titulo", "introduccion", "ejemplo", "tip_seguridad", "narrativa"]:
        match = re.search(rf'"{campo}"\s*:\s*"(.*?)"(?=\s*[,}}])', texto, re.DOTALL)
        if match:
            resultado[campo] = match.group(1).replace('\\"', '"').strip()
    # Extraer puntos_clave
    match_pk = re.search(r'"puntos_clave"\s*:\s*\[(.*?)\]', texto, re.DOTALL)
    if match_pk:
        puntos = re.findall(r'"(.*?)"', match_pk.group(1))
        if puntos:
            resultado["puntos_clave"] = puntos
    return resultado if resultado else None


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

Genera una leccion sobre "{categoria}" para:
- Nombre: {nombre}, Perfil: {tipo_uso}, Moto: {moto}, Zona: {zona}, Nivel: {nivel}

IMPORTANTE: Responde SOLO con JSON valido y CONCISO. Sin caracteres especiales dentro de strings.

{{
  "titulo": "titulo corto personalizado sin comillas internas",
  "introduccion": "un parrafo introductorio sin comillas internas",
  "puntos_clave": ["punto 1 concreto con articulo LOTTTSV", "punto 2", "punto 3"],
  "ejemplo": "ejemplo practico breve en Ecuador para este perfil",
  "tip_seguridad": "consejo de seguridad especifico y breve"
}}

USA SOLO comillas dobles. NO uses apostrofes ni comillas simples dentro del JSON."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        data = parsear_json_seguro(texto)
        if data and "titulo" in data:
            return data
        raise ValueError("JSON invalido")
    except Exception as e:
        return {
            "titulo": categoria,
            "introduccion": f"Leccion sobre {categoria} para motociclistas {tipo_uso} en {zona}.",
            "puntos_clave": ["Respetar velocidades maximas LOTTTSV", "Usar equipamiento certificado ECE 22.06", "Conocer sanciones vigentes"],
            "ejemplo": f"Motociclista {tipo_uso} en {zona} aplicando la LOTTTSV correctamente.",
            "tip_seguridad": "Siempre usa casco certificado ECE 22.06 y chaleco reflectivo.",
            "error": str(e)
        }


# ─── M2 — Generar Quiz ───────────────────────────────────────

async def generar_quiz(categoria: str, perfil: dict, n: int = 10) -> list:
    if USE_MOCK:
        preguntas = []
        for i in range(n):
            preguntas.append({
                "pregunta":    f"[MOCK] Pregunta {i+1} sobre {categoria}",
                "opciones":    ["A) Opcion correcta", "B) Opcion incorrecta", "C) Opcion incorrecta", "D) Opcion incorrecta"],
                "correcta":    "A",
                "explicacion": f"Explicacion de la pregunta {i+1}."
            })
        return preguntas

    tipo_uso = perfil.get("tipo_uso", "urbano")

    prompt = f"""Genera {n} preguntas de opcion multiple sobre "{categoria}" para motociclistas {tipo_uso} en Ecuador.

Responde SOLO con JSON array. Sin caracteres especiales en los strings:
[
  {{
    "pregunta": "texto de la pregunta sin comillas internas",
    "opciones": ["A) opcion", "B) opcion", "C) opcion", "D) opcion"],
    "correcta": "A",
    "explicacion": "explicacion breve citando LOTTTSV si aplica"
  }}
]

USA SOLO comillas dobles. Genera exactamente {n} preguntas."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        texto_limpio = limpiar_json(texto)
        preguntas = json.loads(texto_limpio)
        return preguntas[:n]
    except Exception as e:
        return [{"pregunta": f"Cual es la velocidad maxima en zona urbana en Ecuador?",
                 "opciones": ["A) 50 km/h", "B) 60 km/h", "C) 80 km/h", "D) 40 km/h"],
                 "correcta": "A", "explicacion": "Art. 127 LOTTTSV: 50 km/h en zona urbana."}]


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
7. Se concreto, claro y usa ejemplos del contexto ecuatoriano"""

    messages = historial[-6:] + [{"role": "user", "content": pregunta}]

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_SONNET,
            max_tokens=1000,
            messages=messages,
            system=system_prompt
        )
        return {
            "respuesta":     response.content[0].text,
            "fuentes":       list(set([d.get("fuente", "LOTTTSV") for d in contexto_chromadb])),
            "tokens_usados": response.usage.input_tokens + response.usage.output_tokens,
            "modo":          "claude_api"
        }
    except Exception as e:
        return {
            "respuesta":     f"Error en Claude API: {str(e)}",
            "fuentes":       [],
            "tokens_usados": 0,
            "modo":          "error"
        }


# ─── M4 — Recomendar Moto ────────────────────────────────────

async def recomendar_moto(perfil: dict, catalogo: list) -> dict:
    if USE_MOCK:
        top3 = catalogo[:3]
        return {
            "recomendaciones": [
                {
                    "moto":              f"{m.get('marca','')} {m.get('modelo','')}",
                    "justificacion":     f"Recomendada para perfil {perfil.get('tipo_uso','urbano')} [MOCK]",
                    "ventaja_principal": "Bajo consumo y alta durabilidad",
                    "precio_usd":        m.get("precio_usd", 0)
                }
                for m in top3
            ],
            "razonamiento_general": "[MODO MOCK] Conectar Claude API para recomendaciones personalizadas.",
            "modo": "mock"
        }

    tipo_uso    = perfil.get("tipo_uso", "urbano")
    zona        = perfil.get("zona", "Sierra")
    anos        = perfil.get("anos_experiencia", 1)
    presupuesto = perfil.get("presupuesto_max", 5000)

    catalogo_texto = "\n".join([
        f"- {m.get('marca')} {m.get('modelo')} ({m.get('anio')}): {m.get('cilindrada_cc')}cc, {m.get('potencia_hp')}HP, ${m.get('precio_usd')}, {m.get('uso_recomendado')}"
        for m in catalogo[:15]
    ])

    prompt = f"""Experto en motos Ecuador. Recomienda 3 motos para:
- Uso: {tipo_uso}, Zona: {zona}, Experiencia: {anos} anos, Presupuesto: ${presupuesto}

CATALOGO:
{catalogo_texto}

JSON valido sin caracteres especiales:
{{
  "recomendaciones": [
    {{
      "moto": "Marca Modelo",
      "justificacion": "razon en 2 oraciones mencionando zona y uso sin comillas internas",
      "ventaja_principal": "ventaja clave breve",
      "precio_usd": 0000
    }}
  ],
  "razonamiento_general": "resumen breve sin comillas internas"
}}"""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        data = parsear_json_seguro(texto)
        if data and "recomendaciones" in data:
            data["modo"] = "claude_api"
            return data
        raise ValueError("JSON invalido")
    except Exception as e:
        top3 = catalogo[:3]
        return {
            "recomendaciones": [
                {
                    "moto":              f"{m.get('marca','')} {m.get('modelo','')}",
                    "justificacion":     f"Recomendada para perfil {tipo_uso} en {zona}.",
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

    prompt = f"""Historiador del motociclismo ecuatoriano. Escribe sobre: "{tema}"

JSON valido y conciso sin comillas internas en los valores:
{{
  "titulo": "titulo del tema sin comillas internas",
  "narrativa": "narrativa breve de 2 parrafos con datos reales de Ecuador sin comillas internas",
  "datos_clave": ["dato 1 con cifra", "dato 2 historico", "dato 3 relevante"]
}}

Usa datos: AEADE 274729 motos 2025, ANT 685 fallecidos 2024, Federacion Ecuatoriana de Motociclismo."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL_HAIKU,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()
        data = parsear_json_seguro(texto)
        if data and "titulo" in data:
            data["modo"] = "claude_api"
            return data
        raise ValueError("JSON invalido")
    except Exception as e:
        return {
            "titulo":     tema,
            "narrativa":  "El motociclismo en Ecuador tiene una rica historia desde principios del siglo XX. En 2025 se alcanzó el record histórico de 274.729 motos vendidas según la AEADE.",
            "datos_clave": ["274.729 motos vendidas en 2025 (AEADE)", "685 fallecidos en 2024 (ANT)", "Record historico de ventas en Ecuador"],
            "modo":       "error",
            "error":      str(e)
        }