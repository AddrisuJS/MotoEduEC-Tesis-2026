"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Logo, SpeedBG, IconSalir } from "../../lib/ui"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [cargando, setCargando] = useState(false)

  const entrar = async () => {
    setError(""); setCargando(true)
    try {
      const r = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || "Error al iniciar sesión")
      localStorage.setItem("motoeduc_token", data.token)
      localStorage.setItem("motoeduc_usuario", JSON.stringify(data.usuario))
      router.push("/perfil")
    } catch (e: any) {
      setError(e.message)
    } finally { setCargando(false) }
  }

  const inp: any = { flex: 1, background: "transparent", border: "none", outline: "none", color: "#f1f5f9", fontSize: "0.9rem" }
  const wrap: any = (focus: boolean) => ({ display: "flex", alignItems: "center", gap: 9, background: "rgba(0,0,0,0.25)", border: `1px solid ${focus ? "rgba(255,89,48,0.5)" : "rgba(255,255,255,0.12)"}`, borderRadius: 13, padding: "0.7rem 0.9rem", marginBottom: "0.8rem" })

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem", position: "relative" }}>
      <SpeedBG />
      <div className="fade-up" style={{ width: "100%", maxWidth: 360, position: "relative" }}>

        <div style={{ textAlign: "center", marginBottom: "1.4rem" }}>
          <div style={{ display: "inline-block", marginBottom: "0.7rem" }}><Logo size={64} /></div>
          <div style={{ color: "#f1f5f9", fontSize: "1.5rem", fontWeight: 800, letterSpacing: "-0.02em" }}>MotoEdu <span style={{ color: "#ff5930" }}>EC</span></div>
          <div style={{ color: "#94a3b8", fontSize: "0.8rem", marginTop: 2 }}>Educación vial inteligente 🏍️</div>
        </div>

        <div className="glass" style={{ padding: "1.5rem" }}>
          <div style={{ color: "#e2e8f0", fontSize: "1.05rem", fontWeight: 700, marginBottom: "1.1rem" }}>Inicia sesión</div>

          <div style={{ color: "#94a3b8", fontSize: "0.72rem", fontWeight: 600, marginBottom: 5 }}>CORREO</div>
          <div style={wrap(false)}>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2"><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" /></svg>
            <input style={inp} type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="tu@correo.com" />
          </div>

          <div style={{ color: "#94a3b8", fontSize: "0.72rem", fontWeight: 600, marginBottom: 5 }}>CONTRASEÑA</div>
          <div style={wrap(false)}>
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#ff9575" strokeWidth="2"><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V7a4 4 0 018 0v4" /></svg>
            <input style={inp} type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" onKeyDown={e => e.key === "Enter" && entrar()} />
          </div>

          {error && <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.4)", color: "#fca5a5", borderRadius: 10, padding: "0.55rem 0.8rem", fontSize: "0.8rem", marginBottom: "0.9rem" }}>⚠️ {error}</div>}

          <button onClick={entrar} disabled={cargando} className="btn-race" style={{ width: "100%", opacity: cargando ? 0.7 : 1 }}>
            {cargando ? "Entrando..." : "Entrar a la pista →"}
          </button>

          <div style={{ textAlign: "center", color: "#64748b", fontSize: "0.8rem", marginTop: "1rem" }}>
            ¿No tienes cuenta? <Link href="/registro" style={{ color: "#ff9575", fontWeight: 700 }}>Regístrate gratis</Link>
          </div>
        </div>

        <div style={{ textAlign: "center", color: "#475569", fontSize: "0.68rem", marginTop: "1rem" }}>UPS Cuenca 2026 · Proyecto de titulación</div>
      </div>
    </div>
  )
}
