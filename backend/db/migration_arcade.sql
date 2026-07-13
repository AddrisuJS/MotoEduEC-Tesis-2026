-- Migración M8 ARCADE: XP, rachas, partidas y leaderboard
-- Ejecutar: Get-Content backend\db\migration_arcade.sql | docker exec -i motoeduc_tesis_postgres psql -U motoeduc_user -d motoeduc_tesis

CREATE TABLE IF NOT EXISTS arcade_stats (
  usuario_id     INT PRIMARY KEY REFERENCES usuarios_auth(id) ON DELETE CASCADE,
  xp_total       INT DEFAULT 0,
  partidas       INT DEFAULT 0,
  aciertos_total INT DEFAULT 0,
  racha_actual   INT DEFAULT 0,
  racha_maxima   INT DEFAULT 0,
  ultima_fecha   DATE
);

CREATE TABLE IF NOT EXISTS arcade_partidas (
  id          SERIAL PRIMARY KEY,
  usuario_id  INT REFERENCES usuarios_auth(id) ON DELETE CASCADE,
  modo        VARCHAR(20) NOT NULL,          -- 'relampago' | 'desafio'
  puntos      INT NOT NULL,
  aciertos    INT NOT NULL,
  total       INT NOT NULL,
  jugada_en   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_arcade_xp ON arcade_stats(xp_total DESC);
CREATE INDEX IF NOT EXISTS idx_arcade_partidas_usuario ON arcade_partidas(usuario_id);
