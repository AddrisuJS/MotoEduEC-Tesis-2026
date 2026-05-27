"""
M1 — Perfil Inteligente del Motociclista
Sprint 2 — Onboarding completo con 5 preguntas de clasificacion
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
import uuid

router = APIRouter()

# ─── Configuracion de perfiles ────────────────────────────────
PERFILES = {
    "delivery": {
        "nombre": "Delivery",
        "descripcion": "Motociclista de trabajo intensivo. Alta exposicion al riesgo por largas jornadas.",
        "uso_principal": "Delivery de comida, mensajeria y paqueteria",
        "motos_tipicas": ["Honda CB100", "Bajaj Boxer 150", "Shineray XY150GY", "Daytona VX 125"],
        "riesgos_principales": "Fatiga, exceso de velocidad, semaforos, sin equipamiento completo",
        "velocidad_tipica_kmh": 60,
        "nivel_riesgo": "ALTO",
        "recomendacion_casco": "Casco integral certificado ECE 22.06",
        "equipamiento_minimo": ["Casco integral", "Chaleco reflectivo OBLIGATORIO", "Botas de trabajo cerradas", "Guantes urbanos"]
    },
    "urbano": {
        "nombre": "Urbano Diario",
        "descripcion": "Adulto que usa la moto para transporte diario al trabajo en ciudad.",
        "uso_principal": "Transporte diario, comisiones, trabajo",
        "motos_tipicas": ["Honda CB1 Star", "Yamaha YBR125", "Bajaj NS160", "Yamaha FZ150"],
        "riesgos_principales": "Trafico intenso, semaforos, piso mojado, visibilidad en cruces",
        "velocidad_tipica_kmh": 50,
        "nivel_riesgo": "MEDIO",
        "recomendacion_casco": "Casco integral o modular ECE 22.06",
        "equipamiento_minimo": ["Casco integral", "Chaleco reflectivo", "Chaqueta 3 en 1", "Guantes touring"]
    },
    "touring": {
        "nombre": "Touring",
        "descripcion": "Motociclista experimentado que realiza viajes largos de fin de semana.",
        "uso_principal": "Viajes largos, carretera, rutas turisticas",
        "motos_tipicas": ["Yamaha Tenere 700", "KTM 390 Adventure", "Royal Enfield Himalayan 450", "Kawasaki Versys-X 300"],
        "riesgos_principales": "Alta velocidad sostenida, fatiga, climatologia variable, adelantamientos",
        "velocidad_tipica_kmh": 100,
        "nivel_riesgo": "MEDIO",
        "recomendacion_casco": "Casco modular premium o adventure ECE 22.06",
        "equipamiento_minimo": ["Casco modular/adventure", "Chaqueta 3 en 1 impermeable", "Guantes touring reforzados", "Botas touring", "Espaldera nivel 2"]
    },
    "aventura": {
        "nombre": "Aventura Off-road",
        "descripcion": "Motociclista que disfruta rutas mixtas de asfalto y caminos no asfaltados.",
        "uso_principal": "Off-road, rutas de tierra, aventura en campo",
        "motos_tipicas": ["KTM EXC 300", "Yamaha XTZ250", "Honda CRF300L", "Daytona Sprinter 200"],
        "riesgos_principales": "Terreno irregular, caidas, alejamiento de centros medicos, barro",
        "velocidad_tipica_kmh": 80,
        "nivel_riesgo": "MEDIO",
        "recomendacion_casco": "Casco adventure dual sport o enduro",
        "equipamiento_minimo": ["Casco adventure/enduro", "Chaqueta off-road con pechera", "Guantes off-road", "Botas enduro", "Rodilleras articuladas"]
    },
    "enduro": {
        "nombre": "Enduro",
        "descripcion": "Motociclista especializado en competicion o deporte intenso en terreno irregular.",
        "uso_principal": "Enduro, competicion off-road, pista de tierra",
        "motos_tipicas": ["KTM EXC 300", "Honda CRF450R", "Yamaha YZ", "Kawasaki KX"],
        "riesgos_principales": "Velocidades extremas, terreno exigente, colisiones, lesiones graves",
        "velocidad_tipica_kmh": 90,
        "nivel_riesgo": "ALTO",
        "recomendacion_casco": "Casco de enduro/cross especializado",
        "equipamiento_minimo": ["Casco enduro/cross", "Body armor completo", "Rodilleras nivel 2", "Botas enduro rigidas", "Gogles"]
    },
    "deportivo": {
        "nombre": "Deportivo",
        "descripcion": "Motociclista que prioriza el rendimiento en asfalto y carretera.",
        "uso_principal": "Deporte, carretera, circuito, velocidad",
        "motos_tipicas": ["Kawasaki Ninja 400", "Yamaha R3", "KTM RC 390", "Honda CBR500R"],
        "riesgos_principales": "Alta velocidad, curvas tecnicas, sobreconfianza, adelantamientos",
        "velocidad_tipica_kmh": 150,
        "nivel_riesgo": "ALTO",
        "recomendacion_casco": "Casco integral premium certificado (Shoei/AGV/Arai)",
        "equipamiento_minimo": ["Casco integral premium ECE 22.06", "Chaqueta cuero CE nivel 2", "Guantes racing CE nivel 2", "Botas racing", "Espaldera nivel 2"]
    }
}

OBJETIVOS_APRENDIZAJE = [
    "Mejorar mi seguridad en ciudad",
    "Conocer la normativa LOTTTSV",
    "Aprender tecnicas de conduccion en lluvia",
    "Elegir el equipamiento correcto",
    "Preparar viajes largos seguros",
    "Mejorar tecnicas de manejo off-road",
    "Reducir riesgo de accidentes",
    "Conocer mantenimiento basico"
]


def _clasificar_perfil(datos: dict) -> str:
    """Motor de clasificacion de perfil basado en 5 variables."""
    uso        = datos.get("tipo_uso", "").lower()
    anos       = datos.get("anos_experiencia", 0)
    cilindrada = datos.get("cilindrada_cc", 125)
    horas_dia  = datos.get("horas_uso_diario", 0)
    moto       = datos.get("moto_actual", "").lower()

    # Delivery — prioridad por horas de uso
    if "delivery" in uso or "mensajeria" in uso or horas_dia >= 6:
        return "delivery"

    # Enduro — por tipo de uso especifico
    if "enduro" in uso or "competicion" in uso or "cross" in moto:
        return "enduro"

    # Aventura — off-road con experiencia media
    if "aventura" in uso or "off-road" in uso or "campo" in uso:
        return "aventura"

    # Touring — viajes largos o alta cilindrada con experiencia
    if "touring" in uso or "viaje" in uso or (cilindrada >= 300 and anos >= 3):
        return "touring"

    # Deportivo — sport con cilindrada media-alta
    if "deport" in uso or "velocidad" in uso or ("sport" in moto and cilindrada >= 200):
        return "deportivo"

    # Default: urbano diario
    return "urbano"


def _calcular_nivel(anos: int) -> str:
    if anos < 2:
        return "basico"
    elif anos < 5:
        return "intermedio"
    return "avanzado"


def _construir_system_prompt(perfil_key: str, datos: dict) -> str:
    """Genera el system prompt personalizado para Claude API."""
    perfil = PERFILES[perfil_key]
    return f"""Eres MotoEdu EC, asistente experto en educacion vial para motociclistas ecuatorianos.

PERFIL DEL USUARIO:
- Nombre: {datos.get('nombre', 'Motociclista')}
- Perfil asignado: {perfil['nombre']}
- Tipo de uso: {datos.get('tipo_uso', 'urbano')}
- Anos de experiencia: {datos.get('anos_experiencia', 1)}
- Moto actual: {datos.get('moto_actual', 'No especificada')}
- Zona geografica: {datos.get('zona', 'Sierra')}
- Nivel de conocimiento: {_calcular_nivel(datos.get('anos_experiencia', 1))}
- Objetivos de aprendizaje: {', '.join(datos.get('objetivos', ['mejorar seguridad']))}
- Nivel de riesgo del perfil: {perfil['nivel_riesgo']}

INSTRUCCIONES:
- Adapta SIEMPRE el lenguaje, ejemplos y nivel de detalle a este perfil especifico.
- Para perfil {perfil['nombre']}: {perfil['descripcion']}
- Riesgos principales a abordar: {perfil['riesgos_principales']}
- Solo hablas de motociclismo, seguridad vial y LOTTTSV ecuatoriana.
- Siempre cita la fuente (articulo del reglamento o estadistica verificable).
- Usa ejemplos concretos del contexto ecuatoriano (ciudades, rutas, marcas disponibles).
"""


# ─── ENDPOINTS ───────────────────────────────────────────────

@router.post("/crear", summary="Onboarding completo — crea el perfil del motociclista")
def crear_perfil(
    datos: dict = Body(..., example={
        "nombre": "Carlos Perez",
        "tipo_uso": "delivery",
        "anos_experiencia": 2,
        "moto_actual": "Honda CB100",
        "cilindrada_cc": 100,
        "zona": "Guayas",
        "horas_uso_diario": 8,
        "objetivos": ["conocer la normativa LOTTTSV", "mejorar seguridad en ciudad"]
    }),
    db: Session = Depends(get_db)
):
    """
    Onboarding de 5 datos del motociclista:
    1. tipo_uso (delivery/urbano/touring/aventura/enduro/deportivo)
    2. anos_experiencia
    3. moto_actual + cilindrada_cc
    4. zona (Sierra/Costa/Amazonia)
    5. objetivos[] de aprendizaje
    """
    # Clasificar perfil
    perfil_key  = _clasificar_perfil(datos)
    perfil_info = PERFILES[perfil_key]
    nivel       = _calcular_nivel(datos.get("anos_experiencia", 0))
    usuario_id  = str(uuid.uuid4())

    # Guardar en PostgreSQL
    try:
        db.execute(text("""
            INSERT INTO usuarios (id, nombre, email, provincia, tipo_moto, anos_experiencia, nivel)
            VALUES (:id, :nombre, :email, :provincia, :tipo_moto, :anos, :nivel)
            ON CONFLICT DO NOTHING
        """), {
            "id":        usuario_id,
            "nombre":    datos.get("nombre", "Motociclista"),
            "email":     datos.get("email", f"{usuario_id[:8]}@motoedu.ec"),
            "provincia": datos.get("zona", "Azuay"),
            "tipo_moto": datos.get("tipo_uso", "urbano"),
            "anos":      datos.get("anos_experiencia", 0),
            "nivel":     nivel
        })
        db.commit()
    except Exception as e:
        db.rollback()

    # Construir system prompt personalizado
    system_prompt = _construir_system_prompt(perfil_key, datos)

    return {
        "usuario_id":          usuario_id,
        "perfil_asignado":     perfil_info["nombre"],
        "perfil_key":          perfil_key,
        "nivel":               nivel,
        "zona":                datos.get("zona", "Sierra"),
        "moto_actual":         datos.get("moto_actual", "No especificada"),
        "descripcion_perfil":  perfil_info["descripcion"],
        "motos_tipicas":       perfil_info["motos_tipicas"],
        "riesgos_principales": perfil_info["riesgos_principales"],
        "nivel_riesgo":        perfil_info["nivel_riesgo"],
        "recomendacion_casco": perfil_info["recomendacion_casco"],
        "equipamiento_minimo": perfil_info["equipamiento_minimo"],
        "objetivos":           datos.get("objetivos", []),
        "system_prompt_preview": system_prompt[:300] + "...",
        "siguiente_paso":      "/m2/educacion/categorias",
        "mensaje":             f"Bienvenido {datos.get('nombre','Motociclista')} — perfil {perfil_info['nombre']} configurado exitosamente"
    }


@router.get("/perfiles", summary="Lista los 6 perfiles de motociclista disponibles")
def listar_perfiles():
    return {
        "total": len(PERFILES),
        "perfiles": {
            k: {
                "nombre":        v["nombre"],
                "descripcion":   v["descripcion"],
                "uso_principal": v["uso_principal"],
                "nivel_riesgo":  v["nivel_riesgo"],
                "velocidad_tipica_kmh": v["velocidad_tipica_kmh"]
            }
            for k, v in PERFILES.items()
        }
    }


@router.get("/objetivos", summary="Lista los objetivos de aprendizaje disponibles")
def listar_objetivos():
    return {"objetivos": OBJETIVOS_APRENDIZAJE}


@router.get("/{usuario_id}", summary="Obtiene el perfil completo de un usuario")
def obtener_perfil(usuario_id: str, db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT * FROM usuarios WHERE id = :id"
    ), {"id": usuario_id}).mappings().first()
    if not result:
        return {"error": "Usuario no encontrado", "usuario_id": usuario_id}
    return dict(result)


@router.get("/{usuario_id}/progreso", summary="Resumen de progreso del usuario")
def progreso_usuario(usuario_id: str, db: Session = Depends(get_db)):
    usuario = db.execute(text(
        "SELECT * FROM usuarios WHERE id = :id"
    ), {"id": usuario_id}).mappings().first()
    if not usuario:
        return {"error": "Usuario no encontrado"}

    stats = db.execute(text("""
        SELECT
            COUNT(*) AS total_respuestas,
            SUM(CASE WHEN correcta THEN 1 ELSE 0 END) AS correctas,
            ROUND(100.0 * SUM(CASE WHEN correcta THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS pct_acierto
        FROM historial_evaluaciones WHERE usuario_id = :uid
    """), {"uid": usuario_id}).mappings().first()

    u = dict(usuario)
    s = dict(stats) if stats else {"total_respuestas": 0, "correctas": 0, "pct_acierto": 0}

    return {
        "usuario":           u,
        "puntos":            u.get("puntos_acumulados", 0),
        "nivel":             u.get("nivel", "basico"),
        "evaluaciones":      s,
        "perfil_info":       PERFILES.get(u.get("tipo_moto", "urbano"), PERFILES["urbano"])
    }
