"use client"
import { useState } from "react"
import { useAuth } from "../../lib/useAuth"
import { LoaderMoto } from "../../lib/ui"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

// ─── Escena SVG generada según clima y vía ───
function Escena({ clima, via }: { clima: string, via: string }) {
  const cielos: any = {
    sol:     ["#38bdf8", "#7dd3fc"], lluvia: ["#334155", "#475569"],
    neblina: ["#64748b", "#94a3b8"], noche:  ["#0b1220", "#1e293b"],
  }
  const [c1, c2] = cielos[clima] || cielos.sol
  return (
    <svg viewBox="0 0 400 180" style={{ width: "100%", borderRadius: "14px 14px 0 0", display: "block" }}>
      <defs>
        <linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={c1} /><stop offset="100%" stopColor={c2} />
        </linearGradient>
      </defs>
      <rect width="400" height="180" fill="url(#cielo)" />
      {clima === "sol" && <circle cx="340" cy="35" r="20" fill="#fde047" opacity="0.9" />}
      {clima === "noche" && <><circle cx="340" cy="35" r="14" fill="#f1f5f9" opacity="0.85" />
        {[50,110,180,250].map(x => <circle key={x} cx={x} cy={20 + (x % 30)} r="1.5" fill="#fff" opacity="0.8" />)}</>}
      {/* Montañas Sierra */}
      <polygon points="0,110 70,55 140,110" fill="#1e293b" opacity="0.75" />
      <polygon points="90,110 180,40 280,110" fill="#0f172a" opacity="0.7" />
      <polygon points="240,110 320,60 400,110" fill="#1e293b" opacity="0.75" />
      {/* Vía */}
      {via === "curva" ? (
        <path d="M0,180 Q120,130 220,150 T400,120 L400,180 Z" fill="#1f2937" />
      ) : (
        <polygon points="150,180 250,180 320,110 80,110" fill="#1f2937" />
      )}
      {via !== "curva" && [0,1,2].map(i => (
        <rect key={i} x={196 - i * 2} y={168 - i * 22} width={5 - i} height={11 - i * 2} fill="#fde047" opacity="0.9" />
      ))}
      {/* Moto */}
      <text x="185" y="165" fontSize="30">🏍️</text>
      {/* Clima overlays */}
      {clima === "lluvia" && [...Array(18)].map((_, i) => (
        <line key={i} x1={20 + i * 22} y1={(i * 13) % 100} x2={14 + i * 22} y2={((i * 13) % 100) + 16}
          stroke="#bae6fd" strokeWidth="1.4" opacity="0.65" />
      ))}
      {clima === "neblina" && <>
        <rect y="70" width="400" height="45" fill="#e2e8f0" opacity="0.35" />
        <rect y="100" width="400" height="50" fill="#cbd5e1" opacity="0.3" />
      </>}
      {clima === "noche" && <rect width="400" height="180" fill="#0b1220" opacity="0.35" />}
    </svg>
  )
}

export default function RutaSeguraPage() {
  const { usuario, listo } = useAuth(true, true)
  const [esc, setEsc] = useState<any>(null)
  const [eleccion, setEleccion] = useState<string | null>(null)
  const [premio, setPremio] = useState<any>(null)
  const [cargando, setCargando] = useState(false)

  const perfilM1 = typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("motoeduc_perfil") || "{}") : {}

  const nuevo = async () => {
    setCargando(true); setEleccion(null); setPremio(null); setEsc(null)
    try {
      const r = await fetch(`${API}/m8/ruta/escenario`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario_id: usuario.id, perfil: {
          tipo_uso: perfilM1.tipo_uso || usuario.tipo_uso || "urbano",
          anos_experiencia: perfilM1.anos_experiencia || 1,
          zona: perfilM1.zona || "Sierra", ciudad: perfilM1.ciudad || "Cuenca",
        }}),
      })
      const d = await r.json()
      setEsc(d.escenario)
    } finally { setCargando(false) }
  }

  const elegir = async (id: string) => {
    if (eleccion) return
    setEleccion(id)
    const correcto = id === esc.correcta
    const r = await fetch(`${API}/m8/ruta/resolver`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario_id: usuario.id, correcto }),
    })
    setPremio(await r.json())
  }

  if (!listo || !usuario) return null

  const card: any = { background: "var(--glass)", border: "1px solid var(--glass-brd)", backdropFilter: "blur(16px)", borderRadius: 16, overflow: "hidden" }
  const btn: any = { padding: "0.85rem 1.1rem", borderRadius: 12, border: "none", fontWeight: 700, cursor: "pointer", width: "100%", fontSize: "0.92rem" }

  return (
    <div style={{ minHeight: "calc(100vh - 54px)", padding: "1.5rem clamp(0.6rem,3vw,1.5rem)", display: "flex", justifyContent: "center" }}>
      <div style={{ width: "100%", maxWidth: 620 }}>

        {cargando && (
          <div className="fade-up" style={{ ...card, padding: "2.5rem 1rem" }}>
            <LoaderMoto texto="Generando tu escenario en la vía..." />
          </div>
        )}

        {!esc && !cargando && (
          <div className="fade-up" style={{ ...card, padding: "2rem", textAlign: "center" }}>
            <div style={{ fontSize: "2.8rem" }}>🛣️</div>
            <h1 style={{ color: "#f1f5f9", fontSize: "clamp(1.2rem,4vw,1.5rem)", fontWeight: 800, margin: "0.4rem 0" }}>Ruta Segura</h1>
            <p style={{ color: "#94a3b8", fontSize: "0.88rem", lineHeight: 1.6, maxWidth: 460, margin: "0 auto 1.2rem" }}>
              La vía te pondrá en situaciones reales de tu zona — neblina, lluvia, tráfico — y tú decides.
              Decisión segura: <b style={{ color: "#4ade80" }}>+150 XP</b>. Te equivocas: aprendes igual (+30 XP).
            </p>
            <button onClick={nuevo} disabled={cargando}
              style={{ ...btn, maxWidth: 300, background: cargando ? "#334155" : "linear-gradient(90deg,#f59e0b,#ea580c)", color: "#fff" }}>
              {cargando ? "🏍️ Generando tu escenario..." : "ARRANCAR 🏁"}
            </button>
          </div>
        )}

        {esc && !cargando && (
          <div className="fade-up" style={card}>
            <Escena clima={esc.clima} via={esc.via} />
            <div style={{ padding: "1.1rem 1.2rem" }}>
              <div style={{ display: "flex", gap: "0.4rem", marginBottom: "0.5rem", flexWrap: "wrap" }}>
                <span style={{ background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.4)", color: "#fdba74", borderRadius: 6, padding: "0.15rem 0.55rem", fontSize: "0.65rem", fontWeight: 800 }}>
                  {(esc.clima || "").toUpperCase()}
                </span>
                <span style={{ background: "rgba(59,130,246,0.15)", border: "1px solid rgba(59,130,246,0.4)", color: "#93c5fd", borderRadius: 6, padding: "0.15rem 0.55rem", fontSize: "0.65rem", fontWeight: 800 }}>
                  VÍA {(esc.via || "").toUpperCase()}
                </span>
              </div>
              <h2 style={{ color: "#f1f5f9", fontSize: "1.15rem", fontWeight: 800, marginBottom: "0.4rem" }}>{esc.titulo}</h2>
              <p style={{ color: "#cbd5e1", fontSize: "0.9rem", lineHeight: 1.6, marginBottom: "1rem" }}>{esc.narrativa}</p>

              <div style={{ color: "#94a3b8", fontSize: "0.75rem", fontWeight: 800, marginBottom: "0.5rem", letterSpacing: "0.05em" }}>¿QUÉ HACES?</div>
              {esc.opciones.map((op: any) => {
                let bg = "#0f172a", bd = "#334155", col = "#e2e8f0"
                if (eleccion) {
                  if (op.id === esc.correcta) { bg = "rgba(34,197,94,0.15)"; bd = "#22c55e"; col = "#86efac" }
                  else if (op.id === eleccion) { bg = "rgba(239,68,68,0.12)"; bd = "#ef4444"; col = "#fca5a5" }
                }
                return (
                  <button key={op.id} onClick={() => elegir(op.id)} disabled={!!eleccion}
                    style={{ ...btn, textAlign: "left", background: bg, border: `1.5px solid ${bd}`, color: col, marginBottom: "0.5rem", fontWeight: 500 }}>
                    {op.texto}
                  </button>
                )
              })}

              {eleccion && (
                <div className="fade-up" style={{ marginTop: "0.6rem" }}>
                  <div style={{
                    background: eleccion === esc.correcta ? "rgba(34,197,94,0.1)" : "rgba(239,68,68,0.08)",
                    border: `1px solid ${eleccion === esc.correcta ? "rgba(34,197,94,0.45)" : "rgba(239,68,68,0.4)"}`,
                    borderRadius: 12, padding: "0.9rem 1rem", marginBottom: "0.7rem",
                  }}>
                    <div style={{ fontSize: "1.3rem", marginBottom: "0.3rem" }}>{eleccion === esc.correcta ? "✅ ¡Decisión segura!" : "💥 Consecuencia..."}</div>
                    <p style={{ color: "#e2e8f0", fontSize: "0.86rem", lineHeight: 1.55 }}>{esc.consecuencias[eleccion]}</p>
                    <p style={{ color: "#93c5fd", fontSize: "0.76rem", marginTop: "0.5rem" }}>📖 {esc.articulo}</p>
                    {premio && <div style={{ color: "#facc15", fontWeight: 800, fontSize: "1rem", marginTop: "0.5rem" }}>+{premio.xp_ganado} XP · Total: {premio.xp_total}</div>}
                  </div>
                  <button onClick={nuevo} disabled={cargando}
                    style={{ ...btn, background: "linear-gradient(90deg,#f59e0b,#ea580c)", color: "#fff" }}>
                    {cargando ? "Generando..." : "Otro escenario 🛣️"}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
