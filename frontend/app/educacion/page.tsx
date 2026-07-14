'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const CAT_ICONS: Record<string,string> = {
  "Normativa LOTTTSV y Velocidades": "📋",
  "Conduccion Segura":               "🏍️",
  "Conduccion en Lluvia":            "🌧️",
  "Equipamiento de Seguridad":       "🪖",
  "Mantenimiento Preventivo":        "🔧",
}

export default function EducacionPage() {
  const [categorias, setCats]   = useState<any[]>([])
  const [loading, setLoading]   = useState(true)
  const [seleccionada, setSel]  = useState<any>(null)
  const [leccion, setLeccion]   = useState<any>(null)
  const [quiz, setQuiz]         = useState<any[]>([])
  const [modo, setModo]         = useState<"lista"|"leccion"|"quiz"|"resultado">("lista")
  const [respuestas, setResps]  = useState<Record<number,string>>({})
  const [loadingIA, setLoadIA]  = useState(false)
  const [puntaje, setPuntaje]   = useState(0)

  const perfil = typeof window !== "undefined"
    ? JSON.parse(localStorage.getItem("motoeduc_perfil") || "{}")
    : {}

  useEffect(() => {
    fetch(`${API}/m2/educacion/categorias`)
      .then(r => r.json())
      .then(d => { setCats(d.categorias || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const verLeccion = async (cat: any) => {
    setSel(cat); setModo("leccion"); setLoadIA(true)
    try {
      const r = await fetch(`${API}/m2/educacion/leccion`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify({ categoria: cat.nombre, perfil: perfil || { tipo_uso:"urbano", anos_experiencia:1, nivel:"basico" } })
      })
      const d = await r.json()
      setLeccion(d.leccion)
    } catch { setLeccion(null) }
    setLoadIA(false)
  }

  const iniciarQuiz = async () => {
    setModo("quiz"); setLoadIA(true); setResps({})
    try {
      const r = await fetch(`${API}/m2/educacion/quiz`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify({ categoria: seleccionada?.nombre, perfil: perfil || {}, n_preguntas:10 })
      })
      const d = await r.json()
      setQuiz(d.quiz || [])
    } catch { setQuiz([]) }
    setLoadIA(false)
  }

  const calcularResultado = () => {
    let correctas = 0
    quiz.forEach((q: any, i: number) => {
      if (respuestas[i]?.startsWith(q.correcta)) correctas++
    })
    setPuntaje(correctas)
    setModo("resultado")
  }

  if (loading) return <Cargando />

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"800px", margin:"0 auto" }}>

        {/* LISTA DE CATEGORIAS */}
        {modo === "lista" && (
          <>
            <div style={{ textAlign:"center", marginBottom:"2rem" }}>
              <a href="/" style={{ color:"#64748b", fontSize:"0.85rem" }}>← Dashboard</a>
              <h1 style={{ color:"#f1f5f9", fontSize:"2rem", fontWeight:"bold", marginTop:"0.5rem" }}>📚 Educacion Vial</h1>
              <p style={{ color:"#94a3b8" }}>Selecciona una categoria para comenzar</p>
              {perfil?.perfil_asignado && (
                <span style={{ background:"#3b82f622", color:"#38bdf8", padding:"4px 12px", borderRadius:"20px", fontSize:"0.85rem" }}>
                  Perfil: {perfil.perfil_asignado}
                </span>
              )}
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(260px, 1fr))", gap:"1rem" }}>
              {categorias.map((cat: any) => (
                <button key={cat.id} onClick={() => verLeccion(cat)}
                  style={{
                    background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", border:"1px solid #334155", borderRadius:"12px",
                    padding:"1.5rem", cursor:"pointer", textAlign:"left", color:"#f1f5f9",
                    transition:"transform 0.2s"
                  }}
                  onMouseEnter={e => (e.currentTarget.style.transform="translateY(-3px)")}
                  onMouseLeave={e => (e.currentTarget.style.transform="translateY(0)")}>
                  <div style={{ fontSize:"2rem", marginBottom:"0.75rem" }}>
                    {CAT_ICONS[cat.nombre] || "📖"}
                  </div>
                  <h3 style={{ marginBottom:"0.5rem", fontSize:"1rem" }}>{cat.nombre}</h3>
                  <p style={{ color:"#94a3b8", fontSize:"0.8rem", lineHeight:"1.4" }}>{cat.descripcion}</p>
                  <div style={{ marginTop:"1rem", color:"#3b82f6", fontSize:"0.85rem", fontWeight:"bold" }}>
                    Ver leccion + Quiz →
                  </div>
                </button>
              ))}
            </div>
          </>
        )}

        {/* LECCION */}
        {modo === "leccion" && (
          <div>
            <button onClick={() => setModo("lista")}
              style={{ background:"none", border:"none", color:"#64748b", cursor:"pointer", marginBottom:"1rem", fontSize:"0.9rem" }}>
              ← Volver a categorias
            </button>
            <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"2rem", border:"1px solid #334155" }}>
              {loadingIA ? (
                <div style={{ textAlign:"center", padding:"3rem" }}>
                  <div style={{ fontSize:"2rem", marginBottom:"1rem" }}>🤖</div>
                  <p style={{ color:"#94a3b8" }}>Claude AI generando tu leccion personalizada...</p>
                </div>
              ) : leccion ? (
                <>
                  <h2 style={{ color:"#f1f5f9", fontSize:"1.5rem", marginBottom:"1rem" }}>
                    {CAT_ICONS[seleccionada?.nombre] || "📖"} {leccion.titulo || seleccionada?.nombre}
                  </h2>
                  <p style={{ color:"#cbd5e1", lineHeight:"1.7", marginBottom:"1.5rem" }}>
                    {leccion.introduccion}
                  </p>
                  {leccion.puntos_clave && (
                    <div style={{ marginBottom:"1.5rem" }}>
                      <h3 style={{ color:"#38bdf8", marginBottom:"0.75rem" }}>Puntos Clave</h3>
                      {(Array.isArray(leccion.puntos_clave) ? leccion.puntos_clave : [leccion.puntos_clave]).map((p: string, i: number) => (
                        <div key={i} style={{ display:"flex", gap:"0.75rem", marginBottom:"0.5rem" }}>
                          <span style={{ color:"#3b82f6", fontWeight:"bold" }}>{i+1}.</span>
                          <p style={{ color:"#cbd5e1", margin:0 }}>{p}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  {leccion.ejemplo && (
                    <div style={{ background:"#0f172a", borderRadius:"8px", padding:"1rem", marginBottom:"1rem", borderLeft:"3px solid #3b82f6" }}>
                      <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.25rem" }}>EJEMPLO PRACTICO</p>
                      <p style={{ color:"#cbd5e1" }}>{leccion.ejemplo}</p>
                    </div>
                  )}
                  {leccion.tip_seguridad && (
                    <div style={{ background:"#166534", borderRadius:"8px", padding:"1rem", borderLeft:"3px solid #22c55e" }}>
                      <p style={{ color:"#86efac" }}>💡 {leccion.tip_seguridad}</p>
                    </div>
                  )}
                </>
              ) : (
                <p style={{ color:"#ef4444", textAlign:"center" }}>Error cargando la leccion. Verifica la conexion con la API.</p>
              )}
            </div>
            {!loadingIA && leccion && (
              <button onClick={iniciarQuiz}
                style={{
                  width:"100%", marginTop:"1.5rem", padding:"1rem", background:"#22c55e",
                  border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontSize:"1rem", fontWeight:"bold"
                }}>
                ✅ Entendido — Hacer el Quiz →
              </button>
            )}
          </div>
        )}

        {/* QUIZ */}
        {modo === "quiz" && (
          <div>
            <h2 style={{ color:"#f1f5f9", fontSize:"1.5rem", marginBottom:"1.5rem", textAlign:"center" }}>
              Quiz: {seleccionada?.nombre}
            </h2>
            {loadingIA ? (
              <div style={{ textAlign:"center", padding:"3rem" }}>
                <div style={{ fontSize:"2rem", marginBottom:"1rem" }}>🤖</div>
                <p style={{ color:"#94a3b8" }}>Generando quiz personalizado...</p>
              </div>
            ) : (
              <>
                {quiz.map((q: any, i: number) => (
                  <div key={i} style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"12px", padding:"1.5rem", marginBottom:"1rem", border:"1px solid #334155" }}>
                    <p style={{ color:"#f1f5f9", fontWeight:"bold", marginBottom:"1rem" }}>
                      {i+1}. {q.pregunta}
                    </p>
                    <div style={{ display:"flex", flexDirection:"column", gap:"0.5rem" }}>
                      {q.opciones?.map((op: string) => (
                        <button key={op} onClick={() => setResps(prev => ({ ...prev, [i]: op }))}
                          style={{
                            padding:"0.75rem", background: respuestas[i] === op ? "#1d4ed8" : "#0f172a",
                            border: `2px solid ${respuestas[i] === op ? "#3b82f6" : "#334155"}`,
                            borderRadius:"8px", color:"#f1f5f9", cursor:"pointer", textAlign:"left"
                          }}>
                          {op}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
                <button
                  onClick={calcularResultado}
                  disabled={Object.keys(respuestas).length < quiz.length}
                  style={{
                    width:"100%", padding:"1rem", background: Object.keys(respuestas).length < quiz.length ? "#334155" : "#3b82f6",
                    border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontSize:"1rem", fontWeight:"bold"
                  }}>
                  {Object.keys(respuestas).length}/{quiz.length} — Ver Resultados
                </button>
              </>
            )}
          </div>
        )}

        {/* RESULTADO */}
        {modo === "resultado" && (
          <div style={{ textAlign:"center" }}>
            <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"2rem", marginBottom:"1.5rem" }}>
              <div style={{ fontSize:"4rem", marginBottom:"1rem" }}>
                {puntaje >= 7 ? "🏆" : puntaje >= 5 ? "👍" : "📖"}
              </div>
              <h2 style={{ color:"#f1f5f9", fontSize:"2rem" }}>{puntaje}/{quiz.length} correctas</h2>
              <p style={{ color:"#94a3b8", marginBottom:"1rem" }}>
                {puntaje >= 7 ? "Excelente! Dominas este tema." : puntaje >= 5 ? "Buen resultado. Sigue practicando." : "Repasa la leccion para mejorar."}
              </p>
              <div style={{ background:"#0f172a", borderRadius:"10px", padding:"1rem" }}>
                <p style={{ color:"#22c55e", fontWeight:"bold" }}>+{puntaje * 20} puntos ganados</p>
                {puntaje >= 7 && <p style={{ color:"#f59e0b", fontSize:"0.9rem" }}>🏅 Insignia desbloqueada: {seleccionada?.insignia_nombre}</p>}
              </div>
            </div>
            <div style={{ display:"flex", gap:"1rem" }}>
              <button onClick={() => setModo("lista")}
                style={{ flex:1, padding:"1rem", background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", border:"1px solid #334155", borderRadius:"10px", color:"#94a3b8", cursor:"pointer" }}>
                ← Otras categorias
              </button>
              <button onClick={() => verLeccion(seleccionada)}
                style={{ flex:1, padding:"1rem", background:"var(--race-grad)", border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontWeight:"bold" }}>
                Repasar leccion
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function Cargando() {
  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", display:"flex", alignItems:"center", justifyContent:"center" }}>
      <p style={{ color:"#94a3b8" }}>Cargando modulo de educacion...</p>
    </div>
  )
}
