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

  // ─── Export CSV para el análisis estadístico ───
  const exportarCSV = () => {
    const cab = ["id","nombre","email","tipo_uso","pretest","fecha_pretest","postest","fecha_postest","mejora_pct","xp","racha","partidas","estado"]
    const filas = parts.map(p => cab.map(c => `"${String(p[c] ?? "")}"`).join(","))
    const csv = [cab.join(","), ...filas].join("\n")
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" })
    const a = document.createElement("a")
    a.href = URL.createObjectURL(blob)
    a.download = `piloto_motoeduc_${new Date().toISOString().slice(0,10)}.csv`
    a.click()
  }

  if (!listo || !usuario) return null

  const card: any = { background: "rgba(30,41,59,0.9)", border: "1px solid #2a3852", borderRadius: 16, padding: "1.1rem" }

  if (error) return (
    <div style={{ padding: "3rem 1rem", display: "flex", justifyContent: "center" }}>
      <div style={{ ...card, maxWidth: 440, textAlign: "center" }}>
        <div style={{ fontSize: "2.4rem" }}>🚫</div><p style={{ color: "#fca5a5" }}>{error}</p>
      </div>
    </div>
  )

  const meta = 40
  const completos = resumen?.completos ?? 0
  const pct = Math.min(100, Math.round((completos / meta) * 100))
  const R = 52, CIRC = 2 * Math.PI * R

  const estadoBadge = (e: string) => {
    const m: any = { completado: ["✅ Completado", "#4ade80"], en_intervencion: ["📚 En intervención", "#facc15"], sin_pretest: ["⏳ Sin pretest", "#94a3b8"] }
    const [t, c] = m[e] || m.sin_pretest
    return <span style={{ color: c, fontSize: "0.74rem", fontWeight: 700, whiteSpace: "nowrap" }}>{t}</span>
  }

  const kpi = (label: string, valor: any, color = "#f1f5f9") => (
    <div style={{ ...card, textAlign: "center", minWidth: 118, flex: 1, padding: "0.8rem" }}>
      <div style={{ color, fontSize: "1.4rem", fontWeight: 800 }}>{valor ?? "—"}</div>
      <div style={{ color: "#94a3b8", fontSize: "0.66rem", marginTop: 2, letterSpacing: "0.04em" }}>{label}</div>
    </div>
  )

  const maxScore = 15
  const conPre = parts.filter(p => p.pretest != null)

  return (
    <div style={{ padding: "1.5rem clamp(0.5rem,3vw,1.5rem)", maxWidth: 1150, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.6rem", marginBottom: "1rem" }}>
        <h1 style={{ color: "#f1f5f9", fontSize: "clamp(1.2rem,4vw,1.55rem)", fontWeight: 800 }}>👨‍💼 Panel del Investigador</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={exportarCSV} style={{ background: "rgba(34,197,94,0.12)", border: "1px solid rgba(34,197,94,0.5)", color: "#86efac", borderRadius: 10, padding: "0.45rem 0.9rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 700 }}>
            📥 Exportar CSV
          </button>
          <button onClick={cargar} style={{ background: "rgba(59,130,246,0.12)", border: "1px solid rgba(59,130,246,0.5)", color: "#93c5fd", borderRadius: 10, padding: "0.45rem 0.9rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 700 }}>
            🔄 Actualizar
          </button>
        </div>
      </div>

      {/* Fila: donut + KPIs + barras */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.8rem", marginBottom: "0.9rem" }}>

        {/* Donut de progreso del piloto */}
        <div style={{ ...card, display: "flex", alignItems: "center", gap: "1rem" }}>
          <svg width="130" height="130" viewBox="0 0 130 130">
            <circle cx="65" cy="65" r={R} fill="none" stroke="#1e293b" strokeWidth="13" />
            <circle cx="65" cy="65" r={R} fill="none" stroke={pct >= 75 ? "#22c55e" : pct >= 40 ? "#facc15" : "#3b82f6"} strokeWidth="13"
              strokeDasharray={`${(pct / 100) * CIRC} ${CIRC}`} strokeLinecap="round" transform="rotate(-90 65 65)" />
            <text x="65" y="62" textAnchor="middle" fill="#f1f5f9" fontSize="22" fontWeight="800">{completos}</text>
            <text x="65" y="80" textAnchor="middle" fill="#94a3b8" fontSize="10">de {meta} meta</text>
          </svg>
          <div>
            <div style={{ color: "#f1f5f9", fontWeight: 800, fontSize: "0.95rem" }}>Piloto completado</div>
            <div style={{ color: "#94a3b8", fontSize: "0.78rem", marginTop: 4 }}>
              {resumen?.pretests ?? 0} pretests · {resumen?.en_intervencion ?? 0} en intervención
            </div>
            <div style={{ marginTop: 8, color: (resumen?.mejora_promedio_pct ?? 0) >= 20 ? "#4ade80" : "#facc15", fontWeight: 800, fontSize: "1.3rem" }}>
              {resumen?.mejora_promedio_pct != null ? `${resumen.mejora_promedio_pct > 0 ? "+" : ""}${resumen.mejora_promedio_pct}%` : "—"}
            </div>
            <div style={{ color: "#64748b", fontSize: "0.68rem" }}>mejora promedio (H1: ≥20%)</div>
          </div>
        </div>

        {/* KPIs */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", alignContent: "start" }}>
          {kpi("REGISTRADOS", resumen?.registrados)}
          {kpi("PROM. PRETEST", resumen?.promedio_pretest, "#60a5fa")}
          {kpi("PROM. POSTEST", resumen?.promedio_postest, "#4ade80")}
          {kpi("PARTIDAS ARCADE", resumen?.partidas_arcade, "#fb923c")}
        </div>
      </div>

      {/* Barras pre vs post por participante */}
      {conPre.length > 0 && (
        <div style={{ ...card, marginBottom: "0.9rem" }}>
          <div style={{ color: "#f1f5f9", fontWeight: 800, fontSize: "0.88rem", marginBottom: "0.7rem" }}>
            📊 Pretest <span style={{ color: "#60a5fa" }}>■</span> vs Postest <span style={{ color: "#4ade80" }}>■</span> (sobre 15)
          </div>
          <div style={{ display: "flex", gap: "0.9rem", alignItems: "flex-end", overflowX: "auto", paddingBottom: "0.4rem", minHeight: 120 }}>
            {conPre.map(p => (
              <div key={p.id} style={{ textAlign: "center", minWidth: 46 }}>
                <div style={{ display: "flex", gap: 3, alignItems: "flex-end", height: 90, justifyContent: "center" }}>
                  <div title={`Pretest ${p.pretest}`} style={{ width: 14, height: `${(p.pretest / maxScore) * 100}%`, background: "#60a5fa", borderRadius: "3px 3px 0 0" }} />
                  <div title={`Postest ${p.postest ?? "-"}`} style={{ width: 14, height: `${((p.postest ?? 0) / maxScore) * 100}%`, background: p.postest != null ? "#4ade80" : "#1e293b", borderRadius: "3px 3px 0 0" }} />
                </div>
                <div style={{ color: "#64748b", fontSize: "0.62rem", marginTop: 3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: 52 }}>
                  {p.nombre.split(" ")[0]}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tabla maestra */}
      <div style={{ ...card, overflowX: "auto", padding: "0.5rem" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", minWidth: 840 }}>
          <thead>
            <tr style={{ color: "#94a3b8", textAlign: "left" }}>
              {["#", "Participante", "Estado", "Pretest", "Postest", "Mejora", "XP", "🔥", "Partidas", "Último login", ""].map(h =>
                <th key={h} style={{ padding: "0.55rem 0.5rem", borderBottom: "1px solid #334155", whiteSpace: "nowrap" }}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {parts.map(p => (
              <>
                <tr key={p.id} style={{ color: "#e2e8f0" }}>
                  <td style={{ padding: "0.5rem", color: "#64748b" }}>{p.id}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <div style={{ fontWeight: 600 }}>{p.nombre}</div>
                    <div style={{ color: "#64748b", fontSize: "0.68rem" }}>{p.tipo_uso}</div>
                  </td>
                  <td style={{ padding: "0.5rem" }}>{estadoBadge(p.estado)}</td>
                  <td style={{ padding: "0.5rem" }}>{p.pretest != null ? `${p.pretest}/15` : "—"}<div style={{ color: "#64748b", fontSize: "0.64rem" }}>{p.fecha_pretest || ""}</div></td>
                  <td style={{ padding: "0.5rem" }}>{p.postest != null ? `${p.postest}/15` : "—"}<div style={{ color: "#64748b", fontSize: "0.64rem" }}>{p.fecha_postest || ""}</div></td>
                  <td style={{ padding: "0.5rem", fontWeight: 800, color: p.mejora_pct == null ? "#64748b" : p.mejora_pct >= 20 ? "#4ade80" : p.mejora_pct > 0 ? "#facc15" : "#f87171" }}>
                    {p.mejora_pct != null ? `${p.mejora_pct > 0 ? "+" : ""}${p.mejora_pct}%` : "—"}
                  </td>
                  <td style={{ padding: "0.5rem", color: "#facc15", fontWeight: 700 }}>{p.xp}</td>
                  <td style={{ padding: "0.5rem", color: "#fb923c" }}>{p.racha || ""}</td>
                  <td style={{ padding: "0.5rem" }}>{p.partidas}</td>
                  <td style={{ padding: "0.5rem", color: "#64748b", fontSize: "0.68rem" }}>{p.ultimo_login || "—"}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <button onClick={() => verDetalle(p.id)} style={{ background: "#0f172a", border: "1px solid #334155", color: "#93c5fd", borderRadius: 8, padding: "0.28rem 0.6rem", fontSize: "0.7rem", cursor: "pointer" }}>
                      {detalle?.usuario?.id === p.id ? "Cerrar" : "Ver"}
                    </button>
                  </td>
                </tr>
                {detalle?.usuario?.id === p.id && (
                  <tr><td colSpan={11} style={{ padding: "0.8rem", background: "rgba(11,18,32,0.6)" }}>
                    {detalle.evaluaciones.map((ev: any, i: number) => (
                      <div key={i} style={{ marginBottom: "0.7rem" }}>
                        <div style={{ color: "#93c5fd", fontWeight: 700, fontSize: "0.78rem", marginBottom: "0.3rem" }}>
                          {ev.fase.toUpperCase()} — {ev.score}/{ev.total} — {ev.fecha}
                        </div>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))", gap: "0.25rem" }}>
                          {ev.respuestas.map((r: any, j: number) => (
                            <div key={j} style={{ fontSize: "0.7rem", color: r.correcta ? "#86efac" : "#fca5a5" }}>
                              {r.correcta ? "✅" : "❌"} {r.pregunta?.slice(0, 58)}...
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                    {detalle.evaluaciones.length === 0 && <span style={{ color: "#64748b", fontSize: "0.78rem" }}>Sin evaluaciones aún</span>}
                    {detalle.partidas_arcade.length > 0 && (
                      <div style={{ color: "#94a3b8", fontSize: "0.7rem", marginTop: "0.3rem" }}>
                        🕹️ Últimas: {detalle.partidas_arcade.slice(0, 5).map((pa: any) => `${pa.modo} ${pa.aciertos}/${pa.total} (+${pa.puntos})`).join(" · ")}
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
  )
}
