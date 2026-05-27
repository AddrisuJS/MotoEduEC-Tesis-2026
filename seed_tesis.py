"""
Carga datos de pasantias a la BD de la tesis
PostgreSQL puerto 5434 + ChromaDB puerto 8003
MotoEdu EC — Tesis UPS Cuenca 2026
"""
import json, math, httpx, psycopg2

# ─── Conexion a BD TESIS (puerto 5434) ───────────────────────
DB = {
    "host": "localhost", "port": 5434,
    "dbname": "motoeduc_tesis",
    "user": "motoeduc_user",
    "password": "MotoEduC_2026$"
}

# ─── ChromaDB TESIS (puerto 8003) ────────────────────────────
CHROMA   = "http://localhost:8003"
TENANT   = "default_tenant"
DATABASE = "default_database"
COL_NAME = "motoeduc_knowledge"

DATASET  = r"C:\Tesis\motoeduc\E4-DATASET\dataset_preguntas_viales.json"

print("=" * 55)
print("  MotoEdu EC — Carga de datos a BD Tesis")
print("=" * 55)

# ── 1. Cargar JSON ────────────────────────────────────────────
print("\n📂 Cargando dataset...")
with open(DATASET, "r", encoding="utf-8") as f:
    preguntas = json.load(f)
print(f"✅ {len(preguntas)} preguntas listas")

# ── 2. Cargar motocicletas y datos basicos en PostgreSQL ──────
print("\n🐘 Conectando a PostgreSQL tesis (puerto 5434)...")
conn = psycopg2.connect(**DB)
cur  = conn.cursor()

# Insertar motocicletas desde pasantias via dblink simulado
# (copiamos los datos directamente)
motos_data = [
    ("Honda","Japon","INDUMOT S.A."),("Yamaha","Japon","Moto Power"),
    ("Kawasaki","Japon","Kawasaki Ecuador"),("KTM","Austria","Distribuidores"),
    ("Royal Enfield","India","EFLOSA"),("Bajaj","India","Distribuidores"),
    ("Shineray","China","Distribuidores"),("Daytona","China","Moto Power"),
    ("Factory Bike","Ecuador/China","Moto Power"),("AKT","Colombia","Distribuidores"),
    ("Benelli","Italia/China","Moto Power"),("TVS","India","Distribuidores"),
]
for m in motos_data:
    cur.execute("INSERT INTO marcas_moto (nombre,origen,distribuidor_ec) VALUES (%s,%s,%s) ON CONFLICT (nombre) DO NOTHING", m)

tipos_data = [
    ("Utilitaria","Motos de trabajo y transporte diario"),
    ("Scooter","Transmision automatica CVT para ciudad"),
    ("Naked/Street","Sin carenado, versatil en ciudad y carretera"),
    ("Deportiva","Alta performance, carenado aerodinamico"),
    ("Doble proposito","Apta para asfalto y caminos de tierra"),
    ("Adventure/Touring","Larga distancia con alta capacidad"),
    ("Enduro/Trail","Especializada en off-road"),
    ("Motocross","Solo competicion, sin homologacion vial"),
    ("Cruiser/Custom","Estilo chopper, posicion relajada"),
    ("Cafe Racer","Estilo retro deportivo"),
]
for t in tipos_data:
    cur.execute("INSERT INTO tipos_moto (nombre,descripcion) VALUES (%s,%s) ON CONFLICT (nombre) DO NOTHING", t)

cats = [
    ("Normativa LOTTTSV","M2"),("Conduccion Segura","M2"),
    ("Conduccion en Lluvia","M2"),("Equipamiento de Seguridad","M2"),
    ("Tipos de Motocicletas","M2"),("Llantas y Neumaticos","M2"),
    ("Primeros Auxilios","M2"),
]
for c in cats:
    cur.execute("INSERT INTO categorias_pregunta (nombre,modulo_app) VALUES (%s,%s) ON CONFLICT (nombre) DO NOTHING", c)

brechas = [
    ("Desconoce velocidad maxima urbana (50 km/h)",60,"ALTO","M2"),
    ("Sin capacitacion formal de manejo",35,"ALTO","M2"),
    ("Tecnica incorrecta de frenado en mojado",30,"ALTO","M2"),
    ("No revisa llantas con frecuencia adecuada",45,"MEDIO","M5"),
    ("Desconoce completamente la LOTTTSV",20,"ALTO","M2"),
    ("Sin licencia de conduccion valida",25,"ALTO","M2"),
    ("Ha tenido accidentes o caidas",60,"MEDIO","M2"),
    ("No usa equipamiento completo de seguridad",40,"ALTO","M2"),
]
for b in brechas:
    cur.execute("INSERT INTO brechas_conocimiento (descripcion,pct_con_brecha,nivel_riesgo,modulo_relacionado) VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING", b)

conn.commit()
print("✅ Marcas, tipos, categorias y brechas cargadas")

# ── 3. Cargar preguntas viales ────────────────────────────────
print("\n📝 Cargando 200 preguntas viales...")
cur.execute("SELECT id, nombre FROM categorias_pregunta")
cat_map = {r[1]: r[0] for r in cur.fetchall()}

ok = 0
for p in preguntas:
    cat_id = cat_map.get(p.get("categoria"), list(cat_map.values())[0])
    try:
        cur.execute("""
            INSERT INTO preguntas_viales
                (categoria_id,pregunta,respuesta_correcta,opcion_b,opcion_c,opcion_d,
                 explicacion,dificultad,perfil_objetivo,fuente,activa)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE)
            ON CONFLICT DO NOTHING
        """, (cat_id, p["pregunta"], p["respuesta_correcta"],
              p.get("opcion_b"), p.get("opcion_c"), p.get("opcion_d"),
              p.get("explicacion"), p.get("dificultad","basico"),
              p.get("perfil_objetivo","todos"), p.get("fuente","MotoEdu EC")))
        ok += 1
    except Exception as e:
        pass

conn.commit()
cur.close()
conn.close()
print(f"✅ PostgreSQL tesis: {ok} preguntas cargadas")

# ── 4. Cargar en ChromaDB tesis (puerto 8003) ─────────────────
print("\n🧠 Conectando ChromaDB tesis (puerto 8003)...")
r = httpx.get(f"{CHROMA}/api/v2/heartbeat")
print(f"   Heartbeat: {r.status_code}")

col_url = f"{CHROMA}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections"

# Obtener o crear coleccion
r_get = httpx.get(f"{col_url}/{COL_NAME}")
if r_get.status_code == 200:
    col_id = r_get.json()["id"]
    print(f"✅ Coleccion existente: {col_id}")
else:
    r_new = httpx.post(col_url, json={"name": COL_NAME, "metadata": {"project":"MotoEduEC-Tesis","version":"2026"}})
    col_id = r_new.json()["id"]
    print(f"✅ Coleccion creada: {col_id}")

def embed(text, dim=64):
    vec = [0.0]*dim
    for w in text.lower().split():
        vec[hash(w)%dim] += 1.0
    norm = math.sqrt(sum(x*x for x in vec)) or 1.0
    return [x/norm for x in vec]

upsert_url = f"{CHROMA}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{col_id}/upsert"
total = 0
for i in range(0, len(preguntas), 40):
    lote = preguntas[i:i+40]
    docs = [f"Pregunta: {p['pregunta']} Respuesta: {p['respuesta_correcta']}. {p.get('explicacion','')}" for p in lote]
    payload = {
        "ids":        [f"pregunta_{p['id']}" for p in lote],
        "documents":  docs,
        "embeddings": [embed(d) for d in docs],
        "metadatas":  [{"categoria": p.get("categoria","General"), "dificultad": p.get("dificultad","basico"), "respuesta_correcta": p["respuesta_correcta"]} for p in lote],
    }
    r = httpx.post(upsert_url, json=payload, timeout=30)
    if r.status_code in [200,201]:
        total += len(lote)
        print(f"   ✅ Lote {i//40+1}: {total}/{len(preguntas)}")

count_url = f"{CHROMA}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{col_id}/count"
r = httpx.get(count_url)
print(f"\n✅ ChromaDB tesis: {r.text} documentos")

print("\n" + "="*55)
print("✅ TESIS BD CARGADA COMPLETAMENTE")
print("   Abre: http://localhost:3000")
print("   API:  http://localhost:8010/docs")
print("="*55)
