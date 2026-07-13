'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../lib/useAuth'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const MODULOS = [
  { id:'M1', icon:'👤', titulo:'Perfil Inteligente',      desc:'Configura tu perfil de motociclista y recibe contenido personalizado.',        color:'#3b82f6', pagina:'/perfil' },
  { id:'M2', icon:'📚', titulo:'Educación Vial',          desc:'Lecciones adaptadas a tu perfil sobre normativa LOTTTSV y conducción segura.', color:'#10b981', pagina:'/educacion' },
  { id:'M3', icon:'💬', titulo:'Asistente RAG',           desc:'Consulta al asistente experto sobre el reglamento vial ecuatoriano.',          color:'#8b5cf6', pagina:'/asistente' },
  { id:'M4', icon:'🏍️', titulo:'Recomendador de Motos',  desc:'Encuentra la moto ideal para tu perfil y presupuesto.',                        color:'#f59e0b', pagina:'/motos' },
  { id:'M5', icon:'🔵', titulo:'Recomendador de Llantas', desc:'Elige las llantas correctas según tu uso y condiciones climáticas.',           color:'#06b6d4', pagina:'/llantas' },
  { id:'M6', icon:'🏛️', titulo:'Historia Motera',        desc:'Descubre la rica historia del motociclismo ecuatoriano.',                      color:'#ec4899', pagina:'/historia' },
  { id:'M7', icon:'🏆', titulo:'Gamificación',            desc:'Gana insignias y sube de nivel mientras aprendes.',                            color:'#f97316', pagina:'/gamificacion' },
]

const PILOTO = [
  { icon:'📋', titulo:'Evaluación',   desc:'Tu punto de partida y tu progreso',  color:'#3b82f6', pagina:'/evaluacion' },
  { icon:'🕹️', titulo:'Arcade',      desc:'Duelo relámpago y desafío del día',  color:'#facc15', pagina:'/arcade' },
  { icon:'🏆', titulo:'Top',          desc:'Ranking de motociclistas',           color:'#4ade80', pagina:'/top' },
  { icon:'🔧', titulo:'Garaje',       desc:'Desbloquea piezas con tus logros',   color:'#fb923c', pagina:'/garaje' },
  { icon:'⚔️', titulo:'Duelos 1v1',  desc:'Reta a otros motociclistas',         color:'#ef4444', pagina:'/duelos' },
]

export default function Home() {
  const router = useRouter()
  const { usuario, cerrarSesion } = useAuth(false)   // false: la home no obliga a login
  const [estado, setEstado] = useState<any>(null)
  const [salud, setSalud] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/estadisticas/resumen`).then(r => r.json())
      .then(d => { setEstado(d); setLoading(false) }).catch(() => setLoading(false))
    fetch(`${API}/health`).then(r => r.json()).then(setSalud).catch(() => {})
  }, [])

  return (
    <div style={{ minHeight:'100vh' }}>

      {/* HEADER */}
      <header style={{ background:'linear-gradient(135deg,#1e3a5f,#1e40af)', padding:'clamp(1.2rem,4vw,2rem)', borderBottom:'3px solid #38bdf8', position:'relative' }}>
        <div style={{ textAlign:'center' }}>
          <div style={{ fontSize:'clamp(2.2rem,6vw,3rem)', marginBottom:'0.4rem' }}>🏍️</div>
          <h1 style={{ fontSize:'clamp(1.6rem,5vw,2.5rem)', fontWeight:'bold', color:'#fff', marginBottom:'0.4rem' }}>MotoEdu EC</h1>
          <p style={{ color:'#93c5fd', fontSize:'clamp(0.9rem,3vw,1.1rem)' }}>Plataforma Inteligente de Educación Vial para Motociclistas Ecuatorianos</p>
          <p style={{ color:'#60a5fa', fontSize:'0.85rem', marginTop:'0.4rem' }}>Universidad Politécnica Salesiana — Cuenca 2026</p>
          {usuario && <p style={{ color:'#e0f2fe', fontSize:'0.95rem', marginTop:'0.6rem', fontWeight:700 }}>¡Hola, {usuario.nombre.split(' ')[0]}! 🏍️ ¿Listo para aprender?</p>}
        </div>
      </header>

      {/* KPIs */}
      <div style={{ background:'#1e293b', padding:'1.2rem', display:'flex', justifyContent:'center', gap:'clamp(1rem,3vw,2rem)', flexWrap:'wrap', borderBottom:'1px solid #334155' }}>
        {loading ? <span style={{ color:'#94a3b8' }}>Conectando con la API...</span> : estado ? (
          <>
            <Kpi label="Motocicletas" valor={estado.resumen?.motocicletas || 0} icon="🏍️" />
            <Kpi label="Preguntas Viales" valor={estado.resumen?.preguntas_viales || 0} icon="❓" />
            <Kpi label="Usuarios" valor={estado.resumen?.usuarios || 0} icon="👤" />
            <Kpi label="Evaluaciones" valor={estado.resumen?.historial_evaluaciones || 0} icon="📊" />
            <div style={{ display:'flex', alignItems:'center', gap:'0.5rem' }}>
              <span style={{ width:10, height:10, borderRadius:'50%', background:'#22c55e', display:'inline-block' }}></span>
              <span style={{ color:'#22c55e', fontSize:'0.9rem', fontWeight:'bold' }}>API Activa</span>
            </div>
          </>
        ) : <span style={{ color:'#f87171' }}>⚠️ API no disponible — verifica docker-compose</span>}
      </div>

      <main style={{ maxWidth:1200, margin:'0 auto', padding:'2rem clamp(0.7rem,3vw,1rem)' }}>

        {/* SECCIÓN PILOTO — lo primero que ve el participante */}
        <h2 style={{ textAlign:'center', fontSize:'1.4rem', color:'#fde68a', marginBottom:'0.4rem' }}>⭐ Tu Ruta de Aprendizaje</h2>
        <p style={{ textAlign:'center', color:'#94a3b8', fontSize:'0.85rem', marginBottom:'1.4rem' }}>Empieza por la Evaluación, aprende con los módulos, y compite en los juegos</p>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(170px,1fr))', gap:'0.8rem', marginBottom:'2.5rem' }}>
          {PILOTO.map(p => (
            <div key={p.titulo} onClick={() => router.push(usuario ? p.pagina : '/login')}
              style={{ background:'#1e293b', borderRadius:12, padding:'1.1rem', border:`1px solid ${p.color}55`, cursor:'pointer', textAlign:'center', transition:'transform 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.transform='translateY(-4px)')}
              onMouseLeave={e => (e.currentTarget.style.transform='translateY(0)')}>
              <div style={{ fontSize:'1.9rem' }}>{p.icon}</div>
              <div style={{ color:p.color, fontWeight:800, fontSize:'0.95rem', margin:'0.3rem 0 0.15rem' }}>{p.titulo}</div>
              <div style={{ color:'#94a3b8', fontSize:'0.75rem' }}>{p.desc}</div>
            </div>
          ))}
        </div>

        {/* MÓDULOS */}
        <h2 style={{ textAlign:'center', fontSize:'1.4rem', color:'#cbd5e1', marginBottom:'1.5rem' }}>Los 7 Módulos del Sistema</h2>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))', gap:'1.2rem' }}>
          {MODULOS.map(m => (
            <div key={m.id}
              onClick={() => router.push(usuario ? m.pagina : '/login')}
              style={{ background:'#1e293b', borderRadius:12, padding:'1.4rem', border:`1px solid ${m.color}44`, transition:'transform 0.2s', cursor:'pointer' }}
              onMouseEnter={e => (e.currentTarget.style.transform='translateY(-4px)')}
              onMouseLeave={e => (e.currentTarget.style.transform='translateY(0)')}>
              <div style={{ display:'flex', alignItems:'center', gap:'1rem', marginBottom:'0.9rem' }}>
                <span style={{ fontSize:'2rem' }}>{m.icon}</span>
                <div>
                  <span style={{ background:m.color+'33', color:m.color, padding:'2px 8px', borderRadius:4, fontSize:'0.75rem', fontWeight:'bold' }}>{m.id}</span>
                  <h3 style={{ color:'#f1f5f9', marginTop:4 }}>{m.titulo}</h3>
                </div>
              </div>
              <p style={{ color:'#94a3b8', fontSize:'0.9rem', marginBottom:'1rem', lineHeight:1.5 }}>{m.desc}</p>
              <div style={{ background:m.color, color:'#fff', padding:'0.5rem 1rem', borderRadius:6, fontSize:'0.85rem', fontWeight:'bold', textAlign:'center' }}>
                Entrar a {m.id} →
              </div>
            </div>
          ))}
        </div>

        {/* LINKS DEL SISTEMA — solo visibles para el investigador */}
        {usuario?.rol === 'admin' && (
        <div style={{ marginTop:'3rem', background:'#1e293b', borderRadius:12, padding:'1.5rem', border:'1px solid #334155' }}>
          <h3 style={{ color:'#f1f5f9', marginBottom:'1rem' }}>🔗 Accesos del Sistema</h3>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(250px,1fr))', gap:'1rem' }}>
            <ExtLink href={`${API}/docs`} label="📖 Swagger API" sub="Documentación interactiva" color="#8b5cf6" />
            <ExtLink href="http://localhost:5051" label="🐘 pgAdmin" sub="Administrador PostgreSQL" color="#336791" />
            <ExtLink href="https://github.com/AddrisuJS/MotoEduEC-Tesis-2026" label="📦 GitHub" sub="Repositorio del proyecto" color="#333" />
          </div>
        </div>
        )}

        {/* INFO TESIS + estado REAL de Claude API */}
        <div style={{ marginTop:'2rem', textAlign:'center', color:'#64748b', fontSize:'0.85rem' }}>
          <p>Tesis de Titulación — Ingeniería de Sistemas — UPS Cuenca 2026</p>
          <p>Estudiante: Sanango Romero José Addrisu | Tutor: Omar Gustavo Bravo Quezada Ph.D</p>
          <p style={{ marginTop:'0.5rem' }}>
            Claude API:{' '}
            {salud?.claude_api === 'real'
              ? <span style={{ color:'#4ade80', fontWeight:700 }}>🟢 IA Real conectada</span>
              : salud?.claude_api === 'mock'
              ? <span style={{ color:'#facc15' }}>🟡 Modo Mock (sin API Key)</span>
              : <span style={{ color:'#64748b' }}>verificando...</span>}
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

function ExtLink({ href, label, sub, color }: { href: string, label: string, sub: string, color: string }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" style={{
      display:'block', background:color+'22', border:`1px solid ${color}44`,
      borderRadius:8, padding:'0.75rem 1rem', color:'#e2e8f0', textDecoration:'none'
    }}>
      <div style={{ fontWeight:'bold' }}>{label}</div>
      <div style={{ fontSize:'0.8rem', color:'#94a3b8' }}>{sub}</div>
    </a>
  )
}
