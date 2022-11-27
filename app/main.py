from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Text
from uuid import uuid4 as uuid
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

origins = [
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

class Usuario(BaseModel):
    usuario_id: Optional[str]
    nombres: str
    apellidos: str
    correo: str
    contra: str
    pais: str
    ciudad: str

class Documento(BaseModel):
    documento_id: Optional[str]
    tipo: str
    autor: str
    titulo: str
    descripcion: Text
    categoria: str
    stock: int
    precio: int
    editorial: str
    idioma: str
    paginas: int

class Registro(BaseModel):
    registro_id: Optional[str]
    usuario_id: int
    nombre_documento: str
    tipo_de_venta: str
    cantidad: int

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
