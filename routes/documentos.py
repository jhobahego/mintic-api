from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from typing import List
from bson import ObjectId

from config.db import conn
from auth.autenticacion import esquema_oauth
from models.Documento import Documento, ActualizarDocumento
from models.Id import PyObjectId
from routes.imagenes import guardar_imagen

documento = APIRouter()


@documento.get(
    "/", response_description="Documentos listados", response_model=List[Documento]
)
async def obtener_documentos(token: str = Depends(esquema_oauth)):
    documentos = await conn["documentos"].find().to_list(1000)
    return documentos


@documento.get(
    "/documentos/{documento_id}",
    response_description="Documento obtenido",
    response_model=Documento,
)
async def obtener_documento_por_id(
    documento_id: str, token: str = Depends(esquema_oauth)
):
    if (
        documento := await conn["documentos"].find_one({"_id": documento_id})
    ) is not None:
        return documento

    raise HTTPException(
        status_code=404, detail=f"documento con id {documento_id} no encontrado"
    )


@documento.get(
    "/documentos/titulo/{titulo}",
    response_description="Documento obtenido",
    response_model=Documento,
)
async def obtener_documento_por_titulo(titulo: str = Depends(esquema_oauth)):
    if (documento := await conn["documentos"].find_one({"titulo": titulo})) is not None:
        return documento

    raise HTTPException(status_code=404, detail=f"documento con {titulo} no encontrado")


@documento.post(
    "/documentos/guardar",
    response_description="Documento creado",
    response_model=Documento,
)
async def guardar_documento(
    tipo_documento: str = Form(...),
    autor: str = Form(...),
    titulo: str = Form(...),
    descripcion: str = Form(...),
    categoria: str = Form(...),
    stock: int = Form(...),
    precio: int = Form(...),
    editorial: str = Form(...),
    idioma: str = Form(...),
    paginas: int = Form(...),
    imagen: UploadFile = File(...),
    token: str = Depends(esquema_oauth),
):
    image = await guardar_imagen(imagenAGuardar=imagen)

    documento_id: PyObjectId = ObjectId()
    documento = {
        "_id": str(documento_id),
        "tipo_documento": tipo_documento,
        "autor": autor,
        "titulo": titulo,
        "descripcion": descripcion,
        "imagen": image["url_imagen"],
        "categoria": categoria,
        "stock": stock,
        "precio": precio,
        "editorial": editorial,
        "idioma": idioma,
        "paginas": paginas,
    }

    documento = jsonable_encoder(documento)

    documento_insertado = await conn["documentos"].insert_one(documento)
    documento_creado = await conn["documentos"].find_one(
        {"_id": documento_insertado.inserted_id}
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=documento_creado)


@documento.put(
    "/documentos/actualizar/{documento_id}",
    response_description="Documento actualizado",
    response_model=Documento,
)
async def actualizar_documento(
    documento_id: str,
    actualizarDocumento: ActualizarDocumento = Body(...),
    token: str = Depends(esquema_oauth),
):
    actualizarDocumento = {
        datos: valor
        for datos, valor in actualizarDocumento.dict().items()
        if valor is not None
    }
    if len(actualizarDocumento) >= 1:
        update_result = await conn["documentos"].update_one(
            {"_id": documento_id}, {"$set": actualizarDocumento}
        )

        if update_result.modified_count == 1:
            if (
                documento_actualizado := await conn["documentos"].find_one(
                    {"_id": documento_id}
                )
            ) is not None:
                return documento_actualizado

    if (
        documento_existente := await conn["documentos"].find_one({"_id": documento_id})
    ) is not None:
        return documento_existente

    raise HTTPException(
        status_code=404, detail=f"documento con id: {documento_id} no encontrado"
    )


@documento.delete(
    "/documentos/eliminar/{documento_id}", response_description="documento eliminado"
)
async def eliminar_documento_por_id(
    documento_id: str, token: str = Depends(esquema_oauth)
):
    doc_eliminado = await conn["documentos"].delete_one({"_id": documento_id})
    if doc_eliminado.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404, detail=f"documento con id {documento_id} no encontrado"
    )
