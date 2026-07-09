# INSTALACIÓN DEL LOGIN — 6 pasos (~15 min)

## 1. Copiar archivos
```
backend/routers/auth.py          → C:\Tesis\motoeduc-tesis\backend\routers\auth.py
backend/db/migration_usuarios_auth.sql → C:\Tesis\motoeduc-tesis\backend\db\
frontend/app/login/              → C:\Tesis\motoeduc-tesis\frontend\app\login\
frontend/app/registro/           → C:\Tesis\motoeduc-tesis\frontend\app\registro\
frontend/lib/useAuth.ts          → C:\Tesis\motoeduc-tesis\frontend\lib\useAuth.ts   (crea la carpeta lib si no existe)
```

## 2. Dependencias del backend
Agrega estas 2 líneas a `backend/requirements.txt`:
```
pyjwt
bcrypt
```

## 3. Registrar el router
En `backend/main.py` agrega junto a los otros routers:
```python
from routers import auth
app.include_router(auth.router)
```

## 4. Crear las tablas
```powershell
docker exec -i motoeduc_tesis_postgres psql -U motoeduc_user -d motoeduc_tesis < backend\db\migration_usuarios_auth.sql
```

## 5. Reconstruir la API (por las dependencias nuevas)
```powershell
cd C:\Tesis\motoeduc-tesis
docker-compose build api
docker-compose up -d api
```

## 6. Probar
- Swagger: http://localhost:8010/docs → verás la sección **Autenticación** con /auth/registro, /auth/login, /auth/me
- Frontend: http://localhost:3000/registro → crea una cuenta → te lleva a /perfil
- http://localhost:3000/login → inicia sesión

## Proteger las páginas existentes (opcional pero recomendado)
En cada página (perfil, educacion, asistente, etc.) agrega al inicio del componente:
```tsx
import { useAuth } from "../../lib/useAuth"
// dentro del componente:
const { usuario, listo, cerrarSesion } = useAuth()
if (!listo || !usuario) return null
```
Y usa `{usuario.nombre}` para personalizar el saludo y `cerrarSesion` en un botón "Salir".

## Proteger endpoints del backend (opcional)
```python
from routers.auth import usuario_actual
@router.get("/algo")
def algo(usuario = Depends(usuario_actual)):
    ...
```
