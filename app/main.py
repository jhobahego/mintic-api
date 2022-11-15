from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return {"message": "Hello World"}

@app.get("/saludo")
async def root():
    return {"message": "hola misiontic"}

usuarios = ['jhon', 'maria', 'heidy']
documentos = [
    {
        "documento_id":0,
        "tipo":"fisico",
        "autor": "Robert C. Martin",
        "titulo":"clean code",
        "descripcion":"Handbook of Agile Software Crashmans",
        "categoria":"desarrollo de software",
        "stock":12,
        "precio":40,
        "editoria":"great editorial",
        "paginas":450,
    },
    {
        "documento_id":1,
        "tipo":"digital",
        "autor": "Andy Hunt & Davis Thomas",
        "titulo":"the pragmatic programmer",
        "descripcion":"From journeyman to master",
        "categoria":"desarrollo de software",
        "stock":12,
        "precio":32,
        "editoria":"Ward Cummingham",
        "paginas":350,
    },
]
registros = [
    {
        "registro_id":0,
        "usuario_id":0,
        "documento_id":1,
        "tipo_venta":"prestamo",
        "cantidad":1,
    },
    {
        "registro_id":1,
        "usuario_id":1,
        "documento_id":0,
        "tipo_venta":"compra",
        "cantidad":1,
    },
    {
        "registro_id":2,
        "usuario_id":1,
        "documento_id":1,
        "tipo_venta":"prestamo",
        "cantidad":1,
    },
]

@app.get("/usuarios")
async def obtener_usuarios():
    return usuarios

@app.get("/usuarios/{user_id}")
async def obtener_usuario(user_id: int):
    print(usuarios[user_id])
    return usuarios[user_id]

@app.get("/documentos/")
async def obtener_documentos():
    return documentos

@app.get("/documentos/{documento_id}")
async def obtener_documentos(documento_id: int):
    for documento in documentos:
        dato = documento.get("documento_id")
        if dato == documento_id:
            return documentos[documento_id]
    return None

@app.get("/documentos/titulo=/{titulo}")
async def obtener_documento_por_titulo(titulo:str):
    for documento in documentos:
        dato = documento.get("titulo")
        if dato == titulo:
            return documento
    return None

@app.get("/ventas")
async def obtener_ventas():
    return registros


@app.get("/registro/{documento_id}")
async def obtener_registro_por_id(documento_id:int):
    for registro in registros:
        dato = registro.get("registro_id")
        if dato:
            return registro
    return None