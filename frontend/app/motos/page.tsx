'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const TIPOS_USO = ["delivery","urbano","touring","aventura","enduro","deportivo"]
const ZONAS     = ["Sierra","Costa","Amazonia"]

export default function MotosPage() {
  const [modo, setModo]           = useState<"recomendador"|"catalogo">("recomendador")
  const [perfil, setPerfil]       = useState({ tipo_uso:"urbano", anos_experiencia:1, presupuesto_max:3000, zona:"Sierra" })
  const [resultado, setResultado] = useState<any>(null)
  const [catalogo, setCatalogo]   = useState<any[]>([])
  const [loading, setLoading]     = useState(false)
  const [filtro, setFiltro]       = useState({ tipo:"", marca:"", precio:10000 })

  const recomendar = async () => {
    setLoading(true)
    try {
      const r = await fetch(`${API}/m4/motos/recomendar`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify({ perfil })
      })
      setResultado(await r.json())
    } catch { setResultado(null) }
    setLoading(false)
  }

  const cargarCatalogo = async () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (filtro.tipo)  params.append("tipo",  filtro.tipo)
    if (filtro.marca) params.append("marca", filtro.marca)
    if (filtro.precio < 10000) params.append("precio", String(filtro.precio))
    try {
      const r = await fetch(`${API}/m4/motos/catalogo?${params}`)
      const d = await r.json()
      setCatalogo(d.motos || [])
    } catch { setCatalogo([]) }
    setLoading(false)
  }

  useEffect(() => { if (modo === "catalogo") cargarCatalogo() }, [modo])

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"900px", margin:"0 auto" }}>

        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>🏍️ Recomendador de Motos</h1>
          <p style={{ color:"#94a3b8" }}>48 modelos disponibles en Ecuador 2024-2026</p>
        </div>

        {/* TABS */}
        <div style={{ display:"flex", gap:"1rem", marginBottom:"2rem" }}>
          {["recomendador","catalogo"].map(m => (
            <button key={m} onClick={() => setModo(m as any)}
              style={{
                flex:1, padding:"0.75rem", borderRadius:"10px", cursor:"pointer", fontWeight:"bold",
                background: modo === m ? "#3b82f6" : "#1e293b",
                border: `1px solid ${modo === m ? "#3b82f6" : "#334155"}`,
                color: modo === m ? "#fff" : "#94a3b8"
              }}>
              {m === "recomendador" ? "🤖 Recomendador IA" : "📋 Catalogo Completo"}
            </button>
          ))}
        </div>

        {/* RECOMENDADOR */}
        {modo === "recomendador" && (
          <div>
            <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", border:"1px solid #334155", marginBottom:"1.5rem" }}>
              <h2 style={{ color:"#f1f5f9", marginBottom:"1.5rem" }}>Configura tu perfil</h2>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"1rem" }}>
                <div>
                  <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Tipo de uso</label>
                  <select value={perfil.tipo_uso} onChange={e => setPerfil(p => ({...p, tipo_uso: e.target.value}))}
                    style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                    {TIPOS_USO.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Anos de experiencia</label>
                  <input type="number" min="0" max="30" value={perfil.anos_experiencia}
                    onChange={e => setPerfil(p => ({...p, anos_experiencia: parseInt(e.target.value)||0}))}
                    style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }} />
                </div>
                <div>
                  <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Presupuesto maximo (USD)</label>
                  <input type="number" min="500" max="25000" value={perfil.presupuesto_max}
                    onChange={e => setPerfil(p => ({...p, presupuesto_max: parseInt(e.target.value)||3000}))}
                    style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }} />
                </div>
                <div>
                  <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Zona geografica</label>
                  <select value={perfil.zona} onChange={e => setPerfil(p => ({...p, zona: e.target.value}))}
                    style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                    {ZONAS.map(z => <option key={z} value={z}>{z}</option>)}
                  </select>
                </div>
              </div>
              <button onClick={recomendar} disabled={loading}
                style={{ width:"100%", marginTop:"1.5rem", padding:"1rem", background: loading ? "#334155" : "#f59e0b", border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontWeight:"bold", fontSize:"1rem" }}>
                {loading ? "Analizando catalogo..." : "🤖 Recomendar motos con IA →"}
              </button>
            </div>

            {resultado && (
              <div>
                <p style={{ color:"#94a3b8", fontSize:"0.85rem", marginBottom:"1rem" }}>
                  Analizado {resultado.catalogo_consultado} motos del tipo {resultado.tipos_buscados?.join(", ")}
                </p>
                {resultado.recomendaciones?.map((rec: any, i: number) => (
                  <div key={i} style={{ background:"#1e293b", borderRadius:"12px", padding:"1.5rem", marginBottom:"1rem", border:"1px solid #334155" }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"0.75rem" }}>
                      <h3 style={{ color:"#f1f5f9" }}>#{i+1} {rec.moto}</h3>
                      <span style={{ color:"#22c55e", fontWeight:"bold" }}>${rec.precio_usd?.toLocaleString()}</span>
                    </div>
                    <p style={{ color:"#94a3b8", marginBottom:"0.5rem", fontSize:"0.9rem" }}>{rec.justificacion}</p>
                    {rec.ventaja_principal && (
                      <span style={{ background:"#16a34a22", color:"#22c55e", padding:"4px 10px", borderRadius:"6px", fontSize:"0.8rem" }}>
                        ✅ {rec.ventaja_principal}
                      </span>
                    )}
                  </div>
                ))}
                {resultado.razonamiento && (
                  <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1rem", border:"1px solid #f59e0b44" }}>
                    <p style={{ color:"#f59e0b", fontSize:"0.8rem", marginBottom:"0.25rem" }}>RAZONAMIENTO IA</p>
                    <p style={{ color:"#cbd5e1", fontSize:"0.9rem" }}>{resultado.razonamiento}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* CATALOGO */}
        {modo === "catalogo" && (
          <div>
            <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1rem", marginBottom:"1.5rem", display:"flex", gap:"1rem", flexWrap:"wrap" }}>
              <input placeholder="Filtrar por tipo..." value={filtro.tipo}
                onChange={e => setFiltro(f => ({...f, tipo: e.target.value}))}
                style={{ flex:1, minWidth:"150px", padding:"0.6rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9" }} />
              <input placeholder="Filtrar por marca..." value={filtro.marca}
                onChange={e => setFiltro(f => ({...f, marca: e.target.value}))}
                style={{ flex:1, minWidth:"150px", padding:"0.6rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9" }} />
              <button onClick={cargarCatalogo}
                style={{ padding:"0.6rem 1.5rem", background:"#3b82f6", border:"none", borderRadius:"8px", color:"#fff", cursor:"pointer" }}>
                Filtrar
              </button>
            </div>
            <p style={{ color:"#64748b", fontSize:"0.85rem", marginBottom:"1rem" }}>{catalogo.length} motos encontradas</p>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(280px,1fr))", gap:"1rem" }}>
              {catalogo.map((m: any) => (
                <div key={m.id} style={{ background:"#1e293b", borderRadius:"12px", padding:"1.25rem", border:"1px solid #334155" }}>
                  <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"0.5rem" }}>
                    <span style={{ color:"#64748b", fontSize:"0.75rem" }}>{m.tipo}</span>
                    <span style={{ color:"#22c55e", fontWeight:"bold" }}>${m.precio_usd?.toLocaleString()}</span>
                  </div>
                  <h3 style={{ color:"#f1f5f9", marginBottom:"0.25rem" }}>{m.marca} {m.modelo}</h3>
                  <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.75rem" }}>{m.anio} • {m.cilindrada_cc}cc • {m.potencia_hp}HP</p>
                  <p style={{ color:"#94a3b8", fontSize:"0.8rem" }}>{m.uso_recomendado}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
