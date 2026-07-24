"""
ADMIN — Panel del investigador MotoEdu EC
Solo accesible con rol 'admin'. Vista completa del piloto:
progreso pretest/postest, arcade, y detalle por participante.
Sprint 5 — UPS Cuenca 2026
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db
from routers.auth import usuario_actual

router = APIRouter(prefix="/admin", tags=["Admin — Panel Investigador"])


def admin_requerido(usuario=Depends(usuario_actual)):
    if usuario.get("rol") != "admin":
        raise HTTPException(403, "Solo el investigador puede acceder a este panel")
    return usuario


@router.get("/resumen")
def resumen(admin=Depends(admin_requerido), db: Session = Depends(get_db)):
    """KPIs del piloto para las tarjetas del panel."""
    q = lambda sql, **p: db.execute(text(sql), p).scalar()
    registrados = q("SELECT COUNT(*) FROM usuarios_auth WHERE rol='participante'")
    pretests    = q("SELECT COUNT(*) FROM piloto_evaluaciones WHERE fase='pretest'")
    postests    = q("SELECT COUNT(*) FROM piloto_evaluaciones WHERE fase='postest'")
    prom_pre    = q("SELECT ROUND(AVG(score),2) FROM piloto_evaluaciones WHERE fase='pretest'")
    prom_post   = q("SELECT ROUND(AVG(score),2) FROM piloto_evaluaciones WHERE fase='postest'")
    mejora = None
    if prom_pre and prom_post and float(prom_pre) > 0:
        mejora = round((float(prom_post) - float(prom_pre)) / float(prom_pre) * 100, 1)
    return {
        "registrados": registrados,
        "pretests": pretests,
        "postests": postests,
        "completos": postests,
        "en_intervencion": (pretests or 0) - (postests or 0),
        "promedio_pretest": float(prom_pre) if prom_pre else None,
        "promedio_postest": float(prom_post) if prom_post else None,
        "mejora_promedio_pct": mejora,
        "partidas_arcade": q("SELECT COUNT(*) FROM arcade_partidas"),
        "xp_repartido": q("SELECT COALESCE(SUM(xp_total),0) FROM arcade_stats"),
    }


@router.get("/participantes")
def participantes(admin=Depends(admin_requerido), db: Session = Depends(get_db)):
    """Tabla maestra: cada participante con su avance completo."""
    rows = db.execute(text("""
        SELECT u.id, u.nombre, u.email, u.tipo_uso, u.creado_en, u.ultimo_login,
               pre.score  AS pre_score,  pre.creado_en  AS pre_fecha,
               post.score AS post_score, post.creado_en AS post_fecha,
               s.xp_total, s.racha_actual, s.partidas, s.aciertos_total,
               COALESCE(u.grupo,'intervencion') AS grupo
        FROM usuarios_auth u
        LEFT JOIN piloto_evaluaciones pre  ON pre.usuario_id  = u.id AND pre.fase  = 'pretest'
        LEFT JOIN piloto_evaluaciones post ON post.usuario_id = u.id AND post.fase = 'postest'
        LEFT JOIN arcade_stats s ON s.usuario_id = u.id
        WHERE u.rol = 'participante'
        ORDER BY u.id
    """)).fetchall()
    salida = []
    for r in rows:
        mejora = None
        if r[6] is not None and r[8] is not None and r[6] > 0:
            mejora = round((r[8] - r[6]) / r[6] * 100, 1)
        estado = ("completado" if r[8] is not None else
                  "en_intervencion" if r[6] is not None else "sin_pretest")
        salida.append({
            "id": r[0], "nombre": r[1], "email": r[2], "tipo_uso": r[3],
            "registrado": str(r[4])[:16] if r[4] else None,
            "ultimo_login": str(r[5])[:16] if r[5] else None,
            "pretest": r[6], "fecha_pretest": str(r[7])[:16] if r[7] else None,
            "postest": r[8], "fecha_postest": str(r[9])[:16] if r[9] else None,
            "mejora_pct": mejora,
            "xp": r[10] or 0, "racha": r[11] or 0,
            "partidas": r[12] or 0, "aciertos_arcade": r[13] or 0,
            "grupo": r[14] if len(r) > 14 else "intervencion",
            "estado": estado,
        })
    return {"total": len(salida), "participantes": salida}


@router.get("/participante/{usuario_id}")
def detalle(usuario_id: int, admin=Depends(admin_requerido), db: Session = Depends(get_db)):
    """Detalle completo de un participante: respuestas por pregunta y partidas."""
    u = db.execute(text(
        "SELECT id, nombre, email, tipo_uso, rol, COALESCE(grupo,'intervencion') FROM usuarios_auth WHERE id=:u"), {"u": usuario_id}).fetchone()
    if not u:
        raise HTTPException(404, "Participante no existe")

    evals = db.execute(text("""
        SELECT fase, score, total, detalles, creado_en
        FROM piloto_evaluaciones WHERE usuario_id=:u ORDER BY creado_en
    """), {"u": usuario_id}).fetchall()

    # Mapa id→texto de pregunta para que el detalle sea legible
    pregs = {r[0]: r[1] for r in db.execute(text("""
        SELECT pv.id, pv.pregunta FROM piloto_preguntas pp
        JOIN preguntas_viales pv ON pv.id = pp.pregunta_id
    """)).fetchall()}

    evaluaciones = []
    for e in evals:
        detalles = e[3] or []
        for d in detalles:
            d["pregunta"] = pregs.get(d.get("pregunta_id"), "")
        evaluaciones.append({"fase": e[0], "score": e[1], "total": e[2],
                             "fecha": str(e[4])[:16], "respuestas": detalles})

    partidas = [{"modo": p[0], "puntos": p[1], "aciertos": p[2], "total": p[3],
                 "fecha": str(p[4])[:16]}
                for p in db.execute(text("""
                    SELECT modo, puntos, aciertos, total, jugada_en
                    FROM arcade_partidas WHERE usuario_id=:u
                    ORDER BY jugada_en DESC LIMIT 30
                """), {"u": usuario_id}).fetchall()]

    # ── Insignias conseguidas ──
    from routers.gamificacion import INSIGNIAS, NIVELES
    ganadas_ids = {r[0] for r in db.execute(text(
        "SELECT insignia_id FROM insignias_usuario WHERE usuario_id=:u"), {"u": usuario_id}).fetchall()}
    insignias = [{"id": i["id"], "nombre": i["nombre"], "icono": i["icono"],
                  "descripcion": i["descripcion"], "conseguida": i["id"] in ganadas_ids}
                 for i in INSIGNIAS]

    # ── Nivel actual (por XP) ──
    st = db.execute(text(
        "SELECT COALESCE(xp_total,0), COALESCE(racha_maxima,0), COALESCE(partidas,0) FROM arcade_stats WHERE usuario_id=:u"),
        {"u": usuario_id}).fetchone()
    xp, racha, n_part = (st[0], st[1], st[2]) if st else (0, 0, 0)
    nivel = next((n for n in reversed(NIVELES) if xp >= n["puntos_min"]), NIVELES[0])

    # ── Garaje: piezas desbloqueadas (mismo criterio que el router garaje) ──
    prog = {"xp": xp, "racha": racha, "partidas": n_part}
    items = db.execute(text(
        "SELECT nombre, icono, tipo, requisito_tipo, requisito_valor, rareza FROM garaje_items ORDER BY requisito_tipo, requisito_valor")).fetchall()
    garaje = [{"nombre": it[0], "icono": it[1], "tipo": it[2], "rareza": it[5] or "comun",
               "desbloqueado": prog.get(it[3], 0) >= it[4]} for it in items]
    garaje_desbloqueados = sum(1 for g in garaje if g["desbloqueado"])

    return {"usuario": {"id": u[0], "nombre": u[1], "email": u[2], "tipo_uso": u[3], "grupo": (u[5] if len(u) > 5 else "intervencion")},
            "evaluaciones": evaluaciones, "partidas_arcade": partidas,
            "insignias": insignias,
            "insignias_conseguidas": len(ganadas_ids),
            "insignias_total": len(INSIGNIAS),
            "nivel": {"numero": nivel["nivel"], "nombre": nivel["nombre"], "xp": xp},
            "garaje": garaje,
            "garaje_desbloqueados": garaje_desbloqueados,
            "garaje_total": len(garaje)}


@router.get("/comparacion-grupos", summary="Compara grupo intervencion vs control (cuasi-experimental)")
def comparacion_grupos(db: Session = Depends(get_db)):
    """Nucleo del analisis cuasi-experimental: compara la mejora del grupo que
    uso la app (intervencion) contra el que solo rindio pretest y postest
    (control). Permite atribuir la mejora a la plataforma y descartar el efecto
    de practica."""
    filas = db.execute(text("""
        SELECT COALESCE(u.grupo,'intervencion') AS grupo,
               pre.score AS pretest, post.score AS postest
        FROM usuarios_auth u
        JOIN piloto_evaluaciones pre  ON pre.usuario_id=u.id  AND pre.fase='pretest'
        JOIN piloto_evaluaciones post ON post.usuario_id=u.id AND post.fase='postest'
        WHERE u.rol='participante'
    """)).fetchall()

    grupos = {"intervencion": [], "control": []}
    for g, pre, post in filas:
        key = g if g in grupos else "intervencion"
        grupos[key].append({"pretest": pre, "postest": post,
                            "mejora": post - pre,
                            "mejora_pct": round((post-pre)/pre*100,1) if pre else 0})

    def resumen(lista):
        if not lista:
            return {"n": 0, "pretest_prom": 0, "postest_prom": 0, "mejora_prom": 0, "mejora_pct_prom": 0}
        n = len(lista)
        return {"n": n,
                "pretest_prom": round(sum(x["pretest"] for x in lista)/n, 2),
                "postest_prom": round(sum(x["postest"] for x in lista)/n, 2),
                "mejora_prom": round(sum(x["mejora"] for x in lista)/n, 2),
                "mejora_pct_prom": round(sum(x["mejora_pct"] for x in lista)/n, 1)}

    r_int = resumen(grupos["intervencion"])
    r_ctrl = resumen(grupos["control"])

    # t-test de grupos independientes sobre la mejora (si hay scipy)
    ttest = None
    try:
        from scipy import stats as _st
        a = [x["mejora"] for x in grupos["intervencion"]]
        b = [x["mejora"] for x in grupos["control"]]
        if len(a) >= 2 and len(b) >= 2:
            t, p = _st.ttest_ind(a, b, equal_var=False)
            import statistics as _stt
            sd = ((_stt.pstdev(a)**2 + _stt.pstdev(b)**2)/2) ** 0.5
            d = (sum(a)/len(a) - sum(b)/len(b))/sd if sd else 0
            # Convertir tipos numpy a nativos de Python (FastAPI no serializa numpy)
            ttest = {"t": round(float(t),3), "p": round(float(p),5),
                     "significativo": bool(float(p) < 0.05), "cohen_d": round(float(d),3)}
    except Exception:
        pass

    return {"intervencion": r_int, "control": r_ctrl, "ttest": ttest,
            "conclusion": ("El grupo con app mejoro mas que el control"
                           if r_int["mejora_prom"] > r_ctrl["mejora_prom"] else "Sin diferencia clara")}


@router.post("/asignar-grupo", summary="Asigna grupo (intervencion/control) a un participante")
def asignar_grupo(datos: dict = Body(...), admin=Depends(admin_requerido), db: Session = Depends(get_db)):
    """El investigador marca quien es intervencion y quien control. NO lo elige
    el participante: lo asigna el investigador balanceando perfiles."""
    uid = datos.get("usuario_id")
    grupo = datos.get("grupo")
    if grupo not in ("intervencion", "control"):
        raise HTTPException(400, "grupo debe ser 'intervencion' o 'control'")
    db.execute(text("UPDATE usuarios_auth SET grupo=:g WHERE id=:u"), {"g": grupo, "u": uid})
    db.commit()
    return {"ok": True, "usuario_id": uid, "grupo": grupo}
