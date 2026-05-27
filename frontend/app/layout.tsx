import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'MotoEdu EC — Plataforma de Educación Vial',
  description: 'Plataforma inteligente de educación vial para motociclistas ecuatorianos — UPS Cuenca 2026',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <head>
        <style>{`
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f172a; color: #e2e8f0; }
          a { color: #38bdf8; text-decoration: none; }
          a:hover { text-decoration: underline; }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  )
}
