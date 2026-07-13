'use client'
import { useState } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const TIPOS_MOTO = [
  { valor:"utilitaria",  label:"🛵 Utilitaria" },
  { valor:"scooter",     label:"🛺 Scooter" },
  { valor:"naked",       label:"🏍️ Naked/Street" },
  { valor:"deportiva",   label:"🏎️ Deportiva" },
  { valor:"touring",     label:"🗺️ Touring/Adventure" },
  { valor:"aventura",    label:"⛰️ Aventura Off-road" },
  { valor:"enduro",      label:"🏁 Enduro" },
  { valor:"doble",       label:"🛤️ Doble Proposito" },
]
const USOS   = ["ciudad","carretera","offroad","lluvia"]
const CLIMAS = ["seco","lluvia","variado"]
const GAMAS  = ["economica","media","alta"]

// Severidad de la alerta segun tipo de llanta
const SEVERIDAD: Record<string,{nivel:string,color:string,bg:string,icono:string}> = {
  "Sport":           {nivel:"CRITICO",    color:"#ef4444", bg:"#ef444422", icono:"🔴"},
  "Off-road/Enduro": {nivel:"ADVERTENCIA",color:"#f59e0b", bg:"#f59e0b22", icono:"🟡"},
  "Lluvia/Rain":     {nivel:"INFORMACION",color:"#3b82f6", bg:"#3b82f622", icono:"🔵"},
  "Carretera (Road)":{nivel:"OK",         color:"#22c55e", bg:"#22c55e22", icono:"🟢"},
  "Trail/Adventure": {nivel:"OK",         color:"#22c55e", bg:"#22c55e22", icono:"🟢"},
  "Scooter":         {nivel:"INFORMACION",color:"#8b5cf6", bg:"#8b5cf622", icono:"🟣"},
}

export default function LlantasPage() {
  const [form, setForm]       = useState({ tipo_moto:"utilitaria", uso:"ciudad", clima:"seco", gama:"media", presupuesto_max:100 })
  const [resultado, setRes]   = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState("")
  const [llantaSel, setLSel]  = useState<any>(null)

  const recomendar = async () => {
    setLoading(true); setError(""); setRes(null); setLSel(null)
    try {
      const r = await fetch(`${API}/m5/llantas/recomendar`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify(form)
      })
      setRes(await r.json())
    } catch { setError("Error conectando con la API") }
    setLoading(false)
  }

  const sev = resultado ? (SEVERIDAD[resultado.tipo_llanta_recomendada] || SEVERIDAD["Carretera (Road)"]) : null

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"800px", margin:"0 auto" }}>

        {/* HEADER */}
        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>
            🔵 Recomendador de Llantas
          </h1>
          <p style={{ color:"#94a3b8" }}>Encuentra la llanta correcta para tu moto y condiciones</p>
        </div>

        {/* FORMULARIO */}
        <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", border:"1px solid #334155", marginBottom:"1.5rem" }}>
          <h2 style={{ color:"#f1f5f9", marginBottom:"1.5rem" }}>Configura tu busqueda</h2>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:"1rem" }}>

            <div style={{ gridColumn:"1/-1" }}>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Tipo de moto</label>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(130px, 1fr))", gap:"0.5rem", marginTop:"0.5rem" }}>
                {TIPOS_MOTO.map(t => (
                  <button key={t.valor} onClick={() => setForm(f => ({...f, tipo_moto:t.valor}))}
                    style={{
                      padding:"0.6rem", borderRadius:"8px", cursor:"pointer", textAlign:"left",
                      background: form.tipo_moto === t.valor ? "#06b6d422" : "#0f172a",
                      border: `1px solid ${form.tipo_moto === t.valor ? "#06b6d4" : "#334155"}`,
                      color: form.tipo_moto === t.valor ? "#06b6d4" : "#94a3b8",
                      fontSize:"0.85rem", fontWeight: form.tipo_moto === t.valor ? "bold" : "normal"
                    }}>
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Uso principal</label>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(130px, 1fr))", gap:"0.5rem", marginTop:"0.5rem" }}>
                {USOS.map(u => (
                  <button key={u} onClick={() => setForm(f => ({...f, uso:u}))}
                    style={{
                      padding:"0.5rem", borderRadius:"6px", cursor:"pointer",
                      background: form.uso === u ? "#06b6d422" : "#0f172a",
                      border:`1px solid ${form.uso === u ? "#06b6d4" : "#334155"}`,
                      color: form.uso === u ? "#06b6d4" : "#94a3b8", fontSize:"0.8rem"
                    }}>
                    {u === "ciudad" ? "🏙️" : u === "carretera" ? "🛣️" : u === "offroad" ? "⛰️" : "🌧️"} {u}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Clima predominante</label>
              <div style={{ display:"flex", flexDirection:"column", gap:"0.5rem", marginTop:"0.5rem" }}>
                {CLIMAS.map(c => (
                  <button key={c} onClick={() => setForm(f => ({...f, clima:c}))}
                    style={{
                      padding:"0.5rem", borderRadius:"6px", cursor:"pointer",
                      background: form.clima === c ? "#06b6d422" : "#0f172a",
                      border:`1px solid ${form.clima === c ? "#06b6d4" : "#334155"}`,
                      color: form.clima === c ? "#06b6d4" : "#94a3b8", fontSize:"0.8rem"
                    }}>
                    {c === "seco" ? "☀️" : c === "lluvia" ? "🌧️" : "🌤️"} {c}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Gama</label>
              <div style={{ display:"flex", flexDirection:"column", gap:"0.5rem", marginTop:"0.5rem" }}>
                {GAMAS.map(g => (
                  <button key={g} onClick={() => setForm(f => ({...f, gama:g}))}
                    style={{
                      padding:"0.75rem", borderRadius:"6px", cursor:"pointer", textAlign:"left",
                      background: form.gama === g ? "#06b6d422" : "#0f172a",
                      border:`1px solid ${form.gama === g ? "#06b6d4" : "#334155"}`,
                      color: form.gama === g ? "#06b6d4" : "#94a3b8", fontSize:"0.85rem"
                    }}>
                    {g === "alta" ? "⭐⭐⭐ Alta" : g === "media" ? "⭐⭐ Media" : "⭐ Economica"}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ gridColumn:"1/-1" }}>
              <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>
                Presupuesto maximo por llanta: <strong style={{ color:"#06b6d4" }}>${form.presupuesto_max}</strong>
              </label>
              <input type="range" min="20" max="250" value={form.presupuesto_max}
                onChange={e => setForm(f => ({...f, presupuesto_max:parseInt(e.target.value)}))}
                style={{ width:"100%", marginTop:"0.5rem", accentColor:"#06b6d4" }} />
              <div style={{ display:"flex", justifyContent:"space-between", color:"#475569", fontSize:"0.75rem" }}>
                <span>$20</span><span>$250</span>
              </div>
            </div>
          </div>

          <button onClick={recomendar} disabled={loading}
            style={{
              width:"100%", marginTop:"1.5rem", padding:"1rem",
              background: loading ? "#334155" : "#06b6d4",
              border:"none", borderRadius:"10px", color:"#fff",
              cursor:"pointer", fontWeight:"bold", fontSize:"1rem"
            }}>
            {loading ? "Buscando llantas..." : "🔵 Recomendar llantas →"}
          </button>
          {error && <p style={{ color:"#ef4444", textAlign:"center", marginTop:"0.5rem" }}>{error}</p>}
        </div>

        {/* RESULTADO */}
        {resultado && sev && (
          <div>
            {/* Alerta de severidad */}
            <div style={{
              background: sev.bg, borderRadius:"12px", padding:"1.25rem",
              marginBottom:"1rem", border:`2px solid ${sev.color}`,
              display:"flex", alignItems:"flex-start", gap:"1rem"
            }}>
              <span style={{ fontSize:"2rem", flexShrink:0 }}>{sev.icono}</span>
              <div>
                <div style={{ display:"flex", alignItems:"center", gap:"0.75rem", marginBottom:"0.5rem" }}>
                  <span style={{ color:sev.color, fontWeight:"bold", fontSize:"0.85rem" }}>
                    ALERTA {sev.nivel}
                  </span>
                  <span style={{ background:`${sev.color}33`, color:sev.color, padding:"2px 10px", borderRadius:"20px", fontSize:"0.8rem", fontWeight:"bold" }}>
                    {resultado.tipo_llanta_recomendada}
                  </span>
                </div>
                <p style={{ color:"#e2e8f0", fontSize:"0.9rem", lineHeight:"1.5" }}>
                  {resultado.alerta_seguridad}
                </p>
                <p style={{ color:"#64748b", fontSize:"0.82rem", marginTop:"0.5rem" }}>
                  {resultado.consejo}
                </p>
              </div>
            </div>

            {/* Opciones de llantas */}
            {resultado.opciones?.length > 0 ? (
              <div>
                <p style={{ color:"#64748b", fontSize:"0.85rem", marginBottom:"1rem" }}>
                  {resultado.opciones.length} opciones encontradas para gama <strong style={{ color:"#06b6d4" }}>{resultado.gama}</strong>
                </p>
                {resultado.opciones.map((ll: any, i: number) => (
                  <div key={i}
                    onClick={() => setLSel(llantaSel?.marca === ll.marca && llantaSel?.modelo === ll.modelo ? null : ll)}
                    style={{
                      background: llantaSel?.marca === ll.marca ? "#1e3a5f" : "#1e293b",
                      borderRadius:"12px", padding:"1.25rem", marginBottom:"0.75rem",
                      border:`1px solid ${llantaSel?.marca === ll.marca ? "#06b6d4" : "#334155"}`,
                      cursor:"pointer"
                    }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                      <div>
                        <div style={{ display:"flex", alignItems:"center", gap:"0.75rem" }}>
                          <span style={{ background:"#06b6d422", color:"#06b6d4", padding:"2px 8px", borderRadius:"4px", fontSize:"0.75rem" }}>
                            #{i+1}
                          </span>
                          <h3 style={{ color:"#f1f5f9" }}>{ll.marca} {ll.modelo}</h3>
                        </div>
                        <p style={{ color:"#94a3b8", fontSize:"0.82rem", marginTop:"4px" }}>
                          Medida: {ll.medida_ejemplo} • Gama: {ll.gama}
                        </p>
                      </div>
                      <div style={{ textAlign:"right" }}>
                        <p style={{ color:"#22c55e", fontWeight:"bold", fontSize:"1.1rem" }}>
                          ${ll.precio_min_usd} — ${ll.precio_max_usd}
                        </p>
                        <p style={{ color:"#64748b", fontSize:"0.75rem" }}>por llanta</p>
                      </div>
                    </div>
                    {llantaSel?.marca === ll.marca && llantaSel?.modelo === ll.modelo && (
                      <div style={{ marginTop:"1rem", paddingTop:"1rem", borderTop:"1px solid #334155" }}>
                        <p style={{ color:"#94a3b8", fontSize:"0.85rem", marginBottom:"0.5rem" }}>
                          💡 Par de llantas: <strong style={{ color:"#22c55e" }}>${(ll.precio_min_usd*2).toFixed(0)} — ${(ll.precio_max_usd*2).toFixed(0)}</strong>
                        </p>
                        <a href="/asistente" style={{
                          background:"#8b5cf6", color:"#fff", padding:"0.4rem 0.8rem",
                          borderRadius:"6px", textDecoration:"none", fontSize:"0.8rem"
                        }}>
                          💬 Consultar al asistente sobre esta llanta
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ background:"#1e293b", borderRadius:"12px", padding:"2rem", textAlign:"center" }}>
                <p style={{ color:"#94a3b8", marginBottom:"1rem" }}>
                  No se encontraron llantas con esos filtros.
                </p>
                <button onClick={() => setForm(f => ({...f, presupuesto_max:250, gama:"alta"}))}
                  style={{ background:"#06b6d4", border:"none", borderRadius:"8px", padding:"0.75rem 1.5rem", color:"#fff", cursor:"pointer" }}>
                  Ampliar busqueda
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
