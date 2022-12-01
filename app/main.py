from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Text
from uuid import uuid4 as uuid
from bson import ObjectId
import motor.motor_asyncio
import os

app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])

db = client.misiontic

# origins = [
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins = "http://localhost:8080",
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
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
    id_cliente: int = Field(...)
    id_documento: int = Field(...)
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

usuarios = []

documentos = []

registros = []

@app.get("/usuarios")
async def obtener_usuarios():
    return usuarios

@app.get("/usuarios/{user_id}")
async def obtener_usuario_por_id(user_id: int):
    for usuario in usuarios:
        if usuario["usuario_id"] == user_id:
            return usuario
    raise HTTPException(status_code=404, detail="usuario no encontrado")

@app.get("/usuarios/nombre=/{nombre_usuario}")
async def obtener_usuario_por_nombre(nombre_usuario: str):
    for usuario in usuarios:
        if usuario["nombres"] == nombre_usuario:
            return usuario    
    raise HTTPException(status_code=404, detail="usuario no encontrado")

@app.get("/")
async def obtener_documentos():
    return documentos

@app.get("/documentos/{documento_id}")
async def obtener_documento_por_id(documento_id: int):
    for documento in documentos:
        if documento["documento_id"] == documento_id:
            return documento
    raise HTTPException(status_code=404, detail="documento no encontrado")

@app.get("/documentos/titulo=/{titulo}")
async def obtener_documento_por_titulo(titulo:str):
    for documento in documentos:
        if documento["documento_id"] == titulo:
            return documento
    raise HTTPException(status_code=404, detail="documento no encontrado")

@app.get("/ventas")
async def obtener_ventas():
    return registros

@app.get("/ventas/usuario/{usuario_id}")
async def obtener_ventas_de_usuario(usuario_id:int):
    for registro in registros:
        if registro["usuario_id"] == usuario_id:
            return registro
    raise HTTPException(status_code=404, detail="registro no encontrado")

@app.get("/ventas/documento=/{nombre}")
async def obtener_ventas_de_documento(nombre:str):
    for registro in registros:
        if registro["nombre_documento"] == nombre:
            return registro
    raise HTTPException(status_code=404, detail="registro no encontrado")

@app.get("/ventas/tipo=/{tipo_de_venta}")
async def obtener_ventas_por_tipo(tipo_de_venta:str):
    for registro in registros:
        if registro["tipo_de_venta"] == tipo_de_venta:
            return registro
    raise HTTPException(status_code=404, detail="registro no encontrado")

@app.post("/usuarios/guardar")
async def guardar_usuario(usuario:Usuario):
    usuario.usuario_id = int(uuid())
    usuarios.append(usuario.dict())
    return usuarios[-1]

@app.post("/documentos/guardar")
async def guardar_documento(documento:Documento):
    documento.documento_id = int(uuid())
    documentos.append(documento.dict())
    return documentos[-1]

@app.post("/ventas/guardar")
async def guardar_registro(registro:Registro):
    registro.registro_id = int(uuid())
    registros.append(registro.dict())
    return registros[-1]

@app.put("/usuarios/actualizar/{usuario_id}")
async def actualizar_usuario(usuario_id:int, actualizarUsuario:Usuario):
    for index, usuario in enumerate(usuarios):
        if usuario["usuario_id"] == usuario_id:
            usuarios[index]["usuario_id"] = actualizarUsuario.usuario_id
            usuarios[index]["nombres"] = actualizarUsuario.nombres
            usuarios[index]["apellidos"] = actualizarUsuario.apellidos
            usuarios[index]["correo"] = actualizarUsuario.correo
            usuarios[index]["contra"] = actualizarUsuario.contra
            usuarios[index]["pais"] = actualizarUsuario.pais
            usuarios[index]["ciudad"] = actualizarUsuario.ciudad
            return usuario
    raise HTTPException(status_code=404, detail="usuario no encontrado")

@app.put("documentos/actualizar/{documento_id}")
async def actualizar_documento(documento_id:int, actualizarDocumento:Documento):
    for index, documento in enumerate(documentos):
        if documento["documento_id"] == documento_id:
            documentos[index]["documento_id"] = actualizarDocumento.documento_id
            documentos[index]["tipo"] = actualizarDocumento.tipo
            documentos[index]["autor"] = actualizarDocumento.autor
            documentos[index]["titulo"] = actualizarDocumento.titulo
            documentos[index]["descripcion"] = actualizarDocumento.descripcion
            documentos[index]["categoria"] = actualizarDocumento.categoria
            documentos[index]["stock"] = actualizarDocumento.stock
            documentos[index]["precio"] = actualizarDocumento.precio
            documentos[index]["editorial"] = actualizarDocumento.editorial
            documentos[index]["idioma"] = actualizarDocumento.idioma
            documentos[index]["paginas"] = actualizarDocumento.paginas
            return documento
    raise HTTPException(status_code=404, detail="documento no encontrado")

@app.delete("/usuarios/eliminar/{usuario_id}")
async def eliminar_usuario_por_id(usuario_id:int):
    for index, usuario in enumerate(usuarios):
        if usuario["usuario_id"] == usuario_id:
            usuarios.pop(index)
            return {"message":"usuario eliminado correctamente"}
    raise HTTPException(status_code=404, detail="usuario no encontrado")

@app.delete("/documentos/eliminar/{documento_id}")
async def eliminar_documento_por_id(documento_id:int):
    for index, documento in enumerate(documentos):
        if documento["documento_id"] == documento_id:
            documentos.pop(index)
            return {"message":"documento eliminado correctamente"}
    raise HTTPException(status_code=404, detail="documento no encontrado")
