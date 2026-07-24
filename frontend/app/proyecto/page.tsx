'use client'
import Link from 'next/link'
import { LogoCompleto } from '../../lib/LogoMarca'

/* ═══════════════════════════════════════════════════════════════
   /proyecto — Pagina publica institucional
   Accesible sin iniciar sesion.
   ═══════════════════════════════════════════════════════════════ */

const OBJETIVOS = [
  'Promover una cultura de conducción responsable y prevención de accidentes.',
  'Generar contenidos personalizados de educación vial mediante inteligencia artificial.',
  'Orientar a los usuarios en la selección adecuada de motocicletas según sus necesidades.',
  'Recomendar llantas de acuerdo con el tipo de moto, terreno, clima y uso previsto.',
  'Explicar los riesgos asociados al uso incorrecto de motocicletas, neumáticos y equipamiento.',
  'Facilitar el acceso a información normativa y técnica mediante un asistente conversacional.',
  'Fortalecer el conocimiento sobre mantenimiento preventivo y revisión básica de la motocicleta.',
  'Preservar y difundir historias, experiencias y elementos culturales del motociclismo ecuatoriano.',
  'Utilizar gamificación para mejorar la motivación y el aprendizaje.',
  'Generar información útil para investigaciones sobre seguridad vial y aprendizaje.',
]

const AREAS = [
  { icon: '🛣️', t: 'Seguridad vial', d: 'Normativa, señales, conducción preventiva, distancia de seguimiento, velocidad, lluvia y comportamiento ante situaciones de riesgo.' },
  { icon: '🏍️', t: 'Motocicletas', d: 'Tipos de motos, características, cilindraje, ergonomía, peso, altura, potencia y usos recomendados.' },
  { icon: '⚙️', t: 'Llantas', d: 'Tipos de neumáticos, labrado, presión, desgaste, adherencia y comportamiento en lluvia.' },
  { icon: '🪖', t: 'Equipamiento', d: 'Casco, chaqueta, guantes, botas, protecciones y elementos reflectivos.' },
  { icon: '🔧', t: 'Mantenimiento', d: 'Cadena, frenos, luces, neumáticos, niveles, suspensión y revisiones antes de iniciar una ruta.' },
  { icon: '🤝', t: 'Cultura motera', d: 'Historia, testimonios, experiencias, rutas, valores y convivencia en la comunidad motociclista.' },
]

const FLUJO = [
  'Perfil del motociclista',
  'Necesidades, experiencia y entorno de conducción',
  'Consulta al asistente o selección de un módulo',
  'Recuperación de información verificada',
  'Procesamiento mediante IA generativa',
  'Generación de contenido personalizado',
  'Recomendación de moto, llanta o contenido educativo',
  'Retroalimentación, evaluación y gamificación',
]

const TECNOLOGIAS = [
  { g: 'Frontend', items: ['Next.js', 'TypeScript', 'Interfaz web adaptable'] },
  { g: 'Backend', items: ['FastAPI', 'API REST', 'Autenticación JWT'] },
  { g: 'Inteligencia artificial', items: ['Claude API', 'Ingeniería de prompts', 'Arquitectura RAG'] },
  { g: 'Bases de datos', items: ['PostgreSQL', 'ChromaDB', 'Catálogos estructurados'] },
  { g: 'Infraestructura', items: ['Docker Compose', 'Cloudflare Tunnel', 'Dominio propio'] },
  { g: 'Analítica', items: ['Panel del investigador', 'Pruebas estadísticas', 'Indicadores de aprendizaje'] },
]

const PRINCIPIOS = [
  'Seguridad como prioridad', 'Educación antes que promoción comercial',
  'Uso responsable de la inteligencia artificial', 'Transparencia sobre el funcionamiento',
  'Protección de los datos personales', 'Respeto a la comunidad motera',
  'Rigurosidad técnica', 'Contenidos verificables',
  'Inclusión de todos los niveles de experiencia', 'Prevención de riesgos',
  'Independencia académica', 'Mejora continua',
]

export default function ProyectoPage() {
  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '2rem clamp(0.8rem,3vw,1.5rem) 4rem' }}>

      <div className="fade-up" style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <LogoCompleto max={480} />
        <p style={{ color: 'var(--dorado)', fontSize: 'clamp(0.95rem,3vw,1.15rem)', fontWeight: 700, marginTop: '1.1rem' }}>
          Aprender, elegir y rodar con seguridad
        </p>
      </div>

      <Bloque titulo="¿Qué es MotoEdu EC?">
        <P>MotoEdu EC es una plataforma educativa e interactiva desarrollada para fortalecer la seguridad vial y la cultura motociclista en Ecuador mediante el uso responsable de inteligencia artificial generativa.</P>
        <P>El sistema ofrece contenidos educativos personalizados y responde consultas relacionadas con conducción segura, normativa, equipamiento, mantenimiento preventivo, tipos de motocicletas y selección adecuada de llantas. También dispone de herramientas para recomendar motocicletas y neumáticos según el perfil, experiencia, entorno, presupuesto y necesidades del usuario.</P>
        <P>La plataforma incorpora además un espacio dedicado a la historia, experiencias y memoria de la comunidad motera ecuatoriana, mediante testimonios, contenidos culturales y recursos interactivos.</P>
      </Bloque>

      <Bloque titulo="Nuestro propósito">
        <P>MotoEdu EC nace de una preocupación real: el incremento de los siniestros de tránsito en los que se encuentran involucrados motociclistas y el desconocimiento que todavía existe sobre el uso adecuado de las motocicletas, las llantas y el equipamiento de seguridad.</P>
        <P>Muchas personas adquieren una moto sin conocer plenamente sus características, las condiciones para las que fue diseñada o los riesgos que implica utilizar componentes inadecuados. Una motocicleta de enduro, una urbana o una de turismo responden a necesidades distintas. Lo mismo ocurre con las llantas: no todos los neumáticos ofrecen el mismo comportamiento sobre asfalto, tierra, lluvia o carretera.</P>
        <P>Nuestro propósito es utilizar la inteligencia artificial generativa para ofrecer orientación educativa personalizada, comprensible y contextualizada, que ayude a las personas a tomar decisiones más responsables antes y después de adquirir una motocicleta.</P>
      </Bloque>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: '1rem', marginBottom: '1.4rem' }}>
        <Tarjeta icono="🎯" titulo="Misión">
          Desarrollar y ofrecer herramientas educativas basadas en inteligencia artificial generativa que permitan personalizar el aprendizaje sobre seguridad vial, conducción responsable, tipos de motocicletas, llantas, equipamiento y cultura motera, contribuyendo a una toma de decisiones informada y a la prevención de riesgos entre los motociclistas ecuatorianos.
        </Tarjeta>
        <Tarjeta icono="🔭" titulo="Visión">
          Consolidar a MotoEdu EC como una plataforma ecuatoriana de referencia en educación vial personalizada para motociclistas, reconocida por integrar inteligencia artificial generativa, gamificación, analítica de datos y cultura motera, con capacidad de extenderse a instituciones educativas, escuelas de conducción, organizaciones, comunidades moteras y empresas del sector.
        </Tarjeta>
      </div>

      <Bloque titulo="Objetivos permanentes">
        <div style={{ display: 'grid', gap: '0.55rem' }}>
          {OBJETIVOS.map((o, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <span style={{ color: 'var(--amarillo)', fontWeight: 800, fontSize: '0.85rem', minWidth: 20 }}>{String(i + 1).padStart(2, '0')}</span>
              <span style={{ color: '#CBD8EC', fontSize: '0.9rem', lineHeight: 1.55 }}>{o}</span>
            </div>
          ))}
        </div>
      </Bloque>

      <Bloque titulo="¿Cómo funciona?">
        <P>MotoEdu EC comienza por conocer el perfil del usuario: su nivel de experiencia, tipo de uso, entorno de conducción, ciudad, clima habitual y preferencias. A partir de esa información, la plataforma adapta las explicaciones, escenarios, preguntas y recomendaciones.</P>
        <P>Cuando el usuario realiza una consulta, el sistema busca información en su base de conocimiento y entrega esos contenidos a un modelo de inteligencia artificial generativa. La respuesta se construye considerando tanto las fuentes disponibles como el perfil del motociclista.</P>
        <div style={{ display: 'grid', gap: '0.4rem', marginTop: '1rem' }}>
          {FLUJO.map((f, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(253,181,0,0.14)',
              borderRadius: 12, padding: '0.6rem 0.9rem',
            }}>
              <span style={{
                width: 26, height: 26, borderRadius: 8, flexShrink: 0,
                background: 'var(--race-grad)', color: '#04122B',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 800, fontSize: '0.75rem',
              }}>{i + 1}</span>
              <span style={{ color: '#DCE6F5', fontSize: '0.87rem' }}>{f}</span>
            </div>
          ))}
        </div>
        <P style={{ marginTop: '1rem' }}>De esta manera, una persona que utiliza la moto para reparto urbano recibe orientaciones distintas a las de quien conduce en carretera, practica enduro o realiza viajes de larga distancia.</P>
      </Bloque>

      <Bloque titulo="Áreas de aprendizaje">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(250px,1fr))', gap: '0.8rem' }}>
          {AREAS.map(a => (
            <div key={a.t} className="glass-sm" style={{ padding: '1rem' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: 6 }}>{a.icon}</div>
              <div style={{ color: 'var(--amarillo)', fontWeight: 800, fontSize: '0.92rem', marginBottom: 4 }}>{a.t}</div>
              <div style={{ color: '#9FB2CE', fontSize: '0.8rem', lineHeight: 1.5 }}>{a.d}</div>
            </div>
          ))}
        </div>
      </Bloque>

      <Bloque titulo="La inteligencia artificial como núcleo">
        <P>La inteligencia artificial generativa es el núcleo de MotoEdu EC. Su función no consiste únicamente en responder preguntas, sino en crear experiencias educativas adaptadas a cada motociclista.</P>
        <P>La plataforma genera explicaciones, ejemplos, escenarios de conducción, cuestionarios, retroalimentación y recomendaciones contextualizadas de acuerdo con el perfil del usuario. Una persona que circula diariamente en Cuenca bajo lluvia recibe contenidos específicos sobre adherencia, frenado, visibilidad, presión de neumáticos y selección de llantas para pavimento mojado.</P>
        <P>La inteligencia artificial también permite explicar por qué una recomendación puede ser adecuada o riesgosa, evitando presentar únicamente una lista de productos o modelos sin contexto educativo.</P>
      </Bloque>

      <Bloque titulo="Metodología y confiabilidad de las respuestas">
        <P>MotoEdu EC emplea una arquitectura de inteligencia artificial generativa apoyada en recuperación de información. Antes de generar una respuesta, el sistema busca contenidos relacionados en una base de conocimiento compuesta por normativa, contenidos educativos y documentación previamente seleccionada.</P>
        <P>Esta arquitectura permite disminuir el riesgo de respuestas generadas únicamente desde el conocimiento general del modelo. El proyecto incorpora procesos de evaluación técnica para analizar la pertinencia, recuperación y fidelidad de las respuestas. Sin embargo, como todo sistema de inteligencia artificial, sus resultados deben interpretarse como apoyo educativo y no como una fuente infalible.</P>
      </Bloque>

      <Bloque titulo="Principios">
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {PRINCIPIOS.map(p => (
            <span key={p} style={{
              background: 'rgba(253,181,0,0.10)', border: '1px solid rgba(253,181,0,0.30)',
              color: '#F0DFAE', borderRadius: 999, padding: '0.4rem 0.85rem', fontSize: '0.8rem', fontWeight: 600,
            }}>{p}</span>
          ))}
        </div>
      </Bloque>

      <Bloque titulo="Tecnologías utilizadas">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(230px,1fr))', gap: '0.8rem' }}>
          {TECNOLOGIAS.map(t => (
            <div key={t.g} className="glass-sm" style={{ padding: '0.9rem 1rem' }}>
              <div style={{ color: 'var(--amarillo)', fontWeight: 800, fontSize: '0.85rem', marginBottom: 6 }}>{t.g}</div>
              {t.items.map(i => (
                <div key={i} style={{ color: '#9FB2CE', fontSize: '0.8rem', lineHeight: 1.7 }}>· {i}</div>
              ))}
            </div>
          ))}
        </div>
      </Bloque>

      <Bloque titulo="Equipo responsable">
        <P>MotoEdu EC ha sido desarrollado como trabajo de titulación en la Carrera de Ingeniería de Sistemas de la Universidad Politécnica Salesiana, sede Cuenca.</P>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: '1rem', marginTop: '1rem' }}>
          <Persona rol="Dirección académica y científica" nombre="PhD. Omar Gustavo Bravo Quezada"
            detalle={['Docente-investigador · Carrera de Computación', 'Universidad Politécnica Salesiana, sede Cuenca', 'Miembro del grupo GIHP4C', 'Tutor y director académico del proyecto']} />
          <Persona rol="Desarrollo tecnológico" nombre="José Addrisu Sanango Romero"
            detalle={['Estudiante de Ingeniería de Sistemas', 'Universidad Politécnica Salesiana, sede Cuenca', 'Análisis, diseño, desarrollo, implementación y validación']} />
        </div>
        <P style={{ marginTop: '1rem' }}>El proyecto se concibe como una iniciativa abierta a la participación futura de estudiantes, docentes, investigadores, motociclistas, instituciones y empresas interesadas en contribuir con la educación vial y la seguridad de la comunidad motera.</P>
      </Bloque>

      <Bloque titulo="Grupo de investigación GIHP4C">
        <P>MotoEdu EC constituye una iniciativa académica y tecnológica vinculada al Grupo de Investigación en Cloud Computing, Smart Cities &amp; High Performance Computing (GIHP4C) de la Universidad Politécnica Salesiana.</P>
        <P>El proyecto se alinea con las líneas de investigación relacionadas con inteligencia artificial, plataformas educativas, computación en la nube, analítica de datos, gamificación y desarrollo de soluciones inteligentes orientadas a necesidades reales de la sociedad.</P>
      </Bloque>

      <Bloque titulo="Integración con Edutainment">
        <P>MotoEdu EC fue concebido para su futura integración con Edutainment, plataforma educativa desarrollada en el contexto del grupo GIHP4C. Durante esta primera fase, MotoEdu EC se implementó con infraestructura, autenticación, base de datos y despliegue propios.</P>
        <P>La arquitectura desarrollada permite planificar una integración posterior, de manera que los módulos de educación vial, inteligencia artificial, gamificación y analítica puedan formar parte de un ecosistema educativo más amplio, compartiendo servicios de autenticación, seguimiento de usuarios y análisis de resultados.</P>
      </Bloque>

      <Bloque titulo="Investigación y publicaciones">
        <P>MotoEdu EC se concibe como una plataforma de investigación en crecimiento. Los resultados del proyecto podrán dar lugar a trabajos de titulación, artículos científicos, ponencias y nuevas soluciones tecnológicas relacionadas con inteligencia artificial generativa, educación vial, gamificación y seguridad motociclista.</P>
        <P style={{ color: '#8FA3C0', fontStyle: 'italic' }}>Las publicaciones y productos científicos asociados serán incorporados progresivamente en esta sección.</P>
      </Bloque>

      <div className="glass" style={{ padding: '1.6rem', textAlign: 'center', marginTop: '2rem' }}>
        <div style={{ color: '#F3F6FB', fontSize: '1.05rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          ¿Quieres aprender con MotoEdu EC?
        </div>
        <p style={{ color: '#9FB2CE', fontSize: '0.88rem', marginBottom: '1.1rem' }}>
          Crea tu perfil y recibe contenido adaptado a tu moto, tu experiencia y tu zona de conducción.
        </p>
        <div style={{ display: 'flex', gap: '0.7rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/registro" className="btn-race" style={{ textDecoration: 'none' }}>Crear mi cuenta</Link>
          <Link href="/transparencia" className="btn-ghost" style={{ textDecoration: 'none' }}>Aviso educativo</Link>
        </div>
      </div>

      <div style={{ marginTop: '2rem', textAlign: 'center', color: '#6B82A6', fontSize: '0.78rem' }}>
        Universidad Politécnica Salesiana · Sede Cuenca · 2026
      </div>
    </div>
  )
}

/* ─── Auxiliares ─── */
function Bloque({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <section className="glass fade-up" style={{ padding: 'clamp(1.1rem,3vw,1.7rem)', marginBottom: '1.4rem' }}>
      <h2 style={{
        color: '#F3F6FB', fontSize: 'clamp(1.05rem,3.4vw,1.35rem)', fontWeight: 800,
        marginBottom: '0.9rem', paddingBottom: '0.6rem',
        borderBottom: '1px solid rgba(253,181,0,0.22)',
      }}>{titulo}</h2>
      {children}
    </section>
  )
}
function P({ children, style }: { children: React.ReactNode; style?: any }) {
  return <p style={{ color: '#CBD8EC', fontSize: '0.9rem', lineHeight: 1.7, marginBottom: '0.8rem', textAlign: 'justify', ...style }}>{children}</p>
}
function Tarjeta({ icono, titulo, children }: { icono: string; titulo: string; children: React.ReactNode }) {
  return (
    <div className="glass fade-up" style={{ padding: '1.4rem' }}>
      <div style={{ fontSize: '1.7rem', marginBottom: '0.5rem' }}>{icono}</div>
      <h3 style={{ color: 'var(--amarillo)', fontSize: '1.05rem', fontWeight: 800, marginBottom: '0.6rem' }}>{titulo}</h3>
      <p style={{ color: '#CBD8EC', fontSize: '0.87rem', lineHeight: 1.65, textAlign: 'justify' }}>{children}</p>
    </div>
  )
}
function Persona({ rol, nombre, detalle }: { rol: string; nombre: string; detalle: string[] }) {
  return (
    <div className="glass-sm" style={{ padding: '1rem 1.1rem' }}>
      <div style={{ color: 'var(--dorado)', fontSize: '0.72rem', fontWeight: 800, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: 6 }}>{rol}</div>
      <div style={{ color: '#F3F6FB', fontWeight: 800, fontSize: '0.95rem', marginBottom: 8 }}>{nombre}</div>
      {detalle.map((d, i) => <div key={i} style={{ color: '#9FB2CE', fontSize: '0.79rem', lineHeight: 1.6 }}>{d}</div>)}
    </div>
  )
}
