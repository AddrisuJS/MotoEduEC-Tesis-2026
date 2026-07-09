"""
Tests de Integracion Sprint 3 — M4 + M5 + M6 + M7
MotoEdu EC — UPS Cuenca 2026
Ejecutar: python -m pytest tests/test_integracion_s3.py -v
"""
import pytest
import httpx

BASE = "http://localhost:8010"


# ─── Tests M4 — Recomendador de Motos ────────────────────────

class TestM4Motos:

    def test_catalogo_retorna_motos(self):
        """T01: El catalogo devuelve las 48 motos cargadas."""
        r = httpx.get(f"{BASE}/m4/motos/catalogo", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 40
        assert len(data["motos"]) >= 40

    def test_catalogo_filtro_tipo(self):
        """T02: El filtro por tipo funciona correctamente."""
        r = httpx.get(f"{BASE}/m4/motos/catalogo?tipo=Utilitaria", timeout=10)
        assert r.status_code == 200
        motos = r.json()["motos"]
        assert len(motos) > 0
        for moto in motos:
            assert "utilitaria" in moto["tipo"].lower()

    def test_catalogo_filtro_marca(self):
        """T03: El filtro por marca funciona correctamente."""
        r = httpx.get(f"{BASE}/m4/motos/catalogo?marca=Honda", timeout=10)
        assert r.status_code == 200
        motos = r.json()["motos"]
        assert len(motos) > 0
        for moto in motos:
            assert "honda" in moto["marca"].lower()

    def test_recomendar_delivery_presupuesto_bajo(self):
        """T04: Recomendacion para Delivery con presupuesto $2500 devuelve motos utilitarias."""
        r = httpx.post(f"{BASE}/m4/motos/recomendar", json={
            "perfil": {
                "tipo_uso": "delivery",
                "anos_experiencia": 1,
                "presupuesto_max": 2500,
                "zona": "Guayas"
            }
        }, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["catalogo_consultado"] > 0
        assert "Utilitaria" in data["tipos_buscados"]
        assert len(data["recomendaciones"]) == 3

    def test_recomendar_touring_presupuesto_alto(self):
        """T05: Recomendacion para Touring con presupuesto alto devuelve motos adventure."""
        r = httpx.post(f"{BASE}/m4/motos/recomendar", json={
            "perfil": {
                "tipo_uso": "touring",
                "anos_experiencia": 5,
                "presupuesto_max": 15000,
                "zona": "Sierra"
            }
        }, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["catalogo_consultado"] > 0
        tipos = data["tipos_buscados"]
        assert any("Adventure" in t or "Touring" in t for t in tipos)

    def test_marcas_disponibles(self):
        """T06: El endpoint de marcas devuelve las marcas cargadas."""
        r = httpx.get(f"{BASE}/m4/motos/marcas", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 8
        marcas = [m["nombre"] for m in data["marcas"]]
        assert "Honda" in marcas
        assert "Yamaha" in marcas
        assert "KTM" in marcas


# ─── Tests M5 — Recomendador de Llantas ──────────────────────

class TestM5Llantas:

    def test_recomendar_utilitaria_lluvia(self):
        """T07: Utilitaria en lluvia recomienda llantas tipo Lluvia/Rain."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "utilitaria",
            "uso": "ciudad",
            "clima": "lluvia",
            "gama": "alta",
            "presupuesto_max": 200
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["tipo_llanta_recomendada"] == "Lluvia/Rain"
        assert len(data["alerta_seguridad"]) > 10
        assert "consejo" in data

    def test_recomendar_deportiva_seco(self):
        """T08: Deportiva en seco recomienda llantas Sport o Carretera."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "deportiva",
            "uso": "carretera",
            "clima": "seco",
            "gama": "alta",
            "presupuesto_max": 300
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["tipo_llanta_recomendada"] in ["Sport", "Carretera (Road)"]

    def test_recomendar_enduro_offroad(self):
        """T09: Enduro en offroad recomienda llantas Off-road."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "enduro",
            "uso": "offroad",
            "clima": "variado",
            "gama": "alta",
            "presupuesto_max": 200
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["tipo_llanta_recomendada"] == "Off-road/Enduro"

    def test_alerta_seguridad_presente(self):
        """T10: Siempre hay una alerta de seguridad en la respuesta."""
        r = httpx.post(f"{BASE}/m5/llantas/recomendar", json={
            "tipo_moto": "scooter",
            "uso": "ciudad",
            "clima": "seco",
            "gama": "economica",
            "presupuesto_max": 50
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "alerta_seguridad" in data
        assert len(data["alerta_seguridad"]) > 20

    def test_catalogo_llantas(self):
        """T11: El catalogo de llantas devuelve las 16 llantas."""
        r = httpx.get(f"{BASE}/m5/llantas/catalogo", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 14


# ─── Tests M6 — Historia ─────────────────────────────────────

class TestM6Historia:

    def test_listar_temas(self):
        """T12: El endpoint devuelve exactamente 6 temas historicos."""
        r = httpx.get(f"{BASE}/m6/historia/temas", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert len(data["temas"]) == 6

    def test_obtener_narrativa_tema_1(self):
        """T13: El tema 1 genera una narrativa (mock o real)."""
        r = httpx.get(f"{BASE}/m6/historia/1", timeout=30)
        assert r.status_code == 200
        data = r.json()
        assert "contenido" in data
        assert data["tema"]["id"] == 1

    def test_contribuir_historia(self):
        """T14: POST /contribuir guarda la historia correctamente."""
        r = httpx.post(f"{BASE}/m6/historia/contribuir", json={
            "nombre":   "Test Usuario",
            "ciudad":   "Cuenca",
            "anio":     "2010",
            "historia": "Mi primera moto fue una Yamaha YBR125. La compre para ir al trabajo."
        }, timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["estado"] == "pendiente_revision"
        assert data["total_contribuciones"] >= 1
        assert "id" in data

    def test_listar_contribuciones(self):
        """T15: GET /contribuciones/lista devuelve las contribuciones enviadas."""
        # Primero enviar una
        httpx.post(f"{BASE}/m6/historia/contribuir", json={
            "nombre": "Test Lista", "ciudad": "Quito",
            "anio": "2015", "historia": "Tuve mi primera caida en lluvia."
        }, timeout=10)
        r = httpx.get(f"{BASE}/m6/historia/contribuciones/lista", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1


# ─── Tests M7 — Gamificacion ─────────────────────────────────

class TestM7Gamificacion:

    def test_insignias_completas(self):
        """T16: El sistema devuelve exactamente 12 insignias."""
        r = httpx.get(f"{BASE}/m7/gamificacion/insignias", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 12
        # Verificar que tienen todos los campos
        for ins in data["insignias"]:
            assert "nombre" in ins
            assert "puntos" in ins
            assert "icono" in ins

    def test_niveles_completos(self):
        """T17: El sistema devuelve exactamente 5 niveles."""
        r = httpx.get(f"{BASE}/m7/gamificacion/niveles", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert len(data["niveles"]) == 5
        nombres = [n["nombre"] for n in data["niveles"]]
        assert "Principiante" in nombres
        assert "Experto Vial" in nombres


# ─── Tests Dashboard ─────────────────────────────────────────

class TestDashboard:

    def test_dashboard_retorna_metricas(self):
        """T18: GET /estadisticas/dashboard devuelve todas las metricas."""
        r = httpx.get(f"{BASE}/estadisticas/dashboard", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert "resumen" in data
        assert "distribucion_perfiles" in data
        assert "preguntas_por_categoria" in data
        assert "brechas_top" in data
        assert data["resumen"]["total_motos"] == 48
        assert data["resumen"]["total_preguntas"] == 200

    def test_brechas_sin_duplicados(self):
        """T19: Las brechas no tienen duplicados."""
        r = httpx.get(f"{BASE}/estadisticas/dashboard", timeout=10)
        assert r.status_code == 200
        brechas = r.json()["brechas_top"]
        descripciones = [b["descripcion"] for b in brechas]
        assert len(descripciones) == len(set(descripciones)), "Hay brechas duplicadas"

    def test_preguntas_por_categoria(self):
        """T20: Hay preguntas en todas las categorias."""
        r = httpx.get(f"{BASE}/estadisticas/dashboard", timeout=10)
        assert r.status_code == 200
        cats = r.json()["preguntas_por_categoria"]
        assert len(cats) == 7
        for cat in cats:
            assert cat["total"] > 0
