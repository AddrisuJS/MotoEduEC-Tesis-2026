'use client'
import { useState, useRef, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

interface Mensaje {
  rol:     "usuario" | "asistente"
  texto:   string
  fuentes?: string[]
  docs?:   number
}

const PREGUNTAS_SUGERIDAS = [
  "Cual es la velocidad maxima en zona urbana para motos?",
  "Que documentos debo llevar obligatoriamente?",
  "Como frenar correctamente en piso mojado?",
  "Que equipamiento es obligatorio en Ecuador?",
  "Cuales son las sanciones por conducir sin casco?",
]

export default function AsistentePage() {
  const [mensajes, setMensajes] = useState<Mensaje[]>([])
  const [input, setInput]       = useState("")
  const [loading, setLoading]   = useState(false)
  const [estadoRAG, setEstado]  = useState<any>(null)
  const bottomRef               = useRef<HTMLDivElement>(null)

  const perfil = typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("motoeduc_perfil") || "{}")
    : {}
  const usuarioId = typeof window !== "undefined"
    ? localStorage.getItem("motoeduc_usuario_id") || "anonimo"
    : "anonimo"

  useEffect(() => {
    fetch(`${API}/m3/asistente/estado`)
      .then(r => r.json())
      .then(setEstado)
      .catch(() => {})
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior:"smooth" })
  }, [mensajes])

  const enviar = async (texto: string) => {
    if (!texto.trim() || loading) return
    setInput("")
    const nuevoMensaje: Mensaje = { rol:"usuario", texto }
    setMensajes(prev => [...prev, nuevoMensaje])
    setLoading(true)

    try {
      const r = await fetch(`${API}/m3/asistente/consultar`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify({
          pregunta:   texto,
          usuario_id: usuarioId,
          perfil:     perfil || { tipo_uso:"urbano", anos_experiencia:1 }
        })
      })
      const d = await r.json()
      setMensajes(prev => [...prev, {
        rol:     "asistente",
        texto:   d.respuesta || "No pude obtener una respuesta.",
        fuentes: d.fuentes,
        docs:    d.documentos_recuperados
      }])
    } catch {
      setMensajes(prev => [...prev, {
        rol:   "asistente",
        texto: "Error de conexion. Verifica que la API este activa en localhost:8010."
      }])
    }
    setLoading(false)
  }

  const limpiar = async () => {
    await fetch(`${API}/m3/asistente/historial/${usuarioId}`, { method:"DELETE" })
    setMensajes([])
  }

  return (
    <div style={{ height:"100vh", background:"#0f172a", display:"flex", flexDirection:"column" }}>

      {/* HEADER */}
      <div style={{ background:"#1e293b", padding:"1rem 1.5rem", borderBottom:"1px solid #334155", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <div>
          <a href="/" style={{ color:"#64748b", fontSize:"0.8rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"1.2rem", fontWeight:"bold", marginTop:"0.25rem" }}>
            💬 Asistente Experto RAG
          </h1>
          <p style={{ color:"#64748b", fontSize:"0.75rem" }}>Normativa LOTTTSV + Catalogo MotoEdu EC</p>
        </div>
        <div style={{ textAlign:"right" }}>
          {estadoRAG && (
            <div style={{ fontSize:"0.75rem", color: estadoRAG.chromadb_conectado ? "#22c55e" : "#ef4444" }}>
              {estadoRAG.chromadb_conectado ? "●" : "○"} ChromaDB: {estadoRAG.documentos_indexados} docs
            </div>
          )}
          {perfil?.perfil_asignado && (
            <span style={{ background:"#3b82f622", color:"#38bdf8", padding:"2px 8px", borderRadius:"10px", fontSize:"0.75rem" }}>
              {perfil.perfil_asignado}
            </span>
          )}
        </div>
      </div>

      {/* MENSAJES */}
      <div style={{ flex:1, overflowY:"auto", padding:"1.5rem" }}>
        {mensajes.length === 0 && (
          <div style={{ textAlign:"center", padding:"2rem" }}>
            <div style={{ fontSize:"3rem", marginBottom:"1rem" }}>🤖</div>
            <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>Hola! Soy tu asistente vial</h2>
            <p style={{ color:"#94a3b8", marginBottom:"2rem", fontSize:"0.9rem" }}>
              Puedo responder preguntas sobre la normativa LOTTTSV, conduccion segura y el catalogo de motos.
            </p>
            <div style={{ display:"flex", flexDirection:"column", gap:"0.5rem", maxWidth:"400px", margin:"0 auto" }}>
              <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>PREGUNTAS FRECUENTES</p>
              {PREGUNTAS_SUGERIDAS.map(p => (
                <button key={p} onClick={() => enviar(p)}
                  style={{
                    background:"#1e293b", border:"1px solid #334155", borderRadius:"8px",
                    padding:"0.75rem", color:"#cbd5e1", cursor:"pointer", textAlign:"left", fontSize:"0.85rem"
                  }}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {mensajes.map((msg, i) => (
          <div key={i} style={{
            display:"flex", justifyContent: msg.rol === "usuario" ? "flex-end" : "flex-start",
            marginBottom:"1rem"
          }}>
            <div style={{
              maxWidth:"80%",
              background: msg.rol === "usuario" ? "#1d4ed8" : "#1e293b",
              borderRadius: msg.rol === "usuario" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              padding:"1rem 1.25rem",
              border: msg.rol === "asistente" ? "1px solid #334155" : "none"
            }}>
              {msg.rol === "asistente" && (
                <p style={{ color:"#64748b", fontSize:"0.75rem", marginBottom:"0.5rem" }}>🤖 Asistente MotoEdu EC</p>
              )}
              <p style={{ color:"#f1f5f9", lineHeight:"1.6", margin:0, fontSize:"0.95rem" }}>
                {msg.texto}
              </p>
              {msg.fuentes && msg.fuentes.length > 0 && (
                <div style={{ marginTop:"0.75rem", paddingTop:"0.75rem", borderTop:"1px solid #334155" }}>
                  <p style={{ color:"#64748b", fontSize:"0.75rem", marginBottom:"0.25rem" }}>
                    📚 {msg.docs} documentos recuperados — Fuentes:
                  </p>
                  {msg.fuentes.slice(0,3).map((f,fi) => (
                    <span key={fi} style={{ background:"#0f172a", color:"#38bdf8", padding:"2px 6px", borderRadius:"4px", fontSize:"0.75rem", marginRight:"0.25rem" }}>
                      {f}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display:"flex", justifyContent:"flex-start", marginBottom:"1rem" }}>
            <div style={{ background:"#1e293b", borderRadius:"16px", padding:"1rem 1.5rem", border:"1px solid #334155" }}>
              <p style={{ color:"#94a3b8", margin:0 }}>🤖 Buscando en la normativa...</p>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* INPUT */}
      <div style={{ background:"#1e293b", padding:"1rem 1.5rem", borderTop:"1px solid #334155" }}>
        {mensajes.length > 0 && (
          <button onClick={limpiar}
            style={{ background:"none", border:"none", color:"#64748b", fontSize:"0.8rem", cursor:"pointer", marginBottom:"0.5rem" }}>
            🗑️ Nueva conversacion
          </button>
        )}
        <div style={{ display:"flex", gap:"0.75rem" }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && enviar(input)}
            placeholder="Pregunta sobre la normativa LOTTTSV, conduccion segura o motos..."
            disabled={loading}
            style={{
              flex:1, padding:"0.9rem 1.25rem", background:"#0f172a",
              border:"2px solid #334155", borderRadius:"12px", color:"#f1f5f9",
              fontSize:"0.95rem", outline:"none"
            }}
          />
          <button onClick={() => enviar(input)} disabled={loading || !input.trim()}
            style={{
              padding:"0.9rem 1.5rem", background: loading || !input.trim() ? "#334155" : "#3b82f6",
              border:"none", borderRadius:"12px", color:"#fff", cursor:"pointer", fontWeight:"bold", fontSize:"1.1rem"
            }}>
            ↑
          </button>
        </div>
        <p style={{ color:"#475569", fontSize:"0.75rem", marginTop:"0.5rem", textAlign:"center" }}>
          Respuestas basadas en ChromaDB + Claude API — Siempre verifica con fuentes oficiales
        </p>
      </div>
    </div>
  )
}
