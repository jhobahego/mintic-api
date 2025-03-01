from fastapi import APIRouter, Depends, HTTPException, Body, Path
from typing import Optional
from datetime import datetime

from config.db import conn
from models.Notificacion import (
    TipoNotificacion,
    EstadoNotificacion,
    ConfiguracionRecordatorio
)
from auth.autenticacion import esquema_oauth, obtener_usuario_actual
from utils.serializers import serialize_mongo_doc, serialize_mongo_docs

notificaciones = APIRouter(prefix="/notificaciones", tags=["Notificaciones y Recordatorios"])


@notificaciones.get("", response_description="Lista de notificaciones")
async def listar_notificaciones(
    estado: Optional[EstadoNotificacion] = None,
    tipo: Optional[TipoNotificacion] = None,
    token: str = Depends(esquema_oauth)
):
    """
    Obtiene las notificaciones del usuario actual, con filtros opcionales por estado y tipo.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Construir filtro
    filtro = {"usuario_id": usuario_id}
    if estado:
        filtro["estado"] = estado
    if tipo:
        filtro["tipo"] = tipo
    
    # Obtener notificaciones ordenadas por fecha (las más recientes primero)
    notificaciones_db = await conn["notificaciones"].find(filtro).sort(
        "fecha_creacion", -1
    ).to_list(50)
    
    return serialize_mongo_docs(notificaciones_db)


@notificaciones.post("", response_description="Notificación creada")
async def crear_notificacion(
    tipo: TipoNotificacion = Body(...),
    titulo: str = Body(...),
    mensaje: str = Body(...),
    documento_id: Optional[str] = Body(None),
    accion_url: Optional[str] = Body(None),
    token: str = Depends(esquema_oauth)
):
    """
    Crea una nueva notificación para el usuario actual.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Definir iconos por tipo de notificación
    iconos = {
        TipoNotificacion.INFO: "info-circle",
        TipoNotificacion.ALERTA: "exclamation-triangle",
        TipoNotificacion.ERROR: "times-circle",
        TipoNotificacion.EXITO: "check-circle"
    }
    
    # Verificar si el documento existe (si se proporciona un ID)
    if documento_id:
        documento = await conn["documentos"].find_one({"_id": documento_id})
        if not documento:
            raise HTTPException(status_code=404, detail=f"Documento con ID {documento_id} no encontrado")
    
    # Crear la notificación
    notificacion = {
        "usuario_id": usuario_id,
        "tipo": tipo,
        "titulo": titulo,
        "mensaje": mensaje,
        "documento_id": documento_id,
        "fecha_creacion": datetime.now().isoformat(),
        "estado": EstadoNotificacion.NO_LEIDA,
        "fecha_lectura": None,
        "icono": iconos.get(tipo),
        "accion_url": accion_url
    }
    
    # Guardar en la base de datos
    resultado = await conn["notificaciones"].insert_one(notificacion)
    
    # Recuperar la notificación creada
    notificacion_creada = await conn["notificaciones"].find_one(
        {"_id": resultado.inserted_id}
    )
    
    return serialize_mongo_doc(notificacion_creada)


@notificaciones.put("/{notificacion_id}/leer", response_description="Notificación marcada como leída")
async def marcar_notificacion_como_leida(
    notificacion_id: str = Path(...),
    token: str = Depends(esquema_oauth)
):
    """
    Marca una notificación como leída.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Verificar que la notificación existe y pertenece al usuario
    notificacion = await conn["notificaciones"].find_one({
        "_id": notificacion_id,
        "usuario_id": usuario_id
    })
    
    if not notificacion:
        raise HTTPException(
            status_code=404, 
            detail=f"Notificación con ID {notificacion_id} no encontrada o no pertenece al usuario"
        )
    
    # Actualizar el estado de la notificación
    await conn["notificaciones"].update_one(
        {"_id": notificacion_id},
        {
            "$set": {
                "estado": EstadoNotificacion.LEIDA,
                "fecha_lectura": datetime.now().isoformat()
            }
        }
    )
    
    return {"mensaje": "Notificación marcada como leída", "notificacion_id": notificacion_id}


@notificaciones.put("/leer-todas", response_description="Todas las notificaciones marcadas como leídas")
async def marcar_todas_notificaciones_como_leidas(token: str = Depends(esquema_oauth)):
    """
    Marca todas las notificaciones no leídas del usuario como leídas.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Actualizar todas las notificaciones no leídas del usuario
    resultado = await conn["notificaciones"].update_many(
        {"usuario_id": usuario_id, "estado": EstadoNotificacion.NO_LEIDA},
        {
            "$set": {
                "estado": EstadoNotificacion.LEIDA,
                "fecha_lectura": datetime.now().isoformat()
            }
        }
    )
    
    return {"mensaje": f"{resultado.modified_count} notificaciones marcadas como leídas"}


@notificaciones.post("/recordatorios", response_description="Recordatorio creado")
async def crear_recordatorio(
    config: ConfiguracionRecordatorio = Body(...),
    token: str = Depends(esquema_oauth)
):
    """
    Crea un nuevo recordatorio para un documento.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": config.documento_id})
    if not documento:
        raise HTTPException(status_code=404, detail=f"Documento con ID {config.documento_id} no encontrado")
    
    # Verificar que la fecha de recordatorio es futura
    if config.fecha_recordatorio <= datetime.now():
        raise HTTPException(
            status_code=400, 
            detail="La fecha del recordatorio debe ser futura"
        )
    
    # Crear el recordatorio
    recordatorio = {
        "usuario_id": usuario_id,
        "documento_id": config.documento_id,
        "titulo": config.titulo_recordatorio,
        "mensaje": config.mensaje,
        "fecha_programada": config.fecha_recordatorio.isoformat(),
        "repetir": config.repetir,
        "intervalo_repeticion": config.intervalo_repeticion,
        "proxima_ejecucion": config.fecha_recordatorio.isoformat(),
        "ultima_ejecucion": None,
        "enviado": False,
        "activo": True,
        "enviar_email": config.enviar_email,
        "email_destino": config.email_destino if config.enviar_email else None,
        "fecha_creacion": datetime.now().isoformat()
    }
    
    # Guardar en la base de datos
    resultado = await conn["recordatorios"].insert_one(recordatorio)
    
    # Recuperar el recordatorio creado
    recordatorio_creado = await conn["recordatorios"].find_one(
        {"_id": resultado.inserted_id}
    )
    
    return serialize_mongo_doc(recordatorio_creado)


@notificaciones.get("/recordatorios", response_description="Lista de recordatorios")
async def listar_recordatorios(
    activo: Optional[bool] = None,
    documento_id: Optional[str] = None,
    token: str = Depends(esquema_oauth)
):
    """
    Obtiene los recordatorios del usuario actual, con filtros opcionales.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Construir filtro
    filtro = {"usuario_id": usuario_id}
    if activo is not None:
        filtro["activo"] = activo
    if documento_id:
        filtro["documento_id"] = documento_id
    
    # Obtener recordatorios ordenados por fecha (los más próximos primero)
    recordatorios_db = await conn["recordatorios"].find(filtro).sort(
        "proxima_ejecucion", 1
    ).to_list(50)
    
    return serialize_mongo_docs(recordatorios_db)


@notificaciones.put("/recordatorios/{recordatorio_id}", response_description="Recordatorio actualizado")
async def actualizar_recordatorio(
    recordatorio_id: str = Path(...),
    titulo: Optional[str] = Body(None),
    mensaje: Optional[str] = Body(None),
    fecha_programada: Optional[datetime] = Body(None),
    repetir: Optional[bool] = Body(None),
    intervalo_repeticion: Optional[int] = Body(None),
    activo: Optional[bool] = Body(None),
    enviar_email: Optional[bool] = Body(None),
    email_destino: Optional[str] = Body(None),
    token: str = Depends(esquema_oauth)
):
    """
    Actualiza un recordatorio existente.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Verificar que el recordatorio existe y pertenece al usuario
    recordatorio = await conn["recordatorios"].find_one({
        "_id": recordatorio_id,
        "usuario_id": usuario_id
    })
    
    if not recordatorio:
        raise HTTPException(
            status_code=404, 
            detail=f"Recordatorio con ID {recordatorio_id} no encontrado o no pertenece al usuario"
        )
    
    # Preparar los datos a actualizar
    actualizacion = {}
    
    if titulo is not None:
        actualizacion["titulo"] = titulo
    
    if mensaje is not None:
        actualizacion["mensaje"] = mensaje
    
    if fecha_programada is not None:
        # Verificar que la fecha es futura
        if fecha_programada <= datetime.now():
            raise HTTPException(
                status_code=400, 
                detail="La fecha del recordatorio debe ser futura"
            )
        actualizacion["fecha_programada"] = fecha_programada.isoformat()
        actualizacion["proxima_ejecucion"] = fecha_programada.isoformat()
    
    if repetir is not None:
        actualizacion["repetir"] = repetir
    
    if intervalo_repeticion is not None:
        actualizacion["intervalo_repeticion"] = intervalo_repeticion
    
    if activo is not None:
        actualizacion["activo"] = activo
    
    if enviar_email is not None:
        actualizacion["enviar_email"] = enviar_email
    
    if email_destino is not None:
        actualizacion["email_destino"] = email_destino
    
    # Si no hay nada que actualizar, devolver error
    if not actualizacion:
        raise HTTPException(
            status_code=400, 
            detail="No se proporcionaron datos para actualizar"
        )
    
    # Actualizar el recordatorio
    await conn["recordatorios"].update_one(
        {"_id": recordatorio_id},
        {"$set": actualizacion}
    )
    
    # Obtener el recordatorio actualizado
    recordatorio_actualizado = await conn["recordatorios"].find_one(
        {"_id": recordatorio_id}
    )
    
    return serialize_mongo_doc(recordatorio_actualizado)


@notificaciones.delete("/recordatorios/{recordatorio_id}", response_description="Recordatorio eliminado")
async def eliminar_recordatorio(
    recordatorio_id: str = Path(...),
    token: str = Depends(esquema_oauth)
):
    """
    Elimina un recordatorio.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Verificar que el recordatorio existe y pertenece al usuario
    recordatorio = await conn["recordatorios"].find_one({
        "_id": recordatorio_id,
        "usuario_id": usuario_id
    })
    
    if not recordatorio:
        raise HTTPException(
            status_code=404, 
            detail=f"Recordatorio con ID {recordatorio_id} no encontrado o no pertenece al usuario"
        )
    
    # Eliminar el recordatorio
    await conn["recordatorios"].delete_one({"_id": recordatorio_id})
    
    return {"mensaje": "Recordatorio eliminado correctamente", "recordatorio_id": recordatorio_id}
