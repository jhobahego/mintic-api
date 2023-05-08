from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.usuarios import usuario
from routes.documentos import documento
from routes.registros import registro
from auth.autenticacion import auth


app = FastAPI()

app.include_router(usuario)
app.include_router(documento)
app.include_router(registro)
app.include_router(auth)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

