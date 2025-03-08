from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes.usuarios import usuario, hashear_contra
from routes.documentos import documento
from routes.registros import registro
from routes.imagenes import imagenes
from routes.ia import ia
from routes.integraciones import integracion
from routes.notificaciones import notificaciones
from config.db import conn
from models.Usuario import Role

from auth.autenticacion import auth

from decouple import config

app = FastAPI(
    title="Sistema de Gestión Documental API",
    description="API para el sistema de gestión documental con funcionalidades avanzadas de IA y análisis",
    version="2.0.0"
)

app.include_router(usuario)
app.include_router(documento)
app.include_router(registro)
app.include_router(imagenes)
app.include_router(ia)
app.include_router(integracion)
app.include_router(notificaciones)
app.include_router(auth)

# PRODUCTION_URL = config("PRODUCTION_URL")
DEVELOPT_URL = config("DEVELOPMENT_FRONT")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[DEVELOPT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para inicializar el administrador si no existe
async def init_admin():
    # Verificar si existe algún usuario administrador
    admin_existente = await conn["usuarios"].find_one({"rol": Role.ADMIN})
    
    if admin_existente:
        print("Ya existe un usuario administrador en el sistema.")
        return
    
    # Datos del administrador por defecto
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    
    if not admin_email or not admin_password:
        print("No se ha configurado el correo o la contraseña del administrador.")
        return

    # Crear el administrador
    nuevo_admin = {
        "nombres": "Administrador",
        "apellidos": "Sistema",
        "correo": admin_email,
        "contra": hashear_contra(admin_password),
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "inactivo": False,
        "rol": Role.ADMIN
    }
    
    # Insertar el administrador
    await conn["usuarios"].insert_one(nuevo_admin)
    print(f"Usuario administrador creado con el correo: {admin_email}")
    print("IMPORTANTE: Cambia la contraseña por defecto después del primer inicio de sesión.")

@app.on_event("startup")
async def startup_event():
    # Verificar si se debe inicializar el administrador
    if os.environ.get("INIT_ADMIN", "False").lower() == "true":
        await init_admin()
