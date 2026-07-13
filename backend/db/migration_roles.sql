-- Roles: admin (investigador) vs participante
ALTER TABLE usuarios_auth ADD COLUMN IF NOT EXISTS rol VARCHAR(15) DEFAULT 'participante';

-- ⚠️ EDITA el email por el de TU cuenta antes de correr:
UPDATE usuarios_auth SET rol = 'admin' WHERE email = 'jsanangor@est.ups.edu.ec';

SELECT id, nombre, email, rol FROM usuarios_auth ORDER BY id;
