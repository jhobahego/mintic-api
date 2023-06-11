from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Union
from pydantic import EmailStr
from jose import jwt, JWTError
from datetime import timedelta, datetime
from passlib.context import CryptContext
from dotenv import load_dotenv

from models.Token import Token, TokenData
from models.Usuario import Usuario, UserResponse
from config.db import conn

import os

auth = APIRouter()
load_dotenv()


esquema_oauth = OAuth2PasswordBearer(tokenUrl="token")
contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

CLAVE = os.environ["CLAVE_SECRETA"]
ALGORITMO = "HS256"
TIEMPO_EN_MINUTOS_EXPIRACION_TOKEN = 60

def verificar_contra(contra, contra_hasheada):
    return contexto_pwd.verify(contra, contra_hasheada)

async def autenticar_usuario(correo: EmailStr, contra: str):
    usuario = await conn["usuarios"].find_one({"correo": correo})
    if usuario is None:
        return False
    if not verificar_contra(contra, usuario["contra"]):
        return False
    return usuario


def crear_access_token(datos: dict, expires_delta: Union[timedelta, None] = None):
    a_codificar = datos.copy()
    if expires_delta:
        expirar = datetime.utcnow() + expires_delta
    else:
        expirar = datetime.utcnow() + timedelta(minutes=15)

    a_codificar.update({"exp": expirar})
    jwt_codificado = jwt.encode(
        a_codificar, CLAVE, algorithm=ALGORITMO)
    return jwt_codificado


async def obtener_usuario(correo: EmailStr):
    return await conn["usuarios"].find_one({"correo": correo})


async def obtener_usuario_actual(token: str = Depends(esquema_oauth)):
    excepcion_de_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Las credenciales pueden no ser correctas",
        headers={"WWW-Autenticate": "Bearer"},
    )

    try:
        ejecutador = jwt.decode(token, CLAVE, algorithms=[ALGORITMO])
        correo: EmailStr = ejecutador.get("correo")
        if correo is None:
            raise excepcion_de_credenciales
        token_data = TokenData(correo=correo)
    except JWTError:
        raise excepcion_de_credenciales

    usuario = await obtener_usuario(correo=token_data.correo)

    if usuario is None:
        raise excepcion_de_credenciales

    return usuario


async def obtener_usuario_activo_actual(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    if usuario_actual["inactivo"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return usuario_actual


@auth.post("/token", response_model=Token)
async def generar_token(datos: OAuth2PasswordRequestForm = Depends()):
    usuario = await autenticar_usuario(datos.username, datos.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="correo electronico o contraseña incorrecta",
            headers={"WWW-Autenticate": "Bearer"},
        )
    expiracion_de_token = timedelta(minutes=TIEMPO_EN_MINUTOS_EXPIRACION_TOKEN)
    access_token = crear_access_token(
        datos={"correo": usuario["correo"]}, expires_delta=expiracion_de_token
    )
    return {"access_token": access_token, "tipo_token": "bearer"}


@auth.get("/usuarios/perfil", response_model=UserResponse)
async def obtener_perfil(usuario: Usuario = Depends(obtener_usuario_activo_actual)):
    return usuario