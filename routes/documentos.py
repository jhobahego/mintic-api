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
from bson import ObjectId

from config.db import conn
from auth.autenticacion import esquema_oauth
from auth.services import usuario_admin_requerido
from models.Documento import ActualizarDocumento
from routes.imagenes import guardar_imagen

documento = APIRouter()


@documento.get("/", response_description="Documentos listados")
async def obtener_documentos(token: str = Depends(esquema_oauth)):
    documentos = await conn["documentos"].find().to_list(1000)
    return documentos


@documento.get("/documentos/{documento_id}", response_description="Documento obtenido")
async def obtener_documento_por_id(
    documento_id: str, token: str = Depends(esquema_oauth)
):
    documento = await conn["documentos"].find_one({"_id": documento_id})
    if documento is not None:
        return documento

    raise HTTPException(
        status_code=404, detail=f"documento con id {documento_id} no encontrado"
    )


@documento.get("/documentos/titulo/{titulo}", response_description="Documento obtenido")
async def obtener_documento_por_titulo(titulo: str = Depends(esquema_oauth)):
    documento = await conn["documentos"].find_one({"titulo": titulo})
    if documento is not None:
        return documento

    raise HTTPException(status_code=404, detail=f"documento con {titulo} no encontrado")


@documento.post(
    "/documentos/guardar",
    response_description="Documento creado",
    dependencies=[Depends(usuario_admin_requerido)],
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

    documento_id = str(ObjectId())
    documento = {
        "_id": documento_id,
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
            documento_actualizado = await conn["documentos"].find_one(
                {"_id": documento_id}
            )
            if documento_actualizado is not None:
                return documento_actualizado

    documento_existente = await conn["documentos"].find_one({"_id": documento_id})
    if documento_existente is not None:
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
