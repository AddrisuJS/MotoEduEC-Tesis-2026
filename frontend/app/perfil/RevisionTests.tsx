"use client"

/**
 * RevisionTests — "Mis evaluaciones".
 * Tres pestañas: Inicial, Final y Comparar (pregunta por pregunta).
 * Usa el hook useAuth existente, así que respeta la sesión real.
 *
 * La revisión del pretest se libera solo cuando el participante ya rindió
 * el postest (candado aplicado en el backend, no aquí).
 */

import { useEffect, useState } from "react"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

type Pregunta = {
  orden: number; pregunta_id: number; categoria: string | null; enunciado: string
  opciones: string[]; tu_respuesta: string | null
  respuesta_correcta: string | null; acierto: boolean | null; explicacion: string | null
}
type Fase = {
  rendido: boolean; score?: number; total?: number; porcentaje?: number | null
  fecha?: string; revision_disponible: boolean; motivo: string | null; preguntas: Pregunta[]
}
type Data = {
  nombre: string; grupo: string; pretest: Fase; postest: Fase
  ganancia_bruta: number | null; ganancia_pp: number | null
  hake_g: number | null; hake_nivel: string | null; mejora_pct: number | null
}

const card: any = {
  background: "rgba(255,255,255,0.05)", backdropFilter: "blur(14px)",
  border: "1px solid #334155", borderRadius: 16, padding: "1.1rem", marginBottom: "1rem",
}

export default function RevisionTests({ usuarioId }: { usuarioId?: number }) {
  const { usuario, listo } = useAuth(false)
  const [data, setData] = useState<Data | null>(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<"pretest" | "postest" | "comparar">("postest")

  const uid = usuarioId ?? usuario?.id

  useEffect(() => {
    if (!listo) return
    if (!uid) { setCargando(false); return }
    setCargando(true)
    fetch(`${API}/m10/revision/${uid}`)
      .then(r => { if (!r.ok) throw new Error(`Error ${r.status}`); return r.json() })
      .then((d: Data) => {
        setData(d)
        setTab(d.postest?.revision_disponible ? "postest" : "pretest")
      })
      .catch(e => setError(e.message))
      .finally(() => setCargando(false))
  }, [uid, listo])

  if (cargando) return <div style={{ ...card, color: "#94a3b8" }}>Cargando tus evaluaciones…</div>
  if (!uid) return <div style={{ ...card, color: "#94a3b8" }}>Inicia sesión para ver tus evaluaciones.</div>
  if (error) return <div style={{ ...card, color: "#f87171" }}>No se pudieron cargar ({error})</div>
  if (!data) return null

  if (!data.pretest.rendido && !data.postest.rendido)
    return (
      <div style={{ ...card, textAlign: "center", color: "#94a3b8" }}>
        <div style={{ fontSize: "2rem", marginBottom: 6 }}>📋</div>
        Aún no has rendido ninguna evaluación.
      </div>
    )

  const puedeComparar = data.pretest.revision_disponible && data.postest.revision_disponible

  // ── Comparación pregunta por pregunta ──
  const comparacion = puedeComparar
    ? data.postest.preguntas.map(post => {
        const pre = data.pretest.preguntas.find(p => p.pregunta_id === post.pregunta_id)
        const a = pre?.acierto, b = post.acierto
        const veredicto =
          !a && b ? { txt: "Mejoró", ico: "📈", col: "#4ade80" } :
          a && b ? { txt: "Mantuvo", ico: "✅", col: "#60a5fa" } :
          a && !b ? { txt: "Retrocedió", ico: "📉", col: "#f87171" } :
                    { txt: "Sigue fallando", ico: "❌", col: "#94a3b8" }
        return { post, pre, veredicto }
      })
    : []

  const conteo = {
    mejoro: comparacion.filter(c => c.veredicto.txt === "Mejoró").length,
    mantuvo: comparacion.filter(c => c.veredicto.txt === "Mantuvo").length,
    retrocedio: comparacion.filter(c => c.veredicto.txt === "Retrocedió").length,
    sigue: comparacion.filter(c => c.veredicto.txt === "Sigue fallando").length,
  }

  const tabBtn = (activo: boolean, dis = false): any => ({
    flex: 1, padding: "0.6rem 0.4rem", borderRadius: 12, cursor: dis ? "not-allowed" : "pointer",
    fontSize: "0.82rem", fontWeight: 700, border: "1px solid",
    borderColor: activo ? "rgba(59,130,246,0.6)" : "#2a3852",
    background: activo ? "rgba(59,130,246,0.22)" : "rgba(30,41,59,0.7)",
    color: dis ? "#64748b" : activo ? "#fff" : "#cbd5e1",
    opacity: dis ? 0.55 : 1,
  })

  const ListaPreguntas = ({ fase }: { fase: Fase }) => {
    if (!fase.rendido)
      return <div style={{ ...card, color: "#94a3b8" }}>Aún no has rendido esta evaluación.</div>
    if (!fase.revision_disponible)
      return (
        <div style={{ ...card, color: "#94a3b8", lineHeight: 1.5 }}>
          🔒 {fase.motivo}
          <div style={{ marginTop: 8, color: "#e2e8f0" }}>
            Tu puntaje: <b>{fase.score}/{fase.total}</b> ({fase.porcentaje}%)
          </div>
        </div>
      )
    return (
      <div style={{ display: "grid", gap: "0.7rem" }}>
        {fase.preguntas.map(p => (
          <div key={p.orden} style={{
            background: "rgba(15,23,42,0.85)", borderRadius: 12, padding: "0.85rem",
            borderLeft: `4px solid ${p.acierto ? "#22c55e" : "#ef4444"}`,
          }}>
            <div style={{ color: "#64748b", fontSize: "0.7rem", marginBottom: 4 }}>
              {p.orden}. {p.categoria || "General"}
            </div>
            <div style={{ color: "#e2e8f0", fontSize: "0.9rem", marginBottom: 8, lineHeight: 1.4 }}>
              {p.enunciado}
            </div>
            <div style={{ fontSize: "0.83rem", display: "grid", gap: 4 }}>
              <div style={{ color: p.acierto ? "#4ade80" : "#f87171" }}>
                {p.acierto ? "✅" : "❌"} Tu respuesta: {p.tu_respuesta ?? "sin responder"}
              </div>
              {!p.acierto && <div style={{ color: "#4ade80" }}>✔️ Correcta: {p.respuesta_correcta}</div>}
            </div>
            {p.explicacion && (
              <div style={{
                marginTop: 8, color: "#94a3b8", fontSize: "0.79rem",
                borderTop: "1px solid #1e293b", paddingTop: 6, lineHeight: 1.45,
              }}>💡 {p.explicacion}</div>
            )}
          </div>
        ))}
      </div>
    )
  }

  return (
    <section>
      {/* Resumen superior */}
      <div style={{ ...card, display: "flex", gap: "0.8rem", flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ flex: "1 1 90px", textAlign: "center" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.68rem" }}>INICIAL</div>
          <div style={{ color: "#e2e8f0", fontSize: "1.5rem", fontWeight: 800 }}>
            {data.pretest.rendido ? `${data.pretest.score}/${data.pretest.total}` : "—"}
          </div>
        </div>
        <div style={{ color: "#64748b", fontSize: "1.3rem" }}>→</div>
        <div style={{ flex: "1 1 90px", textAlign: "center" }}>
          <div style={{ color: "#94a3b8", fontSize: "0.68rem" }}>FINAL</div>
          <div style={{ color: "#4ade80", fontSize: "1.5rem", fontWeight: 800 }}>
            {data.postest.rendido ? `${data.postest.score}/${data.postest.total}` : "—"}
          </div>
        </div>
        {data.ganancia_pp !== null && (
          <div style={{ flex: "1 1 90px", textAlign: "center" }}>
            <div style={{ color: "#94a3b8", fontSize: "0.68rem" }}>GANANCIA</div>
            <div style={{ color: "#facc15", fontSize: "1.5rem", fontWeight: 800 }}>
              {data.ganancia_pp > 0 ? "+" : ""}{data.ganancia_pp} pp
            </div>
          </div>
        )}
      </div>

      {/* Detalle de la ganancia — metricas para el analisis */}
      {data.ganancia_pp !== null && (
        <div style={{ ...card, display: "flex", gap: "0.7rem", flexWrap: "wrap", fontSize: "0.78rem" }}>
          <div style={{ flex: "1 1 130px" }}>
            <div style={{ color: "#94a3b8" }}>Aciertos ganados</div>
            <div style={{ color: "#e2e8f0", fontWeight: 800, fontSize: "1rem" }}>
              {data.ganancia_bruta! > 0 ? "+" : ""}{data.ganancia_bruta} de {data.postest.total}
            </div>
          </div>
          <div style={{ flex: "1 1 130px" }}>
            <div style={{ color: "#94a3b8" }}>Puntaje</div>
            <div style={{ color: "#e2e8f0", fontWeight: 800, fontSize: "1rem" }}>
              {data.pretest.porcentaje}% → {data.postest.porcentaje}%
            </div>
          </div>
          {data.hake_g !== null && (
            <div style={{ flex: "1 1 130px" }}>
              <div style={{ color: "#94a3b8" }}>Ganancia normalizada (g)</div>
              <div style={{ color: "#4ade80", fontWeight: 800, fontSize: "1rem" }}>
                {data.hake_g} <span style={{ color: "#94a3b8", fontWeight: 600, fontSize: "0.78rem" }}>({data.hake_nivel})</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Pestañas */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        <button style={tabBtn(tab === "pretest")} onClick={() => setTab("pretest")}>📋 Inicial</button>
        <button style={tabBtn(tab === "postest")} onClick={() => setTab("postest")}>🏁 Final</button>
        <button style={tabBtn(tab === "comparar", !puedeComparar)}
          onClick={() => puedeComparar && setTab("comparar")}
          title={puedeComparar ? "" : "Disponible cuando completes ambas evaluaciones"}>
          ⚖️ Comparar
        </button>
      </div>

      {tab === "pretest" && <ListaPreguntas fase={data.pretest} />}
      {tab === "postest" && <ListaPreguntas fase={data.postest} />}

      {tab === "comparar" && (
        <div>
          <div style={{ ...card, display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {[["📈 Mejoraste", conteo.mejoro, "#4ade80"],
              ["✅ Mantuviste", conteo.mantuvo, "#60a5fa"],
              ["📉 Retrocediste", conteo.retrocedio, "#f87171"],
              ["❌ Sigue fallando", conteo.sigue, "#94a3b8"]].map(([k, v, c]: any) => (
              <div key={k} style={{ flex: "1 1 80px", textAlign: "center" }}>
                <div style={{ color: c, fontSize: "1.4rem", fontWeight: 800 }}>{v}</div>
                <div style={{ color: "#94a3b8", fontSize: "0.68rem" }}>{k}</div>
              </div>
            ))}
          </div>

          <div style={{ display: "grid", gap: "0.7rem" }}>
            {comparacion.map(({ post, pre, veredicto }) => (
              <div key={post.pregunta_id} style={{
                background: "rgba(15,23,42,0.85)", borderRadius: 12, padding: "0.85rem",
                borderLeft: `4px solid ${veredicto.col}`,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 4 }}>
                  <span style={{ color: "#64748b", fontSize: "0.7rem" }}>
                    {post.orden}. {post.categoria || "General"}
                  </span>
                  <span style={{ color: veredicto.col, fontSize: "0.72rem", fontWeight: 800, whiteSpace: "nowrap" }}>
                    {veredicto.ico} {veredicto.txt}
                  </span>
                </div>
                <div style={{ color: "#e2e8f0", fontSize: "0.88rem", marginBottom: 8, lineHeight: 1.4 }}>
                  {post.enunciado}
                </div>
                <div style={{ display: "grid", gap: 5, fontSize: "0.8rem" }}>
                  <div style={{ color: pre?.acierto ? "#4ade80" : "#f87171" }}>
                    <b style={{ color: "#94a3b8" }}>Inicial:</b> {pre?.tu_respuesta ?? "—"} {pre?.acierto ? "✅" : "❌"}
                  </div>
                  <div style={{ color: post.acierto ? "#4ade80" : "#f87171" }}>
                    <b style={{ color: "#94a3b8" }}>Final:</b> {post.tu_respuesta ?? "—"} {post.acierto ? "✅" : "❌"}
                  </div>
                  {!post.acierto && (
                    <div style={{ color: "#4ade80" }}>✔️ Correcta: {post.respuesta_correcta}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
