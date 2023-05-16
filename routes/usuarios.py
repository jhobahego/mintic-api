from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext
from typing import List

from models.Usuario import Usuario, ActualizarUsuario, Role
from config.db import conn
from auth.autenticacion import esquema_oauth
from auth.services import usuario_rol_requerido

usuario = APIRouter()

contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_contra(contra):
    return contexto_pwd.hash(contra)

@usuario.get("/usuarios", response_description="Usuarios listados", response_model=List[Usuario])
async def obtener_usuarios():
    usuarios = await conn["usuarios"].find().to_list(1000)
    return usuarios


# @usuario.get("/usuarios/{usuario_id}", response_description="usuario listado", response_model=Usuario)
# async def obtener_usuario_por_id(usuario_id: str, token: str = Depends(esquema_oauth)):
    if (usuario := await conn["usuarios"].find_one({"_id": usuario_id})) is not None:
        return usuario

    raise HTTPException(
        status_code=404, detail=f"Usuario con id {usuario_id} no encontrado")


@usuario.get("/usuarios/nombre/{nombre_usuario}", response_description="Usuario obtenido", response_model=Usuario)
async def obtener_usuario_por_nombre(nombre_usuario: str, token: str = Depends(esquema_oauth)):
    if (usuario := await conn["usuarios"].find_one({"nombres": nombre_usuario})) is not None:
        return usuario

    raise HTTPException(
        status_code=404, detail=f"Usuario {nombre_usuario} no encontrado")


@usuario.post("/usuarios/guardar", response_description="Usuario guardado", response_model=Usuario)
async def guardar_usuario(usuario: Usuario = Body(...)):
    usuarios = await obtener_usuarios()
    if any(u["correo"] == usuario.correo for u in usuarios):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correo ya registrado"
        )

    if len(usuarios) < 3:
        usuario.rol = Role.ADMIN

    usuario.contra = hashear_contra(usuario.contra)
    usuario = jsonable_encoder(usuario)

    nuevo_usuario = await conn["usuarios"].insert_one(usuario)
    usuario_creado = await conn["usuarios"].find_one({"_id": nuevo_usuario.inserted_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=usuario_creado)

@usuario.put("/usuarios/actualizar/{usuario_id}", response_description="Usuario actualizado", response_model=Usuario, dependencies=[Depends(usuario_rol_requerido)])
async def actualizar_usuario(usuario_id: str, usuario: ActualizarUsuario = Body(...), token: str = Depends(esquema_oauth)):
    usuario = {datos: valor for datos, valor in usuario.dict().items()
               if valor is not None}
    if len(usuario) >= 1:
        update_result = await conn["usuarios"].update_one({"_id": usuario_id}, {"$set": usuario})

        if update_result.modified_count == 1:
            if (
                usuario_actualizado := await conn["usuarios"].find_one({"_id": usuario_id})
            ) is not None:
                return usuario_actualizado

    if (usuario_existente := await conn["usuarios"].find_one({"_id": usuario_id})) is not None:
        return usuario_existente

    raise HTTPException(
        status_code=404, detail=f"usuario con id: {usuario_id} no encontrado")


@usuario.delete("/usuarios/eliminar/{usuario_id}", response_description="usuario eliminado", dependencies=[Depends(usuario_rol_requerido)])
async def eliminar_usuario_por_id(usuario_id: str, token: str = Depends(esquema_oauth)):
    usuario_eliminado = await conn["usuarios"].delete_one({"_id": usuario_id})
    if usuario_eliminado.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404, detail=f"usuario con id {usuario_id} no encontrado")
