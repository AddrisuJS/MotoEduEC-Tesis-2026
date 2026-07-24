"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

export default function TopPage() {
  const { usuario, listo } = useAuth(true, true)
  const [top, setTop] = useState<any[]>([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    fetch(`${API}/m8/arcade/top?limite=20`)
      .then(r => r.json())
      .then(d => setTop(d.top || []))
      .finally(() => setCargando(false))
  }, [])

  if (!listo || !usuario) return null

  const medalla = (pos: number) => pos === 1 ? "🥇" : pos === 2 ? "🥈" : pos === 3 ? "🥉" : `${pos}`

  return (
    <div style={{ minHeight: "100vh", background: "transparent", padding: "2rem 1rem", display: "flex", justifyContent: "center" }}>
      <div style={{ width: "100%", maxWidth: 520 }}>
        <div style={{ textAlign: "center", marginBottom: "1.2rem" }}>
          <div style={{ fontSize: "2.6rem" }}>🏆</div>
          <h1 style={{ color: "#f1f5f9", fontSize: "1.6rem", fontWeight: 800, margin: "0.3rem 0" }}>Top Motociclistas</h1>
          <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Los que más saben de la vía 🏍️</p>
        </div>

        <div style={{ background: "var(--glass)", border: "1px solid var(--glass-brd)", backdropFilter: "blur(16px)", borderRadius: 20, padding: "0.8rem", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }}>
          {cargando && <p style={{ color: "#94a3b8", textAlign: "center", padding: "1rem" }}>Cargando ranking...</p>}
          {!cargando && top.length === 0 && (
            <p style={{ color: "#94a3b8", textAlign: "center", padding: "1.2rem", fontSize: "0.9rem" }}>
              Aún no hay jugadores. ¡Sé el primero en el Arcade! 🕹️
            </p>
          )}
          {top.map(j => {
            const esYo = j.usuario_id === usuario.id
            return (
              <div key={j.usuario_id} style={{
                display: "flex", alignItems: "center", gap: "0.8rem",
                padding: "0.7rem 0.9rem", borderRadius: 12, marginBottom: "0.35rem",
                background: esYo ? "rgba(59,130,246,0.15)" : j.posicion <= 3 ? "rgba(250,204,21,0.06)" : "transparent",
                border: esYo ? "1.5px solid #3b82f6" : "1px solid transparent",
              }}>
                <div style={{ width: 34, textAlign: "center", fontSize: j.posicion <= 3 ? "1.4rem" : "0.95rem", color: "#94a3b8", fontWeight: 800 }}>
                  {medalla(j.posicion)}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ color: esYo ? "#93c5fd" : "#f1f5f9", fontWeight: esYo ? 800 : 600, fontSize: "0.92rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {j.nombre}{esYo && " (tú)"}
                  </div>
                  <div style={{ color: "#64748b", fontSize: "0.72rem" }}>{j.partidas} partidas · {j.aciertos} aciertos</div>
                </div>
                {j.racha > 0 && <div style={{ color: "#FAC74C", fontSize: "0.82rem", fontWeight: 700 }}>🔥{j.racha}</div>}
                <div style={{ color: "#facc15", fontWeight: 800, fontSize: "0.95rem" }}>{j.xp} XP</div>
              </div>
            )
          })}
        </div>

        <Link href="/arcade" style={{ textDecoration: "none" }}>
          <div style={{ marginTop: "1rem", textAlign: "center", background: "linear-gradient(90deg,#3b82f6,#2563eb)", borderRadius: 12, padding: "0.85rem", color: "#fff", fontWeight: 700, cursor: "pointer" }}>
            🕹️ Ir al Arcade
          </div>
        </Link>
      </div>
    </div>
  )
}
