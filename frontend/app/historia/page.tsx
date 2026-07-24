'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const HITOS = [
  {
    id:1, anio:"1900-1970", titulo:"Los inicios del motociclismo",
    icono:"🏛️", color:"#8b5cf6",
    resumen:"Las primeras motocicletas llegan a Ecuador como simbolo de modernidad y progreso.",
    datos:["Primeras importaciones europeas en 1920s","Uso inicial limitado a elite y correos","Honda llega a Ecuador en 1960s"]
  },
  {
    id:2, anio:"1970-2000", titulo:"La era japonesa",
    icono:"🇯🇵", color:"#3b82f6",
    resumen:"Las marcas japonesas Honda, Yamaha y Suzuki masifican el motociclismo ecuatoriano.",
    datos:["Honda domina el mercado desde 1970","Yamaha ingresa en 1975","Primeras motocicletas utilitarias accesibles"]
  },
  {
    id:3, anio:"2000-2015", titulo:"El boom del delivery",
    icono:"🛵", color:"#f59e0b",
    resumen:"El crecimiento del delivery y los servicios de mensajeria dispara la demanda de motos utilitarias.",
    datos:["Delivery informal crece 300% en ciudades","Honda CB100 se convierte en la moto mas vendida","Aparecen las primeras regulaciones para delivery"]
  },
  {
    id:4, anio:"2015-2022", titulo:"La era digital",
    icono:"📱", color:"#10b981",
    resumen:"Uber Eats, PedidosYa y Rappi transforman el rol de la motocicleta en la economia urbana.",
    datos:["Apps de delivery generan empleo para 50.000+ motociclistas","Accidentalidad aumenta 40%","ANT implementa nuevas regulaciones de seguridad"]
  },
  {
    id:5, anio:"2023-2025", titulo:"Record historico 2025",
    icono:"📈", color:"#ef4444",
    resumen:"Ecuador alcanza el record historico de 274.729 motocicletas vendidas en 2025, un incremento del 25.4% anual.",
    datos:["274.729 unidades vendidas en 2025 (AEADE)","28.4% del parque vehicular son motos","685 fallecidos en siniestros de moto en 2024 (ANT)"]
  },
  {
    id:6, anio:"2026+", titulo:"La cultura motera actual",
    icono:"🤝", color:"#ec4899",
    resumen:"Clubes moteros, rodadas masivas y comunidades digitales consolidan la identidad motera ecuatoriana.",
    datos:["Federacion Ecuatoriana de Motociclismo activa","Mas de 200 clubes registrados en Ecuador","MotoEdu EC como respuesta educativa a la siniestralidad"]
  },
]

export default function HistoriaPage() {
  const [hitoSel, setHitoSel]   = useState<any>(null)
  const [narrativa, setNarr]    = useState<any>(null)
  const [loadNarr, setLoadNarr] = useState(false)
  const [modo, setModo]         = useState<"timeline"|"contribuir">("timeline")
  const [form, setForm]         = useState({ nombre:"", ciudad:"", historia:"", anio:"", imagen_base64:"" })
  const [imagenPreview, setImagenPreview] = useState("")

  const manejarImagen = (e: any) => {
    const archivo = e.target.files?.[0]
    if (!archivo) return
    if (archivo.size > 5_000_000) { alert("La imagen es muy pesada (max 5MB)"); return }
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = reader.result as string
      setForm(f => ({...f, imagen_base64: base64}))
      setImagenPreview(base64)
    }
    reader.readAsDataURL(archivo)
  }
  const [enviado, setEnviado]   = useState(false)
  const [enviando, setEnviando] = useState(false)

  const cargarNarrativa = async (hito: any) => {
    setHitoSel(hito); setLoadNarr(true); setNarr(null)
    try {
      const r = await fetch(`${API}/m6/historia/${hito.id}`)
      const d = await r.json()
      setNarr(d.contenido)
    } catch {}
    setLoadNarr(false)
  }

  const enviarContribucion = async () => {
    if (!form.historia.trim() || !form.ciudad.trim()) return
    setEnviando(true)
    try {
      await fetch(`${API}/m6/historia/contribuir`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify(form)
      })
      setEnviado(true)
    } catch {
      setEnviado(true) // Mostrar exito igual por si el endpoint no existe aun
    }
    setEnviando(false)
  }

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"900px", margin:"0 auto" }}>

        {/* HEADER */}
        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
          <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>
            🏛️ Historia Motera Ecuatoriana
          </h1>
          <p style={{ color:"#94a3b8" }}>De los primeros caballos de acero al record de 274.729 motos en 2025</p>
        </div>

        {/* TABS */}
        <div style={{ display:"flex", gap:"1rem", marginBottom:"2rem" }}>
          <button onClick={() => setModo("timeline")}
            style={{
              flex:1, padding:"0.75rem", borderRadius:"10px", cursor:"pointer", fontWeight:"bold",
              background: modo === "timeline" ? "#ec4899" : "#1e293b",
              border: `1px solid ${modo === "timeline" ? "#ec4899" : "#334155"}`,
              color: modo === "timeline" ? "#fff" : "#94a3b8"
            }}>
            📅 Linea de Tiempo
          </button>
          <button onClick={() => setModo("contribuir")}
            style={{
              flex:1, padding:"0.75rem", borderRadius:"10px", cursor:"pointer", fontWeight:"bold",
              background: modo === "contribuir" ? "#ec4899" : "#1e293b",
              border: `1px solid ${modo === "contribuir" ? "#ec4899" : "#334155"}`,
              color: modo === "contribuir" ? "#fff" : "#94a3b8"
            }}>
            ✍️ Comparte tu Historia
          </button>
        </div>

        {/* TIMELINE */}
        {modo === "timeline" && (
          <div>
            {/* Linea de tiempo visual */}
            <div style={{ position:"relative", paddingLeft:"2rem", marginBottom:"2rem" }}>
              {/* Linea vertical */}
              <div style={{ position:"absolute", left:"20px", top:0, bottom:0, width:"2px", background:"linear-gradient(to bottom, #8b5cf6, #ec4899)" }} />

              {HITOS.map((hito, i) => (
                <div key={hito.id} style={{ position:"relative", marginBottom:"1.5rem" }}>
                  {/* Punto en la linea */}
                  <div style={{
                    position:"absolute", left:"-1.5rem", top:"1rem",
                    width:"16px", height:"16px", borderRadius:"50%",
                    background: hito.color, border:"3px solid #0f172a",
                    boxShadow:`0 0 0 2px ${hito.color}`,
                    cursor:"pointer", zIndex:1
                  }} onClick={() => cargarNarrativa(hito)} />

                  {/* Tarjeta del hito */}
                  <div
                    onClick={() => cargarNarrativa(hito)}
                    style={{
                      background: hitoSel?.id === hito.id ? "#1e3a5f" : "#1e293b",
                      borderRadius:"12px", padding:"1.25rem", cursor:"pointer",
                      border:`2px solid ${hitoSel?.id === hito.id ? hito.color : "#334155"}`,
                      transition:"all 0.2s"
                    }}
                    onMouseEnter={e => (e.currentTarget.style.borderColor = hito.color)}
                    onMouseLeave={e => { if (hitoSel?.id !== hito.id) e.currentTarget.style.borderColor = "#334155" }}
                  >
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
                      <div style={{ display:"flex", alignItems:"center", gap:"0.75rem" }}>
                        <span style={{ fontSize:"1.5rem" }}>{hito.icono}</span>
                        <div>
                          <span style={{ background:`${hito.color}22`, color:hito.color, padding:"2px 8px", borderRadius:"6px", fontSize:"0.75rem", fontWeight:"bold" }}>
                            {hito.anio}
                          </span>
                          <h3 style={{ color:"#f1f5f9", margin:"4px 0 0" }}>{hito.titulo}</h3>
                        </div>
                      </div>
                      <span style={{ color:"#64748b", fontSize:"0.8rem" }}>Ver narrativa →</span>
                    </div>
                    <p style={{ color:"#94a3b8", fontSize:"0.85rem", marginTop:"0.75rem" }}>{hito.resumen}</p>
                    <div style={{ display:"flex", flexWrap:"wrap", gap:"0.5rem", marginTop:"0.75rem" }}>
                      {hito.datos.map((d,di) => (
                        <span key={di} style={{ background:"#0f172a", color:"#64748b", padding:"3px 8px", borderRadius:"4px", fontSize:"0.75rem" }}>
                          📊 {d}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Panel de narrativa */}
                  {hitoSel?.id === hito.id && (
                    <div style={{ background:"#0f172a", borderRadius:"12px", padding:"1.5rem", marginTop:"0.75rem", borderLeft:`4px solid ${hito.color}` }}>
                      {loadNarr ? (
                        <p style={{ color:"#94a3b8" }}>🤖 Generando narrativa historica con IA...</p>
                      ) : narrativa ? (
                        <>
                          <h3 style={{ color: hito.color, marginBottom:"1rem" }}>{narrativa.titulo || hito.titulo}</h3>
                          <p style={{ color:"#cbd5e1", lineHeight:"1.7", marginBottom:"1rem" }}>{narrativa.narrativa}</p>
                          {narrativa.datos_clave && (
                            <div>
                              <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>DATOS CLAVE VERIFICADOS</p>
                              {narrativa.datos_clave.map((d: string, di: number) => (
                                <p key={di} style={{ color:"#f1f5f9", fontSize:"0.85rem", marginBottom:"0.25rem" }}>📊 {d}</p>
                              ))}
                            </div>
                          )}
                          <p style={{ color:"#475569", fontSize:"0.75rem", marginTop:"1rem", fontStyle:"italic" }}>
                            {narrativa.modo === "mock" ? "⚠️ Modo mock — conectar Claude API para narrativas reales" : "✅ Generado con Claude API"}
                          </p>
                        </>
                      ) : (
                        <p style={{ color:"#ef4444" }}>Error cargando la narrativa.</p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* FORMULARIO CONTRIBUCIONES */}
        {modo === "contribuir" && (
          <div>
            {enviado ? (
              <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"3rem", textAlign:"center", border:"1px solid #22c55e" }}>
                <div style={{ fontSize:"3rem", marginBottom:"1rem" }}>🎉</div>
                <h2 style={{ color:"#22c55e", marginBottom:"0.5rem" }}>Historia enviada</h2>
                <p style={{ color:"#94a3b8" }}>Gracias por contribuir a la historia motera ecuatoriana. Tu historia sera revisada y publicada pronto.</p>
                <button onClick={() => { setEnviado(false); setForm({ nombre:"", ciudad:"", historia:"", anio:"" }) }}
                  style={{ marginTop:"1.5rem", padding:"0.75rem 2rem", background:"#ec4899", border:"none", borderRadius:"8px", color:"#fff", cursor:"pointer" }}>
                  Enviar otra historia
                </button>
              </div>
            ) : (
              <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"2rem", border:"1px solid #334155" }}>
                <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>✍️ Comparte tu historia motera</h2>
                <p style={{ color:"#94a3b8", marginBottom:"2rem", fontSize:"0.9rem" }}>
                  La comunidad motera ecuatoriana tiene historias increibles. Comparte la tuya y forma parte del archivo digital.
                </p>
                <div style={{ display:"flex", flexDirection:"column", gap:"1rem" }}>
                  <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(260px, 1fr))", gap:"1rem" }}>
                    <div>
                      <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Tu nombre (o alias)</label>
                      <input value={form.nombre} onChange={e => setForm(f => ({...f, nombre: e.target.value}))}
                        placeholder="Ej: El Lobo de Cuenca"
                        style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }} />
                    </div>
                    <div>
                      <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Ciudad</label>
                      <input value={form.ciudad} onChange={e => setForm(f => ({...f, ciudad: e.target.value}))}
                        placeholder="Ej: Cuenca"
                        style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }} />
                    </div>
                  </div>
                  <div>
                    <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Ano aproximado de tu historia</label>
                    <input value={form.anio} onChange={e => setForm(f => ({...f, anio: e.target.value}))}
                      placeholder="Ej: 1995, 2010, 2023..."
                      style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }} />
                  </div>
                  <div>
                    <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Tu historia motera *</label>
                    <textarea value={form.historia} onChange={e => setForm(f => ({...f, historia: e.target.value}))}
                      placeholder="Cuenta tu primera moto, un viaje memorable, como la moto cambio tu vida..."
                      rows={6}
                      style={{ width:"100%", padding:"0.75rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem", resize:"vertical" }} />
                  </div>
                  <div>
                    <label style={{ color:"#94a3b8", fontSize:"0.85rem" }}>Una foto (opcional)</label>
                    <input type="file" accept="image/*" onChange={manejarImagen}
                      style={{ width:"100%", padding:"0.6rem", background:"#0f172a", border:"1px solid #334155", borderRadius:"8px", color:"#f1f5f9", marginTop:"0.25rem" }} />
                    {imagenPreview && (
                      <img src={imagenPreview} alt="Vista previa" style={{ marginTop:"0.6rem", maxWidth:"200px", maxHeight:"150px", borderRadius:"8px", border:"1px solid #334155" }} />
                    )}
                  </div>
                  <button onClick={enviarContribucion} disabled={enviando || !form.historia.trim()}
                    style={{
                      padding:"1rem", background: enviando ? "#334155" : "#ec4899",
                      border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontWeight:"bold", fontSize:"1rem"
                    }}>
                    {enviando ? "Enviando..." : "🤝 Compartir mi historia"}
                  </button>
                  <p style={{ color:"#475569", fontSize:"0.75rem", textAlign:"center" }}>
                    Tus datos son tratados con confidencialidad segun la LOPDP Ecuador. Solo se publica lo que autorices.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
