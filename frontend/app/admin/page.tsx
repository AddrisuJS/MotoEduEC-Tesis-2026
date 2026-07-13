"use client"
import { useState, useEffect } from "react"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

export default function AdminPage() {
  const { usuario, listo, authHeaders } = useAuth()
  const [resumen, setResumen] = useState<any>(null)
  const [parts, setParts] = useState<any[]>([])
  const [detalle, setDetalle] = useState<any>(null)
  const [error, setError] = useState("")

  const cargar = async () => {
    try {
      const [r1, r2] = await Promise.all([
        fetch(`${API}/admin/resumen`, { headers: authHeaders() }),
        fetch(`${API}/admin/participantes`, { headers: authHeaders() }),
      ])
      if (r1.status === 403) { setError("Acceso solo para el investigador"); return }
      setResumen(await r1.json())
      setParts((await r2.json()).participantes || [])
    } catch { setError("No se pudo cargar el panel") }
  }

  useEffect(() => { if (usuario) cargar() }, [usuario])

  const verDetalle = async (id: number) => {
    if (detalle?.usuario?.id === id) { setDetalle(null); return }
    const r = await fetch(`${API}/admin/participante/${id}`, { headers: authHeaders() })
    setDetalle(await r.json())
  }

  if (!listo || !usuario) return null

  const fondo: any = { minHeight: "100vh", background: "linear-gradient(135deg,#0f172a,#1e293b 60%,#172554)", padding: "2rem clamp(0.5rem,3vw,2rem)" }
  const card: any = { background: "rgba(30,41,59,0.85)", border: "1px solid #334155", borderRadius: 16, padding: "1.1rem" }

  if (error) return (
    <div style={fondo}><div style={{ ...card, maxWidth: 480, margin: "3rem auto", textAlign: "center" }}>
      <div style={{ fontSize: "2.4rem" }}>🚫</div>
      <p style={{ color: "#fca5a5" }}>{error}</p>
    </div></div>
  )

  const estadoBadge = (e: string) => {
    const m: any = {
      completado: { t: "✅ Completado", c: "#4ade80" },
      en_intervencion: { t: "📚 En intervención", c: "#facc15" },
      sin_pretest: { t: "⏳ Sin pretest", c: "#94a3b8" },
    }
    const b = m[e] || m.sin_pretest
    return <span style={{ color: b.c, fontSize: "0.75rem", fontWeight: 700 }}>{b.t}</span>
  }

  const kpi = (label: string, valor: any, color = "#f1f5f9") => (
    <div style={{ ...card, textAlign: "center", minWidth: 130, flex: 1 }}>
      <div style={{ color, fontSize: "1.5rem", fontWeight: 800 }}>{valor ?? "—"}</div>
      <div style={{ color: "#94a3b8", fontSize: "0.7rem", marginTop: 2 }}>{label}</div>
    </div>
  )

  return (
    <div style={fondo}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <h1 style={{ color: "#f1f5f9", fontSize: "clamp(1.2rem,4vw,1.6rem)", fontWeight: 800 }}>
          👨‍💼 Panel del Investigador
          <button onClick={cargar} style={{ float: "right", background: "#0f172a", border: "1px solid #3b82f6", color: "#93c5fd", borderRadius: 10, padding: "0.4rem 0.9rem", fontSize: "0.8rem", cursor: "pointer" }}>🔄 Actualizar</button>
        </h1>

        {resumen && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.7rem", margin: "1rem 0" }}>
            {kpi("REGISTRADOS", resumen.registrados)}
            {kpi("PRETESTS", resumen.pretests, "#60a5fa")}
            {kpi("EN INTERVENCIÓN", resumen.en_intervencion, "#facc15")}
            {kpi("COMPLETOS", resumen.completos, "#4ade80")}
            {kpi("MEJORA PROMEDIO", resumen.mejora_promedio_pct != null ? `${resumen.mejora_promedio_pct}%` : "—", resumen.mejora_promedio_pct >= 20 ? "#4ade80" : "#facc15")}
            {kpi("PARTIDAS ARCADE", resumen.partidas_arcade, "#fb923c")}
          </div>
        )}

        <div style={{ ...card, overflowX: "auto", padding: "0.5rem" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem", minWidth: 820 }}>
            <thead>
              <tr style={{ color: "#94a3b8", textAlign: "left" }}>
                {["#", "Participante", "Estado", "Pretest", "Postest", "Mejora", "XP", "🔥", "Partidas", "Último login", ""].map(h =>
                  <th key={h} style={{ padding: "0.6rem 0.5rem", borderBottom: "1px solid #334155", whiteSpace: "nowrap" }}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {parts.map(p => (
                <>
                  <tr key={p.id} style={{ color: "#e2e8f0" }}>
                    <td style={{ padding: "0.55rem 0.5rem", color: "#64748b" }}>{p.id}</td>
                    <td style={{ padding: "0.55rem 0.5rem" }}>
                      <div style={{ fontWeight: 600 }}>{p.nombre}</div>
                      <div style={{ color: "#64748b", fontSize: "0.72rem" }}>{p.tipo_uso}</div>
                    </td>
                    <td style={{ padding: "0.55rem 0.5rem" }}>{estadoBadge(p.estado)}</td>
                    <td style={{ padding: "0.55rem 0.5rem" }}>{p.pretest != null ? `${p.pretest}/15` : "—"}<div style={{ color: "#64748b", fontSize: "0.68rem" }}>{p.fecha_pretest || ""}</div></td>
                    <td style={{ padding: "0.55rem 0.5rem" }}>{p.postest != null ? `${p.postest}/15` : "—"}<div style={{ color: "#64748b", fontSize: "0.68rem" }}>{p.fecha_postest || ""}</div></td>
                    <td style={{ padding: "0.55rem 0.5rem", fontWeight: 800, color: p.mejora_pct == null ? "#64748b" : p.mejora_pct >= 20 ? "#4ade80" : p.mejora_pct > 0 ? "#facc15" : "#f87171" }}>
                      {p.mejora_pct != null ? `${p.mejora_pct > 0 ? "+" : ""}${p.mejora_pct}%` : "—"}
                    </td>
                    <td style={{ padding: "0.55rem 0.5rem", color: "#facc15", fontWeight: 700 }}>{p.xp}</td>
                    <td style={{ padding: "0.55rem 0.5rem", color: "#fb923c" }}>{p.racha || ""}</td>
                    <td style={{ padding: "0.55rem 0.5rem" }}>{p.partidas}</td>
                    <td style={{ padding: "0.55rem 0.5rem", color: "#64748b", fontSize: "0.72rem" }}>{p.ultimo_login || "—"}</td>
                    <td style={{ padding: "0.55rem 0.5rem" }}>
                      <button onClick={() => verDetalle(p.id)} style={{ background: "#0f172a", border: "1px solid #334155", color: "#93c5fd", borderRadius: 8, padding: "0.3rem 0.6rem", fontSize: "0.72rem", cursor: "pointer" }}>
                        {detalle?.usuario?.id === p.id ? "Cerrar" : "Ver"}
                      </button>
                    </td>
                  </tr>
                  {detalle?.usuario?.id === p.id && (
                    <tr><td colSpan={11} style={{ padding: "0.8rem", background: "rgba(15,23,42,0.6)" }}>
                      {detalle.evaluaciones.map((ev: any, i: number) => (
                        <div key={i} style={{ marginBottom: "0.8rem" }}>
                          <div style={{ color: "#93c5fd", fontWeight: 700, fontSize: "0.8rem", marginBottom: "0.3rem" }}>
                            {ev.fase.toUpperCase()} — {ev.score}/{ev.total} — {ev.fecha}
                          </div>
                          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.3rem" }}>
                            {ev.respuestas.map((r: any, j: number) => (
                              <div key={j} style={{ fontSize: "0.72rem", color: r.correcta ? "#86efac" : "#fca5a5" }}>
                                {r.correcta ? "✅" : "❌"} {r.pregunta?.slice(0, 60)}...
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                      {detalle.evaluaciones.length === 0 && <span style={{ color: "#64748b", fontSize: "0.8rem" }}>Sin evaluaciones aún</span>}
                      {detalle.partidas_arcade.length > 0 && (
                        <div style={{ color: "#94a3b8", fontSize: "0.72rem", marginTop: "0.4rem" }}>
                          🕹️ Últimas partidas: {detalle.partidas_arcade.slice(0, 5).map((pa: any) => `${pa.modo} ${pa.aciertos}/${pa.total} (+${pa.puntos})`).join(" · ")}
                        </div>
                      )}
                    </td></tr>
                  )}
                </>
              ))}
              {parts.length === 0 && <tr><td colSpan={11} style={{ padding: "1rem", color: "#64748b", textAlign: "center" }}>Aún no hay participantes registrados</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
