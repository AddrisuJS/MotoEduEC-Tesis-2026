"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

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

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #172554 100%)", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: 420, background: "rgba(30,41,59,0.85)", backdropFilter: "blur(8px)",
        border: "1px solid #334155", borderRadius: 20, padding: "2.5rem 2rem", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }}>

        <div style={{ textAlign: "center", marginBottom: "1.8rem" }}>
          <div style={{ fontSize: "2.8rem" }}>🏍️</div>
          <h1 style={{ color: "#f1f5f9", fontSize: "1.6rem", fontWeight: 800, margin: "0.4rem 0 0.2rem" }}>
            MotoEdu <span style={{ color: "#3b82f6" }}>EC</span>
          </h1>
          <p style={{ color: "#94a3b8", fontSize: "0.85rem", margin: 0 }}>
            Educación vial inteligente para motociclistas
          </p>
        </div>

        <label style={{ color: "#cbd5e1", fontSize: "0.8rem", fontWeight: 600 }}>Correo electrónico</label>
        <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="tu@correo.com"
          style={{ width: "100%", boxSizing: "border-box", margin: "0.35rem 0 1rem", padding: "0.75rem 1rem",
            background: "#0f172a", border: "1px solid #334155", borderRadius: 12, color: "#f1f5f9", fontSize: "0.95rem", outline: "none" }} />

        <label style={{ color: "#cbd5e1", fontSize: "0.8rem", fontWeight: 600 }}>Contraseña</label>
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="••••••••"
          onKeyDown={e => e.key === "Enter" && entrar()}
          style={{ width: "100%", boxSizing: "border-box", margin: "0.35rem 0 1.2rem", padding: "0.75rem 1rem",
            background: "#0f172a", border: "1px solid #334155", borderRadius: 12, color: "#f1f5f9", fontSize: "0.95rem", outline: "none" }} />

        {error && (
          <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid #ef4444", color: "#fca5a5",
            borderRadius: 10, padding: "0.6rem 0.9rem", fontSize: "0.82rem", marginBottom: "1rem" }}>
            ⚠️ {error}
          </div>
        )}

        <button onClick={entrar} disabled={cargando || !email || !password}
          style={{ width: "100%", padding: "0.85rem", background: cargando ? "#334155" : "linear-gradient(90deg,#3b82f6,#2563eb)",
            border: "none", borderRadius: 12, color: "#fff", fontWeight: 700, fontSize: "1rem",
            cursor: cargando ? "wait" : "pointer", transition: "all .2s" }}>
          {cargando ? "Entrando..." : "Iniciar sesión"}
        </button>

        <p style={{ color: "#94a3b8", fontSize: "0.85rem", textAlign: "center", marginTop: "1.3rem" }}>
          ¿No tienes cuenta?{" "}
          <Link href="/registro" style={{ color: "#60a5fa", fontWeight: 700, textDecoration: "none" }}>Regístrate gratis</Link>
        </p>
        <p style={{ color: "#475569", fontSize: "0.7rem", textAlign: "center", marginTop: "1rem" }}>
          UPS Cuenca 2026 — Proyecto de titulación
        </p>
      </div>
    </div>
  )
}
