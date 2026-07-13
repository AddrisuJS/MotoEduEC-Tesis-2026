-- FIX: reinsertar items del garaje con UTF-8 limpio + niveles de rareza
DELETE FROM garaje_items;

ALTER TABLE garaje_items ADD COLUMN IF NOT EXISTS rareza VARCHAR(12) DEFAULT 'comun';

INSERT INTO garaje_items (nombre, icono, tipo, requisito_tipo, requisito_valor, descripcion, rareza) VALUES
 ('Casco basico',           '🪖','equipo','xp',       0,   'Tu primer casco. Nunca salgas sin el.',                              'comun'),
 ('Guantes de proteccion',  '🧤','equipo','xp',       400, 'Protegen tus manos: lo primero que toca el suelo en una caida.',     'comun'),
 ('Chaqueta con protecciones','🧥','equipo','xp',     900, 'Hombros, codos y espalda protegidos.',                               'raro'),
 ('Botas de moto',          '🥾','equipo','xp',       1500,'Cubren el tobillo: adios esguinces.',                                'raro'),
 ('Casco integral premium', '⛑️','equipo','xp',      2500,'Certificacion ECE 22.06. Maxima proteccion.',                        'epico'),
 ('Chaleco con airbag',     '🦺','equipo','xp',       4000,'Tecnologia de punta para el motociclista serio.',                    'epico'),
 ('Llantas nuevas',         '🛞','moto',  'racha',    2,   'Labrado perfecto para lluvia cuencana.',                             'comun'),
 ('Escape deportivo',       '💨','moto',  'racha',    3,   'Suena tan bien como tu conocimiento vial.',                          'raro'),
 ('Faro LED',               '💡','moto',  'racha',    5,   'Que te vean: visibilidad = vida.',                                   'raro'),
 ('Pintura personalizada',  '🎨','moto',  'racha',    7,   'Tu moto, tu estilo. Racha de campeon.',                              'epico'),
 ('Espejos panoramicos',    '🪞','moto',  'partidas', 5,   'Reducen el punto ciego.',                                            'comun'),
 ('Motor mejorado',         '⚙️','moto', 'partidas', 15,  'La constancia tiene premio.',                                        'raro'),
 ('Kit de herramientas',    '🧰','moto',  'partidas', 25,  'Para el mantenimiento que ya sabes hacer.',                          'epico'),
 ('Moto de leyenda',        '🏍️','moto', 'xp',       6000,'La corona del garaje. Solo para expertos viales.',                   'legendario');

SELECT nombre, icono, rareza FROM garaje_items ORDER BY id;
