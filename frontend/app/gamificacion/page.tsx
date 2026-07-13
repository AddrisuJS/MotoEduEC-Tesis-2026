'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const NIVELES = [
  { nivel:1, nombre:"Principiante",  min:0,    max:199,   color:"#94a3b8" },
  { nivel:2, nombre:"Basico",        min:200,  max:499,   color:"#22c55e" },
  { nivel:3, nombre:"Intermedio",    min:500,  max:999,   color:"#3b82f6" },
  { nivel:4, nombre:"Avanzado",      min:1000, max:1999,  color:"#f59e0b" },
  { nivel:5, nombre:"Experto Vial",  min:2000, max:99999, color:"#ec4899" },
]

export default function GamificacionPage() {
  const [insignias, setInsignias] = useState<any[]>([])
  const [dashboard, setDash]      = useState<any>(null)
  const [tab, setTab]             = useState<"dashboard"|"insignias"|"niveles">("dashboard")
  const [loading, setLoading]     = useState(true)

  const usuarioId = typeof window !== "undefined"
    ? localStorage.getItem("motoeduc_usuario_id")
    : null

  useEffect(() => {
    fetch(`${API}/m7/gamificacion/insignias`)
      .then(r => r.json())
      .then(d => setInsignias(d.insignias || []))

    if (usuarioId) {
      fetch(`${API}/m7/gamificacion/dashboard/${usuarioId}`)
        .then(r => r.json())
        .then(d => { setDash(d); setLoading(false) })
        .catch(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [usuarioId])

  const puntos  = dashboard?.puntos || 0
  const nivelAct = NIVELES.find(n => puntos >= n.min && puntos <= n.max) || NIVELES[0]
  const nivelSig = NIVELES[NIVELES.indexOf(nivelAct) + 1]
  const pct     = nivelSig ? Math.round(100 * (puntos - nivelAct.min) / (nivelSig.min - nivelAct.min)) : 100

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"800px", margin:"0 auto" }}>

        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>🏆 Gamificacion Edutainment</h1>
          <p style={{ color:"#94a3b8" }}>Aprende, completa modulos y sube de nivel</p>
        </div>

        {/* TABS */}
        <div style={{ display:"flex", gap:"0.75rem", marginBottom:"2rem" }}>
          {["dashboard","insignias","niveles"].map(t => (
            <button key={t} onClick={() => setTab(t as any)}
              style={{
                flex:1, padding:"0.6rem", borderRadius:"8px", cursor:"pointer",
                background: tab === t ? "#f97316" : "#1e293b",
                border: `1px solid ${tab === t ? "#f97316" : "#334155"}`,
                color: tab === t ? "#fff" : "#94a3b8", fontWeight: tab === t ? "bold" : "normal"
              }}>
              {t === "dashboard" ? "📊 Mi Progreso" : t === "insignias" ? "🏅 Insignias" : "⭐ Niveles"}
            </button>
          ))}
        </div>

        {/* DASHBOARD */}
        {tab === "dashboard" && (
          <div>
            {!usuarioId ? (
              <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", textAlign:"center", border:"1px solid #334155" }}>
                <p style={{ color:"#94a3b8", marginBottom:"1rem" }}>Completa tu perfil para ver tu progreso</p>
                <a href="/perfil" style={{ background:"#f97316", color:"#fff", padding:"0.75rem 2rem", borderRadius:"8px", textDecoration:"none", fontWeight:"bold" }}>
                  Crear mi perfil →
                </a>
              </div>
            ) : loading ? (
              <p style={{ color:"#94a3b8", textAlign:"center" }}>Cargando tu progreso...</p>
            ) : (
              <div>
                {/* Nivel actual */}
                <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", marginBottom:"1.5rem", border:`1px solid ${nivelAct.color}44` }}>
                  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1rem" }}>
                    <div>
                      <p style={{ color:"#64748b", fontSize:"0.8rem" }}>NIVEL ACTUAL</p>
                      <h2 style={{ color: nivelAct.color, fontSize:"1.8rem", fontWeight:"bold" }}>{nivelAct.nombre}</h2>
                    </div>
                    <div style={{ textAlign:"right" }}>
                      <p style={{ color:"#64748b", fontSize:"0.8rem" }}>PUNTOS</p>
                      <h2 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold" }}>{puntos}</h2>
                    </div>
                  </div>
                  {nivelSig && (
                    <>
                      <div style={{ background:"#0f172a", borderRadius:"100px", height:"8px", marginBottom:"0.5rem" }}>
                        <div style={{ background: nivelAct.color, height:"100%", borderRadius:"100px", width:`${pct}%`, transition:"width 0.5s" }} />
                      </div>
                      <p style={{ color:"#64748b", fontSize:"0.8rem" }}>
                        {nivelSig.min - puntos} puntos para {nivelSig.nombre}
                      </p>
                    </>
                  )}
                </div>

                {/* Stats */}
                <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:"1rem", marginBottom:"1.5rem" }}>
                  {[
                    { label:"Evaluaciones", valor: dashboard?.evaluaciones?.total_respuestas || 0, icon:"📝" },
                    { label:"Correctas",    valor: dashboard?.evaluaciones?.correctas || 0,         icon:"✅" },
                    { label:"% Acierto",    valor: `${dashboard?.evaluaciones?.pct_acierto || 0}%`, icon:"🎯" },
                  ].map(s => (
                    <div key={s.label} style={{ background:"#1e293b", borderRadius:"12px", padding:"1.25rem", textAlign:"center", border:"1px solid #334155" }}>
                      <div style={{ fontSize:"1.5rem" }}>{s.icon}</div>
                      <div style={{ color:"#f1f5f9", fontSize:"1.5rem", fontWeight:"bold" }}>{s.valor}</div>
                      <div style={{ color:"#64748b", fontSize:"0.8rem" }}>{s.label}</div>
                    </div>
                  ))}
                </div>

                <a href="/educacion" style={{
                  display:"block", padding:"1rem", background:"#f97316", borderRadius:"10px",
                  color:"#fff", textAlign:"center", fontWeight:"bold", textDecoration:"none"
                }}>
                  📚 Ir a Educacion Vial para ganar puntos →
                </a>
              </div>
            )}
          </div>
        )}

        {/* INSIGNIAS */}
        {tab === "insignias" && (
          <div>
            <p style={{ color:"#94a3b8", marginBottom:"1.5rem" }}>{insignias.length} insignias disponibles para desbloquear</p>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(200px,1fr))", gap:"1rem" }}>
              {insignias.map((ins: any) => (
                <div key={ins.id} style={{ background:"#1e293b", borderRadius:"12px", padding:"1.25rem", textAlign:"center", border:"1px solid #334155" }}>
                  <div style={{ fontSize:"2.5rem", marginBottom:"0.5rem" }}>{ins.icono}</div>
                  <h3 style={{ color:"#f1f5f9", fontSize:"0.95rem", marginBottom:"0.25rem" }}>{ins.nombre}</h3>
                  <p style={{ color:"#94a3b8", fontSize:"0.8rem", marginBottom:"0.75rem" }}>{ins.descripcion}</p>
                  <span style={{ background:"#f9731622", color:"#f97316", padding:"2px 10px", borderRadius:"20px", fontSize:"0.8rem", fontWeight:"bold" }}>
                    +{ins.puntos} pts
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* NIVELES */}
        {tab === "niveles" && (
          <div>
            {NIVELES.map((n, i) => (
              <div key={n.nivel} style={{
                background:"#1e293b", borderRadius:"12px", padding:"1.25rem", marginBottom:"1rem",
                border: `2px solid ${n.nivel === nivelAct.nivel ? n.color : "#334155"}`
              }}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                  <div style={{ display:"flex", alignItems:"center", gap:"1rem" }}>
                    <span style={{ background:`${n.color}22`, color:n.color, padding:"6px 14px", borderRadius:"8px", fontWeight:"bold" }}>
                      Nivel {n.nivel}
                    </span>
                    <h3 style={{ color:"#f1f5f9" }}>{n.nombre}</h3>
                    {n.nivel === nivelAct.nivel && (
                      <span style={{ background:"#22c55e22", color:"#22c55e", padding:"2px 8px", borderRadius:"4px", fontSize:"0.75rem" }}>TU NIVEL</span>
                    )}
                  </div>
                  <span style={{ color:"#64748b", fontSize:"0.85rem" }}>{n.min} — {n.max === 99999 ? "∞" : n.max} pts</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
