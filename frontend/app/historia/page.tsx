'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const TEMAS = [
  { id:1, titulo:"Los inicios del motociclismo en Ecuador",        epoca:"1900-1970", icono:"🏛️" },
  { id:2, titulo:"La llegada de las marcas japonesas",             epoca:"1970-2000", icono:"🇯🇵" },
  { id:3, titulo:"El boom del delivery y la era digital",          epoca:"2000-2020", icono:"📱" },
  { id:4, titulo:"El record historico de 2025: 274.729 motos",     epoca:"2020-2026", icono:"📈" },
  { id:5, titulo:"La Federacion Ecuatoriana de Motociclismo",      epoca:"2000-2026", icono:"🏆" },
  { id:6, titulo:"La cultura motera: clubes, rodadas y comunidad", epoca:"1990-2026", icono:"🤝" },
]

export default function HistoriaPage() {
  const [seleccionado, setSel] = useState<any>(null)
  const [contenido, setCont]   = useState<any>(null)
  const [loading, setLoading]  = useState(false)

  const cargarTema = async (tema: any) => {
    setSel(tema); setLoading(true); setCont(null)
    try {
      const r = await fetch(`${API}/m6/historia/${tema.id}`)
      const d = await r.json()
      setCont(d.contenido)
    } catch {}
    setLoading(false)
  }

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"800px", margin:"0 auto" }}>
        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>🏛️ Historia Motera Ecuatoriana</h1>
          <p style={{ color:"#94a3b8" }}>De los primeros caballos de acero al record de 274.729 motos en 2025</p>
        </div>

        {!seleccionado ? (
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"1rem" }}>
            {TEMAS.map(t => (
              <button key={t.id} onClick={() => cargarTema(t)}
                style={{
                  background:"#1e293b", border:"1px solid #334155", borderRadius:"12px",
                  padding:"1.5rem", cursor:"pointer", textAlign:"left", color:"#f1f5f9"
                }}
                onMouseEnter={e => (e.currentTarget.style.borderColor="#ec4899")}
                onMouseLeave={e => (e.currentTarget.style.borderColor="#334155")}>
                <div style={{ fontSize:"2rem", marginBottom:"0.75rem" }}>{t.icono}</div>
                <h3 style={{ marginBottom:"0.5rem", fontSize:"0.95rem" }}>{t.titulo}</h3>
                <span style={{ background:"#ec489922", color:"#ec4899", padding:"2px 8px", borderRadius:"6px", fontSize:"0.75rem" }}>{t.epoca}</span>
              </button>
            ))}
          </div>
        ) : (
          <div>
            <button onClick={() => setSel(null)}
              style={{ background:"none", border:"none", color:"#64748b", cursor:"pointer", marginBottom:"1rem" }}>
              ← Volver a temas
            </button>
            <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", border:"1px solid #334155" }}>
              <div style={{ fontSize:"3rem", marginBottom:"1rem", textAlign:"center" }}>{seleccionado.icono}</div>
              <h2 style={{ color:"#f1f5f9", fontSize:"1.4rem", marginBottom:"0.5rem", textAlign:"center" }}>{seleccionado.titulo}</h2>
              <span style={{ display:"block", textAlign:"center", background:"#ec489922", color:"#ec4899", padding:"4px 12px", borderRadius:"20px", fontSize:"0.85rem", marginBottom:"1.5rem" }}>
                {seleccionado.epoca}
              </span>
              {loading ? (
                <div style={{ textAlign:"center", padding:"2rem" }}>
                  <p style={{ color:"#94a3b8" }}>🤖 Generando narrativa historica...</p>
                </div>
              ) : contenido ? (
                <>
                  <h3 style={{ color:"#ec4899", marginBottom:"1rem" }}>{contenido.titulo}</h3>
                  <p style={{ color:"#cbd5e1", lineHeight:"1.7", marginBottom:"1.5rem" }}>{contenido.narrativa}</p>
                  {contenido.datos_clave && (
                    <div style={{ background:"#0f172a", borderRadius:"8px", padding:"1rem" }}>
                      <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>DATOS CLAVE</p>
                      {contenido.datos_clave.map((d: string, i: number) => (
                        <p key={i} style={{ color:"#f1f5f9", fontSize:"0.9rem", marginBottom:"0.25rem" }}>📊 {d}</p>
                      ))}
                    </div>
                  )}
                </>
              ) : <p style={{ color:"#ef4444" }}>Error cargando la narrativa.</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
