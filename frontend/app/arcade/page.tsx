"use client"
import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

type Pregunta = { id: number; pregunta: string; opciones: string[]; correcta: string; explicacion: string; categoria: string }

export default function ArcadePage() {
  const { usuario, listo } = useAuth()
  const [fase, setFase] = useState<"menu" | "jugando" | "resultado">("menu")
  const [modo, setModo] = useState<"relampago" | "desafio">("relampago")
  const [preguntas, setPreguntas] = useState<Pregunta[]>([])
  const [idx, setIdx] = useState(0)
  const [segundos, setSegundos] = useState(15)
  const [segMax, setSegMax] = useState(15)
  const [aciertos, setAciertos] = useState(0)
  const [bonusSuma, setBonusSuma] = useState(0)
  const [seleccion, setSeleccion] = useState<string | null>(null)
  const [resultado, setResultado] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [cargando, setCargando] = useState(false)
  const timerRef = useRef<any>(null)

  useEffect(() => {
    if (usuario) fetch(`${API}/m8/arcade/stats/${usuario.id}`).then(r => r.json()).then(setStats).catch(() => {})
  }, [usuario, fase])

  const [errorMsg, setErrorMsg] = useState("")

  const empezar = async (m: "relampago" | "desafio") => {
    setCargando(true); setErrorMsg("")
    try {
      const url = m === "desafio"
        ? `${API}/m8/arcade/desafio?usuario_id=${usuario.id}`
        : `${API}/m8/arcade/quiz?n=10`
      const r = await fetch(url)
      const data = await r.json()
      // Blindaje: si la API falló o no trajo preguntas, NO entrar al juego
      if (!r.ok || !Array.isArray(data.preguntas) || data.preguntas.length === 0) {
        setErrorMsg(data.detail || "No se pudieron cargar las preguntas. Intenta de nuevo en unos segundos.")
        return
      }
      setModo(data.modo || m)          // si ya jugó el desafío hoy, el backend manda ronda extra x1
      setPreguntas(data.preguntas); setIdx(0); setAciertos(0); setBonusSuma(0)
      setSegMax(data.segundos_por_pregunta || 15); setSegundos(data.segundos_por_pregunta || 15)
      setSeleccion(null); setFase("jugando")
      if (data.ronda_extra) setErrorMsg("")
    } catch {
      setErrorMsg("No hay conexión con la API. ¿Están corriendo los contenedores?")
    } finally { setCargando(false) }
  }

  // Timer
  useEffect(() => {
    if (fase !== "jugando" || seleccion !== null) return
    timerRef.current = setInterval(() => {
      setSegundos(s => {
        if (s <= 1) { clearInterval(timerRef.current); setSeleccion("__timeout__"); return 0 }
        return s - 1
      })
    }, 1000)
    return () => clearInterval(timerRef.current)
  }, [fase, idx, seleccion])

  const responder = (op: string) => {
    if (seleccion !== null) return
    clearInterval(timerRef.current)
    setSeleccion(op)
    if (op === preguntas[idx].correcta) {
      setAciertos(a => a + 1)
      setBonusSuma(b => b + segundos)
    }
  }

  const siguiente = async () => {
    if (idx + 1 < preguntas.length) {
      setIdx(idx + 1); setSegundos(segMax); setSeleccion(null)
    } else {
      const r = await fetch(`${API}/m8/arcade/finalizar`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          usuario_id: usuario.id, modo,
          aciertos: seleccion === preguntas[idx].correcta ? aciertos : aciertos,
          total: preguntas.length, segundos_restantes_suma: bonusSuma,
        }),
      })
      setResultado(await r.json()); setFase("resultado")
    }
  }

  if (!listo || !usuario) return null

  const card: any = { background: "var(--glass)", border: "1px solid var(--glass-brd)", backdropFilter: "blur(16px)", borderRadius: 20, padding: "1.6rem", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }
  const fondo: any = { minHeight: "100vh", background: "transparent", padding: "2rem 1rem", display: "flex", justifyContent: "center" }
  const btn: any = { padding: "0.9rem 1.2rem", borderRadius: 12, border: "none", fontWeight: 700, fontSize: "1rem", cursor: "pointer", width: "100%" }

  // ─── MENÚ ────────────────────────────────────────────────
  if (fase === "menu") return (
    <div style={fondo}><div style={{ width: "100%", maxWidth: 480 }}>
      <div style={{ textAlign: "center", marginBottom: "1.2rem" }}>
        <div style={{ fontSize: "2.6rem" }}>🕹️</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.6rem", fontWeight: 800, margin: "0.3rem 0" }}>Arcade Vial</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>Aprende jugando, {usuario.nombre.split(" ")[0]} 🏍️</p>
      </div>

      {stats && (
        <div style={{ ...card, display: "flex", justifyContent: "space-around", textAlign: "center", marginBottom: "1rem", padding: "1rem" }}>
          <div><div style={{ color: "#facc15", fontSize: "1.3rem", fontWeight: 800 }}>{stats.xp_total}</div><div style={{ color: "#94a3b8", fontSize: "0.7rem" }}>XP</div></div>
          <div><div style={{ color: "#fb923c", fontSize: "1.3rem", fontWeight: 800 }}>🔥 {stats.racha_actual}</div><div style={{ color: "#94a3b8", fontSize: "0.7rem" }}>RACHA</div></div>
          <div><div style={{ color: "#60a5fa", fontSize: "1.3rem", fontWeight: 800 }}>#{stats.posicion ?? "—"}</div><div style={{ color: "#94a3b8", fontSize: "0.7rem" }}>RANKING</div></div>
        </div>
      )}
      {errorMsg && (
        <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid #ef4444", color: "#fca5a5", borderRadius: 10, padding: "0.6rem 0.9rem", fontSize: "0.82rem", marginBottom: "1rem", textAlign: "center" }}>
          ⚠️ {errorMsg}
        </div>
      )}
      {stats?.racha_en_riesgo && (
        <div style={{ background: "rgba(251,146,60,0.12)", border: "1px solid #fb923c", color: "#fdba74", borderRadius: 10, padding: "0.6rem 0.9rem", fontSize: "0.82rem", marginBottom: "1rem", textAlign: "center" }}>
          🔥 ¡Tu racha de {stats.racha_actual} días está en riesgo! Juega hoy para no perderla.
        </div>
      )}

      <div style={{ ...card, marginBottom: "1rem" }}>
        <h2 style={{ color: "#f1f5f9", fontSize: "1.1rem", margin: "0 0 0.3rem" }}>⚡ Duelo Relámpago</h2>
        <p style={{ color: "#94a3b8", fontSize: "0.82rem", margin: "0 0 0.9rem" }}>10 preguntas, 15 segundos cada una. Acierta rápido: la velocidad da bonus.</p>
        <button onClick={() => empezar("relampago")} disabled={cargando}
          style={{ ...btn, background: "var(--race-grad)", color: "#fff" }}>
          {cargando ? "Cargando..." : "JUGAR"}
        </button>
      </div>

      <div style={{ ...card, marginBottom: "1rem" }}>
        <h2 style={{ color: "#f1f5f9", fontSize: "1.1rem", margin: "0 0 0.3rem" }}>🎯 Desafío del Día</h2>
        <p style={{ color: "#94a3b8", fontSize: "0.82rem", margin: "0 0 0.9rem" }}>Una pregunta especial que cambia cada día. Paga <b style={{ color: "#facc15" }}>DOBLE XP</b>.</p>
        <button onClick={() => empezar("desafio")} disabled={cargando}
          style={{ ...btn, background: "linear-gradient(90deg,#f59e0b,#d97706)", color: "#fff" }}>
          {cargando ? "Cargando..." : "ACEPTAR DESAFÍO"}
        </button>
      </div>

      <Link href="/top" style={{ textDecoration: "none" }}>
        <div style={{ ...card, textAlign: "center", cursor: "pointer" }}>
          <span style={{ color: "#facc15", fontWeight: 800 }}>🏆 Ver el Top de motociclistas</span>
        </div>
      </Link>
    </div></div>
  )

  // ─── JUGANDO ─────────────────────────────────────────────
  if (fase === "jugando") {
    const p = preguntas[idx]
    if (!p) { setFase("menu"); return null }
    const pct = (segundos / segMax) * 100
    return (
      <div style={fondo}><div style={{ width: "100%", maxWidth: 560 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", color: "#94a3b8", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
          <button onClick={() => { if (confirm("¿Abandonar la partida? Perderás el progreso.")) setFase("menu") }}
            style={{ background: "var(--glass)", border: "1px solid var(--glass-brd)", backdropFilter: "blur(16px)", color: "#94a3b8", borderRadius: 8, padding: "0.25rem 0.6rem", fontSize: "0.72rem", cursor: "pointer" }}>✕ Salir</button>
          <span>Pregunta {idx + 1}/{preguntas.length}</span>
          <span>✅ {aciertos}</span>
          <span style={{ color: segundos <= 5 ? "#ef4444" : "#f1f5f9", fontWeight: 800 }}>⏱️ {segundos}s</span>
        </div>
        <div style={{ height: 8, background: "#1e293b", borderRadius: 6, marginBottom: "1rem", overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${pct}%`, background: pct > 33 ? "#3b82f6" : "#ef4444", transition: "width 1s linear" }} />
        </div>

        <div style={card}>
          <div style={{ color: "#60a5fa", fontSize: "0.72rem", fontWeight: 700, marginBottom: "0.4rem" }}>{p.categoria.toUpperCase()}{modo === "desafio" && " · 🎯 DESAFÍO x2"}</div>
          <h2 style={{ color: "#f1f5f9", fontSize: "1.1rem", margin: "0 0 1.1rem", lineHeight: 1.4 }}>{p.pregunta}</h2>
          {p.opciones.map((op, i) => {
            let bg = "#0f172a", bd = "#334155", col = "#e2e8f0"
            if (seleccion !== null) {
              if (op === p.correcta) { bg = "rgba(34,197,94,0.18)"; bd = "#22c55e"; col = "#86efac" }
              else if (op === seleccion) { bg = "rgba(239,68,68,0.15)"; bd = "#ef4444"; col = "#fca5a5" }
            }
            return (
              <button key={i} onClick={() => responder(op)} disabled={seleccion !== null}
                style={{ ...btn, textAlign: "left", background: bg, border: `1.5px solid ${bd}`, color: col, marginBottom: "0.55rem", fontWeight: 500, fontSize: "0.92rem" }}>
                {op}
              </button>
            )
          })}
          {seleccion !== null && (
            <div style={{ marginTop: "0.6rem" }}>
              <div style={{ background: "rgba(59,130,246,0.1)", border: "1px solid #3b82f6", borderRadius: 10, padding: "0.7rem 0.9rem", color: "#bfdbfe", fontSize: "0.82rem", marginBottom: "0.8rem" }}>
                {seleccion === "__timeout__" ? "⏱️ ¡Se acabó el tiempo! " : seleccion === p.correcta ? `✅ ¡Correcto! +${100 + segundos * 10} pts. ` : "❌ Incorrecto. "}
                {p.explicacion}
              </div>
              <button onClick={siguiente} style={{ ...btn, background: "var(--race-grad)", color: "#fff" }}>
                {idx + 1 < preguntas.length ? "Siguiente →" : "Ver resultado 🏁"}
              </button>
            </div>
          )}
        </div>
      </div></div>
    )
  }

  // ─── RESULTADO ───────────────────────────────────────────
  return (
    <div style={fondo}><div style={{ width: "100%", maxWidth: 480 }}>
      <div style={{ ...card, textAlign: "center" }}>
        <div style={{ fontSize: "3rem" }}>{aciertos === preguntas.length ? "🏆" : aciertos >= preguntas.length * 0.7 ? "🎉" : "💪"}</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.5rem", fontWeight: 800, margin: "0.4rem 0" }}>
          {aciertos}/{preguntas.length} correctas
        </h1>
        <div style={{ color: "#facc15", fontSize: "2rem", fontWeight: 800, margin: "0.6rem 0" }}>+{resultado?.puntos_partida ?? 0} XP</div>
        {resultado?.bonus_velocidad > 0 && <p style={{ color: "#94a3b8", fontSize: "0.82rem" }}>⚡ Incluye {resultado.bonus_velocidad} pts de bonus por velocidad</p>}
        <div style={{ display: "flex", justifyContent: "space-around", margin: "1.2rem 0", textAlign: "center" }}>
          <div><div style={{ color: "#fb923c", fontSize: "1.2rem", fontWeight: 800 }}>🔥 {resultado?.racha_actual}</div><div style={{ color: "#94a3b8", fontSize: "0.7rem" }}>RACHA</div></div>
          <div><div style={{ color: "#facc15", fontSize: "1.2rem", fontWeight: 800 }}>{resultado?.xp_total}</div><div style={{ color: "#94a3b8", fontSize: "0.7rem" }}>XP TOTAL</div></div>
          <div><div style={{ color: "#60a5fa", fontSize: "1.2rem", fontWeight: 800 }}>#{resultado?.posicion_ranking}</div><div style={{ color: "#94a3b8", fontSize: "0.7rem" }}>RANKING</div></div>
        </div>
        <button onClick={() => setFase("menu")} style={{ ...btn, background: "var(--race-grad)", color: "#fff", marginBottom: "0.6rem" }}>Jugar de nuevo</button>
        <Link href="/top"><button style={{ ...btn, background: "#0f172a", border: "1px solid #facc15", color: "#facc15" }}>🏆 Ver el Top</button></Link>
      </div>
    </div></div>
  )
}
