-- Seed basico para tesis (datos minimos para arrancar)
INSERT INTO marcas_moto (nombre,origen,distribuidor_ec) VALUES
('Honda','Japon','INDUMOT S.A.'),('Yamaha','Japon','Moto Power'),
('Kawasaki','Japon','Kawasaki Ecuador'),('KTM','Austria','Distribuidores'),
('Royal Enfield','India','EFLOSA'),('Bajaj','India','Distribuidores'),
('Shineray','China','Distribuidores'),('Daytona','China','Moto Power')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO tipos_moto (nombre,descripcion) VALUES
('Utilitaria','Motos de trabajo y transporte diario'),
('Naked/Street','Sin carenado, versatil en ciudad'),
('Doble proposito','Asfalto y tierra'),
('Adventure/Touring','Larga distancia'),
('Deportiva','Alta performance'),
('Scooter','Automatica para ciudad'),
('Enduro/Trail','Off-road especializada')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO categorias_pregunta (nombre,modulo_app) VALUES
('Normativa LOTTTSV','M2'),('Conduccion Segura','M2'),
('Conduccion en Lluvia','M2'),('Equipamiento de Seguridad','M2'),
('Tipos de Motocicletas','M2'),('Llantas y Neumaticos','M2'),
('Primeros Auxilios','M2')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO brechas_conocimiento (descripcion,pct_con_brecha,nivel_riesgo,modulo_relacionado) VALUES
('Desconoce velocidad maxima urbana (50 km/h)',60,'ALTO','M2'),
('Sin capacitacion formal de manejo',35,'ALTO','M2'),
('Tecnica incorrecta de frenado en mojado',30,'ALTO','M2'),
('No revisa llantas con frecuencia adecuada',45,'MEDIO','M5'),
('Desconoce completamente la LOTTTSV',20,'ALTO','M2'),
('Sin licencia de conduccion valida',25,'ALTO','M2'),
('Ha tenido accidentes o caidas',60,'MEDIO','M2'),
('No usa equipamiento completo de seguridad',40,'ALTO','M2')
ON CONFLICT DO NOTHING;
