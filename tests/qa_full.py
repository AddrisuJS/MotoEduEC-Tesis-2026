"""
QA FULL — MotoEdu EC Tesis
Verifica: Docker, PostgreSQL (5434), ChromaDB (8003), API (8010) y Frontend (3000)
Auto-descubre todos los endpoints GET desde el OpenAPI y prueba POST clave.
Uso:  python tests/qa_full.py
UPS Cuenca 2026
"""
import subprocess, sys, json, time

try:
    import httpx, psycopg2
except ImportError:
    print("Instala dependencias:  pip install httpx psycopg2-binary")
    sys.exit(1)

API   = "http://localhost:8010"
FRONT = "http://localhost:3000"
CHROMA= "http://localhost:8003"
DB = {"host":"localhost","port":5434,"dbname":"motoeduc_tesis","user":"motoeduc_user","password":"MotoEduC_2026$"}

PASS, FAIL, WARN = [], [], []
def ok(msg):   PASS.append(msg); print(f"  ✅ {msg}")
def bad(msg):  FAIL.append(msg); print(f"  ❌ {msg}")
def warn(msg): WARN.append(msg); print(f"  ⚠️  {msg}")

print("="*60)
print("  QA FULL — MotoEdu EC")
print("="*60)

# ── 1. DOCKER ────────────────────────────────────────────────
print("\n[1/5] DOCKER — contenedores de la tesis")
esperados = ["motoeduc_tesis_api","motoeduc_tesis_postgres","motoeduc_tesis_chromadb","motoeduc_tesis_frontend","motoeduc_tesis_pgadmin"]
try:
    out = subprocess.run(["docker","ps","--format","{{.Names}}|{{.Status}}"],capture_output=True,text=True,timeout=15).stdout
    corriendo = {l.split("|")[0]: l.split("|")[1] for l in out.strip().splitlines() if "|" in l}
    for c in esperados:
        if c in corriendo: ok(f"{c} → {corriendo[c]}")
        else: bad(f"{c} NO está corriendo")
except Exception as e:
    bad(f"No se pudo consultar Docker: {e}")

# ── 2. POSTGRESQL ────────────────────────────────────────────
print("\n[2/5] POSTGRESQL — tablas y datos (puerto 5434)")
tablas_clave = ["perfiles","motos","llantas","equipamiento","preguntas","lecciones",
                "sesiones_chat","experimento_piloto","insignias","usuarios_gamificacion"]
try:
    conn = psycopg2.connect(**DB); cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tablas = {r[0] for r in cur.fetchall()}
    ok(f"Conexión OK — {len(tablas)} tablas en public")
    for t in sorted(tablas):
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{t}"'); n = cur.fetchone()[0]
            if n > 0: ok(f"tabla {t}: {n} filas")
            else: warn(f"tabla {t}: VACÍA (0 filas)")
        except Exception as e:
            conn.rollback(); bad(f"tabla {t}: error al contar — {e}")
    faltan = [t for t in tablas_clave if t not in tablas]
    if faltan: warn(f"Tablas esperadas ausentes (verificar nombres reales): {', '.join(faltan)}")
    conn.close()
except Exception as e:
    bad(f"No se pudo conectar a PostgreSQL 5434: {e}")

# ── 3. CHROMADB ──────────────────────────────────────────────
print("\n[3/5] CHROMADB — vectores (puerto 8003)")
try:
    r = httpx.get(f"{CHROMA}/api/v2/heartbeat", timeout=10)
    if r.status_code == 200: ok("Heartbeat v2 OK")
    else:
        r = httpx.get(f"{CHROMA}/api/v1/heartbeat", timeout=10)
        ok("Heartbeat v1 OK") if r.status_code==200 else bad(f"Heartbeat falló: {r.status_code}")
    # conteo vía API interna del backend si existe, si no vía cliente
    try:
        import chromadb
        cli = chromadb.HttpClient(host="localhost", port=8003)
        for col in cli.list_collections():
            c = cli.get_collection(col.name if hasattr(col,'name') else col)
            n = c.count()
            (ok if n>=200 else warn)(f"colección {c.name}: {n} documentos" + ("" if n>=200 else " (esperados 200)"))
    except Exception as e:
        warn(f"No se pudo contar colecciones (pip install chromadb): {e}")
except Exception as e:
    bad(f"ChromaDB no responde: {e}")

# ── 4. API — TODOS LOS ENDPOINTS ─────────────────────────────
print("\n[4/5] API — auto-descubrimiento OpenAPI (puerto 8010)")
try:
    spec = httpx.get(f"{API}/openapi.json", timeout=15).json()
    paths = spec.get("paths", {})
    ok(f"OpenAPI OK — {len(paths)} rutas registradas")
    gets = [(p, d) for p, d in paths.items() if "get" in d and "{" not in p]
    print(f"  → Probando {len(gets)} endpoints GET sin parámetros...")
    for p, d in gets:
        try:
            r = httpx.get(f"{API}{p}", timeout=30)
            (ok if r.status_code < 500 else bad)(f"GET {p} → {r.status_code}")
        except Exception as e:
            bad(f"GET {p} → excepción {type(e).__name__}")
    # GETs con parámetros: solo listar para revisión manual
    con_param = [p for p in paths if "get" in paths[p] and "{" in p]
    if con_param: warn(f"GET con parámetros (probar en Swagger): {', '.join(con_param)}")
except Exception as e:
    bad(f"No se pudo leer el OpenAPI: {e}")

# POST clave con payloads reales
print("\n  → POST clave de los módulos")
posts = [
    ("/m1/perfil/crear", {"nombre":"QA Bot","edad":28,"anos_experiencia":3,"tipo_uso":"urbano","moto":"Honda CB190R","provincia":"Azuay"}),
    ("/m3/asistente/consultar", {"pregunta":"velocidad maxima zona urbana","usuario_id":"qa_bot","perfil":{"tipo_uso":"urbano"}}),
]
for p, body in posts:
    try:
        t0 = time.time()
        r = httpx.post(f"{API}{p}", json=body, timeout=90)
        dt = time.time()-t0
        if r.status_code < 400:
            data = r.json()
            texto = json.dumps(data, ensure_ascii=False)
            vacio = all(not str(v).strip() for v in data.values()) if isinstance(data,dict) else not texto
            if vacio: bad(f"POST {p} → {r.status_code} pero RESPUESTA VACÍA ({dt:.1f}s)")
            else: ok(f"POST {p} → {r.status_code} en {dt:.1f}s — {texto[:120]}...")
            if p.startswith("/m3"):
                campos = list(data.keys()) if isinstance(data,dict) else []
                print(f"     ℹ️  Campos que devuelve M3: {campos}  ← el ragas_eval.py debe leer el campo correcto")
        else:
            bad(f"POST {p} → {r.status_code}: {r.text[:150]}")
    except Exception as e:
        bad(f"POST {p} → excepción: {e}")

# ── 5. FRONTEND ──────────────────────────────────────────────
print("\n[5/5] FRONTEND — páginas (puerto 3000)")
paginas = ["/","/perfil","/educacion","/asistente","/motos","/llantas","/historia","/dashboard","/gamificacion"]
for pg in paginas:
    try:
        r = httpx.get(f"{FRONT}{pg}", timeout=30, follow_redirects=True)
        (ok if r.status_code==200 else warn)(f"página {pg} → {r.status_code}")
    except Exception as e:
        bad(f"página {pg} → {type(e).__name__}")

# ── RESUMEN ──────────────────────────────────────────────────
print("\n" + "="*60)
print(f"  RESULTADO:  ✅ {len(PASS)} PASS   ⚠️ {len(WARN)} WARN   ❌ {len(FAIL)} FAIL")
print("="*60)
if FAIL:
    print("\nFALLOS A CORREGIR:")
    for f in FAIL: print(f"  ❌ {f}")
with open("tests/qa_full_reporte.json","w",encoding="utf-8") as f:
    json.dump({"pass":PASS,"warn":WARN,"fail":FAIL,"fecha":time.strftime("%Y-%m-%d %H:%M")},f,ensure_ascii=False,indent=2)
print("\nReporte guardado en tests/qa_full_reporte.json — pégame el output completo.")
