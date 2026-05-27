"""Estadísticas — MotoEdu EC Tesis"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter()

@router.get("/resumen", summary="Resumen general del sistema")
def resumen(db: Session = Depends(get_db)):
    tablas = ["motocicletas","llantas","usuarios","historial_evaluaciones","preguntas_viales","brechas_conocimiento"]
    counts = {}
    for t in tablas:
        try:
            counts[t] = db.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        except:
            counts[t] = 0
    return {"resumen": counts, "estado": "activo"}


@router.get("/brechas", summary="Mapa de brechas de conocimiento")
def brechas(db: Session = Depends(get_db)):
    result = db.execute(text(
        "SELECT * FROM brechas_conocimiento ORDER BY nivel_riesgo, pct_con_brecha DESC"
    )).mappings().all()
    return {"total": len(result), "brechas": [dict(r) for r in result]}


@router.get("/pretest-postest", summary="Datos para el experimento estadistico")
def datos_experimento(db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT u.id, u.nombre, u.nivel,
               COUNT(h.id) AS total_respuestas,
               SUM(CASE WHEN h.correcta THEN 1 ELSE 0 END) AS correctas,
               ROUND(100.0*SUM(CASE WHEN h.correcta THEN 1 ELSE 0 END)/NULLIF(COUNT(h.id),0),1) AS pct_acierto
        FROM usuarios u
        LEFT JOIN historial_evaluaciones h ON u.id = h.usuario_id
        GROUP BY u.id, u.nombre, u.nivel
        HAVING COUNT(h.id) > 0
        ORDER BY pct_acierto DESC
    """)).mappings().all()
    return {"participantes": len(result), "datos": [dict(r) for r in result]}
