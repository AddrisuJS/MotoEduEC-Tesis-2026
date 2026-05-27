'use client'
import { useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const TIPOS_MOTO = ["utilitaria","scooter","naked","deportiva","touring","aventura","enduro","doble"]
const USOS       = ["ciudad","carretera","offroad","lluvia"]
const CLIMAS     = ["seco","lluvia","variado"]
const GAMAS      = ["economica","media","alta"]

const ALERTA_COLOR: Record<string,string> = {
  "Sport":           "#ef4444",
  "Off-road/Enduro": "#f59e0b",
  "Lluvia/Rain":     "#3b82f6",
  "Carretera (Road)":"#22c55e",
  "Trail/Adventure": "#10b981",
  "Scooter":         "#8b5cf6",
}

export default function LlantasPage() {
  const [form, setForm]       = useState({ tipo_moto:"utilitaria", uso:"ciudad", clima:"seco", gama:"media", presupuesto_max:100 })
  const [resultado, setRes]   = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState("")

  const recomendar = async () => {
    setLoading(true); setError("")
    try {
      const r = await fetch(`${API}/m5/llantas/recomendar`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify(form)
      })
      const d = await r.json()
      setRes(d)
    } catch { setError("Error conectando con la API") }
    setLoading(false)
  }

  const alertColor = resultado ? (ALERTA_COLOR[resultado.tipo_llanta_recomendada] || "#94a3b8") : "#94a3b8"

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"800px", margin:"0 auto" }}>

        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>🔵 Recomendador de Llantas</h1>
          <p style={{ color:"#94a3b8" }}>Encuentra la llanta correcta para tu moto y condiciones</p>
        </div>

        {/* FORMULARIO */}
        <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", border:"1px solid #334155", marginBottom:"1.5rem" }}>
          <h2 style={{ color:"#f1f5f9", marginBottom:"1.5rem" }}>Configura tu busqueda</h2>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"1rem" }}>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Tipo de moto</label>
              <select value={form.tipo_moto} onChange={e => setForm(f => ({...f, tipo_moto: e.target.value}))}
                style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                {TIPOS_MOTO.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Uso principal</label>
              <select value={form.uso} onChange={e => setForm(f => ({...f, uso: e.target.value}))}
                style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                {USOS.map(u => <option key={u} value={u}>{u}</option>)}
              </select>
            </div>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Condicion climatica</label>
              <select value={form.clima} onChange={e => setForm(f => ({...f, clima: e.target.value}))}
                style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                {CLIMAS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Gama de presupuesto</label>
              <select value={form.gama} onChange={e => setForm(f => ({...f, gama: e.target.value}))}
                style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                {GAMAS.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>

            <div style={{ gridColumn:"1/-1" }}>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Presupuesto maximo por llanta (USD)</label>
              <div style={{ display:"flex", alignItems:"center", gap:"1rem", marginTop:"0.25rem" }}>
                <input type="range" min="20" max="250" value={form.presupuesto_max}
                  onChange={e => setForm(f => ({...f, presupuesto_max: parseInt(e.target.value)}))}
                  style={{ flex:1 }} />
                <span style={{ color:"#f1f5f9", fontWeight:"bold", minWidth:"60px" }}>${form.presupuesto_max}</span>
              </div>
            </div>
          </div>

          <button onClick={recomendar} disabled={loading}
            style={{
              width:"100%", marginTop:"1.5rem", padding:"1rem",
              background: loading ? "#334155" : "#06b6d4",
              border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontWeight:"bold", fontSize:"1rem"
            }}>
            {loading ? "Buscando llantas..." : "🔵 Recomendar llantas →"}
          </button>
          {error && <p style={{ color:"#ef4444", textAlign:"center", marginTop:"0.5rem" }}>{error}</p>}
        </div>

        {/* RESULTADO */}
        {resultado && (
          <div>
            {/* Tipo recomendado */}
            <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1.5rem", marginBottom:"1rem", border:`2px solid ${alertColor}44` }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"0.75rem" }}>
                <div>
                  <p style={{ color:"#64748b", fontSize:"0.8rem" }}>TIPO DE LLANTA RECOMENDADA</p>
                  <h2 style={{ color: alertColor, fontSize:"1.5rem" }}>{resultado.tipo_llanta_recomendada}</h2>
                </div>
                <span style={{ background:`${alertColor}22`, color: alertColor, padding:"6px 14px", borderRadius:"20px", fontSize:"0.85rem" }}>
                  {resultado.gama}
                </span>
              </div>
              <p style={{ color:"#cbd5e1", fontSize:"0.9rem", marginBottom:"0.75rem" }}>{resultado.consejo}</p>
              <div style={{ background:"#0f172a", borderRadius:"8px", padding:"0.75rem", borderLeft:`3px solid ${alertColor}` }}>
                <p style={{ color:"#64748b", fontSize:"0.75rem", marginBottom:"0.25rem" }}>⚠️ ALERTA DE SEGURIDAD</p>
                <p style={{ color:"#e2e8f0", fontSize:"0.85rem" }}>{resultado.alerta_seguridad}</p>
              </div>
            </div>

            {/* Opciones */}
            {resultado.opciones?.length > 0 ? (
              <div>
                <p style={{ color:"#64748b", fontSize:"0.85rem", marginBottom:"1rem" }}>
                  {resultado.opciones.length} opciones encontradas
                </p>
                {resultado.opciones.map((ll: any, i: number) => (
                  <div key={i} style={{ background:"#1e293b", borderRadius:"12px", padding:"1.25rem", marginBottom:"0.75rem", border:"1px solid #334155" }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                      <div>
                        <h3 style={{ color:"#f1f5f9" }}>{ll.marca} {ll.modelo}</h3>
                        <p style={{ color:"#94a3b8", fontSize:"0.85rem" }}>{ll.medida_ejemplo} • Gama {ll.gama}</p>
                      </div>
                      <div style={{ textAlign:"right" }}>
                        <p style={{ color:"#22c55e", fontWeight:"bold" }}>${ll.precio_min_usd} — ${ll.precio_max_usd}</p>
                        <p style={{ color:"#64748b", fontSize:"0.75rem" }}>por llanta</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1.5rem", textAlign:"center" }}>
                <p style={{ color:"#94a3b8" }}>No se encontraron llantas con esos filtros. Intenta con otra gama o presupuesto mayor.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
