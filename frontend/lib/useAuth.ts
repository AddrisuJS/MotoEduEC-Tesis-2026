"use client"
// Hook de sesión — protege páginas y expone el usuario logueado.
// Uso en cualquier página:
//   const { usuario, cerrarSesion } = useAuth()      // redirige a /login si no hay sesión
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export function useAuth(redirigir = true) {
  const router = useRouter()
  const [usuario, setUsuario] = useState<any>(null)
  const [listo, setListo] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("motoeduc_token")
    const u = localStorage.getItem("motoeduc_usuario")
    if (!token || !u) {
      if (redirigir) router.push("/login")
    } else {
      setUsuario(JSON.parse(u))
    }
    setListo(true)
  }, [])

  const cerrarSesion = () => {
    localStorage.removeItem("motoeduc_token")
    localStorage.removeItem("motoeduc_usuario")
    router.push("/login")
  }

  const authHeaders = () => ({
    "Content-Type": "application/json",
    Authorization: `Bearer ${localStorage.getItem("motoeduc_token") || ""}`,
  })

  return { usuario, listo, cerrarSesion, authHeaders }
}
