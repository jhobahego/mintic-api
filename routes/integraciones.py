from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
import json
from datetime import datetime, timedelta
import random
import io
import time

from config.db import conn
from models.Integracion import (
    ProveedorNube,
    ConfiguracionIntegracion,
    EstadoSincronizacion,
    DocumentoExportacion,
    DatosEstadisticos
)
from auth.autenticacion import esquema_oauth, obtener_usuario_actual
from utils.serializers import serialize_mongo_doc, serialize_mongo_docs

integracion = APIRouter(prefix="/integracion", tags=["Integraciones"])


@integracion.post("/nube/configurar", response_description="Configuración de integración en la nube guardada")
async def configurar_integracion_nube(
    configuracion: ConfiguracionIntegracion = Body(...),
    token: str = Depends(esquema_oauth)
):
    """
    Configura la integración con un servicio en la nube como Google Drive, Dropbox o OneDrive.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Verificar si ya existe una configuración para este usuario y proveedor
    config_existente = await conn["integraciones_nube"].find_one({
        "usuario_id": usuario_id,
        "proveedor": configuracion.proveedor
    })
    
    # Preparar el documento a guardar
    config_doc = {
        "usuario_id": usuario_id,
        "proveedor": configuracion.proveedor,
        "token_acceso": configuracion.token_acceso,
        "carpeta_id": configuracion.carpeta_id,
        "sincronizacion_automatica": configuracion.sincronizacion_automatica,
        "intervalo_sincronizacion": configuracion.intervalo_sincronizacion,
        "fecha_actualizacion": datetime.now().isoformat()
    }
    
    # Actualizar o insertar
    if config_existente:
        await conn["integraciones_nube"].update_one(
            {"_id": config_existente["_id"]},
            {"$set": config_doc}
        )
        mensaje = f"Configuración para {configuracion.proveedor} actualizada exitosamente"
    else:
        await conn["integraciones_nube"].insert_one(config_doc)
        mensaje = f"Configuración para {configuracion.proveedor} guardada exitosamente"
    
    return {"mensaje": mensaje, "proveedor": configuracion.proveedor}


@integracion.get("/nube/configuraciones", response_description="Configuraciones de integraciones en la nube")
async def listar_configuraciones_nube(token: str = Depends(esquema_oauth)):
    """
    Obtiene las configuraciones de integraciones en la nube para el usuario actual.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    configuraciones = await conn["integraciones_nube"].find(
        {"usuario_id": usuario_id}
    ).to_list(10)
    
    # Por seguridad, no devolvemos el token de acceso completo
    for config in configuraciones:
        if "token_acceso" in config:
            config["token_acceso"] = config["token_acceso"][:10] + "..." if config["token_acceso"] else "No configurado"
    
    return serialize_mongo_docs(configuraciones)


@integracion.post("/nube/sincronizar", response_description="Documento sincronizado con la nube")
async def sincronizar_documento(
    documento_id: str = Body(...),
    proveedor: ProveedorNube = Body(...),
    token: str = Depends(esquema_oauth)
):
    """
    Sincroniza un documento con un servicio en la nube.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": documento_id})
    if not documento:
        raise HTTPException(status_code=404, detail=f"Documento con ID {documento_id} no encontrado")
    
    # Verificar que existe una configuración para el proveedor
    config = await conn["integraciones_nube"].find_one({
        "usuario_id": usuario_id,
        "proveedor": proveedor
    })
    
    if not config:
        raise HTTPException(
            status_code=404, 
            detail=f"No se ha configurado la integración con {proveedor}. Configure primero la integración."
        )
    
    # En un sistema real, aquí se realizaría la sincronización con el API del proveedor
    # Por ahora, simulamos el proceso
    
    # Simular tiempo de procesamiento
    time.sleep(random.uniform(1.0, 2.5))
    
    # Simular ID y URL en la nube
    id_en_nube = f"{proveedor}_{int(time.time())}_{random.randint(1000, 9999)}"
    url_base = {
        ProveedorNube.GOOGLE_DRIVE: "https://drive.google.com/file/d/",
        ProveedorNube.DROPBOX: "https://www.dropbox.com/s/",
        ProveedorNube.ONEDRIVE: "https://1drv.ms/",
    }.get(proveedor, "https://cloud.example.com/")
    
    url_en_nube = f"{url_base}{id_en_nube}/view"
    
    # Crear registro de sincronización
    sincronizacion = {
        "usuario_id": usuario_id,
        "proveedor": proveedor,
        "documento_id": documento_id,
        "documento_nombre": documento.get("titulo", "Documento sin título"),
        "id_en_nube": id_en_nube,
        "url_en_nube": url_en_nube,
        "estado": EstadoSincronizacion.COMPLETADO,
        "ultima_sincronizacion": datetime.now().isoformat(),
        "proxima_sincronizacion": (datetime.now() + timedelta(hours=24)).isoformat() if config.get("sincronizacion_automatica") else None
    }
    
    # Actualizar o insertar el registro de sincronización
    await conn["sincronizaciones"].update_one(
        {"usuario_id": usuario_id, "documento_id": documento_id, "proveedor": proveedor},
        {"$set": sincronizacion},
        upsert=True
    )
    
    return {
        "mensaje": f"Documento sincronizado con {proveedor}",
        "id_en_nube": id_en_nube,
        "url_en_nube": url_en_nube,
        "estado": EstadoSincronizacion.COMPLETADO
    }


@integracion.get("/nube/sincronizaciones", response_description="Historial de sincronizaciones")
async def listar_sincronizaciones(
    proveedor: Optional[ProveedorNube] = None,
    token: str = Depends(esquema_oauth)
):
    """
    Obtiene el historial de sincronizaciones del usuario actual.
    """
    usuario = await obtener_usuario_actual(token)
    usuario_id = usuario["_id"]
    
    # Filtro base
    filtro = {"usuario_id": usuario_id}
    
    # Añadir filtro por proveedor si se especifica
    if proveedor:
        filtro["proveedor"] = proveedor
    
    sincronizaciones = await conn["sincronizaciones"].find(filtro).sort(
        "ultima_sincronizacion", -1
    ).to_list(50)
    
    return serialize_mongo_docs(sincronizaciones)


@integracion.post("/exportar", response_description="Documento exportado")
async def exportar_documento(
    exportacion: DocumentoExportacion = Body(...),
    token: str = Depends(esquema_oauth)
):
    """
    Exporta un documento a diferentes formatos (PDF, DOCX, TXT, etc.)
    """
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": exportacion.documento_id})
    if not documento:
        raise HTTPException(status_code=404, detail=f"Documento con ID {exportacion.documento_id} no encontrado")
    
    # Verificar que el formato es válido
    formatos_validos = ["pdf", "docx", "txt", "csv", "xml", "json"]
    if exportacion.formato.lower() not in formatos_validos:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato no soportado. Formatos válidos: {', '.join(formatos_validos)}"
        )
    
    # En un sistema real, aquí se generaría el documento en el formato especificado
    # Por ahora, simulamos la generación
    
    # Simular tiempo de procesamiento
    time.sleep(random.uniform(0.5, 2.0))
    
    # Generar contenido ficticio para simular el documento exportado
    if exportacion.formato.lower() == "json":
        # Para JSON, devolvemos el documento como JSON
        content = json.dumps(serialize_mongo_doc(documento), indent=2)
        media_type = "application/json"
    else:
        # Para otros formatos, simulamos contenido
        content = f"""
        DOCUMENTO EXPORTADO
        
        Título: {documento.get('titulo', 'Sin título')}
        Autor: {documento.get('autor', 'Sin autor')}
        Descripción: {documento.get('descripcion', 'Sin descripción')}
        
        Este es un documento simulado en formato {exportacion.formato.upper()}.
        En un sistema real, aquí estaría el contenido completo del documento.
        """
        media_type = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain",
            "csv": "text/csv",
            "xml": "application/xml"
        }.get(exportacion.formato.lower(), "text/plain")
    
    # Crear un archivo en memoria
    output = io.BytesIO(content.encode('utf-8'))
    
    # Registrar la exportación en la base de datos
    exportacion_doc = {
        "usuario_id": (await obtener_usuario_actual(token))["_id"],
        "documento_id": exportacion.documento_id,
        "formato": exportacion.formato.lower(),
        "fecha_exportacion": datetime.now().isoformat(),
    }
    
    await conn["exportaciones"].insert_one(exportacion_doc)
    
    # Devolver el archivo como respuesta streaming
    nombre_archivo = f"{documento.get('titulo', 'documento').replace(' ', '_')}.{exportacion.formato.lower()}"
    return StreamingResponse(
        output, 
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"}
    )


@integracion.get("/dashboard/estadisticas", response_description="Estadísticas para el dashboard")
async def obtener_estadisticas(token: str = Depends(esquema_oauth)):
    """
    Obtiene estadísticas generales para mostrar en un dashboard.
    """
    # Contar documentos totales
    total_documentos = await conn["documentos"].count_documents({})
    
    # Obtener documentos por categoría
    pipeline_categorias = [
        {"$group": {"_id": "$categoria", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    categorias = await conn["documentos"].aggregate(pipeline_categorias).to_list(20)
    documentos_por_categoria = {cat["_id"]: cat["count"] for cat in categorias if cat["_id"]}
    
    # Obtener documentos por idioma
    pipeline_idiomas = [
        {"$group": {"_id": "$idioma", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    idiomas = await conn["documentos"].aggregate(pipeline_idiomas).to_list(20)
    documentos_por_idioma = {idioma["_id"]: idioma["count"] for idioma in idiomas if idioma["_id"]}
    
    # En un sistema real, obtendríamos los documentos más vistos de una tabla de estadísticas
    # Por ahora, devolvemos algunos documentos aleatorios
    documentos = await conn["documentos"].find().to_list(20)
    documentos_mas_vistos = []
    for doc in documentos[:5]:
        documentos_mas_vistos.append({
            "id": doc.get("_id"),
            "titulo": doc.get("titulo", "Sin título"),
            "autor": doc.get("autor", "Sin autor"),
            "vistas": random.randint(50, 500)
        })
    
    # Simular usuarios más activos
    usuarios_mas_activos = [
        {"id": f"user_{i}", "nombre": f"Usuario {i}", "documentos_creados": random.randint(5, 30), "acciones": random.randint(20, 100)}
        for i in range(1, 6)
    ]
    
    # Documentos recientes (los mismos documentos pero con fecha simulada)
    documentos_recientes = []
    for i, doc in enumerate(documentos[:8]):
        dias_atras = random.randint(0, 14)
        fecha_creacion = (datetime.now() - timedelta(days=dias_atras)).isoformat()
        documentos_recientes.append({
            "id": doc.get("_id"),
            "titulo": doc.get("titulo", "Sin título"),
            "autor": doc.get("autor", "Sin autor"),
            "fecha_creacion": fecha_creacion
        })
    
    # Ordenar por fecha más reciente
    documentos_recientes.sort(key=lambda x: x["fecha_creacion"], reverse=True)
    
    estadisticas = DatosEstadisticos(
        total_documentos=total_documentos,
        documentos_por_categoria=documentos_por_categoria,
        documentos_por_idioma=documentos_por_idioma,
        documentos_mas_vistos=documentos_mas_vistos,
        usuarios_mas_activos=usuarios_mas_activos,
        documentos_recientes=documentos_recientes
    )
    
    return estadisticas
