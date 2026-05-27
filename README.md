# 🏍️ MotoEdu EC — Tesis 2026

**Universidad Politécnica Salesiana — Sede Cuenca**  
**Carrera de Ingeniería de Sistemas**

> Plataforma inteligente basada en IA Generativa para la educación vial personalizada, recomendación responsable de motocicletas y preservación de la cultura motera ecuatoriana.

**Estudiante:** Sanango Romero José Addrisu — jsanangor@est.ups.edu.ec  
**Tutor:** Omar Gustavo Bravo Quezada Ph.D — obravo@ups.edu.ec  
**Periodo:** 26 mayo al 14 julio 2026 · 400 horas · 6 Sprints

---

## 🚀 Levantar el proyecto

```bash
git clone https://github.com/AddrisuJS/MotoEduEC-Tesis-2026
cd MotoEduEC-Tesis-2026
copy .env.example .env
docker-compose up -d
```

| Servicio | URL | Descripción |
|---------|-----|-------------|
| **Frontend Next.js** | http://localhost:3000 | Interfaz de la plataforma |
| **API + Swagger** | http://localhost:8001/docs | 7 módulos documentados |
| **pgAdmin** | http://localhost:5051 | Administrador PostgreSQL |
| **PostgreSQL** | localhost:5433 | Base de datos |
| **ChromaDB** | http://localhost:8002 | Base vectorial RAG |

---

## 📦 Los 7 Módulos

| M | Módulo | Endpoint | Estado |
|---|--------|---------|--------|
| M1 | Perfil Inteligente | `/m1/perfil` | ✅ |
| M2 | Educación Vial con IA | `/m2/educacion` | ✅ Mock / 🔄 Claude API |
| M3 | Asistente RAG | `/m3/asistente` | ✅ Mock / 🔄 Claude API |
| M4 | Recomendador Motos | `/m4/motos` | ✅ Mock / 🔄 Claude API |
| M5 | Recomendador Llantas | `/m5/llantas` | ✅ |
| M6 | Historia Motera | `/m6/historia` | ✅ Mock / 🔄 Claude API |
| M7 | Gamificación | `/m7/gamificacion` | ✅ |

> **Mock:** funciona sin Claude API  
> **Claude API:** agregar `CLAUDE_API_KEY` en `.env` para activar IA real

---

## 🛠️ Stack Tecnológico

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Next.js | 14 | Frontend React |
| FastAPI | 0.115 | API REST backend |
| PostgreSQL | 16 | Base de datos relacional |
| ChromaDB | 1.5.9 | Base vectorial RAG |
| Claude API | Sonnet/Haiku | IA Generativa |
| Docker | 29+ | Contenedores |

---

## 📅 Sprints

| Sprint | Período | Horas | Entregable |
|--------|---------|-------|-----------|
| S1 | 26 may – 04 jun | 80h | Arquitectura + entorno + Claude API |
| S2 | 05 – 16 jun | 96h | M1 + M2 + M3 |
| S3 | 17 – 26 jun | 80h | M4 + M5 + M6 + M7 |
| S4 | 27 jun – 04 jul | 64h | Integración + RAGAS |
| S5 | 05 – 11 jul | 56h | Piloto 30+ usuarios |
| S6 | 12 – 14 jul | 24h | Documento final |

---

*MotoEdu EC · Tesis UPS Cuenca 2026*
