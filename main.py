from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes.usuarios import usuario
from routes.documentos import documento
from routes.registros import registro
from routes.imagenes import imagenes
from auth.autenticacion import auth


app = FastAPI()

app.include_router(usuario)
app.include_router(documento)
app.include_router(registro)
app.include_router(imagenes)
app.include_router(auth)

# PRODUCTION_URL = os.environ["PRODUCTION_URL"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

