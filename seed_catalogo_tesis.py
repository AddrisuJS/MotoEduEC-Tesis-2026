"""
Carga catalogo completo de motos, llantas y equipamiento a la BD tesis
MotoEdu EC — Sprint 2 — UPS Cuenca 2026
"""
import psycopg2

DB = {
    "host": "localhost", "port": 5434,
    "dbname": "motoeduc_tesis",
    "user": "motoeduc_user",
    "password": "MotoEduC_2026$"
}

conn = psycopg2.connect(**DB)
cur  = conn.cursor()

print("🏍️  Cargando catalogo de motocicletas...")

# ── Tipos de moto ─────────────────────────────────────────────
tipos = [
    ("Utilitaria",        "Motos de trabajo y transporte diario, bajo consumo"),
    ("Scooter",           "Transmision automatica CVT, ideal para ciudad"),
    ("Naked/Street",      "Sin carenado, versatil en ciudad y carretera"),
    ("Deportiva",         "Alta performance, carenado aerodinamico"),
    ("Doble proposito",   "Apta para asfalto y caminos de tierra"),
    ("Adventure/Touring", "Larga distancia con alta capacidad de carga"),
    ("Enduro/Trail",      "Especializada en off-road y competicion"),
    ("Motocross",         "Solo competicion, sin homologacion vial"),
    ("Cruiser/Custom",    "Estilo chopper, posicion relajada"),
    ("Cafe Racer",        "Estilo retro deportivo urbano"),
]
for t in tipos:
    cur.execute("INSERT INTO tipos_moto (nombre,descripcion) VALUES (%s,%s) ON CONFLICT (nombre) DO NOTHING", t)

cur.execute("SELECT id, nombre FROM tipos_moto")
tipo_map = {r[1]: r[0] for r in cur.fetchall()}

cur.execute("SELECT id, nombre FROM marcas_moto")
marca_map = {r[1]: r[0] for r in cur.fetchall()}

# ── Motocicletas ──────────────────────────────────────────────
# (marca, tipo, modelo, anio, cc, hp, kg, precio_usd, uso_recomendado)
motos = [
    # HONDA
    ("Honda","Utilitaria",        "CB100",        2024, 100, 8.0,  96,  1200, "Delivery, ciudad, primer moto"),
    ("Honda","Utilitaria",        "CB1 Star",     2024, 110, 8.5,  99,  1450, "Ciudad, transporte diario"),
    ("Honda","Scooter",           "Navi",         2024, 110, 8.0,  102, 1350, "Ciudad, scooter economico"),
    ("Honda","Doble proposito",   "CRF300L",      2024, 286, 27.0, 140, 5200, "Aventura, doble proposito"),
    ("Honda","Adventure/Touring", "NX500",        2024, 471, 46.0, 196, 7800, "Touring, adventure"),
    ("Honda","Adventure/Touring", "Africa Twin",  2024, 1084,101.0,226,18500, "Gran touring, aventura extrema"),
    ("Honda","Enduro/Trail",      "CRF450R",      2024, 449, 63.0, 111, 9800, "Competicion enduro/motocross"),
    ("Honda","Naked/Street",      "XBlade 160",   2024, 163, 15.4, 139, 2800, "Ciudad, joven conductor"),
    # YAMAHA
    ("Yamaha","Utilitaria",       "YD110",        2024, 110, 8.1,  101, 1300, "Ciudad, primer moto"),
    ("Yamaha","Utilitaria",       "YBR125",       2024, 125, 10.5, 107, 1800, "Ciudad, transporte diario"),
    ("Yamaha","Naked/Street",     "FZ150",        2024, 149, 14.0, 132, 2600, "Ciudad, joven urbano"),
    ("Yamaha","Naked/Street",     "FZ25",         2024, 249, 20.9, 153, 4200, "Ciudad avanzado, carretera"),
    ("Yamaha","Doble proposito",  "XTZ125",       2024, 124, 10.0, 110, 2400, "Doble proposito entrada"),
    ("Yamaha","Doble proposito",  "XTZ250",       2024, 249, 21.0, 134, 4500, "Aventura media"),
    ("Yamaha","Deportiva",        "R3",           2024, 321, 42.0, 167, 5800, "Deporte, circuito"),
    ("Yamaha","Naked/Street",     "MT-03",        2024, 321, 42.0, 168, 5900, "Naked deportivo"),
    ("Yamaha","Naked/Street",     "MT-07",        2024, 689, 75.0, 184, 9200, "Naked media cilindrada"),
    ("Yamaha","Adventure/Touring","Tenere 700",   2024, 689, 73.0, 204,11500, "Adventure, touring largo"),
    # KAWASAKI
    ("Kawasaki","Doble proposito","Versys-X 300", 2024, 296, 39.0, 169, 5500, "Aventura urbana, doble proposito"),
    ("Kawasaki","Naked/Street",   "Z400",         2024, 399, 45.0, 167, 6200, "Naked media cilindrada"),
    ("Kawasaki","Deportiva",      "Ninja 400",    2024, 399, 45.0, 167, 6500, "Deporte, iniciacion"),
    ("Kawasaki","Deportiva",      "Ninja 500",    2024, 499, 61.0, 196, 7800, "Deporte media cilindrada"),
    ("Kawasaki","Naked/Street",   "Z500",         2024, 499, 61.0, 193, 7500, "Naked media"),
    ("Kawasaki","Adventure/Touring","KLR 650",    2024, 652, 53.0, 202, 7200, "Adventure clasico"),
    ("Kawasaki","Doble proposito","KLE 500",      2024, 471, 48.0, 196, 6800, "Doble proposito media"),
    ("Kawasaki","Deportiva",      "ZX-4RR",       2024, 399, 77.0, 183,11200, "Supersport 4 cilindros"),
    # KTM
    ("KTM","Naked/Street",        "Duke 200",     2024, 199, 25.0, 140, 4200, "Iniciacion deportiva"),
    ("KTM","Naked/Street",        "Duke 390",     2024, 373, 45.0, 163, 6500, "Naked deportivo avanzado"),
    ("KTM","Deportiva",           "RC 390",       2024, 373, 45.0, 163, 6800, "Deporte pura"),
    ("KTM","Adventure/Touring",   "390 Adventure",2024, 373, 45.0, 177, 7200, "Adventure compact"),
    ("KTM","Enduro/Trail",        "EXC 300",      2024, 293, 43.0,  98, 9500, "Enduro competicion"),
    ("KTM","Naked/Street",        "890 Duke R",   2024, 889, 121.0,166,14800, "Naked alta performance"),
    # ROYAL ENFIELD
    ("Royal Enfield","Naked/Street",  "Hunter 350",    2024, 349, 20.0, 177, 4800, "Retro urbano"),
    ("Royal Enfield","Naked/Street",  "Classic 350",   2024, 349, 20.0, 195, 5200, "Retro clasico"),
    ("Royal Enfield","Cruiser/Custom","Meteor 350",    2024, 349, 20.0, 191, 5500, "Cruiser moderno"),
    ("Royal Enfield","Adventure/Touring","Himalayan 450",2024,452,40.0,196,7500,"Adventure media"),
    ("Royal Enfield","Adventure/Touring","Guerrilla 450",2024,452,40.0,185,7800,"Adventure moderna"),
    ("Royal Enfield","Cafe Racer", "Continental GT 650",2024,648,47.0,198,9500,"Cafe racer clasico"),
    ("Royal Enfield","Naked/Street","Interceptor 650", 2024, 648, 47.0, 202, 9200, "Retro moderno"),
    # BAJAJ
    ("Bajaj","Utilitaria",        "Boxer 150",    2024, 150, 12.0, 122, 2100, "Delivery, trabajo intensivo"),
    ("Bajaj","Naked/Street",      "Pulsar NS200", 2024, 199, 24.5, 156, 3800, "Naked deportivo economico"),
    ("Bajaj","Naked/Street",      "NS160",        2024, 160, 17.0, 148, 3200, "Ciudad deportivo"),
    ("Bajaj","Adventure/Touring", "Dominar 400",  2024, 373, 40.0, 182, 5800, "Touring economico"),
    ("Bajaj","Cruiser/Custom",    "Avenger 220",  2024, 220, 19.0, 155, 3600, "Cruiser economico"),
    # SHINERAY / DAYTONA / FACTORY
    ("Shineray","Doble proposito","XY200GY",      2024, 200, 14.0, 118, 2200, "Doble proposito economico"),
    ("Shineray","Utilitaria",     "XY150GY",      2024, 150, 11.0, 108, 1600, "Ciudad, delivery economico"),
    ("Daytona","Naked/Street",    "Sprinter 200", 2024, 200, 16.0, 125, 2400, "Ciudad economico"),
    ("Daytona","Utilitaria",      "VX 125",       2024, 125, 9.5,  105, 1500, "Ciudad basico"),
]

ok = 0
for m in motos:
    marca, tipo_n, modelo, anio, cc, hp, kg, precio, uso = m
    marca_id = marca_map.get(marca)
    tipo_id  = tipo_map.get(tipo_n)
    if not marca_id or not tipo_id:
        print(f"  ⚠️  Saltando {marca} {modelo} — marca o tipo no encontrado")
        continue
    cur.execute("""
        INSERT INTO motocicletas
            (marca_id, tipo_id, modelo, anio, cilindrada_cc, potencia_hp, peso_kg, precio_usd, uso_recomendado, disponible_ec)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
        ON CONFLICT DO NOTHING
    """, (marca_id, tipo_id, modelo, anio, cc, hp, kg, precio, uso))
    ok += 1

conn.commit()
print(f"✅ {ok} motocicletas cargadas")

# ── Marcas de llantas ─────────────────────────────────────────
print("\n🔵 Cargando catalogo de llantas...")
marcas_llanta = [
    ("Michelin",   "Francia",  "alta"),
    ("Pirelli",    "Italia",   "alta"),
    ("Bridgestone","Japon",    "alta"),
    ("Metzeler",   "Alemania", "alta"),
    ("Continental","Alemania", "alta"),
    ("Dunlop",     "UK",       "media"),
    ("Maxxis",     "Taiwan",   "media"),
    ("IRC",        "Japon",    "media"),
    ("Kenda",      "Taiwan",   "economica"),
    ("CST",        "China",    "economica"),
]
for ml in marcas_llanta:
    cur.execute("INSERT INTO marcas_llanta (nombre,origen,gama) VALUES (%s,%s,%s) ON CONFLICT (nombre) DO NOTHING", ml)

tipos_llanta = [
    ("Carretera (Road)",  "Asfalto seco y mojado",          "Clima seco y lluvia moderada"),
    ("Trail/Adventure",   "Asfalto y tierra compacta",      "Clima variado"),
    ("Off-road/Enduro",   "Tierra, barro, rocas",           "Clima variado, lluvia intensa"),
    ("Lluvia/Rain",       "Asfalto mojado, canales de agua","Lluvia intensa, ciudad"),
    ("Scooter",           "Asfalto urbano",                 "Ciudad, clima seco y lluvia"),
    ("Sport",             "Asfalto seco, circuito",         "Clima seco"),
]
for tl in tipos_llanta:
    cur.execute("INSERT INTO tipos_llanta (nombre,terreno_ideal,clima_ideal) VALUES (%s,%s,%s) ON CONFLICT (nombre) DO NOTHING", tl)

cur.execute("SELECT id, nombre FROM marcas_llanta")
ml_map = {r[1]: r[0] for r in cur.fetchall()}
cur.execute("SELECT id, nombre FROM tipos_llanta")
tl_map = {r[1]: r[0] for r in cur.fetchall()}

llantas = [
    ("Michelin",   "Carretera (Road)",  "Pilot Street 2",    "110/70-17", 85,  120),
    ("Michelin",   "Trail/Adventure",   "Anakee Adventure",  "90/90-21",  110, 160),
    ("Michelin",   "Lluvia/Rain",       "City Grip 2",       "120/70-14", 95,  130),
    ("Pirelli",    "Carretera (Road)",  "Angel City",        "110/70-17", 75,  110),
    ("Pirelli",    "Trail/Adventure",   "Scorpion Rally STR","90/90-21",  120, 170),
    ("Bridgestone","Carretera (Road)",  "Battlax BT-46",     "110/70-17", 80,  115),
    ("Bridgestone","Off-road/Enduro",   "Battlecross X30",   "80/100-21", 90,  130),
    ("Dunlop",     "Carretera (Road)",  "D107",              "100/90-17", 55,  75),
    ("Dunlop",     "Trail/Adventure",   "Trailmax Mixtour",  "90/90-21",  70,  100),
    ("Maxxis",     "Carretera (Road)",  "MA-ST2",            "110/70-17", 45,  65),
    ("Maxxis",     "Off-road/Enduro",   "M-7305 Enduro",     "90/100-21", 55,  80),
    ("IRC",        "Scooter",           "SS-560",            "120/70-12", 40,  60),
    ("Kenda",      "Carretera (Road)",  "K657 Challenger",   "110/90-16", 30,  45),
    ("CST",        "Scooter",           "CM-SC1",            "130/70-12", 25,  38),
    ("Continental","Sport",             "ContiRaceAttack 2", "120/70-17", 140, 190),
    ("Metzeler",   "Lluvia/Rain",       "Roadtec 01",        "120/70-17", 100, 145),
]

ll_ok = 0
for ll in llantas:
    marca, tipo_n, modelo, medida, pmin, pmax = ll
    mid = ml_map.get(marca)
    tid = tl_map.get(tipo_n)
    if not mid or not tid:
        continue
    cur.execute("""
        INSERT INTO llantas (marca_id, tipo_id, modelo, medida_ejemplo, precio_min_usd, precio_max_usd)
        VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
    """, (mid, tid, modelo, medida, pmin, pmax))
    ll_ok += 1

conn.commit()
print(f"✅ {ll_ok} llantas cargadas")

cur.close()
conn.close()

print("\n" + "="*50)
print("✅ CATALOGO COMPLETO CARGADO")
print(f"   Motos:   {ok}")
print(f"   Llantas: {ll_ok}")
print("="*50)
