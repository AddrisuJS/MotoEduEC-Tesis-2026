-- GARAJE VIRTUAL + DUELOS 1v1
-- Ejecutar: Get-Content backend\db\migration_garaje_duelos.sql | docker exec -i motoeduc_tesis_postgres psql -U motoeduc_user -d motoeduc_tesis

-- ─── GARAJE: catálogo de items desbloqueables ─────────────────
CREATE TABLE IF NOT EXISTS garaje_items (
  id             SERIAL PRIMARY KEY,
  nombre         VARCHAR(60) NOT NULL,
  icono          VARCHAR(8)  NOT NULL,
  tipo           VARCHAR(10) NOT NULL CHECK (tipo IN ('equipo','moto')),
  requisito_tipo VARCHAR(10) NOT NULL CHECK (requisito_tipo IN ('xp','racha','partidas')),
  requisito_valor INT NOT NULL,
  descripcion    VARCHAR(160)
);

INSERT INTO garaje_items (nombre, icono, tipo, requisito_tipo, requisito_valor, descripcion) VALUES
 ('Casco básico',          '🪖','equipo','xp',       0,   'Tu primer casco. Nunca salgas sin él.'),
 ('Guantes de protección', '🧤','equipo','xp',       400, 'Protegen tus manos: lo primero que toca el suelo en una caída.'),
 ('Chaqueta con protecciones','🧥','equipo','xp',    900, 'Hombros, codos y espalda protegidos.'),
 ('Botas de moto',         '🥾','equipo','xp',       1500,'Cubren el tobillo: adiós esguinces.'),
 ('Casco integral premium','⛑️','equipo','xp',      2500,'Certificación ECE 22.06. Máxima protección.'),
 ('Chaleco con airbag',    '🦺','equipo','xp',       4000,'Tecnología de punta para el motociclista serio.'),
 ('Llantas nuevas',        '🛞','moto',  'racha',    2,   'Labrado perfecto para lluvia cuencana.'),
 ('Escape deportivo',      '💨','moto',  'racha',    3,   'Suena tan bien como tu conocimiento vial.'),
 ('Faro LED',              '💡','moto',  'racha',    5,   'Que te vean: visibilidad = vida.'),
 ('Pintura personalizada', '🎨','moto',  'racha',    7,   'Tu moto, tu estilo. Racha de campeón.'),
 ('Espejos panorámicos',   '🪞','moto',  'partidas', 5,   'Reduce el punto ciego.'),
 ('Motor mejorado',        '⚙️','moto',  'partidas', 15,  'La constancia tiene premio.'),
 ('Kit de herramientas',   '🧰','moto',  'partidas', 25,  'Para el mantenimiento que ya sabes hacer.'),
 ('Moto de leyenda',       '🏍️','moto', 'xp',       6000,'La corona del garaje. Solo para expertos viales.')
ON CONFLICT DO NOTHING;

-- ─── DUELOS 1v1 ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS duelos (
  id              SERIAL PRIMARY KEY,
  retador_id      INT REFERENCES usuarios_auth(id) ON DELETE CASCADE,
  rival_id        INT REFERENCES usuarios_auth(id) ON DELETE CASCADE,
  pregunta_ids    JSONB NOT NULL,             -- las 5 preguntas congeladas del duelo
  puntos_retador  INT,
  puntos_rival    INT,
  aciertos_retador INT,
  aciertos_rival  INT,
  estado          VARCHAR(15) DEFAULT 'pendiente',  -- pendiente | esperando_rival | completado
  ganador_id      INT,
  creado_en       TIMESTAMP DEFAULT NOW(),
  resuelto_en     TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_duelos_rival ON duelos(rival_id, estado);
CREATE INDEX IF NOT EXISTS idx_duelos_retador ON duelos(retador_id, estado);

SELECT COUNT(*) AS items_garaje FROM garaje_items;
