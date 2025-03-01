from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext

from models.Usuario import Usuario, ActualizarUsuario, Role, UserResponse
from config.db import conn
from auth.autenticacion import esquema_oauth
from auth.services import usuario_admin_requerido
from utils.serializers import serialize_mongo_doc, serialize_mongo_docs, serialize_mongo_doc_filtered

usuario = APIRouter(tags=["Usuarios"])

contexto_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_contra(contra):
    return contexto_pwd.hash(contra)


@usuario.get(
    "/usuarios",
    response_description="Usuarios listados",
    dependencies=[Depends(usuario_admin_requerido)],
)
async def obtener_usuarios(token: str = Depends(esquema_oauth)):
    usuarios = await conn["usuarios"].find().to_list(1000)
    return serialize_mongo_docs(usuarios)


@usuario.get(
    "/usuarios/correo/{correo}",
    response_description="Usuario obtenido",
)
async def obtener_usuario_por_correo(correo: str, token: str = Depends(esquema_oauth)):
    usuario_obtenido = await conn["usuarios"].find_one({"correo": correo})
    if usuario_obtenido is not None:
        return serialize_mongo_doc(usuario_obtenido)

    raise HTTPException(status_code=404, detail="Usuario con ese correo no encontrado")


@usuario.post(
    "/usuarios/guardar",
    response_description="Usuario guardado",
    response_model=UserResponse,
)
async def guardar_usuario(usuario: Usuario = Body(...)):
    usuarios = await obtener_usuarios()
    if any(u["correo"] == usuario.correo for u in usuarios):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Correo ya registrado"
        )

    if len(usuarios) < 3:
        usuario.rol = Role.ADMIN

    usuario.contra = hashear_contra(usuario.contra)
    
    # Crear un diccionario manualmente para evitar problemas de serialización
    usuario_dict = {
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "correo": usuario.correo,
        "contra": usuario.contra,
        "pais": usuario.pais,
        "ciudad": usuario.ciudad,
        "inactivo": usuario.inactivo,
        "rol": usuario.rol
    }
    
    nuevo_usuario = await conn["usuarios"].insert_one(usuario_dict)
    usuario_creado = await conn["usuarios"].find_one({"_id": nuevo_usuario.inserted_id})
    
    # Utilizamos la función de serialización que elimina campos confidenciales
    campos_excluir = {"contra"}
    usuario_serializado = serialize_mongo_doc_filtered(usuario_creado, campos_excluir)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=usuario_serializado)


@usuario.put(
    "/usuarios/actualizar/{usuario_id}",
    response_description="Usuario actualizado"
)
async def actualizar_usuario(
    usuario_id: str,
    usuario: ActualizarUsuario = Body(...),
    token: str = Depends(esquema_oauth),
):
    usuario_actualizar = {
        datos: valor for datos, valor in usuario.dict().items() if valor is not None
    }
    if len(usuario_actualizar) >= 1:
        update_result = await conn["usuarios"].update_one(
            {"_id": usuario_id}, {"$set": usuario_actualizar}
        )

        if update_result.modified_count == 1:
            usuario_actualizado = await conn["usuarios"].find_one({"_id": usuario_id})
            if usuario_actualizado is not None:
                return serialize_mongo_doc(usuario_actualizado)

    usuario_existente = await conn["usuarios"].find_one({"_id": usuario_id})
    if usuario_existente is not None:
        return serialize_mongo_doc(usuario_existente)

    raise HTTPException(
        status_code=404, detail=f"usuario con id: {usuario_id} no encontrado"
    )


@usuario.delete(
    "/usuarios/eliminar/{usuario_id}", response_description="usuario eliminado"
)
async def eliminar_usuario_por_id(usuario_id: str, token: str = Depends(esquema_oauth)):
    usuario_eliminado = await conn["usuarios"].delete_one({"_id": usuario_id})
    if usuario_eliminado.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404, detail=f"usuario con id {usuario_id} no encontrado"
    )
