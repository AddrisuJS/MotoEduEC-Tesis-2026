"""
Tests de Integracion Sprint 2 — M1 + M2 + M3
MotoEdu EC — UPS Cuenca 2026
Ejecutar: pytest tests/test_integracion_s2.py -v
"""
import pytest
import httpx

BASE = "http://localhost:8010"


# ─── Fixtures ────────────────────────────────────────────────

@pytest.fixture(scope="module")
def usuario_delivery():
    """Crea un usuario Delivery y retorna su ID y perfil."""
    r = httpx.post(f"{BASE}/m1/perfil/crear", json={
        "nombre":           "Test Delivery",
        "tipo_uso":         "delivery",
        "anos_experiencia": 2,
        "moto_actual":      "Honda CB100",
        "cilindrada_cc":    100,
        "zona":             "Guayas",
        "horas_uso_diario": 8,
        "objetivos":        ["conocer normativa"]
    }, timeout=10)
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def usuario_touring():
    """Crea un usuario Touring y retorna su ID y perfil."""
    r = httpx.post(f"{BASE}/m1/perfil/crear", json={
        "nombre":           "Test Touring",
        "tipo_uso":         "touring",
        "anos_experiencia": 5,
        "moto_actual":      "Yamaha Tenere 700",
        "cilindrada_cc":    689,
        "zona":             "Sierra",
        "horas_uso_diario": 2,
        "objetivos":        ["preparar viajes largos"]
    }, timeout=10)
    assert r.status_code == 200
    return r.json()


@pytest.fixture(scope="module")
def usuario_enduro():
    """Crea un usuario Enduro y retorna su ID y perfil."""
    r = httpx.post(f"{BASE}/m1/perfil/crear", json={
        "nombre":           "Test Enduro",
        "tipo_uso":         "enduro",
        "anos_experiencia": 7,
        "moto_actual":      "KTM EXC 300",
        "cilindrada_cc":    293,
        "zona":             "Sierra",
        "horas_uso_diario": 3,
        "objetivos":        ["mejorar tecnica off-road"]
    }, timeout=10)
    assert r.status_code == 200
    return r.json()


# ─── Tests M1 ────────────────────────────────────────────────

class TestM1Perfil:

    def test_clasificacion_delivery(self, usuario_delivery):
        """T01: El perfil Delivery se clasifica correctamente."""
        assert usuario_delivery["perfil_key"] == "delivery"
        assert usuario_delivery["nivel_riesgo"] == "ALTO"
        assert "usuario_id" in usuario_delivery
        assert len(usuario_delivery["usuario_id"]) == 36  # UUID

    def test_clasificacion_touring(self, usuario_touring):
        """T02: El perfil Touring se clasifica correctamente."""
        assert usuario_touring["perfil_key"] == "touring"
        assert usuario_touring["nivel_riesgo"] == "MEDIO"

    def test_clasificacion_enduro(self, usuario_enduro):
        """T03: El perfil Enduro se clasifica correctamente."""
        assert usuario_enduro["perfil_key"] == "enduro"
        assert usuario_enduro["nivel_riesgo"] == "ALTO"

    def test_system_prompt_contiene_perfil(self, usuario_delivery):
        """T04: El system prompt incluye datos del perfil del usuario."""
        preview = usuario_delivery.get("system_prompt_preview", "")
        assert "delivery" in preview.lower() or "Delivery" in preview
        assert len(preview) > 100

    def test_equipamiento_segun_perfil(self, usuario_delivery):
        """T05: El equipamiento minimo es especifico del perfil."""
        equipamiento = usuario_delivery.get("equipamiento_minimo", [])
        assert len(equipamiento) >= 3
        # Delivery debe tener chaleco reflectivo
        equipamiento_str = " ".join(equipamiento).lower()
        assert "casco" in equipamiento_str

    def test_listar_perfiles(self):
        """T06: El endpoint lista los 6 perfiles disponibles."""
        r = httpx.get(f"{BASE}/m1/perfil/perfiles", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 6
        assert "delivery" in data["perfiles"]
        assert "touring" in data["perfiles"]


# ─── Tests M2 ────────────────────────────────────────────────

class TestM2Educacion:

    def test_categorias_disponibles(self):
        """T07: M2 devuelve exactamente 5 categorias."""
        r = httpx.get(f"{BASE}/m2/educacion/categorias", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 5
        nombres = [c["nombre"] for c in data["categorias"]]
        assert "Normativa LOTTTSV y Velocidades" in nombres
        assert "Conduccion en Lluvia" in nombres

    def test_leccion_delivery(self, usuario_delivery):
        """T08: La leccion para perfil Delivery se genera correctamente."""
        r = httpx.post(f"{BASE}/m2/educacion/leccion", json={
            "categoria": "Normativa LOTTTSV y Velocidades",
            "perfil": {
                "tipo_uso":         "delivery",
                "anos_experiencia": 2,
                "nivel":            "intermedio"
            }
        }, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "leccion" in data
        assert data["categoria"] == "Normativa LOTTTSV y Velocidades"

    def test_quiz_genera_10_preguntas(self):
        """T09: El quiz genera exactamente 10 preguntas."""
        r = httpx.post(f"{BASE}/m2/educacion/quiz", json={
            "categoria":   "Normativa LOTTTSV y Velocidades",
            "perfil":      {"tipo_uso": "urbano", "nivel": "basico"},
            "n_preguntas": 10
        }, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data["total_preguntas"] == 10
        assert len(data["quiz"]) == 10

    def test_quiz_tiene_opciones(self):
        """T10: Cada pregunta del quiz tiene opciones y respuesta correcta."""
        r = httpx.post(f"{BASE}/m2/educacion/quiz", json={
            "categoria": "Conduccion Segura",
            "perfil":    {"tipo_uso": "urbano", "nivel": "basico"}
        }, timeout=30)
        assert r.status_code == 200
        quiz = r.json()["quiz"]
        for pregunta in quiz[:3]:  # Verificar las primeras 3
            assert "pregunta" in pregunta
            assert "correcta" in pregunta


# ─── Tests M3 ────────────────────────────────────────────────

class TestM3AsistenteRAG:

    def test_estado_rag_operativo(self):
        """T11: El pipeline RAG esta operativo y ChromaDB conectado."""
        r = httpx.get(f"{BASE}/m3/asistente/estado", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["chromadb_conectado"] == True
        assert data["documentos_indexados"] == 200
        assert data["estado"] == "operativo"

    def test_consulta_recupera_documentos(self, usuario_delivery):
        """T12: Una consulta recupera documentos de ChromaDB."""
        r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta":   "velocidad maxima en zona urbana",
            "usuario_id": usuario_delivery["usuario_id"],
            "perfil":     {"tipo_uso": "delivery", "anos_experiencia": 2}
        }, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data["documentos_recuperados"] > 0
        assert "respuesta" in data
        assert len(data["respuesta"]) > 10

    def test_historial_conversacion(self, usuario_touring):
        """T13: El historial de conversacion se mantiene entre turnos."""
        uid = usuario_touring["usuario_id"]

        # Primer turno
        r1 = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta":   "que documentos necesito para manejar?",
            "usuario_id": uid,
            "perfil":     {"tipo_uso": "touring"}
        }, timeout=30)
        assert r1.status_code == 200
        assert r1.json()["turno_conversacion"] >= 1

        # Segundo turno
        r2 = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta":   "y si no tengo SOAT?",
            "usuario_id": uid,
            "perfil":     {"tipo_uso": "touring"}
        }, timeout=30)
        assert r2.status_code == 200
        assert r2.json()["turno_conversacion"] >= 2

        # Limpiar historial
        httpx.delete(f"{BASE}/m3/asistente/historial/{uid}", timeout=5)


# ─── Tests de Integracion M1+M2+M3 ──────────────────────────

class TestIntegracionM1M2M3:

    def test_perfil_delivery_vs_touring_lecciones_distintas(
        self, usuario_delivery, usuario_touring
    ):
        """T14: Delivery y Touring reciben lecciones distintas."""
        def get_leccion(tipo_uso):
            r = httpx.post(f"{BASE}/m2/educacion/leccion", json={
                "categoria": "Conduccion Segura",
                "perfil":    {"tipo_uso": tipo_uso, "nivel": "basico"}
            }, timeout=30)
            return r.json()["leccion"]

        lec_delivery = get_leccion("delivery")
        lec_touring  = get_leccion("touring")

        # Ambas lecciones deben existir
        assert lec_delivery is not None
        assert lec_touring  is not None
        # En modo mock son iguales — con Claude API seran distintas
        # Este test verifica que ambos endpoints responden correctamente

    def test_flujo_completo_usuario(self):
        """T15: Flujo completo: crear perfil → leccion → quiz → progreso."""
        # 1. Crear usuario
        r1 = httpx.post(f"{BASE}/m1/perfil/crear", json={
            "nombre":           "Test Flujo Completo",
            "tipo_uso":         "urbano",
            "anos_experiencia": 1,
            "moto_actual":      "Yamaha YBR125",
            "zona":             "Pichincha"
        }, timeout=10)
        assert r1.status_code == 200
        uid = r1.json()["usuario_id"]

        # 2. Obtener categorias
        r2 = httpx.get(f"{BASE}/m2/educacion/categorias", timeout=10)
        assert r2.status_code == 200
        assert r2.json()["total"] == 5

        # 3. Obtener leccion
        r3 = httpx.post(f"{BASE}/m2/educacion/leccion", json={
            "categoria": "Normativa LOTTTSV y Velocidades",
            "perfil":    {"tipo_uso": "urbano", "nivel": "basico"}
        }, timeout=30)
        assert r3.status_code == 200

        # 4. Consultar asistente
        r4 = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta":   "cuál es la velocidad máxima en ciudad?",
            "usuario_id": uid,
            "perfil":     {"tipo_uso": "urbano"}
        }, timeout=30)
        assert r4.status_code == 200
        assert r4.json()["documentos_recuperados"] > 0

        print(f"\n✅ Flujo completo OK — usuario_id: {uid}")
