"""
Carga datos de pasantias a la BD de la tesis
PostgreSQL puerto 5434 + ChromaDB puerto 8003
MotoEdu EC — Tesis UPS Cuenca 2026
"""
import json, math, httpx, psycopg2
import hashlib, unicodedata

# ════════════════════════════════════════════════════════════════════════
# BLOQUE CANONICO DE EMBEDDING — v3 (md5-256-idf)
# ════════════════════════════════════════════════════════════════════════
# ⚠️  ESTE BLOQUE DEBE SER BYTE-IDENTICO EN LOS DOS ARCHIVOS:
#         seed_tesis.py                 (indexa el corpus)
#         backend/routers/asistente.py  (consulta el corpus)
#
#     Si divergen, el indice y las consultas viven en espacios vectoriales
#     distintos y la recuperacion falla EN SILENCIO: sin excepciones, sin
#     logs, solo resultados irrelevantes. Ese fallo ya ocurrio una vez en
#     este proyecto (ver historial) y costo semanas detectarlo.
#
#     Verificar la identidad de ambos bloques antes de cada indexacion:
#         python tests/verificar_embedding.py
#
# Historial de versiones:
#   v1  hash() nativo de Python
#       -> Aleatorizado por proceso desde Python 3.3 (PYTHONHASHSEED).
#          El indexador y el consultante usaban semillas distintas.
#          faithfulness 0.351 — la recuperacion era azar.
#   v2  md5-256
#       -> MD5 es estable entre procesos. Normalizacion Unicode, bigramas,
#          256 dimensiones. faithfulness 0.902 / context recall 0.720.
#   v3  md5-256-idf  (actual)
#       -> Anade ponderacion por frecuencia inversa de documento. Sin ella,
#          "moto" (presente en los 200 docs) pesaba igual que "enduro"
#          (presente en 3), y los terminos comunes ahogaban a los
#          distintivos. Diagnostico: 56.5% de los fallos de recall eran
#          de recuperacion, no de cobertura del corpus.
#
# La tabla rag_idf en PostgreSQL es la UNICA fuente de verdad de los pesos.
# La escribe seed_tesis.py al indexar; la lee el backend al consultar.
# Si la tabla esta vacia, ambos caen a peso 1.0 = comportamiento v2.
# ════════════════════════════════════════════════════════════════════════
EMBED_VERSION = "md5-256-idf"
EMBED_DIM     = 256
IDF_DEFAULT   = 1.0
PESO_BIGRAMA  = 0.5


def _normalizar_texto(t: str) -> str:
    """Minusculas, sin tildes, y todo lo no alfanumerico convertido en espacio."""
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return "".join(c if c.isalnum() else " " for c in t)


def _tokens(text: str) -> list:
    """Palabras de contenido: normalizadas y de mas de 2 caracteres."""
    return [w for w in _normalizar_texto(text).split() if len(w) > 2]


def _pos(s: str, dim: int) -> int:
    """Posicion estable en el vector. MD5, no hash(): determinista entre procesos."""
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % dim


def _embed(text: str, idf: dict = None, dim: int = EMBED_DIM) -> list:
    """Vector lexico determinista con ponderacion IDF.

    Cada palabra suma su peso IDF en la posicion que le asigna MD5; cada
    bigrama suma el menor IDF de sus dos palabras, atenuado. Al final se
    normaliza a norma unitaria para que la similitud coseno sea comparable
    entre textos de distinta longitud.

    Sin IDF (idf=None) el peso es 1.0 para toda palabra: comportamiento v2.
    """
    vec = [0.0] * dim
    palabras = _tokens(text)
    for i, w in enumerate(palabras):
        peso = idf.get(w, IDF_DEFAULT) if idf else 1.0
        vec[_pos(w, dim)] += peso
        if i + 1 < len(palabras):
            w2 = palabras[i + 1]
            if idf:
                peso_big = min(idf.get(w, IDF_DEFAULT), idf.get(w2, IDF_DEFAULT)) * PESO_BIGRAMA
            else:
                peso_big = PESO_BIGRAMA
            vec[_pos(w + "_" + w2, dim)] += peso_big
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]
# ════════════════════ FIN DEL BLOQUE CANONICO ═══════════════════════════


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

# Borrar coleccion anterior (cambio de dimension 64 → 256) y crear fresca
httpx.delete(f"{col_url}/{COL_NAME}")
r_new = httpx.post(col_url, json={"name": COL_NAME, "metadata": {"project":"MotoEduEC-Tesis","version":"2026","embedding":EMBED_VERSION}})
col_id = r_new.json()["id"]
print(f"✅ Coleccion creada ({EMBED_VERSION}): {col_id}")



# ─── Calculo de IDF sobre el corpus y persistencia en PostgreSQL ───
def calcular_y_guardar_idf(documentos: list, conn) -> dict:
    """Calcula la frecuencia inversa de documento de cada termino del corpus y
    la persiste en la tabla rag_idf, que es la fuente de verdad compartida con
    el backend.

    Formula suavizada:  idf(t) = ln((N + 1) / (df(t) + 1)) + 1
    Siempre positiva. Un termino presente en los N documentos obtiene 1.0;
    uno presente en pocos obtiene un peso varias veces mayor.
    """
    from collections import Counter
    N = len(documentos)
    df = Counter()
    for doc in documentos:
        for w in set(_tokens(doc)):
            df[w] += 1

    idf = {t: math.log((N + 1) / (n + 1)) + 1.0 for t, n in df.items()}

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rag_idf (
            termino VARCHAR(80) PRIMARY KEY,
            idf     REAL NOT NULL,
            df      INT  NOT NULL
        )
    """)
    cur.execute("TRUNCATE rag_idf")
    cur.executemany(
        "INSERT INTO rag_idf (termino, idf, df) VALUES (%s, %s, %s)",
        [(t, round(idf[t], 4), df[t]) for t in idf]
    )
    conn.commit()
    cur.close()

    top = sorted(idf.items(), key=lambda x: x[1])[:5]
    raros = sorted(idf.items(), key=lambda x: -x[1])[:5]
    print(f"   IDF calculado sobre {N} documentos: {len(idf)} terminos unicos")
    print(f"   Mas comunes (peso bajo):  {', '.join(f'{t}={v:.2f}' for t, v in top)}")
    print(f"   Mas raros (peso alto):    {', '.join(f'{t}={v:.2f}' for t, v in raros)}")
    return idf


upsert_url = f"{CHROMA}/api/v2/tenants/{TENANT}/databases/{DATABASE}/collections/{col_id}/upsert"
total = 0
# El IDF se calcula sobre el corpus COMPLETO antes de indexar, porque cada
# vector depende de la estadistica global de terminos.
_todos_docs = [f"Pregunta: {p['pregunta']} Respuesta: {p['respuesta_correcta']}. {p.get('explicacion','')}" for p in preguntas]
# Se abre una conexion nueva: la anterior ya se cerro tras la carga relacional.
_conn_idf = psycopg2.connect(**DB)
IDF = calcular_y_guardar_idf(_todos_docs, _conn_idf)
_conn_idf.close()

for i in range(0, len(preguntas), 40):
    lote = preguntas[i:i+40]
    docs = [f"Pregunta: {p['pregunta']} Respuesta: {p['respuesta_correcta']}. {p.get('explicacion','')}" for p in lote]
    payload = {
        "ids":        [f"pregunta_{p['id']}" for p in lote],
        "documents":  docs,
        "embeddings": [_embed(d, idf=IDF) for d in docs],
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
