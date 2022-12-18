from fastapi import FastAPI, HTTPException, Body, status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Text, List
from uuid import uuid4 as uuid
from bson import ObjectId
import motor.motor_asyncio
import os

app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
#client = pymongo.MongoClient("mongodb+srv://jhobahego:CGSY44c7EWUin0af@cluster0.xrqddso.mongodb.net/?retryWrites=true&w=majority")
db = client.misiontic

# origins = [
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:8080",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Usuario(BaseModel):
    usuario_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombres: str = Field(...)
    apellidos: str = Field(...)
    correo: EmailStr = Field(...)
    contra: str = Field(...)
    pais: str = Field(...)
    ciudad: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "nombres": "Jane Doe",
                "apellidos": "hernandez gomez",
                "correo": "jdoe@example.com",
                "contra": "pass123",
                "pais": "Colombia",
                "ciudad": "Betulia",
            }
        }


class ActualizarUsuario(BaseModel):
    nombres: Optional[str]
    apellidos: Optional[str]
    correo: Optional[EmailStr]
    contra: Optional[str]
    pais: Optional[str]
    ciudad: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "nombres": "Jane Doe",
                "apellidos": "hernandez gomez",
                "correo": "jdoe@example.com",
                "contra": "pass123",
                "pais": "Colombia",
                "ciudad": "Betulia",
            }
        }


class Documento(BaseModel):
    documento_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    tipo_documento: str = Field(...)
    autor: str = Field(...)
    titulo: str = Field(...)
    descripcion: Text = Field(...)
    categoria: str = Field(...)
    stock: int = Field(...)
    precio: int = Field(...)
    editorial: str = Field(...)
    idioma: str = Field(...)
    paginas: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "tipo_documento": "digital",
                "autor": "Robert C. Martin",
                "titulo": "clean code",
                "descripcion": "un libro para aprender codigo",
                "categoria": "desarrollo de software",
                "stock": "12",
                "precio": "40",
                "editorial": "betulia-editoriales",
                "idioma": "ingles",
                "paginas": "125",
            }
        }


class ActualizarDocumento(BaseModel):
    tipo_documento: Optional[str]
    autor: Optional[str]
    titulo: Optional[str]
    descripcion: Optional[Text]
    categoria: Optional[str]
    stock: Optional[int]
    precio: Optional[int]
    editorial: Optional[str]
    idioma: Optional[str]
    paginas: Optional[int]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "tipo_documento": "digital",
                "autor": "Robert C. Martin",
                "titulo": "clean code",
                "descripcion": "un libro para aprender codigo",
                "categoria": "desarrollo de software",
                "stock": "12",
                "precio": "40",
                "editorial": "betulia-editoriales",
                "idioma": "ingles",
                "paginas": "125",
            }
        }


class Registro(BaseModel):
    registro_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    id_cliente: str = Field(...)
    id_documento: str = Field(...)
    titulo_documento: str = Field(...)
    tipo_de_adquisicion: str = Field(...)
    cantidad: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "cliente_id": "12352252",
                "documento_id": "12425266353",
                "titulo_documento": "hernandez gomez",
                "tipo_de_adquisicion": "prestamo",
                "cantidad": "124",
            }
        }


@app.get("/usuarios", response_description="Usuarios listados", response_model=List[Usuario])
async def obtener_usuarios():
    usuarios = await db["usuarios"].find().to_list(1000)
    return usuarios


@app.get("/usuarios/{usuario_id}", response_description="usuario listado", response_model=Usuario)
async def obtener_usuario_por_id(usuario_id: str):
    if (usuario := await db["usuarios"].find_one({"_id": usuario_id})) is not None:
        return usuario

    raise HTTPException(
        status_code=404, detail=f"Usuario con id {usuario_id} no encontrado")


@app.get("/usuarios/nombre/{nombre_usuario}", response_description="Usuario obtenido", response_model=Usuario)
async def obtener_usuario_por_nombre(nombre_usuario: str):
    if (usuario := await db["usuarios"].find_one({"nombres": nombre_usuario})) is not None:
        return usuario

    raise HTTPException(
        status_code=404, detail=f"Usuario {nombre_usuario} no encontrado")


@app.get("/", response_description="Documentos listados", response_model=List[Documento])
async def obtener_documentos():
    documentos = await db["documentos"].find().to_list(1000)
    return documentos


@app.get("/documentos/{documento_id}", response_description="Documento obtenido", response_model=Documento)
async def obtener_documento_por_id(documento_id: str):
    if (documento := await db["documentos"].find_one({"_id": documento_id})) is not None:
        return documento

    raise HTTPException(
        status_code=404, detail=f"documento con id {documento_id} no encontrado")


@app.get("/documentos/titulo/{titulo}", response_description="Documento obtenido", response_model=Documento)
async def obtener_documento_por_titulo(titulo: str):
    if (documento := await db["documentos"].find_one({"titulo": titulo})) is not None:
        return documento

    raise HTTPException(
        status_code=404, detail=f"documento con {titulo} no encontrado")


@app.get("/ventas", response_description="Registros listados", response_model=Registro)
async def obtener_ventas():
    registros = await db["ventas"].find().to_list(1000)
    return registros


@app.get("/ventas/usuario/{usuario_id}", response_description="Usuario obtenido", response_model=Registro)
async def obtener_ventas_de_usuario(usuario_id: int):
    if (registro := await db["ventas"].find_one({"id_cliente": usuario_id})) is not None:
        return registro

    raise HTTPException(
        status_code=404, detail=f"cliente {usuario_id} no encontrado")


@app.get("/ventas/documento=/{nombre}", response_description="Registro obtenido", response_model=Registro)
async def obtener_ventas_de_documento(nombre: str):
    if (registro := await db["ventas"].find_one({"titulo_documento": nombre})) is not None:
        return registro
    raise HTTPException(status_code=404, detail=f"documento {nombre} no encontrado")

@app.get("/ventas/tipo=/{tipo_de_venta}", response_description="Registro obtenido", response_model=Registro)
async def obtener_ventas_por_tipo(tipo_de_venta: str):
    if (registro := await db["ventas"].find_one({"tipo_de_adquisicion": tipo_de_venta})) is not None:
        return registro
    raise HTTPException(status_code=404, detail=f"el documento {tipo_de_venta} no fue encontrado")

@app.post("/usuarios/guardar", response_description="Usuario guardado", response_model=Usuario)
async def guardar_usuario(usuario:Usuario = Body(...)):
    usuario = jsonable_encoder(usuario)
    nuevo_usuario = await db["usuarios"].insert_one(usuario)
    usuario_creado = await db["usuarios"].find_one({"_id": nuevo_usuario.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=usuario_creado)

@app.post("/documentos/guardar", response_description="Documento creado", response_model=Documento)
async def guardar_documento(documento:Documento = Body(...)):
    documento = jsonable_encoder(documento)
    documento_insertado = await db["documentos"].insert_one(documento)
    documento_creado = await db["documentos"].find_one({"_id": documento_insertado.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=documento_creado)

@app.post("/ventas/guardar", response_description="documento guardado", response_model=Registro)
async def guardar_registro(registro:Registro = Body(...)):
    registro = jsonable_encoder(registro)
    registro_insertado = await db["ventas"].insert_one(registro)
    registro_creado = await db["ventas"].find_one({"registro_id": registro_insertado.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=registro_creado)

@app.put("/usuarios/actualizar/{usuario_id}", response_description="Usuario actualizado", response_model=Usuario)
async def actualizar_usuario(usuario_id:str, usuario:ActualizarUsuario = Body(...)):
    usuario = {datos: valor for datos, valor in usuario.dict().items() if valor is not None}
    if len(usuario) >= 1:
      update_result = await db["usuarios"].update_one({"_id": usuario_id}, {"$set": usuario})

      if update_result.modified_count == 1:
            if (
                usuario_actualizado := await db["usuarios"].find_one({"_id": usuario_id})
            ) is not None:
                return usuario_actualizado

    if (usuario_existente := await db["usuarios"].find_one({"_id": usuario_id})) is not None:
        return usuario_existente

    raise HTTPException(status_code=404, detail=f"usuario con id: {usuario_id} no encontrado")

@app.put("/documentos/actualizar/{documento_id}", response_description="Documento actualizado", response_model=Documento)
async def actualizar_documento(documento_id:str, actualizarDocumento:ActualizarDocumento = Body(...)):
    actualizarDocumento = {datos: valor for datos, valor in actualizarDocumento.dict().items() if valor is not None}
    if len(actualizarDocumento) >= 1:
      update_result = await db["documentos"].update_one({"_id": documento_id}, {"$set": actualizarDocumento})

      if update_result.modified_count == 1:
            if (
                documento_actualizado := await db["documentos"].find_one({"_id": documento_id})
            ) is not None:
                return documento_actualizado

    if (documento_existente := await db["documentos"].find_one({"_id": documento_id})) is not None:
        return documento_existente

    raise HTTPException(status_code=404, detail=f"documento con id: {documento_id} no encontrado")

@app.delete("/usuarios/eliminar/{usuario_id}", response_description="usuario eliminado")
async def eliminar_usuario_por_id(usuario_id:str):
    usuario_eliminado = await db["usuarios"].delete_one({"_id": usuario_id})
    if usuario_eliminado.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"usuario con id {usuario_id} no encontrado")

@app.delete("/documentos/eliminar/{documento_id}", response_description="documento eliminado")
async def eliminar_documento_por_id(documento_id:str):
    doc_eliminado = await db["documentos"].delete_one({"_id": documento_id})
    if doc_eliminado.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"documento con id {documento_id} no encontrado")
