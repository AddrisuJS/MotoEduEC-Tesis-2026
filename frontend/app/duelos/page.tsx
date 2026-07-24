"use client"
import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

export default function DuelosPage() {
  const { usuario, listo } = useAuth(true, true)
  const [rivales, setRivales] = useState<any[]>([])
  const [duelos, setDuelos] = useState<any[]>([])
  const [vista, setVista] = useState<"lobby" | "jugando" | "final">("lobby")
  const [dueloId, setDueloId] = useState<number | null>(null)
  const [preguntas, setPreguntas] = useState<any[]>([])
  const [idx, setIdx] = useState(0)
  const [segundos, setSegundos] = useState(15)
  const [aciertos, setAciertos] = useState(0)
  const [bonus, setBonus] = useState(0)
  const [seleccion, setSeleccion] = useState<string | null>(null)
  const [resultado, setResultado] = useState<any>(null)
  const [msg, setMsg] = useState("")
  const timerRef = useRef<any>(null)

  const cargar = async () => {
    if (!usuario) return
    const [r1, r2] = await Promise.all([
      fetch(`${API}/m8/duelos/rivales/${usuario.id}`),
      fetch(`${API}/m8/duelos/mis-duelos/${usuario.id}`),
    ])
    setRivales((await r1.json()).rivales || [])
    setDuelos((await r2.json()).duelos || [])
  }
  useEffect(() => { cargar() }, [usuario])

  const retar = async (rivalId: number) => {
    setMsg("")
    const r = await fetch(`${API}/m8/duelos/crear`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ retador_id: usuario.id, rival_id: rivalId }),
    })
    const data = await r.json()
    if (!r.ok) { setMsg(data.detail || "No se pudo crear el duelo"); return }
    jugarDuelo(data.duelo_id)
  }

  const jugarDuelo = async (id: number) => {
    const data = await (await fetch(`${API}/m8/duelos/${id}/preguntas`)).json()
    setDueloId(id); setPreguntas(data.preguntas); setIdx(0)
    setAciertos(0); setBonus(0); setSeleccion(null); setSegundos(15)
    setVista("jugando")
  }

  useEffect(() => {
    if (vista !== "jugando" || seleccion !== null) return
    timerRef.current = setInterval(() => setSegundos(s => {
      if (s <= 1) { clearInterval(timerRef.current); setSeleccion("__timeout__"); return 0 }
      return s - 1
    }), 1000)
    return () => clearInterval(timerRef.current)
  }, [vista, idx, seleccion])

  const responder = (op: string) => {
    if (seleccion !== null) return
    clearInterval(timerRef.current)
    setSeleccion(op)
    if (op === preguntas[idx].correcta) { setAciertos(a => a + 1); setBonus(b => b + segundos) }
  }

  const siguiente = async () => {
    if (idx + 1 < preguntas.length) { setIdx(idx + 1); setSegundos(15); setSeleccion(null); return }
    const r = await fetch(`${API}/m8/duelos/${dueloId}/jugar`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario_id: usuario.id, aciertos, segundos_restantes_suma: bonus }),
    })
    setResultado(await r.json()); setVista("final"); cargar()
  }

  if (!listo || !usuario) return null

  const fondo: any = { minHeight: "100vh", background: "transparent", padding: "2rem clamp(0.5rem,3vw,2rem)", display: "flex", justifyContent: "center" }
  const card: any = { background: "var(--glass)", border: "1px solid var(--glass-brd)", backdropFilter: "blur(16px)", borderRadius: 16, padding: "1.1rem" }
  const btn: any = { padding: "0.85rem 1.1rem", borderRadius: 12, border: "none", fontWeight: 700, cursor: "pointer", width: "100%", fontSize: "0.95rem" }

  // ─── JUGANDO ─────────────────────────────────────────────
  if (vista === "jugando") {
    const p = preguntas[idx]
    return (
      <div style={fondo}><div style={{ width: "100%", maxWidth: 560 }}>
        <div style={{ display: "flex", justifyContent: "space-between", color: "#94a3b8", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
          <button onClick={() => { if (confirm("¿Abandonar el duelo? Podrás jugarlo después desde el lobby.")) setVista("lobby") }}
            style={{ background: "var(--glass)", border: "1px solid var(--glass-brd)", backdropFilter: "blur(16px)", color: "#94a3b8", borderRadius: 8, padding: "0.25rem 0.6rem", fontSize: "0.72rem", cursor: "pointer" }}>✕ Salir</button>
          <span>⚔️ Duelo — {idx + 1}/{preguntas.length}</span>
          <span>✅ {aciertos}</span>
          <span style={{ color: segundos <= 5 ? "#ef4444" : "#f1f5f9", fontWeight: 800 }}>⏱️ {segundos}s</span>
        </div>
        <div style={card}>
          <div style={{ color: "#f87171", fontSize: "0.72rem", fontWeight: 700, marginBottom: "0.4rem" }}>{p.categoria.toUpperCase()}</div>
          <h2 style={{ color: "#f1f5f9", fontSize: "1.05rem", margin: "0 0 1rem", lineHeight: 1.4 }}>{p.pregunta}</h2>
          {p.opciones.map((op: string, i: number) => {
            let bg = "#0f172a", bd = "#334155", col = "#e2e8f0"
            if (seleccion !== null) {
              if (op === p.correcta) { bg = "rgba(34,197,94,0.18)"; bd = "#22c55e"; col = "#86efac" }
              else if (op === seleccion) { bg = "rgba(239,68,68,0.15)"; bd = "#ef4444"; col = "#fca5a5" }
            }
            return <button key={i} onClick={() => responder(op)} disabled={seleccion !== null}
              style={{ ...btn, textAlign: "left", background: bg, border: `1.5px solid ${bd}`, color: col, marginBottom: "0.5rem", fontWeight: 500, fontSize: "0.9rem" }}>{op}</button>
          })}
          {seleccion !== null && (
            <button onClick={siguiente} style={{ ...btn, background: "linear-gradient(90deg,#ef4444,#b91c1c)", color: "#fff", marginTop: "0.4rem" }}>
              {idx + 1 < preguntas.length ? "Siguiente →" : "Terminar duelo 🏁"}
            </button>
          )}
        </div>
      </div></div>
    )
  }

  // ─── FINAL ───────────────────────────────────────────────
  if (vista === "final") return (
    <div style={fondo}><div style={{ ...card, width: "100%", maxWidth: 460, textAlign: "center", alignSelf: "flex-start" }}>
      <div style={{ fontSize: "3rem" }}>
        {resultado?.estado === "esperando_rival" ? "⏳" : resultado?.resultado === "gane" ? "🏆" : resultado?.resultado === "empate" ? "🤝" : "😤"}
      </div>
      <h1 style={{ color: "#f1f5f9", fontSize: "1.35rem", fontWeight: 800 }}>
        {resultado?.estado === "esperando_rival" ? "¡Jugado! Esperando al rival" :
         resultado?.resultado === "gane" ? "¡VICTORIA!" :
         resultado?.resultado === "empate" ? "Empate técnico" : "Esta vez no fue..."}
      </h1>
      <div style={{ color: "#facc15", fontSize: "1.5rem", fontWeight: 800, margin: "0.5rem 0" }}>{resultado?.puntos} pts</div>
      {resultado?.estado === "completado" && (
        <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>
          Retador {resultado.puntos_retador} — {resultado.puntos_rival} Rival · +{resultado.xp_ganado} XP para ti
        </p>
      )}
      {resultado?.mensaje && <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>{resultado.mensaje}</p>}
      <button onClick={() => setVista("lobby")} style={{ ...btn, background: "var(--race-grad)", color: "#fff", marginTop: "0.6rem" }}>Volver al lobby</button>
    </div></div>
  )

  // ─── LOBBY ───────────────────────────────────────────────
  const pendientes = duelos.filter(d => d.me_toca_jugar)
  const historial = duelos.filter(d => !d.me_toca_jugar)
  return (
    <div style={fondo}><div style={{ width: "100%", maxWidth: 560 }}>
      <div style={{ textAlign: "center", marginBottom: "1rem" }}>
        <div style={{ fontSize: "2.6rem" }}>⚔️</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "clamp(1.3rem,4vw,1.6rem)", fontWeight: 800, margin: "0.2rem 0" }}>Duelos 1v1</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.82rem" }}>Mismas 5 preguntas para los dos. Gana el más rápido y certero. 🏆 +200 XP</p>
      </div>

      {msg && <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid #ef4444", color: "#fca5a5", borderRadius: 10, padding: "0.6rem 0.9rem", fontSize: "0.82rem", marginBottom: "0.8rem" }}>⚠️ {msg}</div>}

      {pendientes.length > 0 && <>
        <h2 style={{ color: "#facc15", fontSize: "0.9rem", fontWeight: 800, margin: "0.8rem 0 0.5rem" }}>🔔 TE RETARON — ¡te toca jugar!</h2>
        {pendientes.map(d => (
          <div key={d.id} style={{ ...card, display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem", gap: "0.6rem", flexWrap: "wrap" }}>
            <div><div style={{ color: "#f1f5f9", fontWeight: 700 }}>vs {d.oponente}</div><div style={{ color: "#64748b", fontSize: "0.72rem" }}>{d.fecha}</div></div>
            <button onClick={() => jugarDuelo(d.id)} style={{ ...btn, width: "auto", background: "linear-gradient(90deg,#ef4444,#b91c1c)", color: "#fff", padding: "0.6rem 1.2rem" }}>JUGAR</button>
          </div>
        ))}
      </>}

      <h2 style={{ color: "#93c5fd", fontSize: "0.9rem", fontWeight: 800, margin: "1rem 0 0.5rem" }}>🎯 RETAR A UN MOTOCICLISTA</h2>
      <div style={card}>
        {rivales.length === 0 && <p style={{ color: "#64748b", fontSize: "0.85rem", textAlign: "center" }}>Aún no hay más participantes registrados</p>}
        {rivales.map(r => (
          <div key={r.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.5rem 0.3rem", borderBottom: "1px solid #1e293b", gap: "0.5rem" }}>
            <div style={{ color: "#e2e8f0", fontSize: "0.88rem", fontWeight: 600, flex: 1, minWidth: 0, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{r.nombre}</div>
            <div style={{ color: "#facc15", fontSize: "0.78rem", fontWeight: 700 }}>{r.xp} XP</div>
            <button onClick={() => retar(r.id)} style={{ ...btn, width: "auto", background: "#0f172a", border: "1px solid #ef4444", color: "#fca5a5", padding: "0.4rem 0.9rem", fontSize: "0.78rem" }}>⚔️ Retar</button>
          </div>
        ))}
      </div>

      {historial.length > 0 && <>
        <h2 style={{ color: "#94a3b8", fontSize: "0.9rem", fontWeight: 800, margin: "1rem 0 0.5rem" }}>📜 HISTORIAL</h2>
        {historial.map(d => (
          <div key={d.id} style={{ ...card, display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem", padding: "0.7rem 1rem", gap: "0.5rem", flexWrap: "wrap" }}>
            <div style={{ color: "#e2e8f0", fontSize: "0.85rem" }}>vs {d.oponente}</div>
            <div style={{ fontSize: "0.8rem", fontWeight: 800, color: d.resultado === "gane" ? "#4ade80" : d.resultado === "empate" ? "#facc15" : d.resultado === "perdi" ? "#f87171" : "#94a3b8" }}>
              {d.resultado === "gane" ? "🏆 Ganaste" : d.resultado === "empate" ? "🤝 Empate" : d.resultado === "perdi" ? "😤 Perdiste" : "⏳ Esperando rival"}
              {d.mis_puntos != null && ` · ${d.mis_puntos} pts`}
            </div>
          </div>
        ))}
      </>}

      <Link href="/garaje" style={{ textDecoration: "none" }}>
        <div style={{ marginTop: "1rem", textAlign: "center", background: "#0f172a", border: "1px solid #3b82f6", borderRadius: 12, padding: "0.8rem", color: "#93c5fd", fontWeight: 700 }}>🔧 Ver mi Garaje</div>
      </Link>
    </div></div>
  )
}
