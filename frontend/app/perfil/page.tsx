'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const PASOS = [
  { id:1, titulo:"Tipo de uso",       campo:"tipo_uso" },
  { id:2, titulo:"Experiencia",       campo:"anos_experiencia" },
  { id:3, titulo:"Tu moto",           campo:"moto_actual" },
  { id:4, titulo:"Zona geografica",   campo:"zona" },
  { id:5, titulo:"Objetivos",         campo:"objetivos" },
]

const TIPOS_USO = [
  { valor:"delivery",   label:"🛵 Delivery / Mensajeria",   desc:"Trabajo diario de reparto" },
  { valor:"urbano",     label:"🏙️ Urbano Diario",           desc:"Transporte al trabajo en ciudad" },
  { valor:"touring",   label:"🗺️ Touring / Viajes",        desc:"Viajes largos de fin de semana" },
  { valor:"aventura",   label:"⛰️ Aventura Off-road",       desc:"Rutas de tierra y campo" },
  { valor:"enduro",     label:"🏁 Enduro / Competicion",    desc:"Deporte intenso off-road" },
  { valor:"deportivo",  label:"🏎️ Deportivo",               desc:"Velocidad y rendimiento en asfalto" },
]

const ZONAS = ["Sierra","Costa","Amazonia","Galapagos"]

const OBJETIVOS = [
  "Mejorar mi seguridad en ciudad",
  "Conocer la normativa LOTTTSV",
  "Aprender tecnicas de conduccion en lluvia",
  "Elegir el equipamiento correcto",
  "Preparar viajes largos seguros",
  "Reducir riesgo de accidentes",
]

const RIESGO_COLOR: Record<string,string> = {
  "ALTO":  "#ef4444",
  "MEDIO": "#f59e0b",
  "BAJO":  "#22c55e",
}

export default function PerfilPage() {
  const router = useRouter()
  const [paso, setPaso]       = useState(1)
  const [datos, setDatos]     = useState<any>({ objetivos: [] })
  const [resultado, setRes]   = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState("")
  const [verificando, setVerificando] = useState(true)
  const [usuario, setUsuario] = useState<any>(null)

  // ── Comprobacion en el SERVIDOR de si el perfil ya existe ──────────
  // Antes esto dependia de localStorage, pero cerrarSesion() borra
  // "motoeduc_usuario_id" y "motoeduc_perfil": al volver a entrar el
  // navegador no tenia rastro del perfil y el asistente arrancaba de
  // cero aunque el perfil siguiera guardado en la base.
  useEffect(() => {
    const raw = typeof window !== "undefined" ? localStorage.getItem("motoeduc_usuario") : null
    if (!raw) { setVerificando(false); return }
    let u: any = null
    try { u = JSON.parse(raw) } catch { u = null }
    if (!u?.id) { setVerificando(false); return }
    setUsuario(u)

    fetch(`${API}/m13/perfil/estado/${u.id}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.tiene_perfil && d?.perfil_completo) {
          // Restaurar las claves que el cierre de sesion borro
          if (d.perfil_id) localStorage.setItem("motoeduc_usuario_id", d.perfil_id)
          if (d.perfil)    localStorage.setItem("motoeduc_perfil", JSON.stringify(d.perfil))
          router.replace(d.siguiente_paso || "/evaluacion")
        } else {
          setVerificando(false)
        }
      })
      .catch(() => setVerificando(false))   // si falla, se muestra el asistente
  }, [])

  const actualizar = (campo: string, valor: any) =>
    setDatos((prev: any) => ({ ...prev, [campo]: valor }))

  const toggleObjetivo = (obj: string) => {
    const lista: string[] = datos.objetivos || []
    setDatos((prev: any) => ({
      ...prev,
      objetivos: lista.includes(obj) ? lista.filter((o: string) => o !== obj) : [...lista, obj]
    }))
  }

  const enviar = async () => {
    setLoading(true)
    setError("")
    try {
      const r = await fetch(`${API}/m1/perfil/crear`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...datos,
          nombre: datos.nombre || usuario?.nombre || "Motociclista",
          email:  usuario?.email || undefined,
        })
      })
      const d = await r.json()
      if (d.usuario_id) {
        localStorage.setItem("motoeduc_usuario_id", d.usuario_id)
        localStorage.setItem("motoeduc_perfil", JSON.stringify(d))

        // Vincular el perfil con la cuenta autenticada. Sin esto el perfil
        // queda huerfano en la tabla usuarios y el asistente vuelve a
        // mostrarse en el siguiente inicio de sesion.
        if (usuario?.id) {
          try {
            await fetch(`${API}/m13/perfil/vincular`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ usuario_auth_id: usuario.id, perfil_id: d.usuario_id }),
            })
          } catch { /* no bloquea: el perfil ya quedo creado */ }
        }

        setRes(d)
      } else {
        setError("Error al crear el perfil. Intenta de nuevo.")
      }
    } catch {
      setError("No se puede conectar con la API. Verifica que Docker este corriendo.")
    }
    setLoading(false)
  }

  if (verificando) return (
    <div style={{ minHeight:"100vh", background:"#0f172a", display:"flex",
                  alignItems:"center", justifyContent:"center" }}>
      <div style={{ textAlign:"center" }}>
        <div style={{ fontSize:"2.5rem", marginBottom:"0.6rem" }}>🏍️</div>
        <div style={{ color:"#94a3b8", fontSize:"0.9rem" }}>Cargando tu perfil…</div>
      </div>
    </div>
  )

  if (resultado) return <ResultadoPerfil data={resultado} onReset={() => { setRes(null); setPaso(1); setDatos({ objetivos: [] }) }} />

  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"600px", margin:"0 auto" }}>

        {/* Header */}
        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <div style={{ fontSize:"3rem" }}>🏍️</div>
          <h1 style={{ color:"#f1f5f9", fontSize:"1.8rem", fontWeight:"bold" }}>Configura tu Perfil</h1>
          <p style={{ color:"#94a3b8" }}>5 preguntas para personalizar tu experiencia de aprendizaje</p>
        </div>

        {/* Barra de progreso */}
        <div style={{ marginBottom:"2rem" }}>
          <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"0.5rem" }}>
            {PASOS.map(p => (
              <div key={p.id} style={{
                width:"18%", height:"6px", borderRadius:"3px",
                background: p.id <= paso ? "#3b82f6" : "#334155"
              }} />
            ))}
          </div>
          <p style={{ color:"#64748b", fontSize:"0.85rem", textAlign:"center" }}>
            Paso {paso} de 5 — {PASOS[paso-1].titulo}
          </p>
        </div>

        {/* Contenido del paso */}
        <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"2rem", border:"1px solid #334155" }}>

          {paso === 1 && (
            <div>
              <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>¿Como usas tu moto principalmente?</h2>
              <p style={{ color:"#94a3b8", marginBottom:"0.3rem", fontSize:"0.9rem" }}>Esto define tu perfil de riesgo y el contenido que verás</p>
              <p style={{ color:"#60a5fa", marginBottom:"1.2rem", fontSize:"0.82rem" }}>Puedes elegir más de uno si usas tu moto para varias cosas (ej. ciudad + aventura).</p>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))", gap:"0.75rem" }}>
                {TIPOS_USO.map(t => {
                  const seleccionado = Array.isArray(datos.tipo_uso) && datos.tipo_uso.includes(t.valor)
                  return (
                  <button key={t.valor} onClick={() => {
                      const actuales = Array.isArray(datos.tipo_uso) ? datos.tipo_uso : []
                      const nuevos = seleccionado ? actuales.filter((v: string) => v !== t.valor) : [...actuales, t.valor]
                      actualizar("tipo_uso", nuevos)
                    }}
                    style={{
                      background: seleccionado ? "#3b82f6" : "#0f172a",
                      border: `2px solid ${seleccionado ? "#3b82f6" : "#334155"}`,
                      borderRadius:"10px", padding:"1rem", cursor:"pointer", textAlign:"left", color:"#f1f5f9", position:"relative"
                    }}>
                    {seleccionado && <span style={{ position:"absolute", top:8, right:10, color:"#93c5fd", fontSize:"0.9rem" }}>✓</span>}
                    <div style={{ fontWeight:"bold", marginBottom:"0.25rem" }}>{t.label}</div>
                    <div style={{ fontSize:"0.8rem", color:"#94a3b8" }}>{t.desc}</div>
                  </button>
                  )
                })}
              </div>
            </div>
          )}

          {paso === 2 && (
            <div>
              <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>¿Cuantos anos llevas manejando moto?</h2>
              <p style={{ color:"#94a3b8", marginBottom:"1.5rem", fontSize:"0.9rem" }}>Define el nivel de contenido: basico, intermedio o avanzado</p>
              <input
                type="number" min="0" max="50"
                placeholder="Ej: 3"
                value={datos.anos_experiencia || ""}
                onChange={e => actualizar("anos_experiencia", parseInt(e.target.value) || 0)}
                style={{
                  width:"100%", padding:"1rem", background:"#0f172a", border:"2px solid #334155",
                  borderRadius:"10px", color:"#f1f5f9", fontSize:"1.5rem", textAlign:"center"
                }}
              />
              <p style={{ color:"#64748b", textAlign:"center", marginTop:"1rem", fontSize:"0.85rem" }}>
                {(datos.anos_experiencia || 0) < 2 ? "🟢 Nivel Basico" :
                 (datos.anos_experiencia || 0) < 5 ? "🟡 Nivel Intermedio" : "🔴 Nivel Avanzado"}
              </p>
            </div>
          )}

          {paso === 3 && (
            <div>
              <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>¿Que moto tienes actualmente?</h2>
              <p style={{ color:"#94a3b8", marginBottom:"1.5rem", fontSize:"0.9rem" }}>Modelo y cilindraje para recomendaciones precisas</p>
              <input
                type="text" placeholder="Ej: Honda CB100"
                value={datos.moto_actual || ""}
                onChange={e => actualizar("moto_actual", e.target.value)}
                style={{
                  width:"100%", padding:"1rem", background:"#0f172a", border:"2px solid #334155",
                  borderRadius:"10px", color:"#f1f5f9", fontSize:"1rem", marginBottom:"1rem"
                }}
              />
              <input
                type="number" placeholder="Cilindraje en cc (ej: 100)"
                value={datos.cilindrada_cc || ""}
                onChange={e => actualizar("cilindrada_cc", parseInt(e.target.value) || 0)}
                style={{
                  width:"100%", padding:"1rem", background:"#0f172a", border:"2px solid #334155",
                  borderRadius:"10px", color:"#f1f5f9", fontSize:"1rem"
                }}
              />
            </div>
          )}

          {paso === 4 && (
            <div>
              <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>¿En que zona del Ecuador manejas?</h2>
              <p style={{ color:"#94a3b8", marginBottom:"0.3rem", fontSize:"0.9rem" }}>Las condiciones viales varian segun la region</p>
              <p style={{ color:"#60a5fa", marginBottom:"1.2rem", fontSize:"0.82rem" }}>Puedes elegir varias si viajas o recorres más de una región.</p>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(200px, 1fr))", gap:"0.75rem" }}>
                {ZONAS.map(z => {
                  const seleccionada = Array.isArray(datos.zona) && datos.zona.includes(z)
                  return (
                  <button key={z} onClick={() => {
                      const actuales = Array.isArray(datos.zona) ? datos.zona : []
                      const nuevas = seleccionada ? actuales.filter((v: string) => v !== z) : [...actuales, z]
                      actualizar("zona", nuevas)
                    }}
                    style={{
                      background: seleccionada ? "#3b82f6" : "#0f172a",
                      border: `2px solid ${seleccionada ? "#3b82f6" : "#334155"}`,
                      borderRadius:"10px", padding:"1.5rem", cursor:"pointer",
                      color:"#f1f5f9", fontWeight:"bold", fontSize:"1.1rem", position:"relative"
                    }}>
                    {seleccionada && <span style={{ position:"absolute", top:8, right:10, color:"#93c5fd", fontSize:"0.9rem" }}>✓</span>}
                    {z === "Sierra" ? "🏔️" : z === "Costa" ? "🌊" : z === "Amazonia" ? "🌿" : "🏝️"} {z}
                  </button>
                  )
                })}
              </div>
            </div>
          )}

          {paso === 5 && (
            <div>
              <h2 style={{ color:"#f1f5f9", marginBottom:"0.5rem" }}>¿Que quieres aprender? (elige varios)</h2>
              <p style={{ color:"#94a3b8", marginBottom:"1.5rem", fontSize:"0.9rem" }}>Personaliza los modulos que mas te interesan</p>
              <div style={{ display:"flex", flexDirection:"column", gap:"0.5rem" }}>
                {OBJETIVOS.map(obj => (
                  <button key={obj} onClick={() => toggleObjetivo(obj)}
                    style={{
                      background: datos.objetivos?.includes(obj) ? "#1d4ed855" : "#0f172a",
                      border: `2px solid ${datos.objetivos?.includes(obj) ? "#3b82f6" : "#334155"}`,
                      borderRadius:"10px", padding:"0.75rem 1rem", cursor:"pointer",
                      color:"#f1f5f9", textAlign:"left", fontSize:"0.9rem"
                    }}>
                    {datos.objetivos?.includes(obj) ? "✅" : "⬜"} {obj}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Navegacion */}
        {error && <p style={{ color:"#ef4444", textAlign:"center", marginTop:"1rem" }}>{error}</p>}
        <div style={{ display:"flex", gap:"1rem", marginTop:"1.5rem" }}>
          {paso > 1 && (
            <button onClick={() => setPaso(p => p-1)}
              style={{ flex:1, padding:"1rem", background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", border:"1px solid #334155", borderRadius:"10px", color:"#94a3b8", cursor:"pointer", fontSize:"1rem" }}>
              ← Anterior
            </button>
          )}
          {paso < 5 ? (
            <button onClick={() => setPaso(p => p+1)}
              disabled={
                (paso===1 && (!Array.isArray(datos.tipo_uso) || datos.tipo_uso.length === 0)) ||
                (paso===2 && datos.anos_experiencia === undefined) ||
                (paso===3 && !datos.moto_actual) ||
                (paso===4 && (!Array.isArray(datos.zona) || datos.zona.length === 0))
              }
              style={{
                flex:1, padding:"1rem", background:"var(--race-grad)", border:"none",
                borderRadius:"10px", color:"#fff", cursor:"pointer", fontSize:"1rem", fontWeight:"bold"
              }}>
              Siguiente →
            </button>
          ) : (
            <button onClick={enviar} disabled={loading}
              style={{
                flex:1, padding:"1rem", background: loading ? "#334155" : "#22c55e",
                border:"none", borderRadius:"10px", color:"#fff", cursor:"pointer", fontSize:"1rem", fontWeight:"bold"
              }}>
              {loading ? "Creando perfil..." : "✅ Crear mi perfil"}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function ResultadoPerfil({ data, onReset }: { data: any, onReset: () => void }) {
  const rColor = RIESGO_COLOR[data.nivel_riesgo] || "#94a3b8"
  return (
    <div style={{ minHeight:"100vh", background:"#0f172a", padding:"2rem 1rem" }}>
      <div style={{ maxWidth:"600px", margin:"0 auto" }}>
        <div style={{ textAlign:"center", marginBottom:"2rem" }}>
          <div style={{ fontSize:"3rem", marginBottom:"0.5rem" }}>🎉</div>
          <h1 style={{ color:"#f1f5f9", fontSize:"1.8rem", fontWeight:"bold" }}>Perfil Configurado</h1>
          <p style={{ color:"#94a3b8" }}>{data.mensaje}</p>
        </div>
        <div style={{ background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", borderRadius:"16px", padding:"2rem", border:"1px solid #334155", marginBottom:"1.5rem" }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"1.5rem" }}>
            <div>
              <h2 style={{ color:"#f1f5f9", fontSize:"1.5rem" }}>Perfil: {data.perfil_asignado}</h2>
              <p style={{ color:"#94a3b8", fontSize:"0.9rem" }}>{data.descripcion_perfil}</p>
            </div>
            <span style={{ background:rColor+"22", color:rColor, padding:"4px 12px", borderRadius:"20px", fontWeight:"bold", fontSize:"0.85rem" }}>
              Riesgo {data.nivel_riesgo}
            </span>
          </div>
          <div style={{ marginBottom:"1rem" }}>
            <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>MOTOS TIPICAS DE TU PERFIL</p>
            <div style={{ display:"flex", flexWrap:"wrap", gap:"0.5rem" }}>
              {data.motos_tipicas?.map((m: string) => (
                <span key={m} style={{ background:"#0f172a", color:"#38bdf8", padding:"4px 10px", borderRadius:"6px", fontSize:"0.85rem" }}>{m}</span>
              ))}
            </div>
          </div>
          <div style={{ marginBottom:"1rem" }}>
            <p style={{ color:"#64748b", fontSize:"0.8rem", marginBottom:"0.5rem" }}>EQUIPAMIENTO MINIMO RECOMENDADO</p>
            {data.equipamiento_minimo?.map((e: string) => (
              <p key={e} style={{ color:"#e2e8f0", fontSize:"0.9rem" }}>✅ {e}</p>
            ))}
          </div>
          <div style={{ background:"#0f172a", borderRadius:"8px", padding:"0.75rem" }}>
            <p style={{ color:"#64748b", fontSize:"0.75rem" }}>ID DE USUARIO</p>
            <p style={{ color:"#38bdf8", fontSize:"0.8rem", fontFamily:"monospace" }}>{data.usuario_id}</p>
          </div>
        </div>
        <div style={{ display:"flex", gap:"1rem" }}>
          <a href="/educacion" style={{
            flex:2, display:"block", padding:"1rem", background:"var(--race-grad)", borderRadius:"10px",
            color:"#fff", textAlign:"center", fontWeight:"bold", textDecoration:"none"
          }}>
            📚 Iniciar Educacion Vial →
          </a>
          <button onClick={onReset} style={{
            flex:1, padding:"1rem", background:"rgba(255,255,255,0.05)",backdropFilter:"blur(14px)", border:"1px solid #334155",
            borderRadius:"10px", color:"#94a3b8", cursor:"pointer"
          }}>
            Reiniciar
          </button>
        </div>
      </div>
    </div>
  )
}
