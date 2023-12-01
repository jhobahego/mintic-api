from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.usuarios import usuario
from routes.documentos import documento
from routes.registros import registro
from routes.imagenes import imagenes

from auth.autenticacion import auth

from decouple import config

app = FastAPI()

app.include_router(usuario)
app.include_router(documento)
app.include_router(registro)
app.include_router(imagenes)
app.include_router(auth)

# PRODUCTION_URL = config("PRODUCTION_URL")
DEVELOPT_URL = config("DEVELOPMENT_FRONT")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[DEVELOPT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
