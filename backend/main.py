"""
MotoEdu EC — Tesis API
Universidad Politécnica Salesiana — Cuenca 2026
Estudiante: Sanango Romero José Addrisu
Tutor: Omar Gustavo Bravo Quezada Ph.D
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import perfil, educacion, asistente, motos, llantas, historia, gamificacion, estadisticas, auth, arcade, experimento, admin, garaje, duelos, ruta_segura, admin_grupos, revision, ubicacion, perfil_estado
from services.claude_service import USE_MOCK
from middleware_control import instalar_guardia_control


class UTF8JSONResponse(JSONResponse):
    """Declara charset=utf-8 explicito en Content-Type. Sin esto, algunos
    clientes HTTP en Windows (ej. PowerShell Invoke-RestMethod) pueden asumir
    una codificacion distinta y corromper tildes/enies (mojibake tipo 'Ã©')."""
    media_type = "application/json; charset=utf-8"


app = FastAPI(
    title="MotoEdu EC — Tesis API",
    default_response_class=UTF8JSONResponse,
    description="""
    ## Plataforma Inteligente de Educación Vial con IA Generativa
    
    Integrada a Edutainment — UPS Cuenca 2026
    
    ### Módulos:
    - **M1** — Perfil Inteligente del motociclista
    - **M2** — Educación Vial Personalizada con Claude API
    - **M3** — Asistente Experto RAG (LOTTTSV + catálogo)
    - **M4** — Recomendador de Motocicletas
    - **M5** — Recomendador de Llantas
    - **M6** — Historia del Motociclismo Ecuatoriano
    - **M7** — Gamificación Edutainment
    """,
    version="1.0.0",
    contact={
        "name": "Sanango Romero José Addrisu",
        "email": "jsanangor@est.ups.edu.ec"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://motoedu.org", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guardia del experimento: bloquea al grupo CONTROL en los modulos de
# aprendizaje y juego a nivel de API, no solo en el frontend.
instalar_guardia_control(app)

# Módulos de la tesis
app.include_router(perfil.router,       prefix="/m1/perfil",      tags=["M1 — Perfil Inteligente"])
app.include_router(educacion.router,    prefix="/m2/educacion",   tags=["M2 — Educación Vial"])
app.include_router(asistente.router,    prefix="/m3/asistente",   tags=["M3 — Asistente RAG"])
app.include_router(motos.router,        prefix="/m4/motos",       tags=["M4 — Recomendador Motos"])
app.include_router(llantas.router,      prefix="/m5/llantas",     tags=["M5 — Recomendador Llantas"])
app.include_router(historia.router,     prefix="/m6/historia",    tags=["M6 — Historia Motera"])
app.include_router(gamificacion.router, prefix="/m7/gamificacion",tags=["M7 — Gamificación"])
app.include_router(estadisticas.router, prefix="/estadisticas",   tags=["Estadísticas"])
app.include_router(auth.router,         tags=["Autenticación"])
app.include_router(arcade.router)
app.include_router(experimento.router)
app.include_router(admin.router)
app.include_router(garaje.router)
app.include_router(duelos.router)
app.include_router(ruta_segura.router)
app.include_router(admin_grupos.router)
app.include_router(revision.router)
app.include_router(ubicacion.router)
app.include_router(perfil_estado.router)

@app.get("/", tags=["Home"])
def root():
    return {
        "proyecto": "MotoEdu EC",
        "version": "1.0.0",
        "tesis": "UPS Cuenca 2026",
        "modulos": ["M1-Perfil", "M2-Educacion", "M3-RAG", "M4-Motos", "M5-Llantas", "M6-Historia", "M7-Gamificacion"],
        "docs": "/docs",
        "estado": "desarrollo"
    }


@app.get("/health", tags=["Home"])
def health():
    return {"status": "ok", "mensaje": "MotoEdu EC Tesis API activa",
            "claude_api": "mock" if USE_MOCK else "real"}