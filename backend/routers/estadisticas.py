"""
Estadisticas — Dashboard Analitico Sprint 3
MotoEdu EC — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

router = APIRouter()


@router.get("/resumen", summary="Resumen general del sistema")
def resumen(db: Session = Depends(get_db)):
    tablas = [
        "motocicletas", "llantas", "usuarios",
        "historial_evaluaciones", "preguntas_viales", "brechas_conocimiento"
    ]
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


@router.get("/dashboard", summary="Dashboard analitico completo para Edutainment")
def dashboard_analitico(db: Session = Depends(get_db)):
    """
    Endpoint principal del dashboard analitico.
    Retorna todos los datos necesarios para los 5 graficos de Chart.js.
    """

    # 1. Distribucion de perfiles de usuarios
    perfiles_result = db.execute(text("""
        SELECT tipo_moto AS perfil, COUNT(*) AS cantidad
        FROM usuarios
        GROUP BY tipo_moto
        ORDER BY cantidad DESC
    """)).mappings().all()
    distribucion_perfiles = [dict(r) for r in perfiles_result]

    # 2. Progreso promedio por nivel
    progreso_result = db.execute(text("""
        SELECT nivel, COUNT(*) AS usuarios,
               AVG(puntos_acumulados) AS puntos_promedio
        FROM usuarios
        GROUP BY nivel
        ORDER BY CASE nivel WHEN 'basico' THEN 1 WHEN 'intermedio' THEN 2 WHEN 'avanzado' THEN 3 ELSE 0 END
    """)).mappings().all()
    progreso_por_nivel = [dict(r) for r in progreso_result]

    # 3. Puntaje promedio general
    puntaje_result = db.execute(text("""
        SELECT
            ROUND(AVG(puntos_acumulados), 1) AS puntaje_promedio,
            MAX(puntos_acumulados) AS puntaje_maximo,
            COUNT(*) AS total_usuarios
        FROM usuarios
    """)).mappings().first()
    puntaje_stats = dict(puntaje_result) if puntaje_result else {}

    # 4. Estadisticas de evaluaciones
    eval_result = db.execute(text("""
        SELECT
            COUNT(*) AS total_evaluaciones,
            SUM(CASE WHEN correcta THEN 1 ELSE 0 END) AS correctas,
            ROUND(100.0 * SUM(CASE WHEN correcta THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 1) AS pct_acierto_global
        FROM historial_evaluaciones
    """)).mappings().first()
    eval_stats = dict(eval_result) if eval_result else {}

    # 5. Top usuarios por puntos
    top_usuarios = db.execute(text("""
        SELECT nombre, nivel, puntos_acumulados, provincia
        FROM usuarios
        ORDER BY puntos_acumulados DESC
        LIMIT 10
    """)).mappings().all()
    ranking = [dict(r) for r in top_usuarios]

    # 6. Distribucion preguntas por categoria
    cats_result = db.execute(text("""
        SELECT c.nombre AS categoria, COUNT(p.id) AS total
        FROM categorias_pregunta c
        LEFT JOIN preguntas_viales p ON c.id = p.categoria_id
        GROUP BY c.nombre
        ORDER BY total DESC
    """)).mappings().all()
    preguntas_por_categoria = [dict(r) for r in cats_result]

    # 7. Brechas para el mapa de calor
    brechas_result = db.execute(text("""
        SELECT descripcion, pct_con_brecha, nivel_riesgo
        FROM brechas_conocimiento
        ORDER BY pct_con_brecha DESC
        LIMIT 8
    """)).mappings().all()
    brechas_top = [dict(r) for r in brechas_result]

    # 8. Resumen general
    resumen_general = {
        "total_usuarios":      db.execute(text("SELECT COUNT(*) FROM usuarios")).scalar() or 0,
        "total_evaluaciones":  db.execute(text("SELECT COUNT(*) FROM historial_evaluaciones")).scalar() or 0,
        "total_motos":         db.execute(text("SELECT COUNT(*) FROM motocicletas")).scalar() or 0,
        "total_preguntas":     db.execute(text("SELECT COUNT(*) FROM preguntas_viales")).scalar() or 0,
        "total_llantas":       db.execute(text("SELECT COUNT(*) FROM llantas")).scalar() or 0,
        "total_brechas":       db.execute(text("SELECT COUNT(*) FROM brechas_conocimiento")).scalar() or 0,
    }

    return {
        "resumen":                 resumen_general,
        "distribucion_perfiles":   distribucion_perfiles,
        "progreso_por_nivel":      progreso_por_nivel,
        "puntaje_stats":           puntaje_stats,
        "eval_stats":              eval_stats,
        "top_usuarios":            ranking,
        "preguntas_por_categoria": preguntas_por_categoria,
        "brechas_top":             brechas_top,
    }


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
