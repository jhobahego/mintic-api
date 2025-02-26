import asyncio
import argparse
import motor.motor_asyncio
from passlib.context import CryptContext
from decouple import config
import sys

# Configuración para hashear contraseñas
contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de la base de datos
mongodb_url = config("MONGODB_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
db = client.misiontic

# Roles permitidos
ROLE_ADMIN = "ADMIN"

async def crear_admin(nombres, apellidos, correo, contra, pais, ciudad):
    # Verificar si el correo ya está en uso
    usuario_existente = await db["usuarios"].find_one({"correo": correo})
    if usuario_existente:
        print(f"Error: El correo {correo} ya está en uso.")
        return False
    
    # Crear el objeto de usuario administrador
    nuevo_admin = {
        "nombres": nombres,
        "apellidos": apellidos,
        "correo": correo,
        "contra": contexto_pwd.hash(contra),
        "pais": pais,
        "ciudad": ciudad,
        "inactivo": False,
        "rol": ROLE_ADMIN
    }
    
    # Insertar el usuario administrador
    result = await db["usuarios"].insert_one(nuevo_admin)
    
    if result.inserted_id:
        print(f"Usuario administrador creado exitosamente con el correo: {correo}")
        return True
    else:
        print("Error al crear el usuario administrador.")
        return False

async def main():
    parser = argparse.ArgumentParser(description="Crear un usuario administrador para el sistema.")
    parser.add_argument("--nombres", required=True, help="Nombres del administrador")
    parser.add_argument("--apellidos", required=True, help="Apellidos del administrador")
    parser.add_argument("--correo", required=True, help="Correo electrónico del administrador")
    parser.add_argument("--contra", required=True, help="Contraseña del administrador")
    parser.add_argument("--pais", default="Colombia", help="País del administrador")
    parser.add_argument("--ciudad", default="Bogotá", help="Ciudad del administrador")
    
    args = parser.parse_args()
    
    result = await crear_admin(
        args.nombres, 
        args.apellidos, 
        args.correo, 
        args.contra,
        args.pais,
        args.ciudad
    )
    
    if not result:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
