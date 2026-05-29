# 🏍️ MotoEdu EC — Plataforma Inteligente de Educación Vial

**Universidad Politécnica Salesiana — Cuenca 2026**  
**Estudiante:** Sanango Romero José Addrisu (jsanangor@est.ups.edu.ec)  
**Tutor:** Omar Gustavo Bravo Quezada Ph.D  
**Entrega:** 15 julio 2026

---

## 📋 Descripción

MotoEdu EC es una plataforma digital de educación vial para motociclistas ecuatorianos que combina:

- **IA Generativa** (Claude API de Anthropic) para contenido personalizado
- **RAG Pipeline** (ChromaDB + Claude Sonnet) para consultas sobre la LOTTTSV
- **Gamificación** con 12 insignias y 5 niveles de competencia vial
- **Catálogo real** de 48 motocicletas y 16 llantas del mercado ecuatoriano

### El problema
Ecuador vendió **274.729 motos en 2025** (récord histórico) pero en 2024 murieron **685 motociclistas** en accidentes. El 60% desconoce la velocidad máxima urbana (50 km/h).

---

## 🚀 Levantar el sistema en 4 comandos

```bash
git clone https://github.com/AddrisuJS/MotoEduEC-Tesis-2026.git
cd MotoEduEC-Tesis-2026
copy .env.example .env
docker-compose up -d
```

### Servicios disponibles

| Servicio | URL | Descripción |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Dashboard con 7 módulos |
| API + Swagger | http://localhost:8010/docs | 7 módulos documentados |
| pgAdmin | http://localhost:5051 | Administrador PostgreSQL |
| PostgreSQL | localhost:5434 | 14 tablas + datos reales |
| ChromaDB | http://localhost:8003 | 200 documentos vectoriales |

### Credenciales
```
PostgreSQL: motoeduc_user / MotoEduC_2026$
pgAdmin:    jsanangor@est.ups.edu.ec / MotoEduC_2026$
```

---

## ⚙️ Configuración de Claude API (opcional)

Sin API Key el sistema funciona en modo mock. Para activar IA real:

1. Obtener API Key en [console.anthropic.com](https://console.anthropic.com)
2. Editar `.env`:
```
CLAUDE_API_KEY=sk-ant-api03-TU_KEY_AQUI
```
3. Reiniciar la API:
```bash
docker-compose stop api
docker-compose start api
```

---

## 🏗️ Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Frontend | Next.js + TypeScript | 14.2.5 |
| Backend | FastAPI + Python | 0.115 / 3.11 |
| Base de datos | PostgreSQL | 16 |
| Base vectorial | ChromaDB | 1.5.9 |
| IA Generativa | Claude API (Anthropic) | claude-sonnet-4-5 |
| Contenedores | Docker Compose | 29.5.2 |

---

## 📦 Cargar datos iniciales

```bash
# Cargar preguntas viales + brechas + categorías
python seed_tesis.py

# Cargar catálogo de motos y llantas
python seed_catalogo_tesis.py
```

---

## 🧪 Ejecutar Tests

```bash
# Tests integración Sprint 2 (15 tests - M1+M2+M3)
python -m pytest tests/test_integracion_s2.py -v

# Tests integración Sprint 3 (20 tests - M4+M5+M6+M7+Dashboard)
python -m pytest tests/test_integracion_s3.py -v

# Tests E2E Sprint 4 (30 tests - flujos completos)
python -m pytest tests/test_e2e_s4.py -v

# Evaluación RAGAS (20 preguntas - requiere Claude API Key)
python tests/ragas_eval.py

# Evaluación RAGAS formal (55 preguntas)
python tests/ragas_eval_50.py

# Demo pretest-postest estadístico
python tests/pretest_postest.py --modo demo
```

### Resultados de tests

| Suite | Tests | Resultado | Tiempo |
|-------|-------|-----------|--------|
| Sprint 2 — M1+M2+M3 | 15/15 | ✅ PASS | 7.48s |
| Sprint 3 — M4+M5+M6+M7 | 20/20 | ✅ PASS | 8.17s |
| Sprint 4 — E2E completo | 30/30 | ✅ PASS | 23.74s |
| **TOTAL** | **65/65** | **✅ PASS** | **39.39s** |

### Resultados RAGAS

| Ejecución | Preguntas | Faithfulness | Pass |
|-----------|-----------|-------------|------|
| Baseline MOCK | 20 | 0.120 | ❌ |
| Claude API k=10 | 20 | 0.888 | ✅ |
| RAGAS Formal | 55 | 0.889 | ✅ |

---

## 📱 Los 7 Módulos

| Módulo | URL | Descripción |
|--------|-----|-------------|
| M1 Perfil | /perfil | Onboarding 5 pasos — 6 perfiles de motociclista |
| M2 Educación | /educacion | Lecciones + quizzes personalizados con Claude API |
| M3 Asistente RAG | /asistente | Chat sobre LOTTTSV con ChromaDB + Claude Sonnet |
| M4 Motos | /motos | Recomendador de 48 modelos reales Ecuador |
| M5 Llantas | /llantas | Recomendador con alertas de severidad |
| M6 Historia | /historia | Timeline 1900-2026 + contribuciones comunitarias |
| M7 Gamificación | /gamificacion | 12 insignias + 5 niveles de competencia |
| Dashboard | /dashboard | Panel analítico para Edutainment |

---

## 📊 Datos del sistema

- **48 motocicletas** de 8 marcas (Honda, Yamaha, Kawasaki, KTM, Royal Enfield, Bajaj, Shineray, Daytona)
- **16 llantas** de 10 marcas (Michelin, Pirelli, Bridgestone, Dunlop, Maxxis, etc.)
- **200 preguntas viales** sobre LOTTTSV verificadas
- **8 brechas** de conocimiento identificadas
- **14 tablas** en PostgreSQL

---

## 🗂️ Estructura del proyecto

```
motoeduc-tesis/
├── backend/
│   ├── main.py                 # FastAPI — 7 módulos
│   ├── routers/                # M1-M7 + estadísticas
│   ├── services/
│   │   └── claude_service.py   # Wrapper Claude API
│   └── models/
│       └── database.py         # Conexión PostgreSQL
├── frontend/
│   └── app/                    # 9 páginas Next.js
├── tests/
│   ├── test_integracion_s2.py  # 15 tests Sprint 2
│   ├── test_integracion_s3.py  # 20 tests Sprint 3
│   ├── test_e2e_s4.py          # 30 tests E2E Sprint 4
│   ├── ragas_eval.py           # RAGAS 20 preguntas
│   ├── ragas_eval_50.py        # RAGAS 55 preguntas
│   └── pretest_postest.py      # Análisis estadístico
├── seed_tesis.py               # Carga preguntas + brechas
├── seed_catalogo_tesis.py      # Carga motos + llantas
├── docker-compose.yml
└── .env.example
```

---

## 📈 Estado del proyecto

| Sprint | Periodo | Tests | Estado |
|--------|---------|-------|--------|
| S1 — Arquitectura | 26 may - 4 jun | — | ✅ Completo |
| S2 — M1+M2+M3 | 5 - 16 jun | 15/15 | ✅ Completo |
| S3 — M4-M7+Dashboard | 17 - 26 jun | 20/20 | ✅ Completo |
| S4 — E2E + RAGAS | 27 jun - 4 jul | 30/30 | ✅ Completo |
| S5 — Piloto usuarios | 5 - 11 jul | — | ⏳ Pendiente |
| S6 — Documento final | 12 - 14 jul | — | ⏳ Pendiente |

**Entrega al Consejo de Carrera: 15 julio 2026**

---

## 👥 Créditos

- **Estudiante:** Sanando Romero José Addrisu — jsanangor@est.ups.edu.ec
- **Tutor:** Omar Gustavo Bravo Quezada Ph.D — obravo@ups.edu.ec
- **Institución:** Universidad Politécnica Salesiana — Cuenca
- **Empresa colaboradora:** Edutainment Ecuador
