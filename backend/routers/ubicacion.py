"""
M11 — UBICACION DE RESIDENCIA
Guarda provincia y ciudad (canton) de residencia del participante.

Router SEPARADO: no modifica auth.py. El registro existente sigue igual y
el frontend hace una segunda llamada aqui. Si esta falla, el registro no
se pierde.

El catalogo de ciudades corresponde a la division cantonal del Ecuador.
Para Azuay, Canar y Loja se incluye la totalidad de sus cantones, por ser
el ambito geografico del estudio. Para el resto de provincias se listan
los cantones principales, con la opcion "Otra" para casos no cubiertos.

Prefijo: /m11/ubicacion
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.database import get_db

router = APIRouter(prefix="/m11/ubicacion", tags=["M11 Ubicacion"])

OTRA = "Otra"

# ── Catalogo provincia -> cantones ─────────────────────────────────────
CIUDADES = {
    # Ambito del estudio: cantones completos
    "Azuay": ["Cuenca", "Camilo Ponce Enriquez", "Chordeleg", "El Pan", "Giron",
              "Gualaceo", "Guachapala", "Nabon", "Ona", "Paute", "Pucara",
              "San Fernando", "Santa Isabel", "Sevilla de Oro", "Sigsig"],
    "Canar": ["Azogues", "Biblian", "Canar", "Deleg", "El Tambo", "La Troncal", "Suscal"],
    "Loja": ["Loja", "Calvas", "Catamayo", "Celica", "Chaguarpamba", "Espindola",
             "Gonzanama", "Macara", "Olmedo", "Paltas", "Pindal", "Puyango",
             "Quilanga", "Saraguro", "Sozoranga", "Zapotillo"],
    # Resto del pais: cantones principales
    "Bolivar": ["Guaranda", "Caluma", "Chillanes", "Chimbo", "Echeandia",
                "Las Naves", "San Miguel"],
    "Carchi": ["Tulcan", "Bolivar", "Espejo", "Mira", "Montufar", "San Pedro de Huaca"],
    "Chimborazo": ["Riobamba", "Alausi", "Chambo", "Chunchi", "Colta", "Cumanda",
                   "Guamote", "Guano", "Pallatanga", "Penipe"],
    "Cotopaxi": ["Latacunga", "La Mana", "Pangua", "Pujili", "Salcedo",
                 "Saquisili", "Sigchos"],
    "El Oro": ["Machala", "Arenillas", "Atahualpa", "Balsas", "Chilla", "El Guabo",
               "Huaquillas", "Las Lajas", "Marcabeli", "Pasaje", "Pinas",
               "Portovelo", "Santa Rosa", "Zaruma"],
    "Esmeraldas": ["Esmeraldas", "Atacames", "Eloy Alfaro", "La Concordia",
                   "Muisne", "Quininde", "Rioverde", "San Lorenzo"],
    "Galapagos": ["Santa Cruz (Puerto Ayora)", "San Cristobal (Pto. Baquerizo Moreno)",
                  "Isabela (Puerto Villamil)"],
    "Guayas": ["Guayaquil", "Balao", "Balzar", "Colimes", "Daule", "Duran",
               "El Empalme", "El Triunfo", "Milagro", "Naranjal", "Naranjito",
               "Nobol", "Palestina", "Pedro Carbo", "Playas", "Salitre",
               "Samborondon", "Santa Lucia", "Simon Bolivar", "Yaguachi"],
    "Imbabura": ["Ibarra", "Antonio Ante (Atuntaqui)", "Cotacachi", "Otavalo",
                 "Pimampiro", "Urcuqui"],
    "Los Rios": ["Babahoyo", "Baba", "Buena Fe", "Mocache", "Montalvo", "Palenque",
                 "Puebloviejo", "Quevedo", "Quinsaloma", "Urdaneta", "Valencia",
                 "Ventanas", "Vinces"],
    "Manabi": ["Portoviejo", "Manta", "Bolivar (Calceta)", "Chone", "El Carmen",
               "Flavio Alfaro", "Jama", "Jaramijo", "Jipijapa", "Junin",
               "Montecristi", "Olmedo", "Pajan", "Pedernales", "Pichincha",
               "Puerto Lopez", "Rocafuerte", "San Vicente", "Santa Ana",
               "Sucre (Bahia de Caraquez)", "Tosagua", "24 de Mayo"],
    "Morona Santiago": ["Macas (Morona)", "Gualaquiza", "Huamboya", "Limon Indanza",
                        "Logrono", "Pablo Sexto", "Palora", "San Juan Bosco",
                        "Santiago", "Sucua", "Taisha", "Tiwintza"],
    "Napo": ["Tena", "Archidona", "Carlos Julio Arosemena Tola", "El Chaco", "Quijos"],
    "Orellana": ["Francisco de Orellana (Coca)", "Aguarico", "Joya de los Sachas", "Loreto"],
    "Pastaza": ["Puyo (Pastaza)", "Arajuno", "Mera", "Santa Clara"],
    "Pichincha": ["Quito", "Cayambe", "Mejia", "Pedro Moncayo",
                  "Pedro Vicente Maldonado", "Puerto Quito", "Ruminahui",
                  "San Miguel de los Bancos"],
    "Santa Elena": ["Santa Elena", "La Libertad", "Salinas"],
    "Santo Domingo de los Tsachilas": ["Santo Domingo", "La Concordia"],
    "Sucumbios": ["Nueva Loja (Lago Agrio)", "Cascales", "Cuyabeno",
                  "Gonzalo Pizarro", "Putumayo", "Shushufindi", "Sucumbios"],
    "Tungurahua": ["Ambato", "Banos", "Cevallos", "Mocha", "Patate", "Pelileo",
                   "Pillaro", "Quero", "Tisaleo"],
    "Zamora Chinchipe": ["Zamora", "Centinela del Condor", "Chinchipe (Zumba)",
                         "El Pangui", "Nangaritza", "Palanda", "Paquisha",
                         "Yacuambi", "Yantzaza"],
}

PROVINCIAS = sorted(CIUDADES.keys())


class Ubicacion(BaseModel):
    usuario_id: int
    provincia: str
    ciudad: Optional[str] = None


@router.get("/provincias", summary="Provincias del Ecuador con sus cantones")
def provincias():
    """Catalogo completo para poblar los dos desplegables del registro."""
    return {
        "total_provincias": len(PROVINCIAS),
        "provincias": PROVINCIAS,
        "ciudades": {p: CIUDADES[p] + [OTRA] for p in PROVINCIAS},
    }


@router.get("/ciudades/{provincia}", summary="Cantones de una provincia")
def ciudades(provincia: str):
    if provincia not in CIUDADES:
        raise HTTPException(status_code=404,
                            detail=f"Provincia no valida: {provincia}")
    return {"provincia": provincia, "ciudades": CIUDADES[provincia] + [OTRA]}


@router.post("", summary="Registrar provincia y ciudad de residencia")
def guardar(body: Ubicacion, db: Session = Depends(get_db)):
    if body.provincia not in CIUDADES:
        raise HTTPException(status_code=400,
                            detail=f"Provincia no valida: {body.provincia}")

    ciudad = (body.ciudad or "").strip() or None
    # Solo se acepta texto libre cuando el usuario eligio "Otra". Asi el
    # catalogo se mantiene normalizado y agrupable en el analisis.
    if ciudad and ciudad != OTRA and ciudad not in CIUDADES[body.provincia]:
        raise HTTPException(
            status_code=400,
            detail=f"'{ciudad}' no es un canton de {body.provincia}. "
                   f"Selecciona uno del listado o marca '{OTRA}'.")

    existe = db.execute(text("SELECT id, email FROM usuarios_auth WHERE id = :i"),
                        {"i": body.usuario_id}).mappings().first()
    if not existe:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.execute(text("""
        UPDATE usuarios_auth
           SET provincia = :p, ciudad = :c, ubicacion_origen = 'registro_app'
         WHERE id = :i
    """), {"p": body.provincia, "c": ciudad, "i": body.usuario_id})

    db.execute(text("UPDATE usuarios SET provincia = :p WHERE email = :e"),
               {"p": body.provincia, "e": existe["email"]})

    db.commit()
    return {"ok": True, "usuario_id": body.usuario_id,
            "provincia": body.provincia, "ciudad": ciudad,
            "origen": "registro_app"}


@router.get("/{usuario_id}", summary="Consultar la ubicacion registrada")
def consultar(usuario_id: int, db: Session = Depends(get_db)):
    fila = db.execute(text("""
        SELECT id, nombre, provincia, ciudad, ubicacion_origen
          FROM usuarios_auth WHERE id = :i
    """), {"i": usuario_id}).mappings().first()
    if not fila:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(fila)
