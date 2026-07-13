-- M9 EXPERIMENTO: pretest/postest dentro de la app
-- Selecciona y CONGELA 15 preguntas del banco (2 por categoría + 1 extra de Normativa)
-- Ejecutar: Get-Content backend\db\migration_m9_experimento.sql | docker exec -i motoeduc_tesis_postgres psql -U motoeduc_user -d motoeduc_tesis

CREATE TABLE IF NOT EXISTS piloto_preguntas (
  orden       INT PRIMARY KEY,
  pregunta_id INT UNIQUE REFERENCES preguntas_viales(id)
);

-- 2 preguntas por categoría (deterministico: las 2 primeras por id de cada categoría)
INSERT INTO piloto_preguntas (orden, pregunta_id)
SELECT ROW_NUMBER() OVER (ORDER BY categoria_id, id), id
FROM (
  SELECT p.id, p.categoria_id,
         ROW_NUMBER() OVER (PARTITION BY p.categoria_id ORDER BY p.id) AS rn
  FROM preguntas_viales p
  WHERE p.activa = TRUE
) t
WHERE rn <= 2
ON CONFLICT DO NOTHING;

-- Pregunta 15: una extra de Normativa LOTTTSV (la brecha más crítica del diagnóstico)
INSERT INTO piloto_preguntas (orden, pregunta_id)
SELECT 15, p.id
FROM preguntas_viales p
JOIN categorias_pregunta c ON c.id = p.categoria_id
WHERE c.nombre = 'Normativa LOTTTSV' AND p.activa = TRUE
  AND p.id NOT IN (SELECT pregunta_id FROM piloto_preguntas)
ORDER BY p.id
LIMIT 1
ON CONFLICT DO NOTHING;

-- Respuestas y scores del experimento
CREATE TABLE IF NOT EXISTS piloto_evaluaciones (
  id          SERIAL PRIMARY KEY,
  usuario_id  INT REFERENCES usuarios_auth(id) ON DELETE CASCADE,
  fase        VARCHAR(10) NOT NULL CHECK (fase IN ('pretest','postest')),
  score       INT NOT NULL,
  total       INT NOT NULL,
  detalles    JSONB,
  creado_en   TIMESTAMP DEFAULT NOW(),
  UNIQUE(usuario_id, fase)
);

-- Verificación: debe mostrar 15 filas
SELECT pp.orden, pv.pregunta, c.nombre AS categoria
FROM piloto_preguntas pp
JOIN preguntas_viales pv ON pv.id = pp.pregunta_id
LEFT JOIN categorias_pregunta c ON c.id = pv.categoria_id
ORDER BY pp.orden;
