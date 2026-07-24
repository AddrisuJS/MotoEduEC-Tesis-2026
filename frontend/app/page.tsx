'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '../lib/useAuth'
import { LogoCompleto } from '../lib/LogoMarca'
import { IconMoto, IconChat, IconLlanta, IconTrofeo, IconLibro, IconBandera, CountUp, LoaderBarra } from '../lib/ui'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010'

const QUE_HACE = [
  { icon: '💬', t: 'Asistente inteligente', d: 'Consulta en lenguaje natural sobre normativa, seguridad y mantenimiento. Cada respuesta cita las fuentes en que se fundamenta.' },
  { icon: '📚', t: 'Educación personalizada', d: 'Lecciones y evaluaciones adaptadas a tu experiencia, tu moto y la zona donde conduces.' },
  { icon: '🏍️', t: 'Recomendación de motos', d: 'Encuentra la motocicleta adecuada para tu uso real, con una explicación de por qué conviene.' },
  { icon: '⚙️', t: 'Recomendación de llantas', d: 'Elige el neumático correcto según terreno, clima y tipo de moto, con su alerta de seguridad.' },
  { icon: '🕹️', t: 'Aprender jugando', d: 'Retos contrarreloj, duelos entre motociclistas, insignias y garaje virtual.' },
  { icon: '🤝', t: 'Cultura motera', d: 'Historias y testimonios de motociclistas ecuatorianos que se convierten en material educativo.' },
]

const MODULOS = [
  { id: 'M1', Icon: IconMoto,    t: 'Perfil Inteligente',       d: 'Configura tu perfil y recibe contenido personalizado.', pagina: '/perfil' },
  { id: 'M2', Icon: IconLibro,   t: 'Educación Vial',           d: 'Lecciones adaptadas sobre normativa LOTTTSV y conducción segura.', pagina: '/educacion' },
  { id: 'M3', Icon: IconChat,    t: 'Asistente Vial',           d: 'Consulta al experto sobre el reglamento vial ecuatoriano.', pagina: '/asistente' },
  { id: 'M4', Icon: IconMoto,    t: 'Recomendador de Motos',    d: 'Encuentra la moto ideal para tu perfil y presupuesto.', pagina: '/motos' },
  { id: 'M5', Icon: IconLlanta,  t: 'Recomendador de Llantas',  d: 'Elige las llantas correctas según tu uso y clima.', pagina: '/llantas' },
  { id: 'M6', Icon: IconBandera, t: 'Historia Motera',          d: 'Descubre la historia del motociclismo ecuatoriano.', pagina: '/historia' },
  { id: 'M7', Icon: IconTrofeo,  t: 'Gamificación',             d: 'Gana insignias y sube de nivel mientras aprendes.', pagina: '/gamificacion' },
]

export default function Home() {
  const router = useRouter()
  const { usuario } = useAuth(false)
  const [estado, setEstado] = useState<any>(null)
  const [salud, setSalud] = useState<any>(null)
  const [destino, setDestino] = useState<string>('/evaluacion')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/estadisticas/resumen`).then(r => r.json())
      .then(d => { setEstado(d); setLoading(false) }).catch(() => setLoading(false))
    fetch(`${API}/health`).then(r => r.json()).then(setSalud).catch(() => {})
  }, [])

  // Adonde lleva el boton grande: depende del rol y de la fase del usuario
  useEffect(() => {
    if (!usuario?.id) return
    if (usuario.rol === 'admin') { setDestino('/admin'); return }
    fetch(`${API}/m13/perfil/estado/${usuario.id}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.siguiente_paso) setDestino(d.siguiente_paso) })
      .catch(() => {})
  }, [usuario])

  const kpis = estado?.resumen || {}
  const esControl = usuario?.grupo === 'control'

  return (
    <div style={{ maxWidth: 1160, margin: '0 auto', padding: '1.5rem clamp(0.7rem,3vw,1.5rem) 3rem' }}>

      {/* ═══ HERO ═══ */}
      <div className="fade-up glass" style={{ padding: 'clamp(1.6rem,4vw,2.6rem)', marginBottom: '1.4rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -60, right: -60, width: 240, height: 240, background: 'radial-gradient(circle,rgba(253,181,0,0.18),transparent 65%)', borderRadius: '50%' }} />
        <div style={{ position: 'relative', textAlign: 'center' }}>

          <LogoCompleto max={470} />

          <p style={{ color: 'var(--dorado,#FAC74C)', fontSize: 'clamp(0.95rem,3vw,1.2rem)', fontWeight: 700, marginTop: '1.1rem' }}>
            Aprender, elegir y rodar con seguridad
          </p>

          <p style={{ color: '#9FB2CE', fontSize: 'clamp(0.85rem,2.6vw,0.98rem)', maxWidth: 640, margin: '0.9rem auto 0', lineHeight: 1.65 }}>
            Plataforma inteligente de educación vial que utiliza inteligencia artificial generativa
            para ofrecer contenidos personalizados, orientar en la selección responsable de
            motocicletas y llantas, y promover una conducción más segura en Ecuador.
          </p>

          {/* Accion principal */}
          <div style={{ marginTop: '1.6rem' }}>
            {usuario ? (
              <>
                <p style={{ color: '#DCE6F5', fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.9rem' }}>
                  ¡Hola, {usuario.nombre.split(' ')[0]}! 🏍️
                </p>
                <button onClick={() => router.push(destino)} className="btn-race"
                  style={{ fontSize: '1.05rem', padding: '1rem 2.2rem', borderRadius: 16 }}>
                  Ir a mi dashboard →
                </button>
              </>
            ) : (
              <div style={{ display: 'flex', gap: '0.7rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <Link href="/registro" className="btn-race" style={{ textDecoration: 'none', fontSize: '1rem', padding: '0.95rem 1.9rem' }}>
                  Crear mi cuenta gratis
                </Link>
                <Link href="/login" className="btn-ghost" style={{ textDecoration: 'none', fontSize: '0.95rem', padding: '0.95rem 1.6rem' }}>
                  Ya tengo cuenta
                </Link>
              </div>
            )}
          </div>

          {/* Indicadores */}
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 'clamp(1rem,4vw,2.6rem)', marginTop: '1.8rem' }}>
            {loading ? <div style={{ width: 200 }}><LoaderBarra /></div> : <>
              <Kpi n={kpis.motocicletas || 0} label="Motos en catálogo" />
              <Kpi n={kpis.preguntas_viales || 0} label="Preguntas viales" />
              <Kpi n={kpis.llantas || 0} label="Llantas" />
              <Kpi n={kpis.usuarios || 0} label="Motociclistas" />
            </>}
          </div>
        </div>
      </div>

      {/* ═══ QUÉ HACE ═══ */}
      <Titulo t="¿Qué puedes hacer en MotoEdu EC?" s="Seis formas de aprender a rodar con más seguridad" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: '0.9rem', marginBottom: '2.2rem' }}>
        {QUE_HACE.map((q, i) => (
          <div key={q.t} className="glass-sm fade-up" style={{ padding: '1.2rem', animationDelay: `${i * 0.04}s` }}>
            <div style={{ fontSize: '1.7rem', marginBottom: '0.5rem' }}>{q.icon}</div>
            <div style={{ color: 'var(--amarillo,#FDB500)', fontWeight: 800, fontSize: '0.96rem', marginBottom: '0.4rem' }}>{q.t}</div>
            <div style={{ color: '#9FB2CE', fontSize: '0.83rem', lineHeight: 1.6 }}>{q.d}</div>
          </div>
        ))}
      </div>

      {/* ═══ MÓDULOS ═══ */}
      <Titulo t="Los módulos del sistema" s={usuario ? 'Entra a cualquiera para comenzar' : 'Crea tu cuenta para acceder a todos'} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(268px,1fr))', gap: '1rem' }}>
        {MODULOS.map((m, i) => {
          const bloqueado = !usuario || (esControl && m.pagina !== '/perfil')
          return (
            <div key={m.id} onClick={() => router.push(usuario ? (bloqueado ? '/mis-evaluaciones' : m.pagina) : '/registro')}
              className="glass fade-up"
              style={{ padding: '1.3rem', cursor: 'pointer', transition: 'transform .2s', animationDelay: `${i * 0.03}s`, opacity: bloqueado && usuario ? 0.55 : 1 }}
              onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-4px)')}
              onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem', marginBottom: '0.8rem' }}>
                <div style={{ width: 46, height: 46, borderRadius: 13, background: 'radial-gradient(circle at 30% 30%, rgba(253,181,0,0.22), transparent)', border: '1px solid rgba(253,181,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <m.Icon size={24} color="#FDB500" />
                </div>
                <div>
                  <span style={{ background: 'rgba(253,181,0,0.15)', color: 'var(--amarillo,#FDB500)', padding: '2px 8px', borderRadius: 5, fontSize: '0.7rem', fontWeight: 800 }}>{m.id}</span>
                  <div style={{ color: '#F3F6FB', fontWeight: 700, marginTop: 3, fontSize: '0.98rem' }}>{m.t}</div>
                </div>
              </div>
              <p style={{ color: '#9FB2CE', fontSize: '0.85rem', lineHeight: 1.5, marginBottom: '0.9rem' }}>{m.d}</p>
              <div style={{ color: 'var(--dorado,#FAC74C)', fontWeight: 700, fontSize: '0.82rem' }}>
                {!usuario ? 'Regístrate para entrar →' : bloqueado ? 'No disponible para tu grupo' : `Entrar a ${m.id} →`}
              </div>
            </div>
          )
        })}
      </div>

      {/* ═══ CONOCER MÁS ═══ */}
      <div className="glass" style={{ marginTop: '2.2rem', padding: 'clamp(1.2rem,3vw,1.8rem)', textAlign: 'center' }}>
        <div style={{ color: '#F3F6FB', fontSize: '1.05rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          Un proyecto académico de la Universidad Politécnica Salesiana
        </div>
        <p style={{ color: '#9FB2CE', fontSize: '0.87rem', maxWidth: 620, margin: '0 auto 1.2rem', lineHeight: 1.6 }}>
          MotoEdu EC es una iniciativa de investigación desarrollada en la Carrera de Ingeniería de
          Sistemas, vinculada al grupo GIHP4C. Sus contenidos tienen fines educativos y orientativos.
        </p>
        <div style={{ display: 'flex', gap: '0.7rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/proyecto" className="btn-ghost" style={{ textDecoration: 'none' }}>Conocer el proyecto</Link>
          <Link href="/transparencia" className="btn-ghost" style={{ textDecoration: 'none' }}>Aviso educativo y privacidad</Link>
        </div>
      </div>

      {/* ═══ ADMIN ═══ */}
      {usuario?.rol === 'admin' && (
        <div className="glass" style={{ marginTop: '1.4rem', padding: '1.4rem' }}>
          <h3 style={{ color: '#F3F6FB', marginBottom: '1rem', fontSize: '1rem' }}>🔗 Accesos del sistema (investigador)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(220px,1fr))', gap: '0.8rem' }}>
            <ExtLink href={`${API}/docs`} label="📖 Swagger API" sub="Documentación interactiva" />
            <ExtLink href="/admin" label="👨‍💼 Panel del piloto" sub="Seguimiento de participantes" />
            <ExtLink href="/admin/grupos" label="🎛️ Asignación de grupos" sub="Intervención y control" />
          </div>
        </div>
      )}

      <div style={{ marginTop: '2rem', textAlign: 'center', color: '#6B82A6', fontSize: '0.8rem' }}>
        <p>Universidad Politécnica Salesiana · Sede Cuenca · 2026</p>
        <p style={{ fontSize: '0.75rem', marginTop: 4 }}>
          Sanango Romero José Addrisu · Tutor: Omar Gustavo Bravo Quezada, Ph.D.
        </p>
        {usuario?.rol === 'admin' && (
          <p style={{ marginTop: '0.5rem' }}>Claude API: {salud?.claude_api === 'real'
            ? <span style={{ color: '#4ade80', fontWeight: 700 }}>🟢 conectada</span>
            : salud?.claude_api === 'mock' ? <span style={{ color: 'var(--amarillo,#FDB500)' }}>🟡 modo simulado</span>
            : <span style={{ color: '#6B82A6' }}>verificando…</span>}</p>
        )}
      </div>
    </div>
  )
}

function Kpi({ n, label }: { n: number; label: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '1.7rem', fontWeight: 800, background: 'var(--race-grad)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        <CountUp to={n} />
      </div>
      <div style={{ color: '#9FB2CE', fontSize: '0.75rem' }}>{label}</div>
    </div>
  )
}
function Titulo({ t, s }: { t: string; s?: string }) {
  return (
    <div style={{ marginBottom: '1.1rem', textAlign: 'center' }}>
      <h2 style={{ color: '#E8EEF9', fontSize: 'clamp(1.2rem,4vw,1.55rem)', fontWeight: 800 }}>{t}</h2>
      {s && <p style={{ color: '#6B82A6', fontSize: '0.84rem', marginTop: 4 }}>{s}</p>}
    </div>
  )
}
function ExtLink({ href, label, sub }: { href: string; label: string; sub: string }) {
  const externo = href.startsWith('http')
  return (
    <a href={href} target={externo ? '_blank' : undefined} rel={externo ? 'noopener noreferrer' : undefined}
      className="glass-sm" style={{ display: 'block', padding: '0.75rem 1rem', color: '#E8EEF9' }}>
      <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>{label}</div>
      <div style={{ fontSize: '0.75rem', color: '#9FB2CE' }}>{sub}</div>
    </a>
  )
}
