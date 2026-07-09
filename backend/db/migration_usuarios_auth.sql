-- Migración: tabla de usuarios con autenticación
-- Ejecutar:  docker exec -i motoeduc_tesis_postgres psql -U motoeduc_user -d motoeduc_tesis < backend/db/migration_usuarios_auth.sql
CREATE TABLE IF NOT EXISTS usuarios_auth (
  id            SERIAL PRIMARY KEY,
  nombre        VARCHAR(120) NOT NULL,
  email         VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(200) NOT NULL,
  tipo_uso      VARCHAR(30) DEFAULT 'urbano',
  creado_en     TIMESTAMP DEFAULT NOW(),
  ultimo_login  TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_usuarios_auth_email ON usuarios_auth(email);

-- Tabla de contribuciones de historia (pendiente menor que teníamos en RAM)
CREATE TABLE IF NOT EXISTS contribuciones_historia (
  id         SERIAL PRIMARY KEY,
  usuario    VARCHAR(120),
  titulo     VARCHAR(200) NOT NULL,
  relato     TEXT NOT NULL,
  anio       INT,
  aprobado   BOOLEAN DEFAULT FALSE,
  creado_en  TIMESTAMP DEFAULT NOW()
);
