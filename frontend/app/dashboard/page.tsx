'use client'
import { useState, useEffect, useRef } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

// Colores del sistema
const COLORES_PERFILES: Record<string, string> = {
  "delivery":  "#ef4444",
  "urbano":    "#3b82f6",
  "touring":   "#f59e0b",
  "aventura":  "#10b981",
  "enduro":    "#8b5cf6",
  "deportivo": "#ec4899",
}

const COLORES_CHART = ["#3b82f6","#ef4444","#f59e0b","#10b981","#8b5cf6","#ec4899","#06b6d4"]

export default function DashboardPage() {
  const [datos, setDatos]       = useState<any>(null)
  const [loading, setLoading]   = useState(true)
  const [resumen, setResumen]   = useState<any>(null)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/estadisticas/resumen`).then(r => r.json()),
      fetch(`${API}/estadisticas/brechas`).then(r => r.json()),
      fetch(`${API}/m1/perfil/perfiles`).then(r => r.json()),
      fetch(`${API}/m7/gamificacion/insignias`).then(r => r.json()),
    ]).then(([res, brechas, perfiles, insignias]) => {
      setResumen(res.resumen)
      setDatos({ brechas: brechas.brechas, perfiles: perfiles.perfiles, insignias: insignias.insignias })
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return (
    <div style={{ minHeight:"100vh", background:"#0f172a", display:"flex", alignItems:"center", justifyContent:"center" }}>
      <p style={{ color:"#94a3b8", fontSize:"1.2rem" }}>Cargando dashboard analitico...</p>
    </div>
  )

  const brechasAlto  = datos?.brechas?.filter((b: any) => b.nivel_riesgo === "ALTO") || []
  const brechasMedio = datos?.brechas?.filter((b: any) => b.nivel_riesgo === "MEDIO") || []

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"1.5rem" }}>

      {/* HEADER */}
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"2rem" }}>
        <div>
          <a href="/" style={{ color:"#64748b", fontSize:"0.8rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"1.8rem", fontWeight:"bold", marginTop:"0.25rem" }}>
            📊 Dashboard Analitico — MotoEdu EC
          </h1>
          <p style={{ color:"#64748b", fontSize:"0.85rem" }}>Edutainment Integration Panel — UPS Cuenca 2026</p>
        </div>
        <div style={{ textAlign:"right" }}>
          <div style={{ width:"10px", height:"10px", borderRadius:"50%", background:"#22c55e", display:"inline-block", marginRight:"6px" }}></div>
          <span style={{ color:"#22c55e", fontSize:"0.85rem", fontWeight:"bold" }}>Sistema Activo</span>
        </div>
      </div>

      {/* KPIs PRINCIPALES */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(180px,1fr))", gap:"1rem", marginBottom:"2rem" }}>
        {[
          { label:"Motocicletas",    valor: resumen?.motocicletas || 0,            icon:"🏍️", color:"#3b82f6" },
          { label:"Preguntas Viales",valor: resumen?.preguntas_viales || 0,        icon:"❓", color:"#f59e0b" },
          { label:"Usuarios",        valor: resumen?.usuarios || 0,                icon:"👤", color:"#10b981" },
          { label:"Evaluaciones",    valor: resumen?.historial_evaluaciones || 0,  icon:"📝", color:"#8b5cf6" },
          { label:"Brechas Criticas",valor: resumen?.brechas_conocimiento || 0,    icon:"⚠️", color:"#ef4444" },
          { label:"Llantas",         valor: resumen?.llantas || 0,                 icon:"🔵", color:"#06b6d4" },
        ].map(k => (
          <div key={k.label} style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"12px", padding:"1.25rem", border:`1px solid ${k.color}33`, textAlign:"center" }}>
            <div style={{ fontSize:"1.8rem" }}>{k.icon}</div>
            <div style={{ color: k.color, fontSize:"2rem", fontWeight:"bold" }}>{k.valor}</div>
            <div style={{ color:"#64748b", fontSize:"0.8rem" }}>{k.label}</div>
          </div>
        ))}
      </div>

      {/* FILA 1: BRECHAS + PERFILES */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(300px, 1fr))", gap:"1.5rem", marginBottom:"1.5rem" }}>

        {/* Mapa de Brechas */}
        <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"1.5rem", border:"1px solid #334155" }}>
          <h2 style={{ color:"#f1f5f9", marginBottom:"1.25rem", fontSize:"1.1rem" }}>⚠️ Mapa de Brechas de Conocimiento</h2>
          {datos?.brechas?.slice(0,8).map((b: any, i: number) => (
            <div key={i} style={{ marginBottom:"0.75rem" }}>
              <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"4px" }}>
                <span style={{ color:"#cbd5e1", fontSize:"0.82rem", maxWidth:"70%" }}>{b.descripcion?.slice(0,45)}...</span>
                <span style={{
                  color: b.nivel_riesgo === "ALTO" ? "#ef4444" : "#f59e0b",
                  fontSize:"0.75rem", fontWeight:"bold"
                }}>{b.pct_con_brecha}%</span>
              </div>
              <div style={{ background:"#0f172a", borderRadius:"100px", height:"6px" }}>
                <div style={{
                  background: b.nivel_riesgo === "ALTO" ? "#ef4444" : "#f59e0b",
                  height:"100%", borderRadius:"100px",
                  width:`${Math.min(b.pct_con_brecha || 0, 100)}%`,
                  transition:"width 0.8s ease"
                }} />
              </div>
            </div>
          ))}
          <div style={{ display:"flex", gap:"1rem", marginTop:"1rem" }}>
            <span style={{ background:"#ef444422", color:"#ef4444", padding:"4px 10px", borderRadius:"6px", fontSize:"0.75rem" }}>
              ● {brechasAlto.length} ALTO riesgo
            </span>
            <span style={{ background:"#f59e0b22", color:"#f59e0b", padding:"4px 10px", borderRadius:"6px", fontSize:"0.75rem" }}>
              ● {brechasMedio.length} MEDIO riesgo
            </span>
          </div>
        </div>

        {/* Perfiles de Motociclistas */}
        <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"1.5rem", border:"1px solid #334155" }}>
          <h2 style={{ color:"#f1f5f9", marginBottom:"1.25rem", fontSize:"1.1rem" }}>👤 Perfiles de Motociclistas</h2>
          <div style={{ display:"flex", flexDirection:"column", gap:"0.75rem" }}>
            {datos?.perfiles && Object.entries(datos.perfiles).map(([key, perfil]: any, i) => (
              <div key={key} style={{ display:"flex", alignItems:"center", gap:"0.75rem" }}>
                <div style={{ width:"12px", height:"12px", borderRadius:"50%", background: COLORES_PERFILES[key] || COLORES_CHART[i], flexShrink:0 }} />
                <div style={{ flex:1 }}>
                  <div style={{ display:"flex", justifyContent:"space-between" }}>
                    <span style={{ color:"#f1f5f9", fontSize:"0.85rem", fontWeight:"bold" }}>{perfil.nombre}</span>
                    <span style={{ color: perfil.nivel_riesgo === "ALTO" ? "#ef4444" : "#f59e0b", fontSize:"0.75rem" }}>
                      {perfil.nivel_riesgo}
                    </span>
                  </div>
                  <p style={{ color:"#64748b", fontSize:"0.75rem", margin:0 }}>{perfil.velocidad_tipica_kmh} km/h tipico</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* FILA 2: INSIGNIAS + MODULOS */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(320px, 1fr))", gap:"1.5rem", marginBottom:"1.5rem" }}>

        {/* Insignias disponibles */}
        <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"1.5rem", border:"1px solid #334155" }}>
          <h2 style={{ color:"#f1f5f9", marginBottom:"1.25rem", fontSize:"1.1rem" }}>🏅 Sistema de Insignias ({datos?.insignias?.length || 0} disponibles)</h2>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(140px,1fr))", gap:"0.75rem" }}>
            {datos?.insignias?.map((ins: any) => (
              <div key={ins.id} style={{ background:"#0f172a", borderRadius:"10px", padding:"0.75rem", textAlign:"center", border:"1px solid #334155" }}>
                <div style={{ fontSize:"1.5rem" }}>{ins.icono}</div>
                <p style={{ color:"#f1f5f9", fontSize:"0.75rem", margin:"4px 0 2px" }}>{ins.nombre}</p>
                <span style={{ color:"#f97316", fontSize:"0.7rem" }}>+{ins.puntos} pts</span>
              </div>
            ))}
          </div>
        </div>

        {/* Estado del sistema */}
        <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"1.5rem", border:"1px solid #334155" }}>
          <h2 style={{ color:"#f1f5f9", marginBottom:"1.25rem", fontSize:"1.1rem" }}>🔧 Estado del Sistema</h2>
          {[
            { modulo:"M1 Perfil",      estado:"Activo",         color:"#22c55e" },
            { modulo:"M2 Educacion",   estado:"Mock activo",    color:"#f59e0b" },
            { modulo:"M3 RAG",         estado:"ChromaDB OK",    color:"#22c55e" },
            { modulo:"M4 Motos",       estado:"48 modelos",     color:"#22c55e" },
            { modulo:"M5 Llantas",     estado:"16 modelos",     color:"#22c55e" },
            { modulo:"M6 Historia",    estado:"Mock activo",    color:"#f59e0b" },
            { modulo:"M7 Gamificacion",estado:"12 insignias",   color:"#22c55e" },
            { modulo:"Claude API",     estado:"Pendiente key",  color:"#ef4444" },
            { modulo:"PostgreSQL",     estado:"Healthy",        color:"#22c55e" },
            { modulo:"ChromaDB",       estado:"200 docs",       color:"#22c55e" },
          ].map(s => (
            <div key={s.modulo} style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"0.5rem" }}>
              <span style={{ color:"#94a3b8", fontSize:"0.8rem" }}>{s.modulo}</span>
              <span style={{ background:`${s.color}22`, color:s.color, padding:"2px 8px", borderRadius:"4px", fontSize:"0.72rem", fontWeight:"bold" }}>
                {s.estado}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* FILA 3: NIVELES DE COMPETENCIA */}
      <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"1.5rem", border:"1px solid #334155", marginBottom:"1.5rem" }}>
        <h2 style={{ color:"#f1f5f9", marginBottom:"1.25rem", fontSize:"1.1rem" }}>⭐ Niveles de Competencia Vial</h2>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(140px, 1fr))", gap:"1rem" }}>
          {[
            { nivel:1, nombre:"Principiante", min:0,   color:"#94a3b8", desc:"0 — 199 pts" },
            { nivel:2, nombre:"Basico",       min:200, color:"#22c55e", desc:"200 — 499 pts" },
            { nivel:3, nombre:"Intermedio",   min:500, color:"#3b82f6", desc:"500 — 999 pts" },
            { nivel:4, nombre:"Avanzado",     min:1000,color:"#f59e0b", desc:"1000 — 1999 pts" },
            { nivel:5, nombre:"Experto Vial", min:2000,color:"#ec4899", desc:"2000+ pts" },
          ].map(n => (
            <div key={n.nivel} style={{ background:"#0f172a", borderRadius:"12px", padding:"1rem", textAlign:"center", border:`2px solid ${n.color}44` }}>
              <div style={{ color:n.color, fontSize:"1.8rem", fontWeight:"bold" }}>{n.nivel}</div>
              <div style={{ color:"#f1f5f9", fontWeight:"bold", fontSize:"0.9rem" }}>{n.nombre}</div>
              <div style={{ color:"#64748b", fontSize:"0.75rem", marginTop:"4px" }}>{n.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* FILA 4: INFO TESIS */}
      <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"1.5rem", border:"1px solid #334155" }}>
        <h2 style={{ color:"#f1f5f9", marginBottom:"1rem", fontSize:"1.1rem" }}>🎓 Informacion del Proyecto</h2>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(240px, 1fr))", gap:"1rem" }}>
          {[
            { label:"Proyecto",    valor:"MotoEdu EC" },
            { label:"Institucion", valor:"UPS Cuenca 2026" },
            { label:"Estudiante",  valor:"Sanango Romero J.A." },
            { label:"Tutor",       valor:"Omar Bravo Ph.D" },
            { label:"Sprint",      valor:"Sprint 3 en progreso" },
            { label:"Entrega",     valor:"15 julio 2026" },
          ].map(i => (
            <div key={i.label} style={{ background:"#0f172a", borderRadius:"8px", padding:"0.75rem" }}>
              <p style={{ color:"#64748b", fontSize:"0.75rem", marginBottom:"2px" }}>{i.label}</p>
              <p style={{ color:"#f1f5f9", fontSize:"0.9rem", fontWeight:"bold", margin:0 }}>{i.valor}</p>
            </div>
          ))}
        </div>
      </div>

      <p style={{ color:"#334155", textAlign:"center", fontSize:"0.75rem", marginTop:"1.5rem" }}>
        MotoEdu EC Dashboard v1.0 — Sprint 3 — UPS Cuenca 2026
      </p>
    </div>
  )
}
