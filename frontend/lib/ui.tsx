"use client"
import { useState, useEffect, useRef } from "react"

/* ═══════════════════════════════════════════════════
   MotoEdu EC — Librería UI Racing Glass
   Iconos SVG propios + loaders + componentes
   ═══════════════════════════════════════════════════ */

// ─── ICONOS SVG (line-art estilo iOS) ───
type IconProps = { size?: number; color?: string; className?: string }

export const IconMoto = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="5.5" cy="17" r="3.5" /><circle cx="18.5" cy="17" r="3.5" />
    <path d="M5.5 17h6l4-7h3" /><path d="M11 10l2 4" /><path d="M15 6h3" />
  </svg>
)
export const IconCasco = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 13a9 9 0 0118 0v3a2 2 0 01-2 2H8l-3.5-2A3 3 0 013 13z" /><path d="M3 14h11" /><path d="M14 14v4" />
  </svg>
)
export const IconLlanta = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="9" /><circle cx="12" cy="12" r="3.5" />
    <path d="M12 3v5M12 16v5M3 12h5M16 12h5" />
  </svg>
)
export const IconRayo = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M13 2L4 14h6l-1 8 9-12h-6z" />
  </svg>
)
export const IconBandera = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 21V4M4 4h13l-2 4 2 4H4" />
  </svg>
)
export const IconTrofeo = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M7 4h10v5a5 5 0 01-10 0z" /><path d="M7 6H4v1a3 3 0 003 3M17 6h3v1a3 3 0 01-3 3" /><path d="M10 15h4M9 20h6M12 15v5" />
  </svg>
)
export const IconChat = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a8 8 0 01-11.5 7.2L3 21l1.8-6.5A8 8 0 1121 12z" />
  </svg>
)
export const IconEspada = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 4L20 4l0 5.5L8 21l-5-5zM14.5 9.5L18 6" /><path d="M3 21l3-3" />
  </svg>
)
export const IconLibro = ({ size = 24, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z" /><path d="M4 19a2 2 0 012-2h13" />
  </svg>
)
export const IconSalir = ({ size = 20, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
  </svg>
)
export const IconCampana = ({ size = 20, color = "currentColor" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 8a6 6 0 00-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 01-3.4 0" />
  </svg>
)

// ─── LOGO ───
export const Logo = ({ size = 30 }: { size?: number }) => (
  <div style={{ width: size, height: size, borderRadius: size * 0.3, background: "var(--race-grad-v)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 4px 12px rgba(255,89,48,0.4)" }}>
    <IconMoto size={size * 0.56} color="#fff" />
  </div>
)

// ─── LOADER: rueda girando con estela ───
export const LoaderMoto = ({ texto = "Cargando..." }: { texto?: string }) => (
  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "1rem", padding: "3rem 1rem" }}>
    <div style={{ position: "relative", width: 70, height: 70 }}>
      <div style={{ position: "absolute", inset: 0, borderRadius: "50%", background: "conic-gradient(from 0deg, transparent, rgba(255,89,48,0.15), var(--race-2))", animation: "spinWheel 0.9s linear infinite" }} />
      <div style={{ position: "absolute", inset: 6, borderRadius: "50%", background: "var(--bg-1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <IconLlanta size={34} color="#ff9575" />
      </div>
    </div>
    <div style={{ color: "var(--t1)", fontSize: "0.85rem", fontWeight: 600 }}>{texto}</div>
  </div>
)

// ─── LOADER velocímetro (barra que acelera) ───
export const LoaderBarra = () => (
  <div style={{ width: "100%", height: 6, background: "rgba(255,255,255,0.08)", borderRadius: 4, overflow: "hidden", position: "relative" }}>
    <div style={{ position: "absolute", top: 0, left: 0, height: "100%", width: "40%", background: "var(--race-grad)", borderRadius: 4, animation: "speedLine 1.2s ease-in-out infinite" }} />
  </div>
)

// ─── Número que cuenta hacia arriba ───
export function CountUp({ to, dur = 1000, prefix = "", suffix = "" }: { to: number; dur?: number; prefix?: string; suffix?: string }) {
  const [n, setN] = useState(0)
  const ref = useRef<number>()
  useEffect(() => {
    const start = performance.now()
    const tick = (now: number) => {
      const p = Math.min((now - start) / dur, 1)
      const eased = 1 - Math.pow(1 - p, 3)
      setN(Math.round(to * eased))
      if (p < 1) ref.current = requestAnimationFrame(tick)
    }
    ref.current = requestAnimationFrame(tick)
    return () => { if (ref.current) cancelAnimationFrame(ref.current) }
  }, [to, dur])
  return <>{prefix}{n.toLocaleString()}{suffix}</>
}

// ─── Fondo de líneas de velocidad (para login/registro) ───
export const SpeedBG = () => (
  <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
    <div style={{ position: "absolute", top: "15%", left: "-10%", width: "60%", height: 2, background: "linear-gradient(90deg,transparent,rgba(255,89,48,0.5),transparent)", transform: "rotate(-8deg)" }} />
    <div style={{ position: "absolute", top: "28%", left: "20%", width: "70%", height: 1, background: "linear-gradient(90deg,transparent,rgba(255,149,0,0.4),transparent)", transform: "rotate(-8deg)" }} />
    <div style={{ position: "absolute", bottom: "22%", left: "-5%", width: "55%", height: 2, background: "linear-gradient(90deg,transparent,rgba(59,130,246,0.4),transparent)", transform: "rotate(-8deg)" }} />
    <div style={{ position: "absolute", top: -60, right: -60, width: 260, height: 260, background: "radial-gradient(circle,rgba(255,89,48,0.22),transparent 65%)", borderRadius: "50%" }} />
    <div style={{ position: "absolute", bottom: -80, left: -40, width: 240, height: 240, background: "radial-gradient(circle,rgba(59,130,246,0.16),transparent 65%)", borderRadius: "50%" }} />
  </div>
)

export const RAREZA_COLOR: Record<string, { c: string; label: string }> = {
  comun: { c: "#94a3b8", label: "COMÚN" },
  raro: { c: "#60a5fa", label: "RARO" },
  epico: { c: "#c084fc", label: "ÉPICO" },
  legendario: { c: "#facc15", label: "LEGENDARIO" },
}

// ─── Fondo estándar de páginas de juego (Racing Glass) ───
export const FONDO_JUEGO: any = {
  minHeight: "calc(100vh - 54px)",
  padding: "1.5rem clamp(0.6rem,3vw,1.5rem)",
  display: "flex", justifyContent: "center",
}

// ─── Overlay de LOGRO desbloqueado (momento wow) ───
import { useEffect as _useEffect, useState as _useState } from "react"
export function LogroOverlay({ logro, onClose }: { logro: any; onClose: () => void }) {
  if (!logro) return null
  const r = RAREZA_COLOR[logro.rareza || "comun"] || RAREZA_COLOR.comun
  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, zIndex: 300, background: "rgba(5,8,16,0.82)", backdropFilter: "blur(6px)", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <div className="pop-in" onClick={e => e.stopPropagation()} style={{ maxWidth: 340, width: "100%", background: "var(--glass)", backdropFilter: "blur(24px)", border: `1px solid ${r.c}66`, borderRadius: 22, padding: "1.6rem", textAlign: "center", boxShadow: `0 20px 60px rgba(0,0,0,0.6), 0 0 40px ${r.c}22` }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: `${r.c}22`, border: `1px solid ${r.c}66`, borderRadius: 20, padding: "4px 14px", marginBottom: "1rem" }}>
          <span style={{ color: r.c, fontSize: 11, fontWeight: 800, letterSpacing: "0.1em" }}>✦ DESBLOQUEADO</span>
        </div>
        <div style={{ width: 100, height: 100, margin: "0 auto 0.8rem", borderRadius: 24, background: `radial-gradient(circle at 30% 30%, ${r.c}44, transparent)`, border: `1.5px solid ${r.c}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "3rem", animation: "glowPulse 1.6s infinite" }}>{logro.icono || "🏆"}</div>
        <div style={{ color: "#f1f5f9", fontSize: "1.2rem", fontWeight: 800 }}>{logro.nombre}</div>
        <div style={{ color: r.c, fontSize: "0.72rem", fontWeight: 700, letterSpacing: "0.06em", marginBottom: "0.8rem" }}>◆ {r.label}</div>
        {logro.leccion && (
          <div style={{ background: "rgba(74,222,128,0.08)", border: "1px solid rgba(74,222,128,0.3)", borderRadius: 12, padding: "0.7rem", marginBottom: "0.9rem" }}>
            <div style={{ color: "#4ade80", fontSize: "0.8rem", fontWeight: 700, marginBottom: 3 }}>✓ ¡Aprendiste algo!</div>
            <div style={{ color: "#a7f3d0", fontSize: "0.75rem", lineHeight: 1.4 }}>{logro.leccion}</div>
          </div>
        )}
        <button onClick={onClose} className="btn-race" style={{ width: "100%" }}>¡Genial! Seguir</button>
      </div>
    </div>
  )
}
