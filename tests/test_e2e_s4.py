"""
Suite de Pruebas E2E — Sprint 4
MotoEdu EC — UPS Cuenca 2026
30 casos de prueba cubriendo flujos completos de usuario

Ejecutar: python -m pytest tests/test_e2e_s4.py -v
"""
import pytest
import httpx
import time

BASE = "http://localhost:8010"


# ─── Fixtures globales ────────────────────────────────────────

@pytest.fixture(scope="module")
def usuario_e2e_delivery():
    r = httpx.post(f"{BASE}/m1/perfil/crear", json={
        "nombre": "E2E Delivery Cuenca", "tipo_uso": "delivery",
        "anos_experiencia": 1, "moto_actual": "Honda CB100",
        "cilindrada_cc": 100, "zona": "Guayas", "horas_uso_diario": 8,
        "objetivos": ["conocer normativa", "mejorar seguridad"]
    }, timeout=10)
    assert r.status_code == 200
    return r.json()

@pytest.fixture(scope="module")
def usuario_e2e_touring():
    r = httpx.post(f"{BASE}/m1/perfil/crear", json={
        "nombre": "E2E Touring Sierra", "tipo_uso": "touring",
        "anos_experiencia": 6, "moto_actual": "Yamaha Tenere 700",
        "cilindrada_cc": 689, "zona": "Sierra", "horas_uso_diario": 2,
        "objetivos": ["preparar viajes largos"]
    }, timeout=10)
    assert r.status_code == 200
    return r.json()

@pytest.fixture(scope="module")
def usuario_e2e_urbano():
    r = httpx.post(f"{BASE}/m1/perfil/crear", json={
        "nombre": "E2E Urbano Quito", "tipo_uso": "urbano",
        "anos_experiencia": 3, "moto_actual": "Bajaj NS160",
        "cilindrada_cc": 160, "zona": "Sierra", "horas_uso_diario": 1,
        "objetivos": ["mejorar seguridad en ciudad"]
    }, timeout=10)
    assert r.status_code == 200
    return r.json()


# ─── FLUJO 1: Onboarding completo ────────────────────────────

class TestFlujoOnboarding:

    def test_e01_crear_perfil_delivery(self, usuario_e2e_delivery):
        """E01: Crear perfil Delivery — clasificacion y system prompt."""
        assert usuario_e2e_delivery["perfil_key"] == "delivery"
        assert usuario_e2e_delivery["nivel_riesgo"] == "ALTO"
        assert len(usuario_e2e_delivery["equipamiento_minimo"]) >= 3
        assert "system_prompt_preview" in usuario_e2e_delivery

    def test_e02_crear_perfil_touring(self, usuario_e2e_touring):
        """E02: Crear perfil Touring — clasificacion correcta."""
        assert usuario_e2e_touring["perfil_key"] == "touring"
        assert usuario_e2e_touring["nivel"] == "avanzado"

    def test_e03_crear_perfil_urbano(self, usuario_e2e_urbano):
        """E03: Crear perfil Urbano — nivel intermedio."""
        assert usuario_e2e_urbano["perfil_key"] == "urbano"
        assert usuario_e2e_urbano["nivel"] == "intermedio"

    def test_e04_perfiles_distintos_equipamiento(self, usuario_e2e_delivery, usuario_e2e_touring):
        """E04: Delivery y Touring tienen equipamiento minimo diferente."""
        eq_delivery = " ".join(usuario_e2e_delivery["equipamiento_minimo"])
        eq_touring  = " ".join(usuario_e2e_touring["equipamiento_minimo"])
        assert eq_delivery != eq_touring

    def test_e05_usuario_guardado_bd(self, usuario_e2e_delivery):
        """E05: El usuario creado se puede recuperar de la BD."""
        uid = usuario_e2e_delivery["usuario_id"]
        r = httpx.get(f"{BASE}/m1/perfil/{uid}", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "error" not in data
        assert data["id"] == uid


# ─── FLUJO 2: Educacion completa ─────────────────────────────

class TestFlujoEducacion:

    def test_e06_categorias_disponibles(self):
        """E06: Las 5 categorias de educacion estan disponibles."""
        r = httpx.get(f"{BASE}/m2/educacion/categorias", timeout=10)
        assert r.status_code == 200
        assert r.json()["total"] == 5

    def test_e07_leccion_delivery(self, usuario_e2e_delivery):
        """E07: Delivery recibe leccion sobre normativa."""
        r = httpx.post(f"{BASE}/m2/educacion/leccion", json={
            "categoria": "Normativa LOTTTSV y Velocidades",
            "perfil": {"tipo_uso": "delivery", "nivel": "intermedio"}
        }, timeout=30)
        assert r.status_code == 200
        assert "leccion" in r.json()

    def test_e08_leccion_touring(self, usuario_e2e_touring):
        """E08: Touring recibe leccion sobre conduccion segura."""
        r = httpx.post(f"{BASE}/m2/educacion/leccion", json={
            "categoria": "Conduccion Segura",
            "perfil": {"tipo_uso": "touring", "nivel": "avanzado"}
        }, timeout=30)
        assert r.status_code == 200
        assert "leccion" in r.json()

    def test_e09_quiz_10_preguntas(self):
        """E09: El quiz genera exactamente 10 preguntas."""
        r = httpx.post(f"{BASE}/m2/educacion/quiz", json={
            "categoria": "Conduccion en Lluvia",
            "perfil": {"tipo_uso": "urbano", "nivel": "basico"},
            "n_preguntas": 10
        }, timeout=30)
        assert r.status_code == 200
        assert r.json()["total_preguntas"] == 10

    def test_e10_progreso_correcto_suma_puntos(self, usuario_e2e_urbano):
        """E10: Respuesta correcta suma 20 puntos al usuario."""
        uid = usuario_e2e_urbano["usuario_id"]
        r = httpx.post(f"{BASE}/m2/educacion/progreso", json={
            "usuario_id": uid, "pregunta_id": 1,
            "respuesta_dada": "50 km/h", "correcta": True,
            "tiempo_seg": 8, "categoria": "Normativa LOTTTSV y Velocidades"
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["correcta"] == True
        assert data["puntos_ganados"] == 20

    def test_e11_progreso_incorrecto_cero_puntos(self, usuario_e2e_delivery):
        """E11: Respuesta incorrecta da 0 puntos."""
        uid = usuario_e2e_delivery["usuario_id"]
        r = httpx.post(f"{BASE}/m2/educacion/progreso", json={
            "usuario_id": uid, "pregunta_id": 2,
            "respuesta_dada": "80 km/h", "correcta": False,
            "tiempo_seg": 15, "categoria": "Normativa LOTTTSV y Velocidades"
        }, timeout=10)
        assert r.status_code == 200
        assert r.json()["puntos_ganados"] == 0


# ─── FLUJO 3: Asistente RAG ───────────────────────────────────

class TestFlujoRAG:

    def test_e12_estado_rag_operativo(self):
        """E12: ChromaDB conectado con 200 documentos."""
        r = httpx.get(f"{BASE}/m3/asistente/estado", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["chromadb_conectado"] == True
        assert data["documentos_indexados"] == 200

    def test_e13_consulta_velocidad_recupera_docs(self, usuario_e2e_delivery):
        """E13: Consulta sobre velocidad recupera documentos relevantes."""
        r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta": "velocidad maxima zona urbana Ecuador",
            "usuario_id": usuario_e2e_delivery["usuario_id"],
            "perfil": {"tipo_uso": "delivery"}
        }, timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert data["documentos_recuperados"] >= 3
        assert len(data["respuesta"]) > 20

    def test_e14_consulta_casco_recupera_docs(self, usuario_e2e_urbano):
        """E14: Consulta sobre casco recupera documentos."""
        r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta": "obligatorio usar casco en Ecuador LOTTTSV",
            "usuario_id": usuario_e2e_urbano["usuario_id"],
            "perfil": {"tipo_uso": "urbano"}
        }, timeout=30)
        assert r.status_code == 200
        assert r.json()["documentos_recuperados"] > 0

    def test_e15_historial_3_turnos(self, usuario_e2e_touring):
        """E15: El historial se mantiene en 3 turnos consecutivos."""
        uid = usuario_e2e_touring["usuario_id"]
        preguntas = [
            "Que documentos necesito para manejar?",
            "Y el SOAT es obligatorio?",
            "Cuanto cuesta el SOAT?"
        ]
        for i, pregunta in enumerate(preguntas):
            r = httpx.post(f"{BASE}/m3/asistente/consultar", json={
                "pregunta": pregunta, "usuario_id": uid,
                "perfil": {"tipo_uso": "touring"}
            }, timeout=30)
            assert r.status_code == 200
            assert r.json()["turno_conversacion"] == i + 1
        httpx.delete(f"{BASE}/m3/asistente/historial/{uid}", timeout=5)


# ─── FLUJO 4: Recomendaciones ────────────────────────────────

class TestFlujoRecomendaciones:

    def test_e16_motos_delivery_utilitarias(self, usuario_e2e_delivery):
        """E16: Delivery con $2000 recibe motos utilitarias."""
        r = httpx.post(f"{BASE}/m4/motos/recomendar", json={
            "perfil": {"tipo_uso": "delivery", "anos_experiencia": 1,
                       "presupuesto_max": 2000, "zona": "Guayas"}
        }, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "Utilitaria" in data["tipos_buscados"]
        assert len(data["recomendaciones"]) == 3
        for rec in data["recomendaciones"]:
            assert rec["precio_usd"] <= 2000

    def test_e17_motos_touring_adventure(self, usuario_e2e_touring):
        """E17: Touring con $12000 recibe motos adventure/touring."""
        r = httpx.post(f"{BASE}/m4/motos/recomendar", json={
            "perfil": {"tipo_uso": "touring", "anos_experiencia": 6,
                       "presupuesto_max": 12000, "zona": "Sierra"}
        }, timeout=15)
        assert r.status_code == 200
        tipos = r.json()["tipos_buscados"]
        assert any("Adventure" in t or "Touring" in t for t in tipos)

    def test_e18_llantas_delivery_lluvia(self):
        """E18: Delivery en lluvia recibe llantas Lluvia/Rain."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "utilitaria", "uso": "ciudad",
            "clima": "lluvia", "gama": "media", "presupuesto_max": 120
        }, timeout=10)
        assert r.status_code == 200
        assert r.json()["tipo_llanta_recomendada"] == "Lluvia/Rain"

    def test_e19_llantas_touring_carretera(self):
        """E19: Touring en carretera recibe llantas Trail/Adventure."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "touring", "uso": "carretera",
            "clima": "variado", "gama": "alta", "presupuesto_max": 200
        }, timeout=10)
        assert r.status_code == 200
        assert r.json()["tipo_llanta_recomendada"] == "Trail/Adventure"

    def test_e20_alerta_sport_critico(self):
        """E20: Deportiva en seco recibe alerta CRITICO en Sport."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "deportiva", "uso": "carretera",
            "clima": "seco", "gama": "alta", "presupuesto_max": 300
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["alerta_seguridad"] is not None
        assert len(data["alerta_seguridad"]) > 20


# ─── FLUJO 5: Gamificacion y Dashboard ───────────────────────

class TestFlujoGamificacion:

    def test_e21_insignias_12_completas(self):
        """E21: Sistema tiene exactamente 12 insignias con puntos."""
        r = httpx.get(f"{BASE}/m7/gamificacion/insignias", timeout=10)
        assert r.status_code == 200
        insignias = r.json()["insignias"]
        assert len(insignias) == 12
        puntos_totales = sum(i["puntos"] for i in insignias)
        assert puntos_totales > 500

    def test_e22_niveles_5_ordenados(self):
        """E22: Los 5 niveles tienen puntos minimos crecientes."""
        r = httpx.get(f"{BASE}/m7/gamificacion/niveles", timeout=10)
        assert r.status_code == 200
        niveles = r.json()["niveles"]
        assert len(niveles) == 5
        for i in range(1, len(niveles)):
            assert niveles[i]["puntos_min"] > niveles[i-1]["puntos_min"]

    def test_e23_dashboard_datos_reales(self):
        """E23: El dashboard devuelve datos reales de la BD."""
        r = httpx.get(f"{BASE}/estadisticas/dashboard", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["resumen"]["total_motos"] == 48
        assert data["resumen"]["total_preguntas"] == 200
        assert data["resumen"]["total_brechas"] == 8

    def test_e24_brechas_ordenadas_por_porcentaje(self):
        """E24: Las brechas estan ordenadas por porcentaje descendente."""
        r = httpx.get(f"{BASE}/estadisticas/dashboard", timeout=10)
        assert r.status_code == 200
        brechas = r.json()["brechas_top"]
        for i in range(1, len(brechas)):
            assert brechas[i]["pct_con_brecha"] <= brechas[i-1]["pct_con_brecha"]

    def test_e25_otorgar_insignia(self, usuario_e2e_urbano):
        """E25: Se puede otorgar una insignia a un usuario."""
        uid = usuario_e2e_urbano["usuario_id"]
        r = httpx.post(f"{BASE}/m7/gamificacion/otorgar-insignia", json={
            "usuario_id": uid, "insignia_id": 1
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "insignia" in data
        assert data["puntos_ganados"] > 0


# ─── FLUJO 6: Integracion completa end-to-end ─────────────────

class TestFlujoCompleto:

    def test_e26_flujo_delivery_completo(self):
        """E26: Flujo completo Delivery: perfil->leccion->quiz->asistente->moto."""
        # 1. Crear perfil
        r1 = httpx.post(f"{BASE}/m1/perfil/crear", json={
            "nombre": "E2E Flujo Delivery", "tipo_uso": "delivery",
            "anos_experiencia": 2, "moto_actual": "Honda CB100",
            "zona": "Guayas", "horas_uso_diario": 8
        }, timeout=10)
        assert r1.status_code == 200
        uid = r1.json()["usuario_id"]

        # 2. Obtener leccion
        r2 = httpx.post(f"{BASE}/m2/educacion/leccion", json={
            "categoria": "Normativa LOTTTSV y Velocidades",
            "perfil": {"tipo_uso": "delivery", "nivel": "intermedio"}
        }, timeout=30)
        assert r2.status_code == 200

        # 3. Consultar asistente
        r3 = httpx.post(f"{BASE}/m3/asistente/consultar", json={
            "pregunta": "velocidad maxima en ciudad para delivery",
            "usuario_id": uid, "perfil": {"tipo_uso": "delivery"}
        }, timeout=30)
        assert r3.status_code == 200
        assert r3.json()["documentos_recuperados"] > 0

        # 4. Recomendar moto
        r4 = httpx.post(f"{BASE}/m4/motos/recomendar", json={
            "perfil": {"tipo_uso": "delivery", "presupuesto_max": 2000}
        }, timeout=15)
        assert r4.status_code == 200
        assert len(r4.json()["recomendaciones"]) == 3

    def test_e27_flujo_touring_completo(self):
        """E27: Flujo completo Touring: perfil->leccion->RAG->moto->llanta."""
        r1 = httpx.post(f"{BASE}/m1/perfil/crear", json={
            "nombre": "E2E Flujo Touring", "tipo_uso": "touring",
            "anos_experiencia": 5, "zona": "Sierra"
        }, timeout=10)
        uid = r1.json()["usuario_id"]

        r2 = httpx.post(f"{BASE}/m2/educacion/leccion", json={
            "categoria": "Conduccion Segura",
            "perfil": {"tipo_uso": "touring", "nivel": "avanzado"}
        }, timeout=30)
        assert r2.status_code == 200

        r3 = httpx.post(f"{BASE}/m4/motos/recomendar", json={
            "perfil": {"tipo_uso": "touring", "presupuesto_max": 10000, "zona": "Sierra"}
        }, timeout=15)
        assert r3.status_code == 200

        r4 = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "touring", "uso": "carretera",
            "clima": "variado", "gama": "alta", "presupuesto_max": 200
        }, timeout=10)
        assert r4.status_code == 200
        assert r4.json()["tipo_llanta_recomendada"] == "Trail/Adventure"

    def test_e28_historia_y_contribucion(self):
        """E28: Flujo historia: ver tema->contribuir->verificar lista."""
        r1 = httpx.get(f"{BASE}/m6/historia/temas", timeout=10)
        assert r1.status_code == 200
        assert len(r1.json()["temas"]) == 6

        r2 = httpx.get(f"{BASE}/m6/historia/4", timeout=30)
        assert r2.status_code == 200

        r3 = httpx.post(f"{BASE}/m6/historia/contribuir", json={
            "nombre": "E2E Test", "ciudad": "Cuenca",
            "anio": "2020", "historia": "Mi historia motera de prueba E2E."
        }, timeout=10)
        assert r3.status_code == 200
        assert r3.json()["estado"] == "pendiente_revision"

    def test_e29_sistema_estadisticas_completo(self):
        """E29: El sistema de estadisticas refleja datos reales."""
        r1 = httpx.get(f"{BASE}/estadisticas/resumen", timeout=10)
        assert r1.status_code == 200
        res = r1.json()["resumen"]
        assert res["motocicletas"] == 48
        assert res["preguntas_viales"] == 200
        assert res["brechas_conocimiento"] == 8

        r2 = httpx.get(f"{BASE}/estadisticas/brechas", timeout=10)
        assert r2.status_code == 200
        assert r2.json()["total"] == 8

    def test_e30_sistema_health_check(self):
        """E30: Todos los endpoints principales responden 200."""
        endpoints = [
            ("GET", f"{BASE}/"),
            ("GET", f"{BASE}/health"),
            ("GET", f"{BASE}/m1/perfil/perfiles"),
            ("GET", f"{BASE}/m2/educacion/categorias"),
            ("GET", f"{BASE}/m3/asistente/estado"),
            ("GET", f"{BASE}/m4/motos/marcas"),
            ("GET", f"{BASE}/m4/motos/tipos"),
            ("GET", f"{BASE}/m5/llantas/catalogo"),
            ("GET", f"{BASE}/m5/llantas/tipos"),
            ("GET", f"{BASE}/m6/historia/temas"),
            ("GET", f"{BASE}/m7/gamificacion/insignias"),
            ("GET", f"{BASE}/m7/gamificacion/niveles"),
            ("GET", f"{BASE}/estadisticas/resumen"),
            ("GET", f"{BASE}/estadisticas/brechas"),
            ("GET", f"{BASE}/estadisticas/dashboard"),
        ]
        fallidos = []
        for method, url in endpoints:
            try:
                r = httpx.get(url, timeout=10)
                if r.status_code != 200:
                    fallidos.append(f"{url} -> {r.status_code}")
            except Exception as e:
                fallidos.append(f"{url} -> ERROR: {e}")

        assert len(fallidos) == 0, f"Endpoints fallidos: {fallidos}"
