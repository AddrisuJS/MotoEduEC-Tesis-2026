"""
M10 — REVISION DE EVALUACIONES (pretest y postest)
Devuelve, pregunta por pregunta, lo que el participante respondio, cual era
la respuesta correcta y la explicacion.

REGLA METODOLOGICA IMPORTANTE:
  La revision del PRETEST solo se habilita cuando el participante ya rindio
  el POSTEST. Si se mostraran antes las respuestas correctas del pretest,
  el postest mediria memoria y no aprendizaje, y el experimento perderia
  validez. El investigador (rol='admin') si puede verlas en cualquier
  momento pasando ?admin_id=<su_id>.

Este router NO modifica nada: es de solo lectura.
Prefijo: /m10/revision
"""
import json
import random
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.database import get_db

router = APIRouter(prefix="/m10/revision", tags=["M10 Revision"])

LETRAS = ["A", "B", "C", "D", "E", "F"]


# ───────────── normalizadores (toleran distintos esquemas) ─────────────
def _as_obj(v: Any) -> Any:
    """Si viene como texto JSON, lo convierte a objeto."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:
            return v
    return v


def _norm_pregunta(row: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae enunciado, opciones, respuesta correcta y explicacion.

    OJO con el esquema de preguntas_viales: NO hay columna 'opciones' ni
    'opcion_a'. La respuesta correcta vive en la columna respuesta_correcta
    y los distractores en opcion_b / opcion_c / opcion_d. Por eso las
    opciones completas son respuesta_correcta + los distractores.
    Se barajan con una semilla fija por pregunta para que el orden sea
    estable entre recargas y no delate cual es la correcta por su posicion.
    """
    d = dict(row)

    enunciado = next((d[k] for k in ("pregunta", "enunciado", "texto", "titulo")
                      if d.get(k)), "")

    correcta = next((d[k] for k in ("respuesta_correcta", "correcta",
                                    "opcion_correcta")
                     if d.get(k) is not None), None)

    # 1) por si algun dia existiera una columna 'opciones' con todo dentro
    opciones = _as_obj(d.get("opciones"))
    if isinstance(opciones, dict):
        opciones = [opciones[k] for k in sorted(opciones.keys())]
    if not isinstance(opciones, list) or not opciones:
        # 2) esquema real: correcta + distractores
        opciones = [d.get(f"opcion_{l}") for l in ("a", "b", "c", "d", "e")]
        opciones = [o for o in opciones if o]
        if correcta is not None:
            opciones.append(correcta)
        random.Random(d.get("id") or 0).shuffle(opciones)

    opciones = [str(o) for o in opciones]
    # garantia: la correcta siempre debe estar entre las opciones
    if correcta is not None and str(correcta) not in opciones:
        opciones.append(str(correcta))

    explicacion = next((d[k] for k in ("explicacion", "retroalimentacion",
                                       "justificacion", "feedback")
                        if d.get(k)), None)

    return {
        "pregunta_id": d.get("id"),
        "enunciado": enunciado,
        "opciones": opciones,
        "correcta_raw": correcta,
        "explicacion": explicacion,
        "categoria": d.get("categoria"),
    }


def _texto_opcion(valor: Any, opciones: List[str]) -> Optional[str]:
    """Convierte una respuesta (indice, letra o texto) al texto de la opcion."""
    if valor is None:
        return None
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int) and 0 <= valor < len(opciones):
        return opciones[valor]
    s = str(valor).strip()
    if s in opciones:
        return s
    if len(s) == 1 and s.upper() in LETRAS:
        i = LETRAS.index(s.upper())
        if i < len(opciones):
            return opciones[i]
    if s.isdigit():
        i = int(s)
        if 0 <= i < len(opciones):
            return opciones[i]
        if 1 <= i <= len(opciones):          # por si fuera base 1
            return opciones[i - 1]
    return s


def _respuestas_de_detalles(detalles: Any) -> Dict[int, Dict[str, Any]]:
    """Normaliza el JSONB 'detalles' a  {pregunta_id: {respuesta, correcta}}.
    Soporta lista de objetos o diccionario plano."""
    detalles = _as_obj(detalles)
    out: Dict[int, Dict[str, Any]] = {}
    if isinstance(detalles, list):
        for item in detalles:
            if not isinstance(item, dict):
                continue
            pid = item.get("pregunta_id", item.get("id", item.get("pid")))
            if pid is None:
                continue
            resp = next((item[k] for k in ("respuesta", "seleccion", "elegida",
                                           "opcion", "respuesta_usuario", "valor")
                         if k in item), None)
            ok = next((item[k] for k in ("correcta", "acierto", "es_correcta", "ok")
                       if k in item), None)
            out[int(pid)] = {"respuesta": resp, "correcta": ok}
    elif isinstance(detalles, dict):
        for k, v in detalles.items():
            try:
                pid = int(k)
            except (TypeError, ValueError):
                continue
            if isinstance(v, dict):
                resp = next((v[x] for x in ("respuesta", "seleccion", "opcion")
                             if x in v), None)
                ok = next((v[x] for x in ("correcta", "acierto") if x in v), None)
            else:
                resp, ok = v, None
            out[pid] = {"respuesta": resp, "correcta": ok}
    return out


# ──────────────────────────── endpoint ─────────────────────────────────
@router.get("/{usuario_id}", summary="Revision de pretest y postest de un participante")
def revision(usuario_id: int, admin_id: Optional[int] = None,
             db: Session = Depends(get_db)):
    usuario = db.execute(
        text("SELECT id, nombre, grupo, rol FROM usuarios_auth WHERE id = :i"),
        {"i": usuario_id},
    ).mappings().first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    es_admin = False
    if admin_id:
        a = db.execute(text("SELECT rol FROM usuarios_auth WHERE id = :i"),
                       {"i": admin_id}).mappings().first()
        es_admin = bool(a and a["rol"] == "admin")

    evals = {e["fase"]: dict(e) for e in db.execute(
        text("""SELECT fase, score, total, detalles, creado_en
                  FROM piloto_evaluaciones WHERE usuario_id = :i"""),
        {"i": usuario_id},
    ).mappings().all()}

    preguntas = [_norm_pregunta(r) for r in db.execute(text("""
        SELECT pp.orden, pv.*, c.nombre AS categoria
          FROM piloto_preguntas pp
          JOIN preguntas_viales pv ON pv.id = pp.pregunta_id
          LEFT JOIN categorias_pregunta c ON c.id = pv.categoria_id
         ORDER BY pp.orden
    """)).mappings().all()]

    postest_hecho = "postest" in evals

    def armar(fase: str) -> Dict[str, Any]:
        ev = evals.get(fase)
        if not ev:
            return {"rendido": False, "revision_disponible": False,
                    "motivo": "Aun no has rendido esta evaluacion", "preguntas": []}

        base = {
            "rendido": True,
            "score": ev["score"],
            "total": ev["total"],
            "porcentaje": round(100.0 * ev["score"] / ev["total"], 1) if ev["total"] else None,
            "fecha": ev["creado_en"],
        }

        # Candado anti-contaminacion del pretest
        if fase == "pretest" and not postest_hecho and not es_admin:
            base.update({"revision_disponible": False, "preguntas": [],
                         "motivo": "Tus respuestas de la evaluacion inicial se muestran "
                                   "cuando completes la evaluacion final."})
            return base

        dadas = _respuestas_de_detalles(ev["detalles"])
        detalle = []
        for i, p in enumerate(preguntas, start=1):
            r = dadas.get(p["pregunta_id"], {})
            texto_resp = _texto_opcion(r.get("respuesta"), p["opciones"])
            texto_corr = _texto_opcion(p["correcta_raw"], p["opciones"])
            acierto = r.get("correcta")
            if acierto is None and texto_resp is not None and texto_corr is not None:
                acierto = str(texto_resp).strip().lower() == str(texto_corr).strip().lower()
            detalle.append({
                "orden": i,
                "pregunta_id": p["pregunta_id"],
                "categoria": p["categoria"],
                "enunciado": p["enunciado"],
                "opciones": p["opciones"],
                "tu_respuesta": texto_resp,
                "respuesta_correcta": texto_corr,
                "acierto": bool(acierto) if acierto is not None else None,
                "explicacion": p["explicacion"],
            })
        base.update({"revision_disponible": True, "motivo": None, "preguntas": detalle})
        return base

    pre, pos = armar("pretest"), armar("postest")

    # ── Metricas de ganancia ────────────────────────────────────────────
    # La ganancia RELATIVA (post-pre)/pre infla los resultados cuando el
    # pretest es bajo: 6->12 sobre 15 da "+100%", que se lee como si hubiera
    # acertado todo. Por eso el titular son los PUNTOS PORCENTUALES y se
    # reporta ademas la g de Hake, estandar en investigacion educativa:
    #     g = (post - pre) / (total - pre)
    # mide cuanto aprendio de lo que le faltaba por aprender.
    #     g < 0.30 baja | 0.30-0.70 media | > 0.70 alta
    ganancia = ganancia_pp = hake_g = hake_nivel = mejora = None
    if pre.get("rendido") and pos.get("rendido"):
        total = pos["total"] or 0
        ganancia = pos["score"] - pre["score"]
        if total:
            ganancia_pp = round(100.0 * ganancia / total, 1)
        if total > pre["score"]:
            hake_g = round(ganancia / (total - pre["score"]), 2)
            hake_nivel = ("alta" if hake_g > 0.70 else
                          "media" if hake_g >= 0.30 else "baja")
        elif ganancia == 0:
            hake_g, hake_nivel = 1.0, "alta"   # ya tenia el maximo
        if pre["score"]:
            mejora = round(100.0 * ganancia / pre["score"], 1)

    return {
        "usuario_id": usuario["id"],
        "nombre": usuario["nombre"],
        "grupo": usuario["grupo"],
        "pretest": pre,
        "postest": pos,
        "ganancia_bruta": ganancia,     # aciertos ganados
        "ganancia_pp": ganancia_pp,     # puntos porcentuales (titular)
        "hake_g": hake_g,               # ganancia normalizada
        "hake_nivel": hake_nivel,       # baja | media | alta
        "mejora_pct": mejora,           # relativa (solo referencia)
    }
