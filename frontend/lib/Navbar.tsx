"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "./useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

const LINKS = [
  { href: "/evaluacion", icon: "📋", label: "Evaluación" },
  { href: "/educacion",  icon: "📚", label: "Aprender" },
  { href: "/asistente",  icon: "💬", label: "Asistente" },
  { href: "/arcade",     icon: "🕹️", label: "Arcade" },
  { href: "/ruta",       icon: "🛣️", label: "Ruta" },
  { href: "/duelos",     icon: "⚔️", label: "Duelos" },
  { href: "/garaje",     icon: "🔧", label: "Garaje" },
  { href: "/top",        icon: "🏆", label: "Top" },
]

export default function Navbar() {
  const { usuario, cerrarSesion } = useAuth(false)
  const pathname = usePathname()
  const router = useRouter()
  const [stats, setStats] = useState<any>(null)
  const [menu, setMenu] = useState(false)

  useEffect(() => { setMenu(false) }, [pathname])
  useEffect(() => {
    if (usuario) fetch(`${API}/m8/arcade/stats/${usuario.id}`).then(r => r.json()).then(setStats).catch(() => {})
  }, [usuario, pathname])

  // En login/registro solo mostramos la marca
  const minimal = pathname === "/login" || pathname === "/registro"

  const linkStyle = (activo: boolean): any => ({
    display: "flex", alignItems: "center", gap: 5, padding: "0.42rem 0.7rem",
    borderRadius: 10, fontSize: "0.82rem", fontWeight: 600, whiteSpace: "nowrap",
    color: activo ? "#fff" : "#94a3b8",
    background: activo ? "rgba(59,130,246,0.22)" : "transparent",
    border: activo ? "1px solid rgba(59,130,246,0.5)" : "1px solid transparent",
    transition: "all .15s",
  })

  return (
    <>
      <nav style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(11,18,32,0.85)", backdropFilter: "blur(12px)",
        borderBottom: "1px solid #223049",
        padding: "0.5rem clamp(0.7rem, 2.5vw, 1.4rem)",
        display: "flex", alignItems: "center", gap: "0.7rem",
      }}>
        {/* Marca */}
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none", marginRight: "0.4rem" }}>
          <span style={{ fontSize: "1.4rem" }}>🏍️</span>
          <span style={{ color: "#f1f5f9", fontWeight: 800, fontSize: "1.02rem", letterSpacing: "-0.01em" }}>
            MotoEdu <span style={{ color: "#3b82f6" }}>EC</span>
          </span>
        </Link>

        {!minimal && usuario && (
          <div className="nav-links" style={{ flex: 1, overflow: "hidden" }}>
            {LINKS.map(l => (
              <Link key={l.href} href={l.href} style={linkStyle(pathname === l.href)}>
                <span>{l.icon}</span><span>{l.label}</span>
              </Link>
            ))}
          </div>
        )}
        {(!usuario || minimal) && <div style={{ flex: 1 }} />}

        {/* Lado derecho */}
        {usuario && !minimal && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginLeft: "auto" }}>
            {stats && (
              <Link href="/garaje" style={{
                display: "flex", alignItems: "center", gap: 8, textDecoration: "none",
                background: "rgba(30,41,59,0.9)", border: "1px solid #334155",
                borderRadius: 20, padding: "0.28rem 0.75rem",
              }}>
                <span style={{ color: "#facc15", fontSize: "0.78rem", fontWeight: 800 }}>⚡ {stats.xp_total ?? 0}</span>
                <span style={{ color: "#fb923c", fontSize: "0.78rem", fontWeight: 800 }}>🔥 {stats.racha_actual ?? 0}</span>
              </Link>
            )}
            {usuario.rol === "admin" && (
              <button onClick={() => router.push("/admin")} title="Panel del investigador"
                style={{ background: "rgba(250,204,21,0.12)", border: "1px solid rgba(250,204,21,0.5)", color: "#fde68a", borderRadius: 10, padding: "0.4rem 0.7rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 700 }}>
                👨‍💼
              </button>
            )}
            <button onClick={cerrarSesion} title={`Cerrar sesión (${usuario.nombre.split(" ")[0]})`}
              style={{ display: "flex", alignItems: "center", gap: 6, background: "rgba(239,68,68,0.10)", border: "1px solid rgba(239,68,68,0.45)", color: "#fca5a5", borderRadius: 10, padding: "0.4rem 0.75rem", fontSize: "0.8rem", cursor: "pointer", fontWeight: 700 }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              <span className="nav-links">Salir</span>
            </button>
            {/* Hamburguesa móvil */}
            <button className="nav-burger" onClick={() => setMenu(m => !m)}
              style={{ alignItems: "center", justifyContent: "center", background: "rgba(30,41,59,0.9)", border: "1px solid #334155", color: "#e2e8f0", borderRadius: 10, padding: "0.4rem 0.6rem", fontSize: "1rem", cursor: "pointer" }}>
              {menu ? "✕" : "☰"}
            </button>
          </div>
        )}
        {!usuario && !minimal && (
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Link href="/login" style={{ background: "rgba(30,41,59,0.9)", border: "1px solid #3b82f6", color: "#93c5fd", borderRadius: 10, padding: "0.4rem 0.9rem", fontSize: "0.8rem", fontWeight: 700 }}>Entrar</Link>
            <Link href="/registro" style={{ background: "linear-gradient(90deg,#22c55e,#16a34a)", color: "#fff", borderRadius: 10, padding: "0.4rem 0.9rem", fontSize: "0.8rem", fontWeight: 700 }}>Regístrate</Link>
          </div>
        )}
      </nav>

      {/* Menú móvil desplegable */}
      {menu && usuario && !minimal && (
        <div style={{
          position: "sticky", top: 53, zIndex: 99, background: "rgba(11,18,32,0.97)",
          backdropFilter: "blur(12px)", borderBottom: "1px solid #223049",
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "0.4rem", padding: "0.7rem",
        }} className="fade-up">
          {LINKS.map(l => (
            <Link key={l.href} href={l.href} style={{
              display: "flex", alignItems: "center", gap: 8, padding: "0.65rem 0.8rem",
              borderRadius: 12, fontSize: "0.88rem", fontWeight: 600,
              color: pathname === l.href ? "#fff" : "#cbd5e1",
              background: pathname === l.href ? "rgba(59,130,246,0.25)" : "rgba(30,41,59,0.7)",
              border: "1px solid #2a3852",
            }}>
              <span style={{ fontSize: "1.1rem" }}>{l.icon}</span>{l.label}
            </Link>
          ))}
        </div>
      )}
    </>
  )
}
