"use client";

/**
 * /mis-evaluaciones — pagina dedicada donde el participante ve su
 * evaluacion inicial y final con las respuestas que dio.
 * Archivo nuevo: no toca nada existente.
 */

import RevisionTests from "../perfil/RevisionTests";

export default function MisEvaluacionesPage() {
  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", padding: "2rem 1rem" }}>
      <div style={{ maxWidth: 700, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{ fontSize: "2.6rem" }}>📊</div>
          <h1 style={{ color: "#f1f5f9", fontSize: "1.7rem", fontWeight: "bold" }}>
            Mis evaluaciones
          </h1>
          <p style={{ color: "#94a3b8", fontSize: "0.9rem" }}>
            Revisa tus respuestas de la evaluación inicial y final
          </p>
        </div>

        <RevisionTests />
      </div>
    </div>
  );
}
