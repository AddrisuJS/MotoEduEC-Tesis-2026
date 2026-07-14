'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../lib/useAuth'
import { IconMoto, IconChat, IconLlanta, IconTrofeo, IconEspada, IconLibro, IconRayo, IconBandera, CountUp, LoaderBarra } from '../lib/ui'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const PILOTO = [
  { icon: '📋', titulo: 'Evaluación', desc: 'Tu punto de partida y progreso', color: '#3b82f6', pagina: '/evaluacion' },
  { icon: '🕹️', titulo: 'Arcade', desc: 'Duelo relámpago y desafío diario', color: '#facc15', pagina: '/arcade' },
  { icon: '🛣️', titulo: 'Ruta Segura', desc: 'Decide en la vía real', color: '#22d3ee', pagina: '/ruta' },
  { icon: '🏆', titulo: 'Top', desc: 'Ranking de motociclistas', color: '#4ade80', pagina: '/top' },
  { icon: '🔧', titulo: 'Garaje', desc: 'Desbloquea piezas con tus logros', color: '#fb923c', pagina: '/garaje' },
  { icon: '⚔️', titulo: 'Duelos 1v1', desc: 'Reta a otros motociclistas', color: '#ef4444', pagina: '/duelos' },
]

const MODULOS = [
  { id: 'M1', Icon: IconMoto, titulo: 'Perfil Inteligente', desc: 'Configura tu perfil y recibe contenido personalizado.', color: '#3b82f6', pagina: '/perfil' },
  { id: 'M2', Icon: IconLibro, titulo: 'Educación Vial', desc: 'Lecciones adaptadas sobre normativa LOTTTSV y conducción segura.', color: '#10b981', pagina: '/educacion' },
  { id: 'M3', Icon: IconChat, titulo: 'Asistente Vial', desc: 'Consulta al experto sobre el reglamento vial ecuatoriano.', color: '#8b5cf6', pagina: '/asistente' },
  { id: 'M4', Icon: IconMoto, titulo: 'Recomendador de Motos', desc: 'Encuentra la moto ideal para tu perfil y presupuesto.', color: '#f59e0b', pagina: '/motos' },
  { id: 'M5', Icon: IconLlanta, titulo: 'Recomendador de Llantas', desc: 'Elige las llantas correctas según tu uso y clima.', color: '#06b6d4', pagina: '/llantas' },
  { id: 'M6', Icon: IconBandera, titulo: 'Historia Motera', desc: 'Descubre la historia del motociclismo ecuatoriano.', color: '#ec4899', pagina: '/historia' },
  { id: 'M7', Icon: IconTrofeo, titulo: 'Gamificación', desc: 'Gana insignias y sube de nivel mientras aprendes.', color: '#f97316', pagina: '/gamificacion' },
]

export default function Home() {
  const router = useRouter()
  const { usuario } = useAuth(false)
  const [estado, setEstado] = useState<any>(null)
  const [salud, setSalud] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/estadisticas/resumen`).then(r => r.json())
      .then(d => { setEstado(d); setLoading(false) }).catch(() => setLoading(false))
    fetch(`${API}/health`).then(r => r.json()).then(setSalud).catch(() => {})
  }, [])

  const irA = (pagina: string) => router.push(usuario ? pagina : '/login')
  const kpis = estado?.resumen || {}

  return (
    <div style={{ maxWidth: 1160, margin: '0 auto', padding: '1.5rem clamp(0.7rem,3vw,1.5rem)' }}>

      {/* HERO */}
      <div className="fade-up glass" style={{ padding: 'clamp(1.5rem,4vw,2.4rem)', marginBottom: '1.4rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -50, right: -50, width: 220, height: 220, background: 'radial-gradient(circle,rgba(255,89,48,0.2),transparent 65%)', borderRadius: '50%' }} />
        <div style={{ position: 'relative', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'rgba(255,89,48,0.14)', border: '1px solid rgba(255,89,48,0.4)', borderRadius: 20, padding: '4px 14px', marginBottom: '0.9rem' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#4ade80', boxShadow: '0 0 8px #4ade80' }} />
            <span style={{ color: '#ff9575', fontSize: 11, fontWeight: 700, letterSpacing: '0.06em' }}>PLATAFORMA ACTIVA</span>
          </div>
          <h1 style={{ color: '#f1f5f9', fontSize: 'clamp(1.6rem,5vw,2.4rem)', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '0.4rem' }}>
            MotoEdu <span style={{ background: 'var(--race-grad)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>EC</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: 'clamp(0.85rem,3vw,1.05rem)', maxWidth: 560, margin: '0 auto' }}>
            Educación vial inteligente para motociclistas ecuatorianos
          </p>
          {usuario && <p style={{ color: '#e0f2fe', fontSize: '0.95rem', marginTop: '0.7rem', fontWeight: 700 }}>¡Hola, {usuario.nombre.split(' ')[0]}! 🏍️ ¿Listo para aprender?</p>}

          {/* KPIs */}
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 'clamp(1rem,4vw,2.5rem)', marginTop: '1.4rem' }}>
            {loading ? <div style={{ width: 200 }}><LoaderBarra /></div> : <>
              <Kpi n={kpis.motocicletas || 0} label="Motos" />
              <Kpi n={kpis.preguntas_viales || 0} label="Preguntas" />
              <Kpi n={kpis.usuarios || 0} label="Usuarios" />
              <Kpi n={kpis.historial_evaluaciones || 0} label="Evaluaciones" />
            </>}
          </div>
        </div>
      </div>

      {/* RUTA DE APRENDIZAJE */}
      <SectionTitle icon="⭐" title="Tu Ruta de Aprendizaje" sub="Empieza por la Evaluación, aprende y compite" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(158px,1fr))', gap: '0.7rem', marginBottom: '2rem' }}>
        {PILOTO.map((p, i) => (
          <div key={p.titulo} onClick={() => irA(p.pagina)} className="glass-sm fade-up"
            style={{ padding: '1rem', cursor: 'pointer', textAlign: 'center', border: `1px solid ${p.color}44`, transition: 'transform .2s', animationDelay: `${i * 0.04}s` }}
            onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-4px)')}
            onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}>
            <div style={{ width: 46, height: 46, margin: '0 auto 0.5rem', borderRadius: 13, background: `radial-gradient(circle at 30% 30%, ${p.color}33, transparent)`, border: `1px solid ${p.color}55`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>{p.icon}</div>
            <div style={{ color: p.color, fontWeight: 800, fontSize: '0.9rem', marginBottom: 2 }}>{p.titulo}</div>
            <div style={{ color: '#94a3b8', fontSize: '0.72rem', lineHeight: 1.3 }}>{p.desc}</div>
          </div>
        ))}
      </div>

      {/* MÓDULOS */}
      <SectionTitle title="Los 7 Módulos del Sistema" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(270px,1fr))', gap: '1rem' }}>
        {MODULOS.map((m, i) => (
          <div key={m.id} onClick={() => irA(m.pagina)} className="glass fade-up"
            style={{ padding: '1.3rem', cursor: 'pointer', transition: 'transform .2s', animationDelay: `${i * 0.03}s` }}
            onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-4px)')}
            onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem', marginBottom: '0.8rem' }}>
              <div style={{ width: 46, height: 46, borderRadius: 13, background: `radial-gradient(circle at 30% 30%, ${m.color}33, transparent)`, border: `1px solid ${m.color}55`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <m.Icon size={24} color={m.color} />
              </div>
              <div>
                <span style={{ background: m.color + '22', color: m.color, padding: '2px 8px', borderRadius: 5, fontSize: '0.7rem', fontWeight: 800 }}>{m.id}</span>
                <div style={{ color: '#f1f5f9', fontWeight: 700, marginTop: 3, fontSize: '0.98rem' }}>{m.titulo}</div>
              </div>
            </div>
            <p style={{ color: '#94a3b8', fontSize: '0.85rem', lineHeight: 1.5, marginBottom: '0.9rem' }}>{m.desc}</p>
            <div style={{ color: m.color, fontWeight: 700, fontSize: '0.82rem' }}>Entrar a {m.id} →</div>
          </div>
        ))}
      </div>

      {/* ACCESOS ADMIN */}
      {usuario?.rol === 'admin' && (
        <div className="glass" style={{ marginTop: '2rem', padding: '1.4rem' }}>
          <h3 style={{ color: '#f1f5f9', marginBottom: '1rem', fontSize: '1rem' }}>🔗 Accesos del Sistema (admin)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(220px,1fr))', gap: '0.8rem' }}>
            <ExtLink href={`${API}/docs`} label="📖 Swagger API" sub="Documentación interactiva" />
            <ExtLink href="http://localhost:5051" label="🐘 pgAdmin" sub="Administrador PostgreSQL" />
            <ExtLink href="https://github.com/AddrisuJS/MotoEduEC-Tesis-2026" label="📦 GitHub" sub="Repositorio del proyecto" />
          </div>
        </div>
      )}

      <div style={{ marginTop: '2rem', textAlign: 'center', color: '#64748b', fontSize: '0.82rem' }}>
        <p>Tesis de Titulación — Ingeniería de Sistemas — UPS Cuenca 2026</p>
        <p style={{ fontSize: '0.75rem', marginTop: 4 }}>Sanango Romero José Addrisu · Tutor: Omar Gustavo Bravo Quezada Ph.D</p>
        <p style={{ marginTop: '0.5rem' }}>Claude API: {salud?.claude_api === 'real'
          ? <span style={{ color: '#4ade80', fontWeight: 700 }}>🟢 IA Real conectada</span>
          : salud?.claude_api === 'mock' ? <span style={{ color: '#facc15' }}>🟡 Modo Mock</span>
          : <span style={{ color: '#64748b' }}>verificando...</span>}</p>
      </div>
    </div>
  )
}

function Kpi({ n, label }: { n: number; label: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '1.6rem', fontWeight: 800, background: 'var(--race-grad)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}><CountUp to={n} /></div>
      <div style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{label}</div>
    </div>
  )
}
function SectionTitle({ icon, title, sub }: { icon?: string; title: string; sub?: string }) {
  return (
    <div style={{ marginBottom: '1rem', textAlign: 'center' }}>
      <h2 style={{ color: '#e2e8f0', fontSize: 'clamp(1.2rem,4vw,1.5rem)', fontWeight: 800 }}>{icon && <span style={{ color: '#facc15' }}>{icon} </span>}{title}</h2>
      {sub && <p style={{ color: '#64748b', fontSize: '0.82rem', marginTop: 3 }}>{sub}</p>}
    </div>
  )
}
function ExtLink({ href, label, sub }: { href: string; label: string; sub: string }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className="glass-sm" style={{ display: 'block', padding: '0.75rem 1rem', color: '#e2e8f0' }}>
      <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>{label}</div>
      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{sub}</div>
    </a>
  )
}
