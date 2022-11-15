from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return {"message": "Hello World"}

@app.get("/saludo")
async def root():
    return {"message": "hola misiontic"}

usuarios = ['jhon', 'maria', 'heidy']
documentos = []

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
    return documentos[documento_id]
