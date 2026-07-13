import type { Metadata, Viewport } from 'next'
import './globals.css'
import Navbar from '../lib/Navbar'

export const metadata: Metadata = {
  title: 'MotoEdu EC — Plataforma de Educación Vial',
  description: 'Plataforma inteligente de educación vial para motociclistas ecuatorianos — UPS Cuenca 2026',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  )
}
