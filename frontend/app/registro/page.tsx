"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

const PERFILES = [
  { id: "delivery", nombre: "🛵 Delivery / Trabajo" },
  { id: "urbano", nombre: "🏙️ Urbano diario" },
  { id: "touring", nombre: "🛣️ Touring / Viajes" },
  { id: "enduro", nombre: "⛰️ Aventura / Enduro" },
  { id: "deportivo", nombre: "🏁 Deportivo" },
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

  const inputStyle = { width: "100%", boxSizing: "border-box" as const, margin: "0.35rem 0 1rem", padding: "0.75rem 1rem",
    background: "#0f172a", border: "1px solid #334155", borderRadius: 12, color: "#f1f5f9", fontSize: "0.95rem", outline: "none" }
  const labelStyle = { color: "#cbd5e1", fontSize: "0.8rem", fontWeight: 600 }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #172554 100%)", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: 460, background: "rgba(30,41,59,0.85)", backdropFilter: "blur(8px)",
        border: "1px solid #334155", borderRadius: 20, padding: "2.2rem 2rem", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }}>

        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{ fontSize: "2.4rem" }}>🏍️</div>
          <h1 style={{ color: "#f1f5f9", fontSize: "1.45rem", fontWeight: 800, margin: "0.3rem 0 0.2rem" }}>
            Crea tu cuenta en MotoEdu <span style={{ color: "#3b82f6" }}>EC</span>
          </h1>
          <p style={{ color: "#94a3b8", fontSize: "0.82rem", margin: 0 }}>Contenido de seguridad vial hecho a tu medida</p>
        </div>

        <label style={labelStyle}>Nombre completo</label>
        <input value={nombre} onChange={e => setNombre(e.target.value)} placeholder="Carlos Pérez" style={inputStyle} />

        <label style={labelStyle}>Correo electrónico</label>
        <input value={email} onChange={e => setEmail(e.target.value)} type="email" placeholder="tu@correo.com" style={inputStyle} />

        <label style={labelStyle}>Contraseña (mínimo 6 caracteres)</label>
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="••••••••" style={inputStyle} />

        <label style={labelStyle}>¿Cómo usas tu moto?</label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", margin: "0.5rem 0 1.2rem" }}>
          {PERFILES.map(p => (
            <button key={p.id} onClick={() => setTipoUso(p.id)}
              style={{ padding: "0.6rem 0.5rem", borderRadius: 10, fontSize: "0.8rem", cursor: "pointer",
                background: tipoUso === p.id ? "rgba(59,130,246,0.25)" : "#0f172a",
                border: tipoUso === p.id ? "1.5px solid #3b82f6" : "1px solid #334155",
                color: tipoUso === p.id ? "#93c5fd" : "#cbd5e1", fontWeight: tipoUso === p.id ? 700 : 400 }}>
              {p.nombre}
            </button>
          ))}
        </div>

        {error && (
          <div style={{ background: "rgba(239,68,68,0.12)", border: "1px solid #ef4444", color: "#fca5a5",
            borderRadius: 10, padding: "0.6rem 0.9rem", fontSize: "0.82rem", marginBottom: "1rem" }}>
            ⚠️ {error}
          </div>
        )}

        <button onClick={registrar} disabled={cargando || !nombre || !email || !password}
          style={{ width: "100%", padding: "0.85rem", background: cargando ? "#334155" : "linear-gradient(90deg,#22c55e,#16a34a)",
            border: "none", borderRadius: 12, color: "#fff", fontWeight: 700, fontSize: "1rem",
            cursor: cargando ? "wait" : "pointer" }}>
          {cargando ? "Creando cuenta..." : "Crear cuenta gratis"}
        </button>

        <p style={{ color: "#94a3b8", fontSize: "0.85rem", textAlign: "center", marginTop: "1.2rem" }}>
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" style={{ color: "#60a5fa", fontWeight: 700, textDecoration: "none" }}>Inicia sesión</Link>
        </p>
      </div>
    </div>
  )
}
