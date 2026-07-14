"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

const REQ_LABEL: any = { xp: "XP", racha: "días de racha", partidas: "partidas" }

// Fallback de iconos por nombre — inmune a problemas de codificación en BD
const ICONOS: Record<string, string> = {
  "casco basico": "🪖", "guantes de proteccion": "🧤", "chaqueta con protecciones": "🧥",
  "botas de moto": "🥾", "casco integral premium": "⛑️", "chaleco con airbag": "🦺",
  "llantas nuevas": "🛞", "escape deportivo": "💨", "faro led": "💡",
  "pintura personalizada": "🎨", "espejos panoramicos": "🪞", "motor mejorado": "⚙️",
  "kit de herramientas": "🧰", "moto de leyenda": "🏍️",
}
const icono = (it: any) => {
  const k = (it.nombre || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
  return ICONOS[k] || (it.icono && !it.icono.includes("?") ? it.icono : "🎁")
}

const RAREZA: any = {
  comun:      { label: "COMÚN",      color: "#94a3b8", glow: "rgba(148,163,184,0.15)" },
  raro:       { label: "RARO",       color: "#60a5fa", glow: "rgba(96,165,250,0.18)" },
  epico:      { label: "ÉPICO",      color: "#c084fc", glow: "rgba(192,132,252,0.20)" },
  legendario: { label: "LEGENDARIO", color: "#facc15", glow: "rgba(250,204,21,0.22)" },
}

export default function GarajePage() {
  const { usuario, listo } = useAuth()
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    if (usuario) fetch(`${API}/m8/garaje/${usuario.id}`).then(r => r.json()).then(setData).catch(() => {})
  }, [usuario])

  if (!listo || !usuario) return null

  const fondo: any = { minHeight: "100vh", background: "transparent", padding: "2rem clamp(0.5rem,3vw,2rem)" }

  const Item = ({ it }: any) => {
    const r = RAREZA[it.rareza] || RAREZA.comun
    const pct = it.requisito_valor > 0 ? (it.progreso_actual / it.requisito_valor) * 100 : 100
    return (
      <div style={{
        background: it.desbloqueado ? `linear-gradient(160deg, rgba(30,41,59,0.95), ${r.glow})` : "rgba(30,41,59,0.6)",
        border: it.desbloqueado ? `1.5px solid ${r.color}` : "1px solid #2a3648",
        borderRadius: 16, padding: "1.1rem", position: "relative", overflow: "hidden",
        boxShadow: it.desbloqueado ? `0 8px 24px ${r.glow}` : "none",
        transition: "transform .2s",
      }}
        onMouseEnter={e => (e.currentTarget.style.transform = "translateY(-3px)")}
        onMouseLeave={e => (e.currentTarget.style.transform = "translateY(0)")}>

        {/* Badge de rareza */}
        <div style={{ position: "absolute", top: 10, right: 10, background: r.color + "22", color: r.color, border: `1px solid ${r.color}55`, borderRadius: 6, padding: "1px 7px", fontSize: "0.6rem", fontWeight: 800, letterSpacing: "0.05em" }}>
          {r.label}
        </div>

        {/* Icono en medallón */}
        <div style={{
          width: 64, height: 64, borderRadius: 16, display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "2rem", marginBottom: "0.6rem",
          background: it.desbloqueado ? `radial-gradient(circle at 30% 30%, ${r.color}33, #0f172a)` : "#0f172a",
          border: it.desbloqueado ? `1px solid ${r.color}66` : "1px solid #1e293b",
          filter: it.desbloqueado ? "none" : "grayscale(1) opacity(0.5)",
        }}>
          {icono(it)}
        </div>

        <div style={{ color: it.desbloqueado ? "#f1f5f9" : "#7c8aa0", fontWeight: 800, fontSize: "0.92rem", marginBottom: "0.2rem" }}>
          {it.nombre} {it.desbloqueado && <span style={{ color: r.color }}>✓</span>}
        </div>
        <div style={{ color: "#64748b", fontSize: "0.74rem", lineHeight: 1.4, minHeight: "2.1em" }}>{it.descripcion}</div>

        {!it.desbloqueado ? (
          <div style={{ marginTop: "0.7rem" }}>
            <div style={{ height: 7, background: "#0b1220", borderRadius: 5, overflow: "hidden", border: "1px solid #1e293b" }}>
              <div style={{ height: "100%", width: `${pct}%`, background: `linear-gradient(90deg, ${r.color}88, ${r.color})`, transition: "width .4s" }} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
              <span style={{ color: "#7c8aa0", fontSize: "0.68rem" }}>🔒 Faltan {it.falta} {REQ_LABEL[it.requisito_tipo]}</span>
              <span style={{ color: r.color, fontSize: "0.68rem", fontWeight: 700 }}>{Math.floor(pct)}%</span>
            </div>
          </div>
        ) : (
          <div style={{ marginTop: "0.7rem", color: r.color, fontSize: "0.72rem", fontWeight: 700 }}>✨ DESBLOQUEADO</div>
        )}
      </div>
    )
  }

  return (
    <div style={fondo}><div style={{ maxWidth: 980, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: "1.2rem" }}>
        <div style={{ fontSize: "2.6rem" }}>🔧</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "clamp(1.3rem,4vw,1.7rem)", fontWeight: 800, margin: "0.2rem 0" }}>Tu Garaje</h1>
        {data && (
          <div style={{ display: "inline-flex", gap: "1.2rem", background: "rgba(30,41,59,0.8)", border: "1px solid #334155", borderRadius: 14, padding: "0.6rem 1.4rem", marginTop: "0.4rem", flexWrap: "wrap", justifyContent: "center" }}>
            <span style={{ color: "#4ade80", fontWeight: 800, fontSize: "0.9rem" }}>🏆 {data.desbloqueados}/{data.total} piezas</span>
            <span style={{ color: "#facc15", fontWeight: 800, fontSize: "0.9rem" }}>⚡ {data.stats.xp} XP</span>
            <span style={{ color: "#fb923c", fontWeight: 800, fontSize: "0.9rem" }}>🔥 {data.stats.racha} racha</span>
            <span style={{ color: "#60a5fa", fontWeight: 800, fontSize: "0.9rem" }}>🕹️ {data.stats.partidas} partidas</span>
          </div>
        )}
      </div>

      {data && <>
        <h2 style={{ color: "#93c5fd", fontSize: "0.95rem", fontWeight: 800, margin: "1.2rem 0 0.7rem", letterSpacing: "0.04em" }}>🧍 TU EQUIPO DE PROTECCIÓN</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(215px, 1fr))", gap: "0.8rem" }}>
          {data.equipo.map((it: any) => <Item key={it.id} it={it} />)}
        </div>

        <h2 style={{ color: "#fdba74", fontSize: "0.95rem", fontWeight: 800, margin: "1.6rem 0 0.7rem", letterSpacing: "0.04em" }}>🏍️ TU MOTO</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(215px, 1fr))", gap: "0.8rem" }}>
          {data.moto.map((it: any) => <Item key={it.id} it={it} />)}
        </div>
      </>}

      <div style={{ display: "flex", gap: "0.7rem", marginTop: "1.6rem", flexWrap: "wrap" }}>
        <Link href="/arcade" style={{ flex: 1, minWidth: 200, textDecoration: "none" }}>
          <div style={{ textAlign: "center", background: "linear-gradient(90deg,#3b82f6,#2563eb)", borderRadius: 12, padding: "0.85rem", color: "#fff", fontWeight: 700 }}>🕹️ Ganar más XP</div>
        </Link>
        <Link href="/duelos" style={{ flex: 1, minWidth: 200, textDecoration: "none" }}>
          <div style={{ textAlign: "center", background: "linear-gradient(90deg,#ef4444,#b91c1c)", borderRadius: 12, padding: "0.85rem", color: "#fff", fontWeight: 700 }}>⚔️ Retar a alguien</div>
        </Link>
      </div>
    </div></div>
  )
}
