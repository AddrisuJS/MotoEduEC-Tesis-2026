"use client"
import { useState, useEffect } from "react"
import Link from "next/link"
import { useAuth } from "../../../lib/useAuth"

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010"

const input = { width: "100%", padding: "0.55rem 0.7rem", borderRadius: 8, border: "1px solid #334155", background: "#0f172a", color: "#e2e8f0", fontSize: "0.85rem", marginBottom: "0.55rem" }
const label = { fontSize: "0.7rem", color: "#94a3b8", fontWeight: 600, display: "block", marginBottom: "0.2rem" }
const btn = { padding: "0.55rem 1rem", borderRadius: 8, border: "none", cursor: "pointer", fontWeight: 700, fontSize: "0.82rem" }

export default function Catalogo() {
  const { usuario, listo, authHeaders } = useAuth(true)
  const [tipo, setTipo] = useState<"moto" | "llanta">("moto")
  const [marca, setMarca] = useState("")
  const [modelo, setModelo] = useState("")
  const [sugerencia, setSugerencia] = useState<any>(null)
  const [form, setForm] = useState<any>({})
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState("")
  const [lista, setLista] = useState<any[]>([])
  const [busqueda, setBusqueda] = useState("")
  const [expandido, setExpandido] = useState<number | null>(null)
  const [opciones, setOpciones] = useState<{marcas:string[],tipos:string[]}>({marcas:[],tipos:[]})
  const [marcaNueva, setMarcaNueva] = useState(false)
  const [tipoSel, setTipoSel] = useState("")

  const normaliza = (s: string) => s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]/g, "")

  const similar = lista.find((x: any) => {
    const nm = normaliza(marca), no = normaliza(modelo)
    if (!nm || !no) return false
    return normaliza(x.marca).includes(nm) && normaliza(x.modelo).includes(no)
  })

  const base = tipo === "moto" ? `${API}/m4/motos` : `${API}/m5/llantas`
  const claveLista = tipo === "moto" ? "motos" : "llantas"

  const cargarLista = async () => {
    try {
      const r = await fetch(`${base}/catalogo`)
      const d = await r.json()
      setLista(d[claveLista] || [])
    } catch { setLista([]) }
  }

  useEffect(() => {
    cargarLista()
    fetch(`${base}/admin/opciones`).then(r => r.json()).then(setOpciones).catch(() => {})
    setMarcaNueva(false); setTipoSel("")
  }, [tipo])

  const autocompletar = async () => {
    if (!marca || !modelo) { setMensaje("⚠️ Escribe marca y modelo primero"); return }
    setCargando(true); setMensaje("")
    try {
      const r = await fetch(`${base}/admin/autocompletar`, {
        method: "POST", headers: authHeaders(), body: JSON.stringify({ marca, modelo }),
      })
      const d = await r.json()
      setSugerencia(d)
      setForm({ marca, modelo, tipo: tipoSel, ...d.sugerencia })
    } catch { setMensaje("❌ No se pudo generar la sugerencia. Completa manualmente.") }
    setCargando(false)
  }

  const guardar = async () => {
    setCargando(true); setMensaje("")
    try {
      const r = await fetch(`${base}/admin/crear`, {
        method: "POST", headers: authHeaders(), body: JSON.stringify(form),
      })
      const d = await r.json()
      setMensaje(r.ok ? `✅ ${d.mensaje}` : `❌ ${d.detail || "Error al guardar"}`)
      if (r.ok) { setMarca(""); setModelo(""); setSugerencia(null); setForm({}); cargarLista() }
    } catch { setMensaje("❌ No se pudo guardar. Revisa la conexión con la API.") }
    setCargando(false)
  }

  if (!listo) return null
  if (usuario?.rol !== "admin") return <div style={{ padding: "2rem", color: "#fca5a5" }}>Acceso solo para el investigador.</div>

  const listaFiltrada = lista.filter((x: any) =>
    !busqueda || `${x.marca} ${x.modelo}`.toLowerCase().includes(busqueda.toLowerCase()))

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "1.5rem clamp(0.5rem,3vw,1.5rem)", color: "#e2e8f0", fontFamily: "sans-serif" }}>
      <Link href="/admin" style={{ color: "#93c5fd", fontSize: "0.85rem", textDecoration: "none" }}>← Volver al panel</Link>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 800, margin: "0.6rem 0 0.3rem" }}>🏍️ Catálogo del sistema</h1>
      <p style={{ color: "#94a3b8", fontSize: "0.85rem", marginBottom: "1.2rem" }}>Consulta lo que ya existe y agrega modelos nuevos con ayuda de IA.</p>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.2rem" }}>
        <button onClick={() => { setTipo("moto"); setSugerencia(null); setForm({}); setBusqueda("") }}
          style={{ ...btn, background: tipo === "moto" ? "#2563eb" : "#1e293b", color: "#fff" }}>🏍️ Motos</button>
        <button onClick={() => { setTipo("llanta"); setSugerencia(null); setForm({}); setBusqueda("") }}
          style={{ ...btn, background: tipo === "llanta" ? "#2563eb" : "#1e293b", color: "#fff" }}>🛞 Llantas</button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "1.2rem", alignItems: "start" }}>

        {/* ── Columna izquierda: catálogo existente ── */}
        <div style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 12, padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.7rem" }}>
            <div style={{ fontWeight: 700, fontSize: "0.95rem" }}>
              📋 Catálogo actual <span style={{ color: "#64748b", fontWeight: 400 }}>({lista.length})</span>
            </div>
          </div>
          <input style={{ ...input, marginBottom: "0.7rem" }} placeholder="🔎 Buscar por marca o modelo..."
            value={busqueda} onChange={e => setBusqueda(e.target.value)} />

          <div style={{ maxHeight: 520, overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {listaFiltrada.length === 0 && (
              <div style={{ color: "#64748b", fontSize: "0.82rem", textAlign: "center", padding: "1.5rem 0" }}>
                Sin resultados. Agrega el primero con el formulario →
              </div>
            )}
            {listaFiltrada.map((x: any) => {
              const abierta = expandido === x.id
              return (
              <div key={x.id} onClick={() => setExpandido(abierta ? null : x.id)}
                style={{ background: "#1e293b", borderRadius: 10, padding: "0.7rem 0.9rem", cursor: "pointer",
                  border: abierta ? "1px solid #7c3aed" : "1px solid transparent", transition: "border-color 0.15s" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.5rem" }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: "0.88rem" }}>{x.marca} {x.modelo}</div>
                    <div style={{ fontSize: "0.72rem", color: "#94a3b8" }}>
                      {tipo === "moto"
                        ? `${x.tipo || ""} · ${x.cilindrada_cc || "?"}cc`
                        : `${x.tipo || ""} · ${x.medida_ejemplo || "sin medida"}`}
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexShrink: 0 }}>
                    <div style={{ color: "#4ade80", fontWeight: 700, fontSize: "0.85rem" }}>
                      ${tipo === "moto" ? (x.precio_usd ?? "?") : `${x.precio_min_usd ?? "?"}-${x.precio_max_usd ?? "?"}`}
                    </div>
                    <span style={{ color: "#64748b", fontSize: "0.7rem" }}>{abierta ? "▲" : "▼"}</span>
                  </div>
                </div>
                {abierta && (
                  <div style={{ marginTop: "0.7rem", paddingTop: "0.7rem", borderTop: "1px solid #334155",
                    display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.4rem 1rem", fontSize: "0.78rem" }}>
                    {tipo === "moto" ? (
                      <>
                        <div><span style={{ color: "#64748b" }}>Año:</span> {x.anio ?? "—"}</div>
                        <div><span style={{ color: "#64748b" }}>Cilindrada:</span> {x.cilindrada_cc ?? "—"} cc</div>
                        <div><span style={{ color: "#64748b" }}>Potencia:</span> {x.potencia_hp ?? "—"} hp</div>
                        <div><span style={{ color: "#64748b" }}>Peso:</span> {x.peso_kg ?? "—"} kg</div>
                        <div style={{ gridColumn: "1 / -1" }}><span style={{ color: "#64748b" }}>Uso recomendado:</span> {x.uso_recomendado || "—"}</div>
                      </>
                    ) : (
                      <>
                        <div><span style={{ color: "#64748b" }}>Medida:</span> {x.medida_ejemplo ?? "—"}</div>
                        <div><span style={{ color: "#64748b" }}>Tipo:</span> {x.tipo ?? "—"}</div>
                        <div style={{ gridColumn: "1 / -1" }}><span style={{ color: "#64748b" }}>Descripción:</span> {x.descripcion || "—"}</div>
                      </>
                    )}
                  </div>
                )}
              </div>
              )
            })}
          </div>
        </div>

        {/* ── Columna derecha: formulario de alta ── */}
        <div style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 12, padding: "1rem", position: "sticky", top: "1rem" }}>
          <div style={{ fontWeight: 700, fontSize: "0.95rem", marginBottom: "0.4rem" }}>➕ Agregar {tipo === "moto" ? "moto" : "llanta"} nueva</div>
          <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: "0.8rem" }}>
            Escribe marca y modelo; la IA sugiere los datos técnicos como punto de partida — revísalos antes de guardar.
          </div>

          <label style={label}>Marca</label>
          {!marcaNueva ? (
            <select style={input} value={marca} onChange={e => {
              if (e.target.value === "__nueva__") { setMarcaNueva(true); setMarca("") }
              else setMarca(e.target.value)
            }}>
              <option value="">Selecciona una marca...</option>
              {opciones.marcas.map(m => <option key={m} value={m}>{m}</option>)}
              <option value="__nueva__">➕ Otra marca (escribir nueva)</option>
            </select>
          ) : (
            <div style={{ display: "flex", gap: "0.4rem" }}>
              <input style={{ ...input, flex: 1 }} placeholder="Escribe la marca nueva" value={marca} onChange={e => setMarca(e.target.value)} autoFocus />
              <button onClick={() => { setMarcaNueva(false); setMarca("") }}
                style={{ ...btn, background: "#334155", color: "#fff", padding: "0.4rem 0.7rem" }}>↩</button>
            </div>
          )}
          <label style={label}>Modelo</label>
          <input style={input} placeholder={tipo === "moto" ? "ej. FZ150" : "ej. Pilot Street 2"} value={modelo} onChange={e => setModelo(e.target.value)} />
          <label style={label}>Tipo ({tipo === "moto" ? "categoría de moto" : "categoría de llanta"})</label>
          <select style={input} value={tipoSel} onChange={e => setTipoSel(e.target.value)}>
            <option value="">Selecciona el tipo...</option>
            {opciones.tipos.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          {!tipoSel && <div style={{ fontSize: "0.7rem", color: "#fbbf24", marginTop: "-0.35rem", marginBottom: "0.5rem" }}>
            ⚠️ Sin tipo exacto, el recomendador por perfil podría no encontrarla.
          </div>}

          {similar && (
            <div style={{ fontSize: "0.75rem", color: "#fbbf24", background: "rgba(251,191,36,0.1)", border: "1px solid rgba(251,191,36,0.3)", borderRadius: 8, padding: "0.55rem 0.7rem", marginBottom: "0.7rem" }}>
              ⚠️ Ya existe algo similar: <b>{similar.marca} {similar.modelo}</b>
              {tipo === "moto" && similar.anio ? ` (${similar.anio})` : ""}.
              Puedes seguir si es un año o variante distinta.
            </div>
          )}
          <button onClick={autocompletar} disabled={cargando}
            style={{ ...btn, background: "#7c3aed", color: "#fff", width: "100%", marginBottom: "0.9rem", opacity: cargando ? 0.6 : 1 }}>
            {cargando ? "Consultando IA..." : "✨ Autocompletar con IA"}
          </button>

          {sugerencia && (
            <div style={{ borderTop: "1px solid #1e293b", paddingTop: "0.8rem" }}>
              <div style={{ fontSize: "0.72rem", color: "#fbbf24", marginBottom: "0.7rem", background: "rgba(251,191,36,0.08)", padding: "0.4rem 0.6rem", borderRadius: 6 }}>
                ⚠️ {sugerencia.advertencia}
              </div>
              {tipo === "moto" ? (
                <>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 0.6rem" }}>
                    <div><label style={label}>Cilindrada (cc)</label><input style={input} type="number" value={form.cilindrada_cc || ""} onChange={e => setForm({ ...form, cilindrada_cc: +e.target.value })} /></div>
                    <div><label style={label}>Potencia (hp)</label><input style={input} type="number" value={form.potencia_hp || ""} onChange={e => setForm({ ...form, potencia_hp: +e.target.value })} /></div>
                    <div><label style={label}>Peso (kg)</label><input style={input} type="number" value={form.peso_kg || ""} onChange={e => setForm({ ...form, peso_kg: +e.target.value })} /></div>
                    <div><label style={label}>Año</label><input style={input} type="number" value={form.anio || 2026} onChange={e => setForm({ ...form, anio: +e.target.value })} /></div>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 0.6rem" }}>
                    <div><label style={label}>Precio min (USD)</label><input style={input} type="number" value={form.precio_min_usd || ""} onChange={e => setForm({ ...form, precio_min_usd: +e.target.value })} /></div>
                    <div><label style={label}>Precio max (USD)</label><input style={input} type="number" value={form.precio_max_usd || ""} onChange={e => setForm({ ...form, precio_max_usd: +e.target.value })} /></div>
                  </div>
                  <label style={label}>Uso recomendado</label>
                  <input style={input} value={form.uso_recomendado || ""} onChange={e => setForm({ ...form, uso_recomendado: e.target.value })} />
                </>
              ) : (
                <>
                  <label style={label}>Medida (ej. 110/70-17)</label>
                  <input style={input} value={form.medida_ejemplo || ""} onChange={e => setForm({ ...form, medida_ejemplo: e.target.value })} />
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 0.6rem" }}>
                    <div><label style={label}>Precio min (USD)</label><input style={input} type="number" value={form.precio_min_usd || ""} onChange={e => setForm({ ...form, precio_min_usd: +e.target.value })} /></div>
                    <div><label style={label}>Precio max (USD)</label><input style={input} type="number" value={form.precio_max_usd || ""} onChange={e => setForm({ ...form, precio_max_usd: +e.target.value })} /></div>
                  </div>
                  <label style={label}>Terreno ideal</label>
                  <input style={input} value={form.terreno_ideal || ""} onChange={e => setForm({ ...form, terreno_ideal: e.target.value })} />
                  <label style={label}>Clima ideal</label>
                  <input style={input} value={form.clima_ideal || ""} onChange={e => setForm({ ...form, clima_ideal: e.target.value })} />
                </>
              )}
              <button onClick={guardar} disabled={cargando}
                style={{ ...btn, background: "#16a34a", color: "#fff", width: "100%", marginTop: "0.5rem", opacity: cargando ? 0.6 : 1 }}>
                {cargando ? "Guardando..." : "💾 Guardar en el catálogo"}
              </button>
            </div>
          )}
          {mensaje && <div style={{ marginTop: "0.7rem", fontSize: "0.82rem" }}>{mensaje}</div>}
        </div>
      </div>
    </div>
  )
}
