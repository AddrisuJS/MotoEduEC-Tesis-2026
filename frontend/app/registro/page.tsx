"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Logo, SpeedBG } from "../../lib/ui"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

const USOS = [
  { v: "urbano", l: "Ciudad", icon: "🏙️" },
  { v: "delivery", l: "Delivery", icon: "📦" },
  { v: "carretera", l: "Carretera", icon: "🛣️" },
  { v: "aventura", l: "Aventura", icon: "⛰️" },
]

export default function RegistroPage() {
  const router = useRouter()
  const [nombre, setNombre] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [tipoUso, setTipoUso] = useState("urbano")
  const [error, setError] = useState("")
  const [cargando, setCargando] = useState(false)

  const registrar = async () => {
    setError("")
    if (password.length < 6) { setError("La contraseña debe tener mínimo 6 caracteres"); return }
    setCargando(true)
    try {
      const r = await fetch(`${API}/auth/registro`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, email, password, tipo_uso: tipoUso }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.detail || "Error al registrarse")
      localStorage.setItem("motoeduc_token", data.token)
      localStorage.setItem("motoeduc_usuario", JSON.stringify(data.usuario))
      router.push("/perfil")
    } catch (e: any) {
      setError(e.message)
    } finally { setCargando(false) }
  }

  const inp: any = { width: "100%", boxSizing: "border-box", marginBottom: "0.8rem", padding: "0.7rem 0.9rem", background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 13, color: "#f1f5f9", fontSize: "0.9rem", outline: "none" }
  const lbl: any = { color: "#94a3b8", fontSize: "0.72rem", fontWeight: 600, marginBottom: 5, display: "block" }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem", position: "relative" }}>
      <SpeedBG />
      <div className="fade-up" style={{ width: "100%", maxWidth: 380, position: "relative" }}>

        <div style={{ textAlign: "center", marginBottom: "1.2rem" }}>
          <div style={{ display: "inline-block", marginBottom: "0.6rem" }}><Logo size={58} /></div>
          <div style={{ color: "#f1f5f9", fontSize: "1.4rem", fontWeight: 800 }}>Únete a MotoEdu <span style={{ color: "#ff5930" }}>EC</span></div>
          <div style={{ color: "#94a3b8", fontSize: "0.78rem", marginTop: 2 }}>Empieza a dominar la vía 🏍️</div>
        </div>

        <div className="glass" style={{ padding: "1.4rem" }}>
          <label style={lbl}>NOMBRE COMPLETO</label>
          <input style={inp} value={nombre} onChange={e => setNombre(e.target.value)} placeholder="Tu nombre" />

          <label style={lbl}>CORREO</label>
          <input style={inp} type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="tu@correo.com" />

          <label style={lbl}>CONTRASEÑA</label>
          <input style={inp} type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Mínimo 6 caracteres" />

          <label style={lbl}>¿CÓMO USAS TU MOTO?</label>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", marginBottom: "0.9rem" }}>
            {USOS.map(u => (
              <button key={u.v} onClick={() => setTipoUso(u.v)}
                style={{ display: "flex", alignItems: "center", gap: 7, padding: "0.6rem 0.7rem", borderRadius: 12, fontSize: "0.82rem", fontWeight: 600, cursor: "pointer",
                  background: tipoUso === u.v ? "linear-gradient(90deg,rgba(255,89,48,0.22),rgba(255,149,0,0.12))" : "rgba(0,0,0,0.2)",
                  border: `1px solid ${tipoUso === u.v ? "rgba(255,89,48,0.5)" : "rgba(255,255,255,0.1)"}`,
                  color: tipoUso === u.v ? "#fff" : "#94a3b8" }}>
                <span>{u.icon}</span>{u.l}
              </button>
            ))}
          </div>

          {error && <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.4)", color: "#fca5a5", borderRadius: 10, padding: "0.55rem 0.8rem", fontSize: "0.8rem", marginBottom: "0.9rem" }}>⚠️ {error}</div>}

          <button onClick={registrar} disabled={cargando} className="btn-race" style={{ width: "100%", opacity: cargando ? 0.7 : 1 }}>
            {cargando ? "Creando cuenta..." : "Crear cuenta y arrancar 🏁"}
          </button>

          <div style={{ textAlign: "center", color: "#64748b", fontSize: "0.8rem", marginTop: "1rem" }}>
            ¿Ya tienes cuenta? <Link href="/login" style={{ color: "#ff9575", fontWeight: 700 }}>Inicia sesión</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
