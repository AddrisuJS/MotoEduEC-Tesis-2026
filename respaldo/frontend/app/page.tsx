'use client'
import { useState, useEffect } from 'react'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const MODULOS = [
  { id:'M1', icon:'👤', titulo:'Perfil Inteligente',       desc:'Configura tu perfil de motociclista y recibe contenido personalizado.',  color:'#3b82f6', ruta:'/m1/perfil/' },
  { id:'M2', icon:'📚', titulo:'Educación Vial',           desc:'Lecciones adaptadas a tu perfil sobre normativa LOTTTSV y conducción segura.', color:'#10b981', ruta:'/m2/educacion/categorias' },
  { id:'M3', icon:'💬', titulo:'Asistente RAG',            desc:'Consulta al asistente experto sobre el reglamento vial ecuatoriano.',   color:'#8b5cf6', ruta:'/m3/asistente/' },
  { id:'M4', icon:'🏍️', titulo:'Recomendador de Motos',   desc:'Encuentra la moto ideal para tu perfil y presupuesto.',                color:'#f59e0b', ruta:'/m4/motos/catalogo' },
  { id:'M5', icon:'🔵', titulo:'Recomendador de Llantas', desc:'Elige las llantas correctas según tu uso y condiciones climáticas.',    color:'#06b6d4', ruta:'/m5/llantas/' },
  { id:'M6', icon:'🏛️', titulo:'Historia Motera',         desc:'Descubre la rica historia del motociclismo ecuatoriano.',              color:'#ec4899', ruta:'/m6/historia/temas' },
  { id:'M7', icon:'🏆', titulo:'Gamificación',             desc:'Gana insignias y sube de nivel mientras aprendes.',                    color:'#f97316', ruta:'/m7/gamificacion/insignias' },
]

export default function Home() {
  const [estado, setEstado] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [perfil, setPerfil] = useState<any>(null)

  useEffect(() => {
    fetch(`${API}/estadisticas/resumen`)
      .then(r => r.json())
      .then(d => { setEstado(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const probarModulo = async (ruta: string, id: string) => {
    try {
      const r = await fetch(`${API}${ruta}`)
      const d = await r.json()
      alert(`✅ ${id} funcionando:\n${JSON.stringify(d, null, 2).slice(0, 300)}...`)
    } catch(e) {
      alert(`❌ Error conectando a ${id}`)
    }
  }

  return (
    <div style={{ minHeight:'100vh', padding:'0' }}>

      {/* HEADER */}
      <header style={{ background:'linear-gradient(135deg,#1e3a5f,#1e40af)', padding:'2rem', textAlign:'center', borderBottom:'3px solid #38bdf8' }}>
        <div style={{ fontSize:'3rem', marginBottom:'0.5rem' }}>🏍️</div>
        <h1 style={{ fontSize:'2.5rem', fontWeight:'bold', color:'#fff', marginBottom:'0.5rem' }}>MotoEdu EC</h1>
        <p style={{ color:'#93c5fd', fontSize:'1.1rem' }}>Plataforma Inteligente de Educación Vial para Motociclistas Ecuatorianos</p>
        <p style={{ color:'#60a5fa', fontSize:'0.9rem', marginTop:'0.5rem' }}>Universidad Politécnica Salesiana — Cuenca 2026</p>
      </header>

      {/* KPIs */}
      <div style={{ background:'#1e293b', padding:'1.5rem', display:'flex', justifyContent:'center', gap:'2rem', flexWrap:'wrap', borderBottom:'1px solid #334155' }}>
        {loading ? (
          <span style={{ color:'#94a3b8' }}>Conectando con la API...</span>
        ) : estado ? (
          <>
            <Kpi label="Motocicletas" valor={estado.resumen?.motocicletas || 0} icon="🏍️" />
            <Kpi label="Preguntas Viales" valor={estado.resumen?.preguntas_viales || 0} icon="❓" />
            <Kpi label="Usuarios" valor={estado.resumen?.usuarios || 0} icon="👤" />
            <Kpi label="Evaluaciones" valor={estado.resumen?.historial_evaluaciones || 0} icon="📊" />
            <div style={{ display:'flex', alignItems:'center', gap:'0.5rem' }}>
              <span style={{ width:'10px', height:'10px', borderRadius:'50%', background:'#22c55e', display:'inline-block' }}></span>
              <span style={{ color:'#22c55e', fontSize:'0.9rem', fontWeight:'bold' }}>API Activa</span>
            </div>
          </>
        ) : (
          <span style={{ color:'#f87171' }}>⚠️ API no disponible — verifica docker-compose</span>
        )}
      </div>

      {/* MÓDULOS */}
      <main style={{ maxWidth:'1200px', margin:'0 auto', padding:'2rem 1rem' }}>
        <h2 style={{ textAlign:'center', fontSize:'1.5rem', color:'#cbd5e1', marginBottom:'2rem' }}>
          Los 7 Módulos del Sistema
        </h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(320px,1fr))', gap:'1.5rem' }}>
          {MODULOS.map(m => (
            <div key={m.id} style={{
              background:'#1e293b', borderRadius:'12px', padding:'1.5rem',
              border:`1px solid ${m.color}44`, transition:'transform 0.2s',
              cursor:'pointer'
            }}
              onMouseEnter={e => (e.currentTarget.style.transform='translateY(-4px)')}
              onMouseLeave={e => (e.currentTarget.style.transform='translateY(0)')}
            >
              <div style={{ display:'flex', alignItems:'center', gap:'1rem', marginBottom:'1rem' }}>
                <span style={{ fontSize:'2rem' }}>{m.icon}</span>
                <div>
                  <span style={{ background:m.color+'33', color:m.color, padding:'2px 8px', borderRadius:'4px', fontSize:'0.75rem', fontWeight:'bold' }}>{m.id}</span>
                  <h3 style={{ color:'#f1f5f9', marginTop:'4px' }}>{m.titulo}</h3>
                </div>
              </div>
              <p style={{ color:'#94a3b8', fontSize:'0.9rem', marginBottom:'1rem', lineHeight:'1.5' }}>{m.desc}</p>
              <button
                onClick={() => probarModulo(m.ruta, m.id)}
                style={{
                  background:m.color, color:'#fff', border:'none', padding:'0.5rem 1rem',
                  borderRadius:'6px', cursor:'pointer', fontSize:'0.85rem', fontWeight:'bold',
                  width:'100%'
                }}
              >
                Probar {m.id} →
              </button>
            </div>
          ))}
        </div>

        {/* LINKS */}
        <div style={{ marginTop:'3rem', background:'#1e293b', borderRadius:'12px', padding:'1.5rem', border:'1px solid #334155' }}>
          <h3 style={{ color:'#f1f5f9', marginBottom:'1rem' }}>🔗 Accesos del Sistema</h3>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(250px,1fr))', gap:'1rem' }}>
            <Link href={`${API}/docs`} label="📖 Swagger API" sub="Documentación interactiva" color="#8b5cf6" />
            <Link href="http://localhost:5051" label="🐘 pgAdmin" sub="Administrador PostgreSQL" color="#336791" />
            <Link href="https://github.com/AddrisuJS/MotoEduEC-Tesis-2026" label="📦 GitHub" sub="Repositorio del proyecto" color="#333" />
          </div>
        </div>

        {/* INFO TESIS */}
        <div style={{ marginTop:'2rem', textAlign:'center', color:'#64748b', fontSize:'0.85rem' }}>
          <p>Tesis de Titulación — Ingeniería de Sistemas — UPS Cuenca 2026</p>
          <p>Estudiante: Sanango Romero José Addrisu | Tutor: Omar Gustavo Bravo Quezada Ph.D</p>
          <p style={{ marginTop:'0.5rem' }}>
            Claude API: {' '}
            <span style={{ color: '#f87171' }}>Mock (conectar API Key para IA real)</span>
          </p>
        </div>
      </main>
    </div>
  )
}

function Kpi({ label, valor, icon }: { label: string, valor: number, icon: string }) {
  return (
    <div style={{ textAlign:'center' }}>
      <div style={{ fontSize:'1.5rem', fontWeight:'bold', color:'#38bdf8' }}>{icon} {valor}</div>
      <div style={{ color:'#94a3b8', fontSize:'0.8rem' }}>{label}</div>
    </div>
  )
}

function Link({ href, label, sub, color }: { href: string, label: string, sub: string, color: string }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" style={{
      display:'block', background:color+'22', border:`1px solid ${color}44`,
      borderRadius:'8px', padding:'0.75rem 1rem', color:'#e2e8f0'
    }}>
      <div style={{ fontWeight:'bold' }}>{label}</div>
      <div style={{ fontSize:'0.8rem', color:'#94a3b8' }}>{sub}</div>
    </a>
  )
}
