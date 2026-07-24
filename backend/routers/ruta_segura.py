"""
RUTA SEGURA — MotoEdu EC (v2 ampliada)
Escenarios de decision en la via, generados por Claude con contexto
geografico variado de TODO Ecuador. Correcta = +150 XP, incorrecta = +30 XP.
Sprint 5 — UPS Cuenca 2026
"""
import json
import random
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from services.claude_service import client, CLAUDE_MODEL_HAIKU, USE_MOCK
from services.zonas_ecuador import contexto_geografico

router = APIRouter(prefix="/m8/ruta", tags=["M8 — Ruta Segura"])

XP_CORRECTO, XP_INCORRECTO = 150, 30

# Escenografías variadas para forzar diversidad en la generación
ESCENOGRAFIAS_POR_ZONA = {
    "Cuenca": [
        "la Av. de las Americas (Circunvalacion de Cuenca), una avenida ancha de alto trafico",
        "una calle adoquinada del Centro Historico de Cuenca, angosta y con pendiente",
        "la subida a Turi, una via en cuesta a las afueras de Cuenca",
        "la via Cuenca-Molleturo bajando de El Cajas, carretera de montana",
        "la via Cuenca-Giron, carretera interprovincial con curvas",
        "la Av. Ordonez Lasso, una avenida amplia del noroeste de Cuenca",
        "la autopista Cuenca-Azogues, via rapida de dos carriles",
        "la Av. Loja de Cuenca, avenida urbana de doble sentido",
    ],
    "Quito": [
        "la Av. Gonzalez Suarez de Quito junto al bordillo del valle",
        "la Av. de los Shyris de Quito con trafico denso",
        "la bajada de la Av. Simon Bolivar con neblina",
        "el Centro Historico de Quito con calles empinadas y adoquin",
        "la Av. Mariscal Sucre (Occidental) en hora pico",
        "la via a los valles (Cumbaya-Tumbaco) con curvas",
    ],
    "Guayaquil": [
        "la Av. de las Americas de Guayaquil con trafico pesado",
        "la Perimetral de Guayaquil junto a camiones de carga",
        "el centro de Guayaquil con calor y trafico denso",
        "la via a Samborondon con lluvia tropical repentina",
        "la via a la costa (Guayaquil-Salinas) con sol fuerte",
    ],
    "Costa": [
        "una playa de Manabi con arena arrastrada sobre el asfalto",
        "un tramo recto entre Manta y Portoviejo con sol fuerte",
        "la via Jipijapa-Guayaquil con lluvia tropical",
    ],
    "Sierra": [
        "un camino de tercer orden de tierra y lastre en la sierra",
        "una via de paramo con neblina espesa",
        "una calle empinada de pueblo andino con adoquin",
    ],
}

# Lista plana de respaldo (si no hay zona reconocida)
ESCENOGRAFIAS = ESCENOGRAFIAS_POR_ZONA["Cuenca"]

CLIMAS = ["lluvia", "neblina", "sol", "noche"]

# Banco mock ampliado (12) — respaldo variado cuando Claude no responde
ESCENARIOS_MOCK = [
    {"titulo": "Arena en la playa de Manta", "clima": "sol", "via": "carretera",
     "narrativa": "Vas por la via costera cerca de Manta. El viento arrastro arena sobre el asfalto en plena curva y sientes que la rueda trasera resbala un poco.",
     "opciones": [{"id":"a","texto":"Acelero para salir rapido de la curva"},{"id":"b","texto":"Suelto el acelerador suave, enderezo la moto y freno con cuidado en recta"},{"id":"c","texto":"Freno fuerte de inmediato con el delantero"}],
     "correcta":"b","consecuencias":{"a":"Al acelerar sobre arena perdiste mas traccion y casi te vas al piso.","b":"Enderezar y esperar la recta para frenar mantuvo el control. La arena reduce el agarre como el agua.","c":"El delantero se bloqueo sobre la arena y la moto se fue de lado."},
     "articulo":"Adaptar la velocidad a la superficie de la via es un principio basico de conduccion segura."},
    {"titulo": "Tierra y lastre a Paute", "clima": "sol", "via": "curva",
     "narrativa": "Tomas un desvio de tercer orden hacia Paute. El camino es de tierra suelta con piedras y viene una bajada con curva.",
     "opciones": [{"id":"a","texto":"Bajo rapido usando solo el freno trasero"},{"id":"b","texto":"Bajo despacio, cuerpo atras, frenos suaves y mirada larga a la salida"},{"id":"c","texto":"Bloqueo el trasero para derrapar controlado"}],
     "correcta":"b","consecuencias":{"a":"Solo trasero en bajada de tierra te dejo casi sin control de direccion.","b":"Velocidad baja, peso atras y frenado suave: asi se dominan los caminos de tierra.","c":"El derrape se te fue de las manos en la piedra suelta."},
     "articulo":"En superficies sueltas se prioriza el control sobre la velocidad; el frenado debe ser progresivo."},
    {"titulo": "Adoquin del Centro de Cuenca", "clima": "lluvia", "via": "urbana",
     "narrativa": "Llueve en el Centro Historico de Cuenca. El adoquin y la piedra estan brillantes y un peaton cruza de golpe entre autos parqueados.",
     "opciones": [{"id":"a","texto":"Freno fuerte con ambos frenos de inmediato"},{"id":"b","texto":"Ya venia lento; freno progresivo, moto recta, y me detengo antes del peaton"},{"id":"c","texto":"Esquivo rapido al peaton hacia la izquierda"}],
     "correcta":"b","consecuencias":{"a":"Frenar fuerte sobre adoquin mojado casi bloquea las ruedas.","b":"Venir despacio en el centro y frenar progresivo te dio margen para el peaton.","c":"Esquivar hacia el carril contrario te expuso a los autos que venian."},
     "articulo":"En zonas urbanas con peatones, la velocidad precautoria permite reaccionar a lo imprevisto."},
    {"titulo": "Trafico en la Perimetral de Guayaquil", "clima": "sol", "via": "carretera",
     "narrativa": "Vas por la Perimetral de Guayaquil con trafico pesado. Un camion cambia de carril sin senalizar y te deja poco espacio.",
     "opciones": [{"id":"a","texto":"Acelero para pasarlo por la derecha"},{"id":"b","texto":"Reduzco, me hago ver, y me mantengo fuera de su punto ciego"},{"id":"c","texto":"Me pego al costado del camion para que me vea"}],
     "correcta":"b","consecuencias":{"a":"Pasar por la derecha te metio justo donde el camion no te ve.","b":"Reducir y salir del punto ciego es la jugada segura junto a vehiculos grandes.","c":"Pegarte al costado te dejo en el angulo muerto mas peligroso."},
     "articulo":"Mantenerse fuera de los puntos ciegos de vehiculos pesados previene siniestros graves."},
    {"titulo": "Neblina camino a los valles de Quito", "clima": "neblina", "via": "curva",
     "narrativa": "Bajas de Quito hacia un valle y la neblina se cierra. Apenas ves unos metros y detras un auto te apura con las luces.",
     "opciones": [{"id":"a","texto":"Acelero para que el auto no me presione"},{"id":"b","texto":"Enciendo luz baja, reduzco y me oriento por la linea de la via"},{"id":"c","texto":"Pongo las luces altas para ver mejor"}],
     "correcta":"b","consecuencias":{"a":"Acelerar a ciegas en neblina te dejo sin margen ante una curva.","b":"Luz baja y velocidad reducida: correcto. La alta rebota en la neblina.","c":"La luz alta creo una pared blanca y viste aun menos."},
     "articulo":"Con visibilidad reducida se usa luz baja y se reduce la velocidad segun la distancia visible."},
    {"titulo": "Sol fuerte Manta-Portoviejo", "clima": "sol", "via": "carretera",
     "narrativa": "Recta larga entre Manta y Portoviejo, sol de mediodia. El calor genera un espejismo y un vehiculo lento aparece de golpe adelante.",
     "opciones": [{"id":"a","texto":"Adelanto sin mirar porque la recta es larga"},{"id":"b","texto":"Confirmo via libre, senalizo y adelanto por la izquierda con decision"},{"id":"c","texto":"Me pego atras esperando que acelere"}],
     "correcta":"b","consecuencias":{"a":"Adelantar sin confirmar en pleno espejismo casi te cuesta caro.","b":"Confirmar, senalizar y adelantar por izquierda con decision: de manual.","c":"Quedarte pegado atras te quito visibilidad de lo que venia."},
     "articulo":"El adelantamiento se hace por la izquierda, con visibilidad confirmada y senalizacion previa."},
    {"titulo": "Malecon de Guayaquil de noche", "clima": "noche", "via": "urbana",
     "narrativa": "Circulas de noche por el malecon con poca luz. Un grupo cruza fuera del paso peatonal y tu visera esta un poco empanada.",
     "opciones": [{"id":"a","texto":"Sigo a la misma velocidad, ellos se apuraran"},{"id":"b","texto":"Reduzco, aumento distancia y limpio la visera en la siguiente parada"},{"id":"c","texto":"Toco bocina y mantengo velocidad"}],
     "correcta":"b","consecuencias":{"a":"A esa velocidad y con poca visibilidad casi no alcanzas a frenar.","b":"Reducir de noche con visibilidad reducida es lo correcto; la visera limpia salva.","c":"La bocina no reemplaza reducir la velocidad ante peatones."},
     "articulo":"De noche se aumenta la distancia de seguimiento y se reduce la velocidad por la menor visibilidad."},
    {"titulo": "Curva ciega Cuenca-Giron", "clima": "sol", "via": "curva",
     "narrativa": "Vas por la via Cuenca-Giron y entras a una curva ciega cerrada. No ves lo que viene y hay linea continua.",
     "opciones": [{"id":"a","texto":"Corto la curva por dentro para salir rapido"},{"id":"b","texto":"Abro la trazada, reduzco antes de entrar y mantengo mi carril"},{"id":"c","texto":"Acelero en plena curva para terminarla antes"}],
     "correcta":"b","consecuencias":{"a":"Cortar la curva te metio al carril contrario donde venia un auto.","b":"Reducir antes y respetar tu carril en curva ciega es lo seguro.","c":"Acelerar en curva ciega redujo tu margen si algo aparecia."},
     "articulo":"En curvas sin visibilidad se reduce antes de entrar y se respeta rigurosamente el carril propio."},
    {"titulo": "Cruce escolar en Azuay", "clima": "sol", "via": "urbana",
     "narrativa": "Pasas por una parroquia de Azuay a la hora de salida de clases. Hay ninos en la vereda y un bus escolar detenido con luces.",
     "opciones": [{"id":"a","texto":"Adelanto al bus escolar rapido mientras pueda"},{"id":"b","texto":"Reduzco casi al paso, listo para frenar, y no adelanto al bus detenido"},{"id":"c","texto":"Toco bocina para que los ninos no crucen"}],
     "correcta":"b","consecuencias":{"a":"Adelantar un bus escolar detenido es de altisimo riesgo: un nino pudo cruzar.","b":"Reducir al paso junto a un bus escolar detenido protege a los ninos.","c":"La bocina no garantiza que un nino no cruce; hay que reducir."},
     "articulo":"Junto a buses escolares detenidos y zonas escolares se extrema la precaucion y se reduce la velocidad."},
    {"titulo": "Viento cruzado en Riobamba", "clima": "sol", "via": "carretera",
     "narrativa": "En la panamericana cerca de Riobamba sopla viento cruzado fuerte. Una racha empuja tu moto hacia el carril de al lado.",
     "opciones": [{"id":"a","texto":"Me aferro rigido al manillar y acelero"},{"id":"b","texto":"Aflojo el cuerpo, inclino levemente contra el viento y reduzco un poco"},{"id":"c","texto":"Suelto una mano para acomodarme"}],
     "correcta":"b","consecuencias":{"a":"Ir rigido y rapido te hizo mas vulnerable a la siguiente racha.","b":"Cuerpo suelto, leve inclinacion al viento y menos velocidad: control recuperado.","c":"Soltar una mano con viento fuerte casi te desestabiliza."},
     "articulo":"Ante viento cruzado se reduce la velocidad y se ajusta la postura para mantener la estabilidad."},
    {"titulo": "Via inundada en Los Rios", "clima": "lluvia", "via": "carretera",
     "narrativa": "Tras un aguacero en Los Rios, un tramo de la via quedo cubierto de agua y no ves el fondo ni los huecos.",
     "opciones": [{"id":"a","texto":"Cruzo rapido para no mojar el motor"},{"id":"b","texto":"Evaluo la profundidad, cruzo lento y constante si es seguro, o busco otra via"},{"id":"c","texto":"Cruzo por el borde donde parece menos hondo sin mirar"}],
     "correcta":"b","consecuencias":{"a":"Cruzar rapido levanto agua al motor y ocultaste un hueco.","b":"Evaluar antes y cruzar lento y constante, o rodear, es lo prudente.","c":"El borde tenia un hueco que no viste bajo el agua."},
     "articulo":"Ante agua sobre la via se evalua la profundidad; si hay duda, no se cruza."},
    {"titulo": "Mercado de Loja", "clima": "sol", "via": "urbana",
     "narrativa": "Entras a una calle junto a un mercado de Loja llena de peatones, triciclos de carga y autos mal parqueados que abren puertas.",
     "opciones": [{"id":"a","texto":"Avanzo entre los autos aprovechando los huecos"},{"id":"b","texto":"Voy al paso, atento a puertas que se abren y peatones, listo para frenar"},{"id":"c","texto":"Acelero en los tramos libres entre puestos"}],
     "correcta":"b","consecuencias":{"a":"Meterte entre autos casi te golpea una puerta que se abrio.","b":"Ir al paso y anticipar puertas y peatones es lo correcto en zonas de mercado.","c":"Acelerar en los huecos te dejo sin margen cuando salio un triciclo."},
     "articulo":"En zonas comerciales congestionadas se circula a velocidad de paso, anticipando obstaculos."},
]


class EscenarioIn(BaseModel):
    usuario_id: int
    perfil: dict = {}


@router.post("/escenario")
def nuevo_escenario(datos: EscenarioIn, db: Session = Depends(get_db)):
    perfil = datos.perfil or {}
    if USE_MOCK:
        return {"modo": "mock", "escenario": random.choice(ESCENARIOS_MOCK)}

    ciudad = perfil.get("ciudad", "") or ""
    zona_raw = perfil.get("zona", "Sierra") or "Sierra"
    zona = random.choice(zona_raw) if isinstance(zona_raw, list) and zona_raw else (zona_raw or "Sierra")
    geo = contexto_geografico(ciudad, perfil.get("provincia", ""), zona)
    # Soporta multiples perfiles: si el usuario eligio varios tipos de uso,
    # alterna al azar entre ellos en cada escenario -- asi alguien con
    # "aventura + urbano" ve ambos contextos con el tiempo, no solo uno.
    tipo_uso_raw = perfil.get("tipo_uso", "urbano")
    tipo_uso = random.choice(tipo_uso_raw) if isinstance(tipo_uso_raw, list) and tipo_uso_raw else (tipo_uso_raw or "urbano")

    # Elegir escenografia COHERENTE con la ubicacion del motociclista.
    # Antes se elegia al azar de TODAS las ciudades, lo que mezclaba lugares de
    # distintas urbes (p.ej. Av. Gonzalez Suarez de Quito "cerca de Turi" de Cuenca).
    ciudad_l = ciudad.lower()
    if "cuenca" in ciudad_l:       claves = "Cuenca"
    elif "quito" in ciudad_l:      claves = "Quito"
    elif "guayaquil" in ciudad_l:  claves = "Guayaquil"
    elif zona.lower() == "costa":  claves = "Costa"
    else:                          claves = "Cuenca"  # default del proyecto (UPS Cuenca)
    pool = ESCENOGRAFIAS_POR_ZONA.get(claves, ESCENOGRAFIAS_POR_ZONA["Cuenca"])
    escenografia = random.choice(pool)
    clima_sug = random.choice(CLIMAS)

    prompt = f"""Genera UN escenario UNICO y variado de decision de seguridad vial para un motociclista ecuatoriano.

Perfil del motociclista: {tipo_uso}, {perfil.get('anos_experiencia', 1)} anos de experiencia.
Contexto: motociclista ecuatoriano. Clima serrano variable (neblina matinal, lluvia vespertina).

UBICA el escenario EXACTAMENTE en: {escenografia}.
Usa SOLO ese lugar. NO lo combines con otro sector, avenida o barrio. NO digas "en el corazon de" ni "cerca de" otro lugar. El unico lugar mencionado en toda la narrativa debe ser ese.
Clima sugerido: {clima_sug}.
NO uses siempre El Cajas ni el mismo lugar; VARIA el clima y el tipo de riesgo.
IMPORTANTE: usa UNICAMENTE el lugar indicado arriba. NO combines calles ni sectores de ciudades distintas. Si nombras una via, debe ser real y pertenecer a esa misma ciudad.
Riesgos posibles (elige uno distinto cada vez): superficie resbalosa, punto ciego, peaton imprevisto,
adelantamiento, curva ciega, animal en via, viento, bache, vehiculo detenido, zona escolar, agua en via.

Responde SOLO con JSON valido, sin markdown ni texto extra, con esta estructura EXACTA:
{{"titulo":"titulo corto y evocador (usa SOLO el lugar indicado, sin combinarlo con otro)",
"clima":"{clima_sug}",
"via":"urbana|carretera|curva",
"narrativa":"situacion en segunda persona, 2-3 frases, tension real. Menciona UNICAMENTE el lugar indicado, sin agregar otros sectores ni barrios",
"opciones":[{{"id":"a","texto":"..."}},{{"id":"b","texto":"..."}},{{"id":"c","texto":"..."}}],
"correcta":"a|b|c",
"consecuencias":{{"a":"que pasa si elige a (1-2 frases)","b":"...","c":"..."}},
"articulo":"referencia breve a la LOTTTSV o principio de seguridad aplicable"}}
La opcion correcta debe estar en posicion ALEATORIA (no siempre la b). Las incorrectas deben ser tentadoras pero peligrosas."""

    try:
        resp = client.messages.create(model=CLAUDE_MODEL_HAIKU, max_tokens=900,
                                      messages=[{"role": "user", "content": prompt}])
        texto = resp.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1].replace("json", "", 1).strip()
        escenario = json.loads(texto)
        # Validacion minima de estructura
        if not all(k in escenario for k in ("titulo", "opciones", "correcta", "consecuencias")):
            raise ValueError("estructura incompleta")
        return {"modo": "claude_api", "escenario": escenario}
    except Exception:
        return {"modo": "fallback", "escenario": random.choice(ESCENARIOS_MOCK)}


class ResolverIn(BaseModel):
    usuario_id: int
    correcto: bool


@router.post("/resolver")
def resolver(datos: ResolverIn, db: Session = Depends(get_db)):
    xp = XP_CORRECTO if datos.correcto else XP_INCORRECTO
    existe = db.execute(text("SELECT 1 FROM arcade_stats WHERE usuario_id=:u"),
                        {"u": datos.usuario_id}).fetchone()
    if existe:
        db.execute(text("UPDATE arcade_stats SET xp_total = xp_total + :x, partidas = partidas + 1 WHERE usuario_id=:u"),
                   {"x": xp, "u": datos.usuario_id})
    else:
        db.execute(text("""INSERT INTO arcade_stats (usuario_id, xp_total, partidas, aciertos_total, racha_actual, racha_maxima, ultima_fecha)
                           VALUES (:u, :x, 1, 0, 0, 0, :hoy)"""),
                   {"u": datos.usuario_id, "x": xp, "hoy": date.today()})
    db.execute(text("INSERT INTO arcade_partidas (usuario_id, modo, puntos, aciertos, total) VALUES (:u,'ruta',:p,:a,1)"),
               {"u": datos.usuario_id, "p": xp, "a": 1 if datos.correcto else 0})
    db.commit()
    xp_total = db.execute(text("SELECT xp_total FROM arcade_stats WHERE usuario_id=:u"),
                          {"u": datos.usuario_id}).scalar()
    return {"ok": True, "xp_ganado": xp, "xp_total": xp_total}
