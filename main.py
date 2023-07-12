from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

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

# PRODUCTION_URL = os.environ.get("PRODUCTION_URL")
DEVELOPT_URL = os.environ.get("DEVELOPMENT_FRONT")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[DEVELOPT_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

