"""
Auth — MotoEdu EC
Registro, login y sesión con JWT + bcrypt
Sprint 5 — UPS Cuenca 2026
"""
import os, jwt, bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.database import get_db

SECRET = os.getenv("JWT_SECRET", "motoeduc_jwt_secret_2026_ups")
ALGO = "HS256"
TOKEN_HORAS = 72

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class RegistroIn(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=6, max_length=100)
    tipo_uso: str = "urbano"


class LoginIn(BaseModel):
    email: str
    password: str


def _crear_token(usuario_id: int, email: str, nombre: str) -> str:
    payload = {
        "sub": str(usuario_id), "email": email, "nombre": nombre,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HORAS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def usuario_actual(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Dependencia para proteger endpoints: Authorization: Bearer <token>"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Token requerido")
    try:
        payload = jwt.decode(authorization.split(" ", 1)[1], SECRET, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Sesión expirada, inicia sesión de nuevo")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token inválido")
    row = db.execute(text("SELECT id, nombre, email, tipo_uso, rol, COALESCE(grupo,'intervencion') FROM usuarios_auth WHERE id=:i"),
                     {"i": int(payload["sub"])}).fetchone()
    if not row:
        raise HTTPException(401, "Usuario no existe")
    return {"id": row[0], "nombre": row[1], "email": row[2], "tipo_uso": row[3], "rol": row[4], "grupo": (row[5] if len(row) > 5 else "intervencion")}


@router.post("/registro")
def registro(datos: RegistroIn, db: Session = Depends(get_db)):
    email = datos.email.strip().lower()
    if "@" not in email or "." not in email:
        raise HTTPException(400, "Email inválido")
    existe = db.execute(text("SELECT id FROM usuarios_auth WHERE email=:e"), {"e": email}).fetchone()
    if existe:
        raise HTTPException(409, "Ese email ya está registrado — inicia sesión")
    ph = bcrypt.hashpw(datos.password.encode(), bcrypt.gensalt()).decode()
    row = db.execute(text("""
        INSERT INTO usuarios_auth (nombre, email, password_hash, tipo_uso)
        VALUES (:n, :e, :p, :t) RETURNING id
    """), {"n": datos.nombre.strip(), "e": email, "p": ph, "t": datos.tipo_uso}).fetchone()
    db.commit()
    token = _crear_token(row[0], email, datos.nombre.strip())
    return {"ok": True, "token": token,
            "usuario": {"id": row[0], "nombre": datos.nombre.strip(), "email": email, "tipo_uso": datos.tipo_uso, "rol": "participante"},
            "siguiente_paso": "/perfil"}


@router.post("/login")
def login(datos: LoginIn, db: Session = Depends(get_db)):
    email = datos.email.strip().lower()
    row = db.execute(text("SELECT id, nombre, password_hash, tipo_uso, rol, COALESCE(grupo,'intervencion') FROM usuarios_auth WHERE email=:e"),
                     {"e": email}).fetchone()
    if not row or not bcrypt.checkpw(datos.password.encode(), row[2].encode()):
        raise HTTPException(401, "Email o contraseña incorrectos")
    db.execute(text("UPDATE usuarios_auth SET ultimo_login=NOW() WHERE id=:i"), {"i": row[0]})
    db.commit()
    token = _crear_token(row[0], email, row[1])
    return {"ok": True, "token": token,
            "usuario": {"id": row[0], "nombre": row[1], "email": email, "tipo_uso": row[3], "rol": row[4], "grupo": (row[5] if len(row) > 5 else "intervencion")}}


@router.get("/me")
def me(usuario=Depends(usuario_actual)):
    return {"ok": True, "usuario": usuario}
