"use client"

/**
 * /admin/grupos — Panel del investigador.
 * Asigna cada participante a INTERVENCION o CONTROL con un toggle visible.
 * Solo accesible con rol = 'admin'.
 */

import { useEffect, useState } from "react"
import { useAuth } from "../../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

type P = {
  id: number; nombre: string; email: string; grupo: string
  pretest_score: number | null; pretest_total: number | null
  postest_score: number | null; postest_total: number | null
  pretest_hecho: boolean; postest_hecho: boolean; bloqueado: boolean
}
type Resumen = {
  total: number; intervencion: number; control: number
  pretest_completados: number; postest_completados: number
}

export default function AdminGrupos() {
  const { usuario, listo } = useAuth()
  const [lista, setLista] = useState<P[]>([])
  const [resumen, setResumen] = useState<Resumen | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [filtro, setFiltro] = useState("")
  const [ocupado, setOcupado] = useState<number | null>(null)

  const cargar = async (adminId: number) => {
    try {
      const r = await fetch(`${API}/m10/admin/participantes?admin_id=${adminId}`)
      if (!r.ok) { setMsg("No autorizado o error del servidor"); return }
      const d = await r.json()
      setLista(d.participantes); setResumen(d.resumen)
    } catch { setMsg("No se pudo conectar con la API") }
  }

  useEffect(() => { if (usuario?.id && usuario.rol === "admin") cargar(usuario.id) }, [usuario])

  const cambiar = async (p: P, grupo: string, confirmar = false) => {
    if (p.grupo === grupo) return
    setMsg(null); setOcupado(p.id)
    try {
      const r = await fetch(`${API}/m10/admin/participantes/${p.id}/grupo`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grupo, admin_id: usuario.id, confirmar,
          motivo: "Asignacion manual desde el panel" }),
      })
      const d = await r.json()
      if (r.status === 409) {
        setOcupado(null)
        if (confirm(`${d.detail}\n\n¿Continuar de todos modos?`)) return cambiar(p, grupo, true)
        return
      }
      if (!r.ok) { setMsg(d.detail || "Error al cambiar el grupo"); return }
      setMsg(d.mensaje)
      await cargar(usuario.id)
    } finally { setOcupado(null) }
  }

  const aleatorizar = async () => {
    if (!confirm("Se repartirán al azar 50/50 los participantes que aún NO han rendido ninguna evaluación. ¿Continuar?")) return
    const r = await fetch(`${API}/m10/admin/participantes/aleatorizar`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ admin_id: usuario.id, solo_sin_evaluaciones: true }),
    })
    const d = await r.json()
    setMsg(r.ok ? `${d.asignados} asignados (semilla ${d.semilla})` : d.detail)
    cargar(usuario.id)
  }

  if (!listo) return <div style={{ padding: "2rem", color: "#94a3b8" }}>Cargando…</div>
  if (!usuario || usuario.rol !== "admin")
    return (
      <div style={{ padding: "3rem 1rem", color: "#f87171", textAlign: "center" }}>
        🔒 Esta sección es exclusiva del investigador.
      </div>
    )

  const visibles = filtro
    ? lista.filter(p => (p.nombre + p.email).toLowerCase().includes(filtro.toLowerCase()))
    : lista

  // Botón del toggle
  const opt = (activo: boolean, color: string): any => ({
    padding: "0.42rem 0.75rem", borderRadius: 10, cursor: "pointer",
    fontSize: "0.76rem", fontWeight: 800, whiteSpace: "nowrap",
    border: `1px solid ${activo ? color : "#334155"}`,
    background: activo ? `${color}22` : "rgba(15,23,42,0.8)",
    color: activo ? color : "#64748b",
  })

  return (
    <div style={{ minHeight: "100vh", padding: "1.4rem clamp(0.6rem,3vw,1.5rem)" }}>
      <div style={{ maxWidth: 980, margin: "0 auto" }}>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.45rem", fontWeight: 800 }}>🎛️ Asignación de grupos</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "1rem", lineHeight: 1.5 }}>
          <b style={{ color: "#4ade80" }}>Intervención</b> usa la plataforma completa.{" "}
          <b style={{ color: "#fbbf24" }}>Control</b> solo rinde la evaluación inicial y final.
        </p>

        {resumen && (
          <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "1rem" }}>
            {[["Total", resumen.total, "#f1f5f9"],
              ["Intervención", resumen.intervencion, "#4ade80"],
              ["Control", resumen.control, "#fbbf24"],
              ["Pretest", resumen.pretest_completados, "#60a5fa"],
              ["Postest", resumen.postest_completados, "#c084fc"]].map(([k, v, c]: any) => (
              <div key={k} style={{
                background: "rgba(255,255,255,0.05)", backdropFilter: "blur(14px)",
                border: "1px solid #334155", borderRadius: 12,
                padding: "0.6rem 0.9rem", minWidth: 92, flex: "1 1 92px",
              }}>
                <div style={{ color: "#94a3b8", fontSize: "0.66rem" }}>{k}</div>
                <div style={{ color: c, fontSize: "1.35rem", fontWeight: 800 }}>{v}</div>
              </div>
            ))}
          </div>
        )}

        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          <input value={filtro} onChange={e => setFiltro(e.target.value)} placeholder="Buscar por nombre o correo…"
            style={{
              flex: "1 1 220px", background: "rgba(15,23,42,0.8)", border: "1px solid #334155",
              borderRadius: 10, padding: "0.55rem 0.8rem", color: "#e2e8f0", fontSize: "0.85rem",
            }} />
          <button onClick={aleatorizar} style={{
            background: "linear-gradient(90deg,#3b82f6,#2563eb)", color: "#fff", border: "none",
            borderRadius: 10, padding: "0.55rem 1rem", fontWeight: 700, cursor: "pointer", fontSize: "0.83rem",
          }}>🎲 Asignar al azar</button>
        </div>

        {msg && (
          <div style={{
            background: "rgba(15,23,42,0.9)", border: "1px solid #334155", borderRadius: 10,
            padding: "0.7rem", color: "#e2e8f0", fontSize: "0.84rem", marginBottom: "1rem",
          }}>{msg}</div>
        )}

        <div style={{ display: "grid", gap: "0.6rem" }}>
          {visibles.map(p => (
            <div key={p.id} style={{
              background: "rgba(255,255,255,0.05)", backdropFilter: "blur(14px)",
              border: "1px solid #334155", borderRadius: 14, padding: "0.85rem",
              display: "flex", gap: "0.8rem", alignItems: "center", flexWrap: "wrap",
              opacity: ocupado === p.id ? 0.5 : 1,
            }}>
              <div style={{ flex: "1 1 210px", minWidth: 0 }}>
                <div style={{ color: "#f1f5f9", fontWeight: 700, fontSize: "0.92rem" }}>{p.nombre}</div>
                <div style={{ color: "#64748b", fontSize: "0.73rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {p.email}
                </div>
                <div style={{ color: "#94a3b8", fontSize: "0.73rem", marginTop: 3 }}>
                  Pre: {p.pretest_hecho ? `${p.pretest_score}/${p.pretest_total}` : "—"}
                  {"  ·  "}Post: {p.postest_hecho ? `${p.postest_score}/${p.postest_total}` : "—"}
                  {p.bloqueado && <span style={{ color: "#fbbf24" }}> · ⚠️ con datos</span>}
                </div>
              </div>

              <div style={{ display: "flex", gap: "0.4rem" }}>
                <button onClick={() => cambiar(p, "intervencion")}
                  style={opt(p.grupo === "intervencion", "#4ade80")}>
                  {p.grupo === "intervencion" ? "✅" : "⬜"} Intervención
                </button>
                <button onClick={() => cambiar(p, "control")}
                  style={opt(p.grupo === "control", "#fbbf24")}>
                  {p.grupo === "control" ? "✅" : "⬜"} Control
                </button>
              </div>
            </div>
          ))}
        </div>

        {visibles.length === 0 && (
          <div style={{ color: "#64748b", textAlign: "center", padding: "2rem" }}>
            Sin resultados para “{filtro}”.
          </div>
        )}
      </div>
    </div>
  )
}
