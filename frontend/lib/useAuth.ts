"use client"
// Hook de sesión — protege páginas y expone el usuario logueado.
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

const API = process.env.NEXT_PUBLIC_API_URL || ""

export function useAuth(redirigir = true, soloIntervencion = false) {
  const router = useRouter()
  const [usuario, setUsuario] = useState<any>(null)
  const [listo, setListo] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("motoeduc_token")
    const u = localStorage.getItem("motoeduc_usuario")
    if (!token || !u) {
      if (redirigir) router.push("/login")
      setListo(true)
      return
    }
    // 1) Setear de inmediato lo que hay en la sesión (síncrono, no rompe el navbar)
    let parsed: any = null
    try { parsed = JSON.parse(u) } catch { parsed = null }
    if (parsed) setUsuario(parsed)
    setListo(true)

    // 2) En paralelo, refrescar el grupo real desde el backend (sin bloquear)
    if (parsed && parsed.rol === "participante") {
      fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => (r.ok ? r.json() : null))
        .then(d => {
          const grupoReal = d?.usuario?.grupo
          if (grupoReal && grupoReal !== parsed.grupo) {
            const actualizado = { ...parsed, grupo: grupoReal }
            localStorage.setItem("motoeduc_usuario", JSON.stringify(actualizado))
            setUsuario(actualizado)
          }
          // Bloqueo del control en páginas de juego
          if (soloIntervencion && (grupoReal || parsed.grupo) === "control") {
            router.push("/evaluacion")
          }
        })
        .catch(() => {
          // Si falla el backend, usar lo que hay en sesión para el bloqueo
          if (soloIntervencion && parsed.grupo === "control") router.push("/evaluacion")
        })
    }
  }, [])

  const cerrarSesion = () => {
    localStorage.removeItem("motoeduc_token")
    localStorage.removeItem("motoeduc_usuario")
    localStorage.removeItem("motoeduc_usuario_id")
    localStorage.removeItem("motoeduc_perfil")
    router.push("/login")
  }

  const authHeaders = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("motoeduc_token") || ""}`,
  })

  return { usuario, listo, cerrarSesion, authHeaders }
}
