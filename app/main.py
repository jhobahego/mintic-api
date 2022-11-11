from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return {"message": "Hello World"}

@app.get("/saludo")
async def root():
    return {"message": "hola misiontic"}

@app.get("usuarios/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}

cursos = [{"curso": "fundamentos programacion"}, {"curso": "programacion basica"}, {"curso": "Desarrollo de software"}, {"curso": "Desarrollo de app webs"}]

@app.get("/cursos/")
async def read_item(skip: int = 0, limit: int = 10):
    return cursos[skip: skip + limit]
        