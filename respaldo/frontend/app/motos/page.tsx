'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const TIPOS_USO = ["delivery","urbano","touring","aventura","enduro","deportivo"]
const ZONAS     = ["Sierra","Costa","Amazonia","Galapagos"]

const PERFIL_ICONS: Record<string,string> = {
  delivery:"🛵", urbano:"🏙️", touring:"🗺️",
  aventura:"⛰️", enduro:"🏁", deportivo:"🏎️"
}

const RIESGO_COLOR: Record<string,string> = {
  ALTO:"#ef4444", MEDIO:"#f59e0b", BAJO:"#22c55e"
}

export default function MotosPage() {
  const [modo, setModo]           = useState<"recomendador"|"catalogo">("recomendador")
  const [perfil, setPerfil]       = useState({ tipo_uso:"urbano", anos_experiencia:1, presupuesto_max:3000, zona:"Sierra" })
  const [resultado, setResultado] = useState<any>(null)
  const [catalogo, setCatalogo]   = useState<any[]>([])
  const [loading, setLoading]     = useState(false)
  const [filtro, setFiltro]       = useState({ tipo:"", marca:"", precio:15000 })
  const [marcas, setMarcas]       = useState<string[]>([])
  const [seleccionada, setSel]    = useState<any>(null)

  useEffect(() => {
    fetch(`${API}/m4/motos/marcas`)
      .then(r => r.json())
      .then(d => setMarcas(d.marcas?.map((m: any) => m.nombre) || []))
  }, [])

  const recomendar = async () => {
    setLoading(true); setResultado(null)
    try {
      const r = await fetch(`${API}/m4/motos/recomendar`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ perfil })
      })
      setResultado(await r.json())
    } catch {}
    setLoading(false)
  }

  const cargarCatalogo = async () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (filtro.tipo)  params.append("tipo",  filtro.tipo)
    if (filtro.marca) params.append("marca", filtro.marca)
    if (filtro.precio < 15000) params.append("precio", String(filtro.precio))
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
      <div style={{ maxWidth:"960px", margin:"0 auto" }}>

        {/* HEADER */}
        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>
            🏍️ Recomendador de Motos
          </h1>
          <p style={{ color:"#94a3b8" }}>48 modelos disponibles en Ecuador 2024-2026</p>
        </div>

        {/* TABS */}
        <div style={{ display:"flex", gap:"1rem", marginBottom:"2rem" }}>
          {[
            { id:"recomendador", label:"🤖 Recomendador IA" },
            { id:"catalogo",     label:"📋 Catalogo Completo" }
          ].map(t => (
            <button key={t.id} onClick={() => setModo(t.id as any)}
              style={{
                flex:1, padding:"0.75rem", borderRadius:"10px", cursor:"pointer", fontWeight:"bold",
                background: modo === t.id ? "#f59e0b" : "#1e293b",
                border: `1px solid ${modo === t.id ? "#f59e0b" : "#334155"}`,
                color: modo === t.id ? "#fff" : "#94a3b8"
              }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* ── RECOMENDADOR ── */}
        {modo === "recomendador" && (
          <div>
            {/* Formulario */}
            <div style={{ background:"#1e293b", borderRadius:"16px", padding:"2rem", border:"1px solid #334155", marginBottom:"1.5rem" }}>
              <h2 style={{ color:"#f1f5f9", marginBottom:"1.5rem" }}>Configura tu perfil</h2>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"1rem" }}>
                <div>
                  <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Tipo de uso</label>
                  <select value={perfil.tipo_uso} onChange={e => setPerfil(p => ({...p, tipo_uso:e.target.value}))}
                    style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                    {TIPOS_USO.map(t => <option key={t} value={t}>{PERFIL_ICONS[t]} {t}</option>)}
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
                  <select value={perfil.zona} onChange={e => setPerfil(p => ({...p, zona:e.target.value}))}
                    style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }}>
                    {ZONAS.map(z => <option key={z} value={z}>{z}</option>)}
                  </select>
                </div>
              </div>
              <button onClick={recomendar} disabled={loading}
                style={{
                  width:"100%", marginTop:"1.5rem", padding:"1rem",
                  background: loading ? "#334155" : "#f59e0b",
                  border:"none", borderRadius:"10px", color:"#fff",
                  cursor:"pointer", fontWeight:"bold", fontSize:"1rem"
                }}>
                {loading ? "Analizando 48 motos..." : `🤖 Recomendar motos para ${PERFIL_ICONS[perfil.tipo_uso]} ${perfil.tipo_uso} →`}
              </button>
            </div>

            {/* RESULTADO con tabla comparativa */}
            {resultado && (
              <div>
                <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1rem", marginBottom:"1rem", border:"1px solid #334155" }}>
                  <p style={{ color:"#64748b", fontSize:"0.85rem" }}>
                    Analizado <strong style={{ color:"#f59e0b" }}>{resultado.catalogo_consultado}</strong> motos
                    de tipo {resultado.tipos_buscados?.join(", ")} |
                    Zona: <strong style={{ color:"#38bdf8" }}>{perfil.zona}</strong> |
                    Presupuesto: <strong style={{ color:"#22c55e" }}>${perfil.presupuesto_max.toLocaleString()}</strong>
                  </p>
                </div>

                {/* Tabla comparativa */}
                <div style={{ background:"#1e293b", borderRadius:"16px", overflow:"hidden", border:"1px solid #334155", marginBottom:"1.5rem" }}>
                  <table style={{ width:"100%", borderCollapse:"collapse" }}>
                    <thead>
                      <tr style={{ background:"#0f172a" }}>
                        <th style={{ padding:"1rem", textAlign:"left", color:"#64748b", fontSize:"0.8rem", fontWeight:"bold" }}>POSICION</th>
                        <th style={{ padding:"1rem", textAlign:"left", color:"#64748b", fontSize:"0.8rem", fontWeight:"bold" }}>MOTOCICLETA</th>
                        <th style={{ padding:"1rem", textAlign:"right", color:"#64748b", fontSize:"0.8rem", fontWeight:"bold" }}>PRECIO</th>
                        <th style={{ padding:"1rem", textAlign:"left", color:"#64748b", fontSize:"0.8rem", fontWeight:"bold" }}>VENTAJA</th>
                        <th style={{ padding:"1rem", textAlign:"center", color:"#64748b", fontSize:"0.8rem", fontWeight:"bold" }}>DETALLE</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.recomendaciones?.map((rec: any, i: number) => (
                        <tr key={i} style={{ borderTop:"1px solid #334155", background: i === 0 ? "#1d4ed808" : "transparent" }}>
                          <td style={{ padding:"1rem" }}>
                            <span style={{
                              background: i===0?"#f59e0b":i===1?"#94a3b8":"#cd7f32",
                              color:"#fff", width:"32px", height:"32px", borderRadius:"50%",
                              display:"inline-flex", alignItems:"center", justifyContent:"center",
                              fontWeight:"bold", fontSize:"0.9rem"
                            }}>
                              {i===0?"🥇":i===1?"🥈":"🥉"}
                            </span>
                          </td>
                          <td style={{ padding:"1rem" }}>
                            <p style={{ color:"#f1f5f9", fontWeight:"bold", margin:0 }}>{rec.moto}</p>
                            <p style={{ color:"#64748b", fontSize:"0.8rem", margin:0 }}>{rec.justificacion?.slice(0,60)}...</p>
                          </td>
                          <td style={{ padding:"1rem", textAlign:"right" }}>
                            <span style={{ color:"#22c55e", fontWeight:"bold", fontSize:"1.1rem" }}>
                              ${rec.precio_usd?.toLocaleString()}
                            </span>
                          </td>
                          <td style={{ padding:"1rem" }}>
                            <span style={{ background:"#22c55e22", color:"#22c55e", padding:"4px 10px", borderRadius:"6px", fontSize:"0.8rem" }}>
                              ✅ {rec.ventaja_principal}
                            </span>
                          </td>
                          <td style={{ padding:"1rem", textAlign:"center" }}>
                            <button onClick={() => setSel(rec)}
                              style={{ background:"#334155", border:"none", borderRadius:"6px", padding:"6px 12px", color:"#94a3b8", cursor:"pointer", fontSize:"0.8rem" }}>
                              Ver →
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Panel detalle moto seleccionada */}
                {seleccionada && (
                  <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1.5rem", marginBottom:"1rem", border:"1px solid #f59e0b44" }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1rem" }}>
                      <h3 style={{ color:"#f59e0b" }}>{seleccionada.moto}</h3>
                      <button onClick={() => setSel(null)} style={{ background:"none", border:"none", color:"#64748b", cursor:"pointer", fontSize:"1.2rem" }}>✕</button>
                    </div>
                    <p style={{ color:"#cbd5e1", lineHeight:"1.6", marginBottom:"1rem" }}>{seleccionada.justificacion}</p>
                    <div style={{ display:"flex", gap:"0.75rem", flexWrap:"wrap" }}>
                      <a href="/asistente" style={{
                        background:"#8b5cf6", color:"#fff", padding:"0.5rem 1rem",
                        borderRadius:"8px", textDecoration:"none", fontSize:"0.85rem", fontWeight:"bold"
                      }}>
                        💬 Preguntar al asistente sobre esta moto
                      </a>
                      <a href="/llantas" style={{
                        background:"#06b6d4", color:"#fff", padding:"0.5rem 1rem",
                        borderRadius:"8px", textDecoration:"none", fontSize:"0.85rem", fontWeight:"bold"
                      }}>
                        🔵 Ver llantas compatibles
                      </a>
                    </div>
                  </div>
                )}

                {/* Razonamiento IA */}
                {resultado.razonamiento && (
                  <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1rem", border:"1px solid #f59e0b44" }}>
                    <p style={{ color:"#f59e0b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>🤖 RAZONAMIENTO IA</p>
                    <p style={{ color:"#94a3b8", fontSize:"0.9rem" }}>{resultado.razonamiento}</p>
                    {resultado.modo === "mock" && (
                      <p style={{ color:"#475569", fontSize:"0.75rem", marginTop:"0.5rem", fontStyle:"italic" }}>
                        ⚠️ Modo mock — conectar Claude API para razonamiento real personalizado
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── CATALOGO ── */}
        {modo === "catalogo" && (
          <div>
            {/* Filtros */}
            <div style={{ background:"#1e293b", borderRadius:"12px", padding:"1rem", marginBottom:"1.5rem", display:"flex", gap:"0.75rem", flexWrap:"wrap", alignItems:"flex-end" }}>
              <div style={{ flex:1, minWidth:"140px" }}>
                <label style={{ color:"#64748b", fontSize:"0.75rem" }}>TIPO</label>
                <input placeholder="Utilitaria, Naked..." value={filtro.tipo}
                  onChange={e => setFiltro(f => ({...f, tipo:e.target.value}))}
                  style={{ width:"100%", padding:"0.6rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"4px" }} />
              </div>
              <div style={{ flex:1, minWidth:"140px" }}>
                <label style={{ color:"#64748b", fontSize:"0.75rem" }}>MARCA</label>
                <select value={filtro.marca} onChange={e => setFiltro(f => ({...f, marca:e.target.value}))}
                  style={{ width:"100%", padding:"0.6rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"4px" }}>
                  <option value="">Todas</option>
                  {marcas.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <div style={{ flex:1, minWidth:"140px" }}>
                <label style={{ color:"#64748b", fontSize:"0.75rem" }}>PRECIO MAX (USD)</label>
                <input type="number" value={filtro.precio}
                  onChange={e => setFiltro(f => ({...f, precio:parseInt(e.target.value)||15000}))}
                  style={{ width:"100%", padding:"0.6rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"4px" }} />
              </div>
              <button onClick={cargarCatalogo} disabled={loading}
                style={{ padding:"0.6rem 1.5rem", background:"#f59e0b", border:"none", borderRadius:"8px", color:"#fff", cursor:"pointer", fontWeight:"bold" }}>
                Filtrar
              </button>
            </div>

            <p style={{ color:"#64748b", fontSize:"0.85rem", marginBottom:"1rem" }}>
              {loading ? "Cargando..." : `${catalogo.length} motos encontradas`}
            </p>

            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(280px,1fr))", gap:"1rem" }}>
              {catalogo.map((m: any) => (
                <div key={m.id} style={{ background:"#1e293b", borderRadius:"12px", padding:"1.25rem", border:"1px solid #334155" }}
                  onMouseEnter={e => (e.currentTarget.style.borderColor="#f59e0b")}
                  onMouseLeave={e => (e.currentTarget.style.borderColor="#334155")}>
                  <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"0.5rem" }}>
                    <span style={{ background:"#f59e0b22", color:"#f59e0b", padding:"2px 8px", borderRadius:"4px", fontSize:"0.75rem" }}>{m.tipo}</span>
                    <span style={{ color:"#22c55e", fontWeight:"bold" }}>${m.precio_usd?.toLocaleString()}</span>
                  </div>
                  <h3 style={{ color:"#f1f5f9", marginBottom:"0.25rem" }}>{m.marca} {m.modelo}</h3>
                  <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>
                    {m.anio} • {m.cilindrada_cc}cc • {m.potencia_hp}HP • {m.peso_kg}kg
                  </p>
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
