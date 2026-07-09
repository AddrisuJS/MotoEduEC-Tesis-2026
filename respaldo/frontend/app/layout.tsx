import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MotoEdu EC - Plataforma de Educacion Vial',
  description: 'Plataforma inteligente de educacion vial para motociclistas ecuatorianos - UPS Cuenca 2026',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}