from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
import shutil

imagenes = APIRouter(tags=["Imagenes"])


@imagenes.get("/images/{nombre_imagen}")
async def obtener_imagen(nombre_imagen: str):
    ruta_imagen = Path(f"images/{nombre_imagen}").absolute()

    if ruta_imagen.exists():
        return FileResponse(ruta_imagen)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Imagen con nombre {nombre_imagen} no encontrada",
    )


async def guardar_imagen(imagenAGuardar: UploadFile = File(...)):
    try:
        ruta_guardado = f"images/{imagenAGuardar.filename}"
        ruta_completa = Path(ruta_guardado).absolute()
        with open(ruta_completa, "wb") as archivo:
            shutil.copyfileobj(imagenAGuardar.file, archivo)
        url_imagen = f"http:localhost:8000/{ruta_guardado}"
        return {"url_imagen": url_imagen}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
