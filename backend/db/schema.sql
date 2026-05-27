-- MotoEdu EC Tesis — Schema PostgreSQL
-- Reutiliza tablas de pasantias + agrega tablas nuevas de tesis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tablas heredadas de pasantias (simplificadas para tesis)
CREATE TABLE IF NOT EXISTS marcas_moto (
    id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE,
    origen VARCHAR(100), distribuidor_ec VARCHAR(200), activa BOOLEAN DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS tipos_moto (
    id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE, descripcion TEXT
);
CREATE TABLE IF NOT EXISTS motocicletas (
    id SERIAL PRIMARY KEY, marca_id INTEGER REFERENCES marcas_moto(id),
    tipo_id INTEGER REFERENCES tipos_moto(id), modelo VARCHAR(150) NOT NULL,
    anio INTEGER, cilindrada_cc INTEGER, potencia_hp DECIMAL(6,2),
    peso_kg DECIMAL(6,2), precio_usd DECIMAL(10,2),
    uso_recomendado VARCHAR(200), disponible_ec BOOLEAN DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS marcas_llanta (
    id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE,
    origen VARCHAR(100), gama VARCHAR(20)
);
CREATE TABLE IF NOT EXISTS tipos_llanta (
    id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE,
    terreno_ideal VARCHAR(200), clima_ideal VARCHAR(200)
);
CREATE TABLE IF NOT EXISTS llantas (
    id SERIAL PRIMARY KEY, marca_id INTEGER REFERENCES marcas_llanta(id),
    tipo_id INTEGER REFERENCES tipos_llanta(id), modelo VARCHAR(150),
    medida_ejemplo VARCHAR(50), precio_min_usd DECIMAL(8,2), precio_max_usd DECIMAL(8,2),
    descripcion TEXT
);
CREATE TABLE IF NOT EXISTS perfiles_motociclista (
    id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT, uso_principal VARCHAR(200), riesgos_principales VARCHAR(300)
);
CREATE TABLE IF NOT EXISTS categorias_pregunta (
    id SERIAL PRIMARY KEY, nombre VARCHAR(100) NOT NULL UNIQUE, modulo_app VARCHAR(100)
);
CREATE TABLE IF NOT EXISTS preguntas_viales (
    id SERIAL PRIMARY KEY, categoria_id INTEGER REFERENCES categorias_pregunta(id),
    pregunta TEXT NOT NULL, respuesta_correcta TEXT NOT NULL,
    opcion_b TEXT, opcion_c TEXT, opcion_d TEXT, explicacion TEXT,
    dificultad VARCHAR(20), perfil_objetivo VARCHAR(100), fuente VARCHAR(300),
    activa BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS brechas_conocimiento (
    id SERIAL PRIMARY KEY, descripcion VARCHAR(300), pct_con_brecha DECIMAL(5,2),
    nivel_riesgo VARCHAR(20), modulo_relacionado VARCHAR(100)
);

-- Tablas nuevas de tesis
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(200), email VARCHAR(200) UNIQUE,
    provincia VARCHAR(100), tipo_moto VARCHAR(100),
    anos_experiencia INTEGER DEFAULT 0,
    nivel VARCHAR(20) DEFAULT 'basico',
    puntos_acumulados INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS historial_evaluaciones (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    pregunta_id INTEGER REFERENCES preguntas_viales(id),
    respuesta_dada TEXT, correcta BOOLEAN NOT NULL,
    tiempo_seg INTEGER, fecha TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sesiones_chat (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios(id),
    pregunta TEXT, respuesta TEXT,
    fuentes_rag TEXT[], tokens_usados INTEGER,
    fecha TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS experimento_piloto (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios(id),
    tipo VARCHAR(10) CHECK (tipo IN ('pretest','postest')),
    puntaje INTEGER, total_preguntas INTEGER,
    pct_acierto DECIMAL(5,2), fecha TIMESTAMP DEFAULT NOW()
);

-- Vista util
CREATE OR REPLACE VIEW v_motos_completo AS
SELECT m.id, ma.nombre AS marca, m.modelo, m.anio, t.nombre AS tipo,
       m.cilindrada_cc, m.potencia_hp, m.precio_usd, m.uso_recomendado, m.disponible_ec
FROM motocicletas m
JOIN marcas_moto ma ON m.marca_id = ma.id
JOIN tipos_moto t ON m.tipo_id = t.id
ORDER BY ma.nombre, m.modelo;
