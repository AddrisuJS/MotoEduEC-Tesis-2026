"""
RUTA SEGURA — MotoEdu EC
Escenarios de decision en la via, generados por Claude con contexto
geografico del usuario. Decision correcta = +150 XP, incorrecta = +30 XP.
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
from services.claude_service import client, CLAUDE_MODEL_SONNET, USE_MOCK
from services.zonas_ecuador import contexto_geografico

router = APIRouter(prefix="/m8/ruta", tags=["M8 — Ruta Segura"])

XP_CORRECTO, XP_INCORRECTO = 150, 30

ESCENARIOS_MOCK = [
    {"titulo": "Neblina en El Cajas", "clima": "neblina", "via": "curva",
     "narrativa": "Bajas de El Cajas hacia Cuenca. La neblina se cierra de golpe y apenas ves 20 metros. Un bus aparece atras y te presiona con las luces.",
     "opciones": [
        {"id": "a", "texto": "Acelero para que el bus no me alcance"},
        {"id": "b", "texto": "Reduzco velocidad, enciendo luces bajas y me orillo a la derecha para dejarlo pasar"},
        {"id": "c", "texto": "Freno en seco en plena via para que el bus frene tambien"}],
     "correcta": "b",
     "consecuencias": {
        "a": "Aceleraste a ciegas: una curva cerrada aparecio de la nada y casi sales de la via. En neblina, mas velocidad = menos tiempo de reaccion.",
        "b": "El bus paso con seguridad y tu mantuviste el control total. Luz baja (la alta rebota en la neblina), velocidad reducida y dejar pasar: la formula correcta.",
        "c": "El bus casi te impacta por detras. Frenar en seco con poca visibilidad es de las maniobras mas peligrosas."},
     "articulo": "El Reglamento a la LOTTTSV exige adaptar la velocidad a las condiciones de visibilidad y clima de la via."},
    {"titulo": "Lluvia en la Perimetral", "clima": "lluvia", "via": "urbana",
     "narrativa": "Primeros minutos de un aguacero en la ciudad. El semaforo adelante cambia a amarillo y el pavimento brilla con esa mezcla de agua y grasa.",
     "opciones": [
        {"id": "a", "texto": "Acelero para pasar el amarillo"},
        {"id": "b", "texto": "Freno progresivo con ambos frenos, moto en linea recta, y me detengo"},
        {"id": "c", "texto": "Freno solo con el delantero para detenerme mas rapido"}],
     "correcta": "b",
     "consecuencias": {
        "a": "El semaforo cambio a rojo antes de cruzar y un auto arranco: esquivaste de milagro sobre piso mojado. El amarillo significa detenerse si es seguro.",
        "b": "Te detuviste con control total. Frenado progresivo, ambos frenos y en linea recta: exactamente lo que pide el piso mojado.",
        "c": "La rueda delantera se bloqueo sobre la mancha de grasa y casi te vas al piso. En mojado el delantero solo es receta para caida."},
     "articulo": "La luz amarilla indica detenerse si es seguro hacerlo. En lluvia la distancia de frenado puede duplicarse."},
    {"titulo": "Punto ciego del camion", "clima": "sol", "via": "carretera",
     "narrativa": "Vas por carretera detras de un camion lento. Quieres adelantar. Hay linea discontinua pero el camion es largo y no ves bien adelante.",
     "opciones": [
        {"id": "a", "texto": "Me pego al camion y adelanto rapido por la derecha"},
        {"id": "b", "texto": "Me alejo para ganar vision, confirmo via libre, senalizo y adelanto por la izquierda con decision"},
        {"id": "c", "texto": "Adelanto lento por la izquierda quedandome junto al camion"}],
     "correcta": "b",
     "consecuencias": {
        "a": "Adelantar por la derecha es contravencion y el conductor no te vio: casi te cierra al orillarse.",
        "b": "Distancia para ver, senal clara y maniobra decidida por la izquierda: adelantamiento de manual.",
        "c": "Te quedaste en el punto ciego del camion demasiado tiempo. Si debia esquivar algo, no te habria visto."},
     "articulo": "La LOTTTSV establece que el adelantamiento se realiza por la izquierda, en zona permitida y con visibilidad suficiente."},
]


class EscenarioIn(BaseModel):
    usuario_id: int
    perfil: dict = {}


@router.post("/escenario")
def nuevo_escenario(datos: EscenarioIn, db: Session = Depends(get_db)):
    perfil = datos.perfil or {}
    if USE_MOCK:
        return {"modo": "mock", "escenario": random.choice(ESCENARIOS_MOCK)}

    geo = contexto_geografico(perfil.get("ciudad", ""), perfil.get("provincia", ""), perfil.get("zona", "Sierra"))
    tipo_uso = perfil.get("tipo_uso", "urbano")
    prompt = f"""Genera UN escenario de decision de seguridad vial para un motociclista ecuatoriano.
Perfil: {tipo_uso}, {perfil.get('anos_experiencia', 1)} anos de experiencia.
{geo}

Responde SOLO con JSON valido, sin markdown ni texto extra, con esta estructura exacta:
{{"titulo": "titulo corto y evocador",
"clima": "lluvia|neblina|sol|noche",
"via": "urbana|carretera|curva",
"narrativa": "situacion en segunda persona, 2-3 frases, tension real, con un lugar LOCAL de su zona",
"opciones": [{{"id":"a","texto":"..."}},{{"id":"b","texto":"..."}},{{"id":"c","texto":"..."}}],
"correcta": "a|b|c",
"consecuencias": {{"a":"que pasa si elige a (2 frases)","b":"...","c":"..."}},
"articulo": "referencia breve a la LOTTTSV o principio de seguridad aplicable"}}
La opcion correcta debe estar en posicion ALEATORIA. Las incorrectas deben ser tentadoras pero peligrosas."""

    try:
        resp = client.messages.create(model=CLAUDE_MODEL_SONNET, max_tokens=800,
                                      messages=[{"role": "user", "content": prompt}])
        texto = resp.content[0].text.strip()
        if texto.startswith("```"):
            texto = texto.split("```")[1].replace("json", "", 1).strip()
        escenario = json.loads(texto)
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
