"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { useAuth } from "../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

type Pregunta = { orden: number; pregunta_id: number; pregunta: string; opciones: string[]; categoria: string }

export default function EvaluacionPage() {
  const { usuario, listo } = useAuth()
  const [estado, setEstado] = useState<any>(null)
  const [preguntas, setPreguntas] = useState<Pregunta[]>([])
  const [idx, setIdx] = useState(0)
  const [respuestas, setRespuestas] = useState<Record<number, string>>({})
  const [fase, setFase] = useState<"pretest" | "postest">("pretest")
  const [pantalla, setPantalla] = useState<"cargando" | "intro" | "quiz" | "enviando" | "final">("cargando")
  const [resultado, setResultado] = useState<any>(null)

  useEffect(() => {
    if (!usuario) return
    fetch(`${API}/m9/experimento/estado/${usuario.id}`)
      .then(r => r.json())
      .then(e => { setEstado(e); setPantalla("intro") })
      .catch(() => setPantalla("intro"))
  }, [usuario])

  const empezar = async (f: "pretest" | "postest") => {
    const data = await (await fetch(`${API}/m9/experimento/preguntas`)).json()
    setPreguntas(data.preguntas); setFase(f); setIdx(0); setRespuestas({}); setPantalla("quiz")
  }

  const responder = (op: string) => {
    const nuevas = { ...respuestas, [preguntas[idx].pregunta_id]: op }
    setRespuestas(nuevas)
    if (idx + 1 < preguntas.length) setTimeout(() => setIdx(idx + 1), 250)
    else enviar(nuevas)
  }

  const enviar = async (resps: Record<number, string>) => {
    setPantalla("enviando")
    const r = await fetch(`${API}/m9/experimento/enviar`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        usuario_id: usuario.id, fase,
        respuestas: Object.entries(resps).map(([pid, resp]) => ({ pregunta_id: Number(pid), respuesta: resp })),
      }),
    })
    setResultado(await r.json()); setPantalla("final")
  }

  if (!listo || !usuario || pantalla === "cargando") return null

  const fondo: any = { minHeight: "100vh", background: "linear-gradient(135deg,#0f172a 0%,#1e293b 60%,#172554 100%)", padding: "2rem 1rem", display: "flex", justifyContent: "center", alignItems: "flex-start" }
  const card: any = { background: "rgba(30,41,59,0.85)", border: "1px solid #334155", borderRadius: 20, padding: "1.8rem", boxShadow: "0 20px 60px rgba(0,0,0,0.5)", width: "100%", maxWidth: 560 }
  const btn: any = { padding: "0.9rem 1.2rem", borderRadius: 12, border: "none", fontWeight: 700, fontSize: "1rem", cursor: "pointer", width: "100%" }

  // ─── INTRO / RUTEO POR FASE ──────────────────────────────
  if (pantalla === "intro") {
    const f = estado?.fase_actual || "pretest"

    if (f === "pretest") return (
      <div style={fondo}><div style={card}>
        <div style={{ textAlign: "center", fontSize: "2.6rem" }}>📋</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800, textAlign: "center" }}>Evaluación Inicial</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.9rem", lineHeight: 1.6 }}>
          Antes de empezar a aprender, queremos conocer tu punto de partida: <b style={{ color: "#e2e8f0" }}>15 preguntas</b> sobre
          normativa y seguridad vial (~10 minutos).
        </p>
        <p style={{ color: "#94a3b8", fontSize: "0.9rem", lineHeight: 1.6 }}>
          No verás cuáles acertaste — no es un examen para aprobar, es tu foto inicial 📸.
          Después de <b style={{ color: "#e2e8f0" }}>3 días usando la plataforma</b>, la repetirás y verás cuánto mejoraste.
        </p>
        <p style={{ color: "#64748b", fontSize: "0.78rem" }}>Responde honestamente y sin ayuda: así tu progreso será real.</p>
        <button onClick={() => empezar("pretest")} style={{ ...btn, background: "linear-gradient(90deg,#3b82f6,#2563eb)", color: "#fff", marginTop: "0.6rem" }}>
          Comenzar evaluación inicial
        </button>
      </div></div>
    )

    if (f === "intervencion") return (
      <div style={fondo}><div style={{ ...card, textAlign: "center" }}>
        <div style={{ fontSize: "2.6rem" }}>🔒</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>Evaluación final bloqueada</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.9rem", lineHeight: 1.6 }}>
          Se desbloquea el <b style={{ color: "#facc15" }}>{estado.fecha_desbloqueo}</b>
          {estado.dias_restantes ? ` (en ~${estado.dias_restantes} día${estado.dias_restantes > 1 ? "s" : ""})` : ""}.
          Mientras tanto, ¡a subir ese conocimiento! 💪
        </p>
        <div style={{ display: "grid", gap: "0.6rem", marginTop: "1rem" }}>
          <Link href="/educacion"><button style={{ ...btn, background: "#0f172a", border: "1px solid #3b82f6", color: "#93c5fd" }}>📚 Lecciones personalizadas</button></Link>
          <Link href="/asistente"><button style={{ ...btn, background: "#0f172a", border: "1px solid #22c55e", color: "#86efac" }}>🤖 Preguntar al asistente</button></Link>
          <Link href="/arcade"><button style={{ ...btn, background: "#0f172a", border: "1px solid #facc15", color: "#fde68a" }}>🕹️ Jugar en el Arcade</button></Link>
        </div>
      </div></div>
    )

    if (f === "postest") return (
      <div style={fondo}><div style={{ ...card, textAlign: "center" }}>
        <div style={{ fontSize: "2.6rem" }}>🏁</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>¡Evaluación final desbloqueada!</h1>
        <p style={{ color: "#94a3b8", fontSize: "0.9rem", lineHeight: 1.6 }}>
          Las mismas 15 preguntas del inicio. Al terminar verás <b style={{ color: "#facc15" }}>cuánto mejoraste</b>. Sin ayuda, como la primera vez 😉
        </p>
        <button onClick={() => empezar("postest")} style={{ ...btn, background: "linear-gradient(90deg,#f59e0b,#d97706)", color: "#fff", marginTop: "0.6rem" }}>
          Comenzar evaluación final
        </button>
      </div></div>
    )

    // completado
    const r = estado?.resultados
    return (
      <div style={fondo}><div style={{ ...card, textAlign: "center" }}>
        <div style={{ fontSize: "3rem" }}>{r && r.mejora_pct >= 20 ? "🏆" : "🎉"}</div>
        <h1 style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>Experimento completado</h1>
        {r && <>
          <div style={{ display: "flex", justifyContent: "space-around", margin: "1.2rem 0" }}>
            <div><div style={{ color: "#94a3b8", fontSize: "0.72rem" }}>INICIAL</div><div style={{ color: "#e2e8f0", fontSize: "1.5rem", fontWeight: 800 }}>{r.pretest}/{r.total}</div></div>
            <div style={{ color: "#64748b", fontSize: "1.5rem", alignSelf: "center" }}>→</div>
            <div><div style={{ color: "#94a3b8", fontSize: "0.72rem" }}>FINAL</div><div style={{ color: "#4ade80", fontSize: "1.5rem", fontWeight: 800 }}>{r.postest}/{r.total}</div></div>
          </div>
          <div style={{ color: "#facc15", fontSize: "2rem", fontWeight: 800 }}>{r.mejora_pct > 0 ? "+" : ""}{r.mejora_pct}%</div>
          <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>de mejora en tu conocimiento vial 🏍️ ¡Gracias por participar!</p>
        </>}
        <Link href="/arcade"><button style={{ ...btn, background: "linear-gradient(90deg,#3b82f6,#2563eb)", color: "#fff", marginTop: "0.8rem" }}>Seguir aprendiendo en el Arcade</button></Link>
      </div></div>
    )
  }

  // ─── QUIZ (sin feedback de aciertos) ─────────────────────
  if (pantalla === "quiz") {
    const p = preguntas[idx]
    return (
      <div style={fondo}><div style={{ width: "100%", maxWidth: 560 }}>
        <div style={{ display: "flex", justifyContent: "space-between", color: "#94a3b8", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
          <button onClick={() => { if (confirm("¿Salir de la evaluación? Tus respuestas no se guardarán y podrás empezarla de nuevo.")) setPantalla("intro") }}
            style={{ background: "rgba(30,41,59,0.9)", border: "1px solid #334155", color: "#94a3b8", borderRadius: 8, padding: "0.25rem 0.6rem", fontSize: "0.72rem", cursor: "pointer" }}>✕ Salir</button>
          <span>{fase === "pretest" ? "📋 Evaluación inicial" : "🏁 Evaluación final"}</span>
          <span>{idx + 1} / {preguntas.length}</span>
        </div>
        <div style={{ height: 8, background: "#1e293b", borderRadius: 6, marginBottom: "1rem", overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${((idx) / preguntas.length) * 100}%`, background: "#3b82f6", transition: "width .3s" }} />
        </div>
        <div style={card}>
          <div style={{ color: "#60a5fa", fontSize: "0.72rem", fontWeight: 700, marginBottom: "0.4rem" }}>{p.categoria.toUpperCase()}</div>
          <h2 style={{ color: "#f1f5f9", fontSize: "1.08rem", margin: "0 0 1.1rem", lineHeight: 1.45 }}>{p.pregunta}</h2>
          {p.opciones.map((op, i) => (
            <button key={i} onClick={() => responder(op)}
              style={{ ...btn, textAlign: "left", background: "#0f172a", border: "1.5px solid #334155", color: "#e2e8f0", marginBottom: "0.55rem", fontWeight: 500, fontSize: "0.92rem" }}>
              {op}
            </button>
          ))}
        </div>
      </div></div>
    )
  }

  if (pantalla === "enviando") return (
    <div style={fondo}><div style={{ ...card, textAlign: "center" }}>
      <div style={{ fontSize: "2.4rem" }}>📨</div>
      <p style={{ color: "#94a3b8" }}>Registrando tu evaluación...</p>
    </div></div>
  )

  // ─── FINAL ───────────────────────────────────────────────
  if (fase === "pretest") return (
    <div style={fondo}><div style={{ ...card, textAlign: "center" }}>
      <div style={{ fontSize: "2.6rem" }}>✅</div>
      <h1 style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>¡Evaluación inicial registrada!</h1>
      <p style={{ color: "#94a3b8", fontSize: "0.9rem", lineHeight: 1.6 }}>{resultado?.mensaje}</p>
      <div style={{ display: "grid", gap: "0.6rem", marginTop: "1rem" }}>
        <Link href="/educacion"><button style={{ ...btn, background: "linear-gradient(90deg,#3b82f6,#2563eb)", color: "#fff" }}>📚 Empezar a aprender</button></Link>
        <Link href="/arcade"><button style={{ ...btn, background: "#0f172a", border: "1px solid #facc15", color: "#fde68a" }}>🕹️ Ir al Arcade</button></Link>
      </div>
    </div></div>
  )

  return (
    <div style={fondo}><div style={{ ...card, textAlign: "center" }}>
      <div style={{ fontSize: "3rem" }}>{resultado?.mejora_pct >= 20 ? "🏆" : resultado?.mejora_pct > 0 ? "🎉" : "💪"}</div>
      <h1 style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>Tu progreso</h1>
      <div style={{ display: "flex", justifyContent: "space-around", margin: "1.2rem 0" }}>
        <div><div style={{ color: "#94a3b8", fontSize: "0.72rem" }}>INICIAL</div><div style={{ color: "#e2e8f0", fontSize: "1.6rem", fontWeight: 800 }}>{resultado?.pretest}/{resultado?.total}</div></div>
        <div style={{ color: "#64748b", fontSize: "1.6rem", alignSelf: "center" }}>→</div>
        <div><div style={{ color: "#94a3b8", fontSize: "0.72rem" }}>FINAL</div><div style={{ color: "#4ade80", fontSize: "1.6rem", fontWeight: 800 }}>{resultado?.postest}/{resultado?.total}</div></div>
      </div>
      <div style={{ color: "#facc15", fontSize: "2.2rem", fontWeight: 800 }}>{resultado?.mejora_pct > 0 ? "+" : ""}{resultado?.mejora_pct}%</div>
      <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>de mejora en tu conocimiento vial. ¡Gracias por ser parte del piloto! 🏍️</p>
      <Link href="/arcade"><button style={{ ...btn, background: "linear-gradient(90deg,#3b82f6,#2563eb)", color: "#fff", marginTop: "0.8rem" }}>Seguir en el Arcade</button></Link>
    </div></div>
  )
}
