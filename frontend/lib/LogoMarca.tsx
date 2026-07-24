"use client"

/* ═══════════════════════════════════════════════════════════════
   MotoEdu EC — Componentes de marca
   El logo institucional conserva sus colores originales (azul
   marino #012350 y amarillo #FDB500). Como el azul marino no se
   lee sobre el fondo oscuro de la aplicacion, se presenta siempre
   sobre una placa marfil que actua de soporte.

   Uso:
     import { LogoMarca, LogoCompleto } from "../lib/LogoMarca"
     <LogoMarca size={58} />          // icono, para navbar y formularios
     <LogoCompleto max={520} />       // logo completo, para el hero
   ═══════════════════════════════════════════════════════════════ */

const MARFIL = "#F6F8FC"

export function LogoMarca({ size = 58, radio }: { size?: number; radio?: number }) {
  const pad = Math.round(size * 0.14)
  return (
    <div
      style={{
        width: size, height: size, padding: pad,
        background: MARFIL,
        borderRadius: radio ?? Math.round(size * 0.28),
        display: "flex", alignItems: "center", justifyContent: "center",
        boxShadow: "0 8px 22px rgba(0,0,0,0.35)",
        flexShrink: 0,
      }}
    >
      <img
        src="/logo-icono.png"
        alt="MotoEdu EC"
        style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
      />
    </div>
  )
}

export function LogoCompleto({ max = 520 }: { max?: number }) {
  return (
    <div
      style={{
        display: "inline-block",
        background: MARFIL,
        borderRadius: 22,
        padding: "clamp(0.9rem, 3vw, 1.5rem) clamp(1.1rem, 4vw, 2rem)",
        boxShadow: "0 16px 44px rgba(0,0,0,0.42)",
        maxWidth: "100%",
      }}
    >
      <img
        src="/logo.png"
        alt="MotoEdu EC — Plataforma inteligente de educación vial"
        style={{ width: "100%", maxWidth: max, height: "auto", display: "block" }}
      />
    </div>
  )
}

/* Bloque de marca para encabezados: logo + eslogan */
export function MarcaHero({ max = 560 }: { max?: number }) {
  return (
    <div style={{ textAlign: "center" }}>
      <LogoCompleto max={max} />
      <p
        style={{
          marginTop: "1rem", color: "var(--dorado, #FAC74C)",
          fontSize: "clamp(0.9rem, 3vw, 1.1rem)", fontWeight: 700,
          letterSpacing: "0.01em",
        }}
      >
        Aprender, elegir y rodar con seguridad
      </p>
    </div>
  )
}
