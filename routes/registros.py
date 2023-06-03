from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from config.db import conn
from auth.autenticacion import esquema_oauth
from models.Registro import Registro
from typing import List

registro = APIRouter()


@registro.get("/ventas", response_description="Registros listados", response_model=List[Registro])
async def obtener_ventas(token: str = Depends(esquema_oauth)):
    registros = await conn["ventas"].find().to_list(1000)
    return registros


@registro.get("/ventas/usuario/{usuario_id}", response_description="Usuario obtenido", response_model=List[Registro])
async def obtener_adquisicion_de_usuario(usuario_id: str, token: str = Depends(esquema_oauth)):
    registros = await conn["ventas"].find({"id_cliente": usuario_id}).to_list(length=None)
    if registros:
        return registros

    raise HTTPException(
        status_code=404, detail=f"No se encontraron registros para el cliente con id: {usuario_id}")


@registro.get("/ventas/documento/{nombre}", response_description="Registro obtenido", response_model=List[Registro])
async def obtener_ventas_de_documento(nombre: str, token: str = Depends(esquema_oauth)):
    registros = await conn["ventas"].find({"titulo_documento": nombre}).to_list(length=None)
    if registros:
        return registros
    raise HTTPException(
        status_code=404, detail=f"documento {nombre} no encontrado")


@registro.get("/ventas/tipo/{tipo_de_venta}", response_description="Registro obtenido", response_model=Registro)
async def obtener_ventas_por_tipo(tipo_de_venta: str, token: str = Depends(esquema_oauth)):
    registro_obtenido = await conn["ventas"].find_one({"tipo_de_adquisicion": tipo_de_venta})
    if registro_obtenido is not None:
        return registro_obtenido
    raise HTTPException(
        status_code=404, detail=f"el documento {tipo_de_venta} no fue encontrado")


@registro.post("/ventas/guardar", response_description="documento guardado", response_model=Registro)
async def guardar_registro(registro: Registro = Body(...), token: str = Depends(esquema_oauth)):
    registro = jsonable_encoder(registro)
    registro_insertado = await conn["ventas"].insert_one(registro)
    registro_creado = await conn["ventas"].find_one({"_id": registro_insertado.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=registro_creado)
