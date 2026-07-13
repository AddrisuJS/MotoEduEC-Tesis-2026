'use client'
import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../../lib/useAuth'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

interface Mensaje {
  rol: "usuario" | "asistente"
  texto: string
  fuentes?: string[]
  docs?: number
  error?: boolean
}

const PREGUNTAS_SUGERIDAS = [
  "¿Cuál es la velocidad máxima en zona urbana para motos?",
  "¿Qué documentos debo llevar obligatoriamente?",
  "¿Cómo frenar correctamente en piso mojado?",
  "¿Qué equipamiento es obligatorio en Ecuador?",
  "¿Cómo conducir seguro en la neblina del Cajas?",
]

export default function AsistentePage() {
  const { usuario, listo } = useAuth()
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [estadoRAG, setEstado] = useState<any>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const perfilM1 = typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("motoeduc_perfil") || "{}") : {}

  useEffect(() => {
    fetch(`${API}/m3/asistente/estado`).then(r => r.json()).then(setEstado).catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [mensajes, loading])

  const enviar = async (texto: string) => {
    if (!texto.trim() || loading || !usuario) return
    setInput("")
    setMensajes(prev => [...prev, { rol: "usuario", texto }])
    setLoading(true)
    try {
      const r = await fetch(`${API}/m3/asistente/consultar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pregunta: texto,
          usuario_id: String(usuario.id),
          perfil: {
            nombre: usuario.nombre,
            tipo_uso: perfilM1.tipo_uso || usuario.tipo_uso || "urbano",
            anos_experiencia: perfilM1.anos_experiencia || 1,
            moto_actual: perfilM1.moto_actual || "",
            zona: perfilM1.zona || "Sierra",
            ciudad: perfilM1.ciudad || "Cuenca",
            nivel: perfilM1.nivel || "basico",
          },
        }),
      })
      const d = await r.json().catch(() => ({}))
      if (!r.ok) {
        setMensajes(prev => [...prev, {
          rol: "asistente", error: true,
          texto: `El asistente respondió con un error (${r.status}): ${typeof d.detail === "string" ? d.detail : "revisa los logs de la API"}. Intenta de nuevo.`,
        }])
      } else {
        setMensajes(prev => [...prev, {
          rol: "asistente",
          texto: d.respuesta || "No pude obtener una respuesta. Intenta reformular tu pregunta.",
          fuentes: d.fuentes,
          docs: d.documentos_recuperados,
        }])
      }
    } catch {
      setMensajes(prev => [...prev, {
        rol: "asistente", error: true,
        texto: "Sin conexión con el asistente en este momento. Espera unos segundos e intenta de nuevo.",
      }])
    }
    setLoading(false)
  }

  const limpiar = async () => {
    if (usuario) await fetch(`${API}/m3/asistente/historial/${usuario.id}`, { method: "DELETE" }).catch(() => {})
    setMensajes([])
  }

  if (!listo || !usuario) return null

  const esAdmin = usuario.rol === "admin"

  return (
    <div style={{ minHeight: "calc(100vh - 54px)", display: "flex", flexDirection: "column", maxWidth: 860, margin: "0 auto", padding: "1rem clamp(0.6rem, 2.5vw, 1.2rem)" }}>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.6rem", marginBottom: "0.8rem", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.7rem" }}>
          <div style={{ width: 44, height: 44, borderRadius: 14, background: "radial-gradient(circle at 30% 30%, rgba(139,92,246,0.45), #0f172a)", border: "1px solid rgba(139,92,246,0.5)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.4rem" }}>💬</div>
          <div>
            <h1 style={{ color: "#f1f5f9", fontSize: "clamp(1.05rem, 3.5vw, 1.3rem)", fontWeight: 800, lineHeight: 1.1 }}>Asistente Vial</h1>
            <p style={{ color: "#94a3b8", fontSize: "0.75rem" }}>Experto en la LOTTTSV y seguridad para motociclistas 🇪🇨</p>
          </div>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {esAdmin && estadoRAG && (
            <span style={{ background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.4)", color: "#86efac", borderRadius: 8, padding: "0.25rem 0.6rem", fontSize: "0.68rem", fontWeight: 700 }}>
              ● RAG {estadoRAG.documentos ?? estadoRAG.total_documentos ?? "OK"}
            </span>
          )}
          {mensajes.length > 0 && (
            <button onClick={limpiar} style={{ background: "rgba(30,41,59,0.9)", border: "1px solid #334155", color: "#94a3b8", borderRadius: 8, padding: "0.3rem 0.7rem", fontSize: "0.72rem", cursor: "pointer", fontWeight: 600 }}>
              🗑️ Limpiar
            </button>
          )}
        </div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.7rem", paddingBottom: "0.8rem" }}>
        {mensajes.length === 0 && (
          <div className="fade-up" style={{ textAlign: "center", marginTop: "clamp(1rem, 8vh, 4rem)" }}>
            <div style={{ fontSize: "2.8rem", marginBottom: "0.5rem" }}>🏍️💬</div>
            <p style={{ color: "#cbd5e1", fontWeight: 700, marginBottom: "0.3rem" }}>¡Hola {usuario.nombre.split(" ")[0]}! Pregúntame lo que quieras sobre la vía</p>
            <p style={{ color: "#64748b", fontSize: "0.8rem", marginBottom: "1.2rem" }}>Normativa, sanciones, técnica de manejo, equipamiento, clima...</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", justifyContent: "center", maxWidth: 620, margin: "0 auto" }}>
              {PREGUNTAS_SUGERIDAS.map((q, i) => (
                <button key={i} onClick={() => enviar(q)}
                  style={{ background: "rgba(30,41,59,0.85)", border: "1px solid #334155", color: "#93c5fd", borderRadius: 20, padding: "0.5rem 0.9rem", fontSize: "0.78rem", cursor: "pointer", fontWeight: 500 }}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {mensajes.map((m, i) => (
          <div key={i} className="fade-up" style={{ display: "flex", justifyContent: m.rol === "usuario" ? "flex-end" : "flex-start" }}>
            <div style={{
              maxWidth: "82%",
              background: m.rol === "usuario" ? "linear-gradient(135deg,#2563eb,#3b82f6)"
                : m.error ? "rgba(239,68,68,0.1)" : "rgba(30,41,59,0.92)",
              border: m.rol === "usuario" ? "none" : m.error ? "1px solid rgba(239,68,68,0.5)" : "1px solid #2a3852",
              borderRadius: m.rol === "usuario" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              padding: "0.75rem 0.95rem",
            }}>
              <div style={{ color: m.rol === "usuario" ? "#fff" : m.error ? "#fca5a5" : "#e2e8f0", fontSize: "0.9rem", lineHeight: 1.55, whiteSpace: "pre-wrap" }}>
                {m.error && "⚠️ "}{m.texto}
              </div>
              {m.fuentes && m.fuentes.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.55rem" }}>
                  {m.fuentes.slice(0, 4).map((f, j) => (
                    <span key={j} style={{ background: "rgba(139,92,246,0.12)", border: "1px solid rgba(139,92,246,0.35)", color: "#c4b5fd", borderRadius: 6, padding: "0.15rem 0.5rem", fontSize: "0.65rem" }}>
                      📎 {f}
                    </span>
                  ))}
                  {esAdmin && m.docs != null && (
                    <span style={{ color: "#64748b", fontSize: "0.65rem", alignSelf: "center" }}>{m.docs} docs</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start" }}>
            <div style={{ background: "rgba(30,41,59,0.92)", border: "1px solid #2a3852", borderRadius: "16px 16px 16px 4px", padding: "0.8rem 1.1rem", display: "flex", gap: 5 }}>
              {[0, 1, 2].map(i => (
                <span key={i} style={{ width: 7, height: 7, borderRadius: "50%", background: "#8b5cf6", animation: `pulseDot 1.2s ${i * 0.2}s infinite` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{ display: "flex", gap: "0.5rem", background: "rgba(15,23,42,0.92)", border: "1px solid #2a3852", borderRadius: 16, padding: "0.5rem", position: "sticky", bottom: "0.6rem", backdropFilter: "blur(8px)" }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && enviar(input)}
          placeholder="Escribe tu pregunta sobre normativa o seguridad vial..."
          disabled={loading}
          style={{ flex: 1, background: "transparent", border: "none", outline: "none", color: "#f1f5f9", fontSize: "0.92rem", padding: "0.45rem 0.6rem" }}
        />
        <button onClick={() => enviar(input)} disabled={loading || !input.trim()}
          style={{ background: loading || !input.trim() ? "#1e293b" : "linear-gradient(90deg,#8b5cf6,#7c3aed)", border: "none", color: "#fff", borderRadius: 12, padding: "0.55rem 1.1rem", fontSize: "0.88rem", fontWeight: 700, cursor: loading || !input.trim() ? "default" : "pointer" }}>
          {loading ? "..." : "Enviar ➤"}
        </button>
      </div>
    </div>
  )
}
