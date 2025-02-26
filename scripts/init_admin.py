import asyncio
import sys
import os
import motor.motor_asyncio
from passlib.context import CryptContext
from decouple import config

# Configuración para hashear contraseñas
contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de la base de datos
mongodb_url = config("MONGODB_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
db = client.misiontic

# Roles permitidos
ROLE_ADMIN = "ADMIN"
ROLE_USER = "USER"

async def crear_admin_si_no_existe():
    # Verificar si ya existe un usuario administrador
    admin_existente = await db["usuarios"].find_one({"rol": ROLE_ADMIN})
    
    if admin_existente:
        print("Ya existe un usuario administrador en el sistema.")
        return
    
    # Datos del administrador por defecto
    admin_email = os.environ.get("ADMIN_EMAIL") or "admin@sistema.com"
    admin_password = os.environ.get("ADMIN_PASSWORD") or "Admin123!"
    
    # Verificar si el correo ya está en uso
    usuario_existente = await db["usuarios"].find_one({"correo": admin_email})
    if usuario_existente:
        print(f"El correo {admin_email} ya está en uso. No se creó el administrador.")
        return
    
    # Crear el objeto de usuario administrador
    nuevo_admin = {
        "nombres": "Administrador",
        "apellidos": "Sistema",
        "correo": admin_email,
        "contra": contexto_pwd.hash(admin_password),
        "pais": "Colombia",
        "ciudad": "Bogotá",
        "inactivo": False,
        "rol": ROLE_ADMIN
    }
    
    # Insertar el usuario administrador
    result = await db["usuarios"].insert_one(nuevo_admin)
    
    if result.inserted_id:
        print(f"Usuario administrador creado exitosamente con el correo: {admin_email}")
        print("IMPORTANTE: Cambia la contraseña por defecto después del primer inicio de sesión.")
    else:
        print("Error al crear el usuario administrador.")

async def main():
    print("Iniciando script de creación de usuario administrador...")
    await crear_admin_si_no_existe()
    print("Script finalizado.")

if __name__ == "__main__":
    asyncio.run(main())
