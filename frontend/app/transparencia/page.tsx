'use client'
import Link from 'next/link'
import { useState } from 'react'

/* ═══════════════════════════════════════════════════════════════
   /transparencia — Aviso educativo, privacidad, uso de IA y FAQ
   Accesible sin iniciar sesion.
   ═══════════════════════════════════════════════════════════════ */

const FAQ = [
  { p: '¿MotoEdu EC reemplaza una escuela de conducción?',
    r: 'No. Es una herramienta educativa complementaria que permite reforzar conocimientos y recibir orientación personalizada. La formación práctica y la licencia de conducir se obtienen exclusivamente en escuelas autorizadas.' },
  { p: '¿La inteligencia artificial puede equivocarse?',
    r: 'Sí. Por ello las respuestas deben interpretarse como apoyo educativo. Las decisiones técnicas, mecánicas o legales deben verificarse con fuentes oficiales y especialistas. El asistente está configurado para declarar explícitamente cuando una información no consta en su base de conocimiento, en lugar de improvisar una respuesta.' },
  { p: '¿Cómo se genera una recomendación?',
    r: 'Se analizan las necesidades, experiencia, entorno, tipo de recorrido y preferencias del usuario. Posteriormente el sistema consulta su catálogo y genera una explicación personalizada. El modelo selecciona dentro del catálogo real de la plataforma: no propone modelos inexistentes.' },
  { p: '¿La plataforma vende motocicletas?',
    r: 'No. Su finalidad es exclusivamente educativa. MotoEdu EC no comercializa motocicletas, llantas ni equipamiento, y no percibe ingresos por las recomendaciones que genera.' },
  { p: '¿De dónde se obtiene la información?',
    r: 'De normativa vigente, contenidos educativos, catálogos técnicos, testimonios de la comunidad y fuentes seleccionadas que conforman la base de conocimiento del sistema. Cada respuesta del asistente cita los documentos en que se fundamenta.' },
  { p: '¿Puedo compartir mi historia como motociclista?',
    r: 'Sí. Los usuarios pueden aportar testimonios que, tras una revisión, podrán formar parte del archivo cultural de MotoEdu EC. Las contribuciones se publican de forma seudonimizada.' },
  { p: '¿MotoEdu EC recomienda marcas específicas?',
    r: 'La recomendación se basa en las necesidades del usuario y en las características técnicas de las motocicletas, no en criterios comerciales. El catálogo incluye distintas marcas y rangos de precio.' },
  { p: '¿Qué datos se registran sobre mí?',
    r: 'Únicamente los necesarios para personalizar la experiencia: perfil de conducción, respuestas a las evaluaciones e interacciones con los módulos. No se recopila información que no tenga una finalidad educativa o de investigación previamente informada.' },
]

export default function TransparenciaPage() {
  const [abierta, setAbierta] = useState<number | null>(0)

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem clamp(0.8rem,3vw,1.5rem) 4rem' }}>

      <div className="fade-up" style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div style={{ fontSize: '2.6rem', marginBottom: '0.4rem' }}>🛡️</div>
        <h1 style={{ color: '#F3F6FB', fontSize: 'clamp(1.5rem,5vw,2.1rem)', fontWeight: 800 }}>Transparencia</h1>
        <p style={{ color: '#9FB2CE', fontSize: '0.92rem', marginTop: 6 }}>
          Cómo funciona MotoEdu EC, qué puede y qué no puede hacer
        </p>
      </div>

      {/* AVISO PRINCIPAL */}
      <div className="fade-up" style={{
        background: 'rgba(253,181,0,0.08)', border: '1px solid rgba(253,181,0,0.35)',
        borderLeft: '5px solid var(--amarillo)', borderRadius: 16,
        padding: 'clamp(1.1rem,3vw,1.6rem)', marginBottom: '1.4rem',
      }}>
        <h2 style={{ color: 'var(--amarillo)', fontSize: '1.05rem', fontWeight: 800, marginBottom: '0.8rem' }}>
          Aviso educativo y de responsabilidad
        </h2>
        <P>MotoEdu EC constituye un proyecto académico, educativo y de investigación desarrollado para promover la seguridad vial, la formación responsable y la cultura motociclista mediante inteligencia artificial generativa.</P>
        <P>Los contenidos y recomendaciones generados por la plataforma tienen fines educativos y orientativos. <b style={{ color: '#F0DFAE' }}>No sustituyen</b> la formación impartida por escuelas de conducción autorizadas, las indicaciones de las autoridades de tránsito, las especificaciones de los fabricantes, la revisión de un técnico mecánico ni la asesoría de profesionales especializados.</P>
        <P>La recomendación de una motocicleta o una llanta debe verificarse considerando la compatibilidad técnica, la homologación, el manual del fabricante, las condiciones reales de uso y la normativa vigente.</P>
        <P style={{ marginBottom: 0 }}>MotoEdu EC no promueve conductas de riesgo, competencias ilegales, exceso de velocidad ni modificaciones que puedan comprometer la seguridad del conductor o de terceros.</P>
      </div>

      <Bloque icono="🤖" titulo="Uso responsable de la inteligencia artificial">
        <P>El asistente de MotoEdu EC no responde desde el conocimiento general del modelo de lenguaje. Antes de generar una respuesta recupera fragmentos de una base de conocimiento compuesta por normativa y contenidos educativos previamente seleccionados, y está instruido para fundamentar cada afirmación en esos documentos.</P>
        <P>Cuando la información solicitada no consta en su base de conocimiento, el sistema debe declararlo explícitamente en lugar de improvisar. Esta salvaguarda es especialmente relevante en educación vial: un dato normativo incorrecto puede derivar en una sanción o en un siniestro.</P>
        <P>Aun así, ningún sistema de inteligencia artificial está libre de error. Los resultados deben interpretarse como apoyo al aprendizaje y contrastarse con fuentes oficiales cuando se trate de decisiones técnicas, mecánicas o legales.</P>
      </Bloque>

      <Bloque icono="🔒" titulo="Protección de datos y privacidad">
        <P>MotoEdu EC recopila únicamente la información necesaria para personalizar la experiencia educativa, evaluar el aprendizaje y mejorar el funcionamiento de la plataforma.</P>
        <P>Los datos de los participantes utilizados en investigaciones son tratados de forma confidencial, anonimizados en los análisis y empleados exclusivamente para las finalidades previamente informadas mediante consentimiento.</P>
        <P>La plataforma no comparte información personal con terceros sin autorización expresa del usuario y sin el respaldo institucional correspondiente.</P>
        <P style={{ marginBottom: 0 }}>Los testimonios publicados en el espacio de cultura motera se difunden de forma seudonimizada: el contenido del relato se conserva íntegro, pero la identidad de su autor no se revela.</P>
      </Bloque>

      <Bloque icono="⚖️" titulo="Independencia académica">
        <P>MotoEdu EC es un proyecto académico de la Universidad Politécnica Salesiana. Su finalidad es educativa y de investigación, y no responde a intereses comerciales.</P>
        <P style={{ marginBottom: 0 }}>Las recomendaciones de motocicletas y llantas se elaboran a partir de las necesidades declaradas por el usuario y de las características técnicas de los productos, no de criterios de promoción. La plataforma no percibe ingresos por las recomendaciones que genera.</P>
      </Bloque>

      <Bloque icono="❓" titulo="Preguntas frecuentes">
        <div style={{ display: 'grid', gap: '0.5rem' }}>
          {FAQ.map((f, i) => (
            <div key={i} style={{
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.10)',
              borderRadius: 12, overflow: 'hidden',
            }}>
              <button onClick={() => setAbierta(abierta === i ? null : i)}
                style={{
                  width: '100%', textAlign: 'left', background: 'transparent', border: 'none',
                  padding: '0.85rem 1rem', color: '#F3F6FB', fontSize: '0.89rem', fontWeight: 700,
                  display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center',
                }}>
                <span>{f.p}</span>
                <span style={{ color: 'var(--amarillo)', fontSize: '1.1rem', flexShrink: 0 }}>{abierta === i ? '−' : '+'}</span>
              </button>
              {abierta === i && (
                <div style={{ padding: '0 1rem 0.95rem', color: '#B9C9E2', fontSize: '0.85rem', lineHeight: 1.65, textAlign: 'justify' }}>
                  {f.r}
                </div>
              )}
            </div>
          ))}
        </div>
      </Bloque>

      <Bloque icono="✉️" titulo="Contacto">
        <P style={{ marginBottom: 0 }}>Para consultas académicas, propuestas de colaboración o participación en investigaciones relacionadas con MotoEdu EC, puede contactarse con el equipo responsable a través de los canales institucionales de la Universidad Politécnica Salesiana, sede Cuenca.</P>
      </Bloque>

      <div style={{ display: 'flex', gap: '0.7rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '1.8rem' }}>
        <Link href="/proyecto" className="btn-ghost" style={{ textDecoration: 'none' }}>Conocer el proyecto</Link>
        <Link href="/" className="btn-race" style={{ textDecoration: 'none' }}>Volver al inicio</Link>
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center', color: '#6B82A6', fontSize: '0.78rem' }}>
        Universidad Politécnica Salesiana · Sede Cuenca · 2026
      </div>
    </div>
  )
}

function Bloque({ icono, titulo, children }: { icono: string; titulo: string; children: React.ReactNode }) {
  return (
    <section className="glass fade-up" style={{ padding: 'clamp(1.1rem,3vw,1.6rem)', marginBottom: '1.3rem' }}>
      <h2 style={{
        color: '#F3F6FB', fontSize: 'clamp(1rem,3.2vw,1.25rem)', fontWeight: 800,
        marginBottom: '0.9rem', paddingBottom: '0.6rem',
        borderBottom: '1px solid rgba(253,181,0,0.22)',
        display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <span>{icono}</span>{titulo}
      </h2>
      {children}
    </section>
  )
}
function P({ children, style }: { children: React.ReactNode; style?: any }) {
  return <p style={{ color: '#CBD8EC', fontSize: '0.89rem', lineHeight: 1.7, marginBottom: '0.8rem', textAlign: 'justify', ...style }}>{children}</p>
}
