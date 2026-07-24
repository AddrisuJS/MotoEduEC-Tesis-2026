"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

export default function AdminPage() {
  const { usuario, listo, authHeaders } = useAuth()
  const [resumen, setResumen] = useState<any>(null)
  const [parts, setParts] = useState<any[]>([])
  const [detalle, setDetalle] = useState<any>(null)
  const [compGrupos, setCompGrupos] = useState<any>(null)
  const [filtroGrupo, setFiltroGrupo] = useState<string>("todos")
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
      // La comparación de grupos se carga aparte: si falla, NO tumba el panel.
      try {
        const r3 = await fetch(`${API}/admin/comparacion-grupos`, { headers: authHeaders() })
        if (r3.ok) setCompGrupos(await r3.json())
      } catch {}
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


  // ─── Cruce pretest vs postest: qué aprendió, qué sigue fallando ───
  const cambiarGrupo = async (id: number, grupo: string) => {
    try {
      await fetch(`${API}/admin/asignar-grupo`, {
        method: "POST", headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ usuario_id: id, grupo }),
      })
      setParts(prev => prev.map((p: any) => p.id === id ? { ...p, grupo } : p))
      // recargar comparación
      const r = await fetch(`${API}/admin/comparacion-grupos`, { headers: authHeaders() })
      if (r.ok) setCompGrupos(await r.json())
    } catch {}
  }

  const analizarEvolucion = (evals: any[]) => {
    const pre = evals.find(e => e.fase === "pretest")
    const post = evals.find(e => e.fase === "postest")
    if (!pre || !post) return null
    const mapPre: any = {}, mapPost: any = {}
    pre.respuestas.forEach((r: any) => { mapPre[r.pregunta_id] = r })
    post.respuestas.forEach((r: any) => { mapPost[r.pregunta_id] = r })
    const aprendio: any[] = [], yaSabia: any[] = [], olvido: any[] = [], sigueFallando: any[] = []
    Object.keys(mapPost).forEach(pid => {
      const a = mapPre[pid], b = mapPost[pid]
      if (!a || !b) return
      const texto = b.pregunta || ""
      if (!a.correcta && b.correcta) aprendio.push(texto)
      else if (a.correcta && b.correcta) yaSabia.push(texto)
      else if (a.correcta && !b.correcta) olvido.push(texto)
      else sigueFallando.push(texto)
    })
    return { aprendio, yaSabia, olvido, sigueFallando }
  }

  // Tabla comparativa pregunta por pregunta (pretest vs postest)
  const comparativaPregunta = (evals: any[]) => {
    const pre = evals.find(e => e.fase === "pretest")
    const post = evals.find(e => e.fase === "postest")
    if (!pre || !post) return null
    const mapPre: any = {}, mapPost: any = {}
    pre.respuestas.forEach((r: any) => { mapPre[r.pregunta_id] = r })
    post.respuestas.forEach((r: any) => { mapPost[r.pregunta_id] = r })
    return Object.keys(mapPost).map(pid => {
      const a = mapPre[pid], b = mapPost[pid]
      let estado = "igual", color = "#64748b", icono = "—"
      if (a && b) {
        if (!a.correcta && b.correcta) { estado = "aprendió"; color = "#4ade80"; icono = "▲" }
        else if (a.correcta && b.correcta) { estado = "ya sabía"; color = "#60a5fa"; icono = "✓" }
        else if (a.correcta && !b.correcta) { estado = "retrocedió"; color = "#fbbf24"; icono = "⚠" }
        else { estado = "sigue mal"; color = "#f87171"; icono = "✕" }
      }
      return { pregunta: b?.pregunta || `Pregunta ${pid}`,
               pre_ok: a?.correcta, post_ok: b?.correcta, estado, color, icono }
    })
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
          <Link href="/admin/catalogo" style={{ background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.5)", color: "#c4b5fd", borderRadius: 10, padding: "0.45rem 0.9rem", fontSize: "0.8rem", fontWeight: 700, textDecoration: "none" }}>
            🏍️ Catálogo (motos/llantas)
          </Link>
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
          {kpi("PARTIDAS ARCADE", resumen?.partidas_arcade, "#FAC74C")}
        </div>
      </div>

      {/* ── Comparación cuasi-experimental: intervención vs control ── */}
      {compGrupos && compGrupos.control && compGrupos.control.n > 0 && (
        <div style={{ ...card, marginBottom: "0.9rem", border: "1px solid #7c3aed44" }}>
          <div style={{ color: "#f1f5f9", fontWeight: 800, fontSize: "0.88rem", marginBottom: "0.7rem" }}>
            🔬 Comparación cuasi-experimental
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: "0.9rem", alignItems: "center" }}>
            <div style={{ background: "rgba(34,197,94,0.1)", borderRadius: 10, padding: "0.8rem 1rem" }}>
              <div style={{ color: "#4ade80", fontSize: "0.72rem", fontWeight: 700, marginBottom: 4 }}>GRUPO INTERVENCIÓN (usó la app)</div>
              <div style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>+{compGrupos.intervencion.mejora_pct_prom}%</div>
              <div style={{ color: "#94a3b8", fontSize: "0.68rem" }}>n={compGrupos.intervencion.n} · {compGrupos.intervencion.pretest_prom} → {compGrupos.intervencion.postest_prom}</div>
            </div>
            <div style={{ background: "rgba(148,163,184,0.1)", borderRadius: 10, padding: "0.8rem 1rem" }}>
              <div style={{ color: "#94a3b8", fontSize: "0.72rem", fontWeight: 700, marginBottom: 4 }}>GRUPO CONTROL (sin app)</div>
              <div style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>+{compGrupos.control.mejora_pct_prom}%</div>
              <div style={{ color: "#94a3b8", fontSize: "0.68rem" }}>n={compGrupos.control.n} · {compGrupos.control.pretest_prom} → {compGrupos.control.postest_prom}</div>
            </div>
            {compGrupos.ttest && (
              <div style={{ textAlign: "center", padding: "0 0.5rem" }}>
                <div style={{ color: compGrupos.ttest.significativo ? "#4ade80" : "#fbbf24", fontSize: "0.8rem", fontWeight: 700 }}>
                  {compGrupos.ttest.significativo ? "✓ Significativo" : "○ No significativo"}
                </div>
                <div style={{ color: "#94a3b8", fontSize: "0.66rem", marginTop: 3 }}>
                  p = {compGrupos.ttest.p}<br/>d = {compGrupos.ttest.cohen_d}
                </div>
              </div>
            )}
          </div>
          <div style={{ color: "#c4b5fd", fontSize: "0.7rem", marginTop: "0.6rem", fontStyle: "italic" }}>
            {compGrupos.conclusion}
          </div>
          {/* Cuadros comparativos adicionales */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "0.6rem", marginTop: "0.8rem" }}>
            <div style={{ background: "rgba(15,23,42,0.5)", borderRadius: 8, padding: "0.6rem" }}>
              <div style={{ color: "#94a3b8", fontSize: "0.64rem", fontWeight: 700, marginBottom: 4 }}>PRETEST PROMEDIO</div>
              <div style={{ fontSize: "0.78rem" }}>
                <span style={{ color: "#4ade80" }}>Int {compGrupos.intervencion.pretest_prom}</span>
                <span style={{ color: "#64748b" }}> vs </span>
                <span style={{ color: "#cbd5e1" }}>Ctrl {compGrupos.control.pretest_prom}</span>
              </div>
              <div style={{ color: "#64748b", fontSize: "0.62rem", marginTop: 2 }}>
                {Math.abs(compGrupos.intervencion.pretest_prom - compGrupos.control.pretest_prom) <= 1.5 ? "✓ Grupos comparables" : "⚠ Diferencia inicial"}
              </div>
            </div>
            <div style={{ background: "rgba(15,23,42,0.5)", borderRadius: 8, padding: "0.6rem" }}>
              <div style={{ color: "#94a3b8", fontSize: "0.64rem", fontWeight: 700, marginBottom: 4 }}>POSTEST PROMEDIO</div>
              <div style={{ fontSize: "0.78rem" }}>
                <span style={{ color: "#4ade80" }}>Int {compGrupos.intervencion.postest_prom}</span>
                <span style={{ color: "#64748b" }}> vs </span>
                <span style={{ color: "#cbd5e1" }}>Ctrl {compGrupos.control.postest_prom}</span>
              </div>
              <div style={{ color: "#4ade80", fontSize: "0.62rem", marginTop: 2 }}>
                +{(compGrupos.intervencion.postest_prom - compGrupos.control.postest_prom).toFixed(1)} a favor de intervención
              </div>
            </div>
            <div style={{ background: "rgba(15,23,42,0.5)", borderRadius: 8, padding: "0.6rem" }}>
              <div style={{ color: "#94a3b8", fontSize: "0.64rem", fontWeight: 700, marginBottom: 4 }}>DIFERENCIA DE MEJORA</div>
              <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "#c4b5fd" }}>
                {(compGrupos.intervencion.mejora_pct_prom - compGrupos.control.mejora_pct_prom).toFixed(1)} pp
              </div>
              <div style={{ color: "#64748b", fontSize: "0.62rem" }}>puntos porcentuales más</div>
            </div>
            <div style={{ background: "rgba(15,23,42,0.5)", borderRadius: 8, padding: "0.6rem" }}>
              <div style={{ color: "#94a3b8", fontSize: "0.64rem", fontWeight: 700, marginBottom: 4 }}>TAMAÑO MUESTRAL</div>
              <div style={{ fontSize: "0.78rem" }}>
                <span style={{ color: "#4ade80" }}>{compGrupos.intervencion.n} int</span>
                <span style={{ color: "#64748b" }}> · </span>
                <span style={{ color: "#cbd5e1" }}>{compGrupos.control.n} ctrl</span>
              </div>
              {compGrupos.ttest && (
                <div style={{ color: compGrupos.ttest.significativo ? "#4ade80" : "#facc15", fontSize: "0.62rem", marginTop: 2 }}>
                  Cohen d = {compGrupos.ttest.cohen_d} ({Math.abs(compGrupos.ttest.cohen_d) >= 0.8 ? "efecto grande" : Math.abs(compGrupos.ttest.cohen_d) >= 0.5 ? "efecto medio" : "efecto pequeño"})
                </div>
              )}
            </div>
          </div>
        </div>
      )}

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

      {/* Filtro por grupo */}
      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.6rem", flexWrap: "wrap" }}>
        <span style={{ color: "#94a3b8", fontSize: "0.75rem", fontWeight: 600 }}>Filtrar:</span>
        {[["todos", "Todos"], ["intervencion", "🟢 Intervención"], ["control", "⚪ Control"]].map(([val, lbl]) => (
          <button key={val} onClick={() => setFiltroGrupo(val)}
            style={{ padding: "0.3rem 0.8rem", borderRadius: 8, fontSize: "0.72rem", fontWeight: 700, cursor: "pointer",
              border: filtroGrupo === val ? "1px solid #7c3aed" : "1px solid #334155",
              background: filtroGrupo === val ? "rgba(124,58,237,0.2)" : "transparent",
              color: filtroGrupo === val ? "#c4b5fd" : "#94a3b8" }}>
            {lbl} ({val === "todos" ? parts.length : parts.filter((p: any) => p.grupo === val).length})
          </button>
        ))}
        <span style={{ marginLeft: "auto", color: "#64748b", fontSize: "0.68rem", fontStyle: "italic" }}>
          Cambia el grupo de cada participante con el selector de la columna Grupo
        </span>
      </div>

      {/* Tabla maestra */}
      <div style={{ ...card, overflowX: "auto", padding: "0.5rem" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem", minWidth: 840 }}>
          <thead>
            <tr style={{ color: "#94a3b8", textAlign: "left" }}>
              {["#", "Participante", "Grupo", "Estado", "Pretest", "Postest", "Mejora", "XP", "🔥", "Partidas", ""].map(h =>
                <th key={h} style={{ padding: "0.55rem 0.5rem", borderBottom: "1px solid #334155", whiteSpace: "nowrap" }}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {parts.filter(p => filtroGrupo === "todos" || p.grupo === filtroGrupo).map(p => (
              <>
                <tr key={p.id} style={{ color: "#e2e8f0" }}>
                  <td style={{ padding: "0.5rem", color: "#64748b" }}>{p.id}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <div style={{ fontWeight: 600 }}>{p.nombre}</div>
                    <div style={{ color: "#64748b", fontSize: "0.68rem" }}>{p.tipo_uso}</div>
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    <select value={p.grupo || "intervencion"} onChange={e => cambiarGrupo(p.id, e.target.value)}
                      style={{ background: p.grupo === "control" ? "#334155" : "rgba(34,197,94,0.15)",
                        color: p.grupo === "control" ? "#cbd5e1" : "#4ade80", border: "none",
                        borderRadius: 6, padding: "0.2rem 0.4rem", fontSize: "0.68rem", fontWeight: 700, cursor: "pointer" }}>
                      <option value="intervencion">🟢 Intervención</option>
                      <option value="control">⚪ Control</option>
                    </select>
                  </td>
                  <td style={{ padding: "0.5rem" }}>{estadoBadge(p.estado)}</td>
                  <td style={{ padding: "0.5rem" }}>{p.pretest != null ? `${p.pretest}/15` : "—"}<div style={{ color: "#64748b", fontSize: "0.64rem" }}>{p.fecha_pretest || ""}</div></td>
                  <td style={{ padding: "0.5rem" }}>{p.postest != null ? `${p.postest}/15` : "—"}<div style={{ color: "#64748b", fontSize: "0.64rem" }}>{p.fecha_postest || ""}</div></td>
                  <td style={{ padding: "0.5rem", fontWeight: 800, color: p.mejora_pct == null ? "#64748b" : p.mejora_pct >= 20 ? "#4ade80" : p.mejora_pct > 0 ? "#facc15" : "#f87171" }}>
                    {p.mejora_pct != null ? `${p.mejora_pct > 0 ? "+" : ""}${p.mejora_pct}%` : "—"}
                  </td>
                  <td style={{ padding: "0.5rem", color: "#facc15", fontWeight: 700 }}>{p.xp}</td>
                  <td style={{ padding: "0.5rem", color: "#FAC74C" }}>{p.racha || ""}</td>
                  <td style={{ padding: "0.5rem" }}>{p.partidas}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <button onClick={() => verDetalle(p.id)} style={{ background: "#0f172a", border: "1px solid #334155", color: "#93c5fd", borderRadius: 8, padding: "0.28rem 0.6rem", fontSize: "0.7rem", cursor: "pointer" }}>
                      {detalle?.usuario?.id === p.id ? "Cerrar" : "Ver"}
                    </button>
                  </td>
                </tr>
                {detalle?.usuario?.id === p.id && (() => {
                  const evo = analizarEvolucion(detalle.evaluaciones)
                  const compPreg = comparativaPregunta(detalle.evaluaciones)
                  const chip = (txt: string, color: string, bg: string) => (
                    <div style={{ fontSize: "0.7rem", color, background: bg, borderRadius: 6, padding: "0.3rem 0.5rem", marginBottom: 3 }}>{txt}</div>
                  )
                  return (
                  <tr><td colSpan={11} style={{ padding: "0.9rem", background: "rgba(11,18,32,0.6)" }}>
                    {evo ? (
                      <>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.8rem", marginBottom: "0.8rem" }}>
                          <div>
                            <div style={{ color: "#4ade80", fontWeight: 700, fontSize: "0.74rem", marginBottom: "0.35rem" }}>▲ APRENDIÓ ({evo.aprendio.length}) — falló y luego acertó</div>
                            {evo.aprendio.map((t, k) => chip(t.slice(0, 60), "#bbf7d0", "rgba(34,197,94,0.12)"))}
                            {evo.aprendio.length === 0 && <span style={{ color: "#64748b", fontSize: "0.7rem" }}>—</span>}
                          </div>
                          <div>
                            <div style={{ color: "#f87171", fontWeight: 700, fontSize: "0.74rem", marginBottom: "0.35rem" }}>✕ SIGUE FALLANDO ({evo.sigueFallando.length})</div>
                            {evo.sigueFallando.map((t, k) => chip(t.slice(0, 60), "#fecaca", "rgba(239,68,68,0.12)"))}
                            {evo.sigueFallando.length === 0 && <span style={{ color: "#64748b", fontSize: "0.7rem" }}>Ninguna 🎉</span>}
                          </div>
                          <div>
                            <div style={{ color: "#93c5fd", fontWeight: 700, fontSize: "0.74rem", marginBottom: "0.35rem" }}>✓ YA SABÍA ({evo.yaSabia.length})</div>
                            {evo.yaSabia.slice(0, 4).map((t, k) => chip(t.slice(0, 60), "#bfdbfe", "rgba(59,130,246,0.1)"))}
                            {evo.yaSabia.length > 4 && <span style={{ color: "#64748b", fontSize: "0.68rem" }}>+{evo.yaSabia.length - 4} más</span>}
                          </div>
                        </div>
                        {evo.olvido.length > 0 && (
                          <div style={{ color: "#fbbf24", fontSize: "0.7rem", marginBottom: "0.5rem" }}>
                            ⚠ Retrocedió en {evo.olvido.length}: acertó en pretest pero falló en postest
                          </div>
                        )}
                        {/* Tabla comparativa pregunta por pregunta (pre vs post) */}
                        {compPreg && (
                          <details style={{ marginTop: "0.6rem" }}>
                            <summary style={{ cursor: "pointer", color: "#93c5fd", fontSize: "0.74rem", fontWeight: 700, marginBottom: "0.4rem" }}>
                              📊 Ver comparación pregunta por pregunta ({compPreg.length})
                            </summary>
                            <div style={{ marginTop: "0.5rem", display: "grid", gap: "0.2rem" }}>
                              <div style={{ display: "grid", gridTemplateColumns: "1fr 60px 60px 90px", gap: "0.4rem", fontSize: "0.62rem", color: "#64748b", fontWeight: 700, padding: "0.2rem 0.4rem" }}>
                                <span>Pregunta</span><span style={{ textAlign: "center" }}>Pre</span><span style={{ textAlign: "center" }}>Post</span><span>Evolución</span>
                              </div>
                              {compPreg.map((c: any, k: number) => (
                                <div key={k} style={{ display: "grid", gridTemplateColumns: "1fr 60px 60px 90px", gap: "0.4rem", fontSize: "0.66rem", padding: "0.3rem 0.4rem", background: "rgba(15,23,42,0.4)", borderRadius: 4, alignItems: "center" }}>
                                  <span style={{ color: "#cbd5e1" }}>{c.pregunta.slice(0, 52)}{c.pregunta.length > 52 ? "…" : ""}</span>
                                  <span style={{ textAlign: "center" }}>{c.pre_ok === undefined ? "—" : c.pre_ok ? "✅" : "❌"}</span>
                                  <span style={{ textAlign: "center" }}>{c.post_ok === undefined ? "—" : c.post_ok ? "✅" : "❌"}</span>
                                  <span style={{ color: c.color, fontWeight: 700 }}>{c.icono} {c.estado}</span>
                                </div>
                              ))}
                            </div>
                          </details>
                        )}
                      </>
                    ) : (
                      <div style={{ color: "#94a3b8", fontSize: "0.76rem", marginBottom: "0.6rem" }}>
                        {detalle.evaluaciones.length === 0 ? "Sin evaluaciones aún" : "Solo tiene una fase rendida — la evolución se calcula al completar pretest y postest"}
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))", gap: "0.25rem", marginTop: "0.4rem" }}>
                          {(detalle.evaluaciones[0]?.respuestas || []).map((r: any, j: number) => (
                            <div key={j} style={{ fontSize: "0.7rem", color: r.correcta ? "#86efac" : "#fca5a5" }}>
                              {r.correcta ? "✅" : "❌"} {r.pregunta?.slice(0, 55)}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* ── Nivel + insignias + garaje (Opción A) ── */}
                    {detalle.nivel && (
                      <div style={{ borderTop: "1px solid #1e293b", paddingTop: "0.6rem", marginTop: "0.5rem", marginBottom: "0.5rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.8rem", flexWrap: "wrap", marginBottom: "0.5rem" }}>
                          <span style={{ background: "rgba(124,119,221,0.18)", color: "#c4b5fd", padding: "0.2rem 0.6rem", borderRadius: 8, fontSize: "0.72rem", fontWeight: 700 }}>
                            🏆 Nivel {detalle.nivel.numero} · {detalle.nivel.nombre}
                          </span>
                          <span style={{ color: "#facc15", fontSize: "0.72rem", fontWeight: 700 }}>⚡ {detalle.nivel.xp} XP</span>
                          <span style={{ color: "#93c5fd", fontSize: "0.72rem" }}>🎖️ {detalle.insignias_conseguidas}/{detalle.insignias_total} insignias</span>
                          <span style={{ color: "#86efac", fontSize: "0.72rem" }}>🔧 {detalle.garaje_desbloqueados}/{detalle.garaje_total} garaje</span>
                        </div>
                        {/* Insignias */}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem", marginBottom: "0.4rem" }}>
                          {detalle.insignias.map((ins: any) => (
                            <span key={ins.id} title={ins.descripcion}
                              style={{ fontSize: "0.68rem", padding: "0.2rem 0.45rem", borderRadius: 6,
                                background: ins.conseguida ? "rgba(34,197,94,0.14)" : "rgba(30,41,59,0.5)",
                                color: ins.conseguida ? "#bbf7d0" : "#475569",
                                opacity: ins.conseguida ? 1 : 0.5 }}>
                              {ins.icono} {ins.nombre}
                            </span>
                          ))}
                        </div>
                        {/* Garaje */}
                        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.25rem" }}>
                          {detalle.garaje.map((g: any, k: number) => {
                            const col: any = { comun: "#64748b", raro: "#378ADD", epico: "#7c77dd", legendario: "#f59e0b" }
                            return (
                              <span key={k} title={`${g.nombre} (${g.rareza})`}
                                style={{ fontSize: "0.9rem", padding: "0.1rem 0.25rem", borderLeft: `2px solid ${col[g.rareza] || "#64748b"}`,
                                  opacity: g.desbloqueado ? 1 : 0.28, filter: g.desbloqueado ? "none" : "grayscale(1)" }}>
                                {g.icono}
                              </span>
                            )
                          })}
                        </div>
                      </div>
                    )}
                    {detalle.partidas_arcade.length > 0 && (
                      <div style={{ borderTop: "1px solid #1e293b", paddingTop: "0.5rem", marginTop: "0.3rem" }}>
                        <span style={{ color: "#94a3b8", fontSize: "0.72rem", fontWeight: 600 }}>🎮 Actividad de juego: </span>
                        <span style={{ color: "#cbd5e1", fontSize: "0.7rem" }}>
                          {detalle.partidas_arcade.slice(0, 6).map((pa: any) => `${pa.modo} ${pa.aciertos}/${pa.total}`).join(" · ")}
                          {detalle.partidas_arcade.length > 6 ? ` · +${detalle.partidas_arcade.length - 6} más` : ""}
                        </span>
                      </div>
                    )}
                  </td></tr>
                  )
                })()}
              </>
            ))}
            {parts.length === 0 && <tr><td colSpan={11} style={{ padding: "1rem", color: "#64748b", textAlign: "center" }}>Aún no hay participantes registrados</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  )
}
