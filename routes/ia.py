from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
import time
from datetime import datetime
import random  # Simulación - en producción usar bibliotecas de ML/AI
import os

from config.db import conn
from models.IA import (
    ConsultaBusquedaSemantica,
    RespuestaBusquedaSemantica,
    ResultadoBusqueda,
    SolicitudTraduccion,
    ResultadoOCR,
    DocumentoEtiquetas,
    EtiquetaIA
)
from auth.autenticacion import esquema_oauth

ia = APIRouter(prefix="/ia", tags=["Inteligencia Artificial"])


@ia.post("/clasificar", response_description="Documento clasificado automáticamente")
async def clasificar_documento(documento_id: str, token: str = Depends(esquema_oauth)):
    """
    Clasifica automáticamente un documento basándose en su contenido utilizando IA.
    """
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": documento_id})
    if not documento:
        raise HTTPException(status_code=404, detail=f"Documento con ID {documento_id} no encontrado")
    
    # Categorías predefinidas para clasificación
    categorias = [
        "tecnología", "ciencia", "literatura", "negocios", 
        "arte", "medicina", "derecho", "ingeniería", "educación"
    ]
    
    # En un sistema real, aquí se llamaría a un modelo de ML/IA para clasificar
    # Por ahora, simulamos la respuesta
    clasificacion = random.choice(categorias)
    confianza = round(random.uniform(0.65, 0.98), 2)
    
    # Guardar la clasificación en la base de datos
    clasificacion_doc = {
        "documento_id": documento_id,
        "clasificacion": clasificacion,
        "confianza": confianza,
        "fecha_clasificacion": datetime.now().isoformat(),
        "metodo": "auto-IA"
    }
    
    await conn["clasificaciones"].insert_one(clasificacion_doc)
    
    # Si la confianza es alta, actualizar la categoría del documento
    if confianza > 0.85:
        await conn["documentos"].update_one(
            {"_id": documento_id},
            {"$set": {"categoria": clasificacion}}
        )
    
    return {"documento_id": documento_id, "clasificacion": clasificacion, "confianza": confianza}


@ia.post("/ocr", response_description="Texto extraído del documento")
async def extraer_texto_documento(
    archivo: UploadFile = File(...), 
    token: str = Depends(esquema_oauth)
):
    """
    Extrae texto de un documento utilizando OCR (Reconocimiento Óptico de Caracteres).
    """
    # Verificar que es un tipo de archivo permitido
    extensiones_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
    ext = os.path.splitext(archivo.filename)[1].lower()
    
    if ext not in extensiones_permitidas:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no soportado. Extensiones permitidas: {', '.join(extensiones_permitidas)}"
        )
    
    # En un sistema real, aquí se procesaría el archivo con una biblioteca de OCR
    # Por ahora, simulamos la respuesta
    tiempo_espera = random.uniform(1.0, 3.0)  # Simular tiempo de procesamiento
    time.sleep(tiempo_espera)
    
    # Generar texto simulado basado en el tipo de documento
    if ext == '.pdf':
        texto_simulado = f"Contenido extraído del PDF: {archivo.filename}. Este documento parece contener información sobre..."
    else:
        texto_simulado = f"Texto detectado en la imagen: {archivo.filename}. Se identifican varios párrafos y tablas..."
    
    # Simular metadatos extraídos
    metadatos = {
        "num_paginas": random.randint(1, 30),
        "idioma_detectado": random.choice(["es", "en", "fr"]),
        "tiene_tablas": random.choice([True, False]),
        "tiene_imagenes": random.choice([True, False]),
    }
    
    # Simular nivel de confianza
    confianza = round(random.uniform(0.70, 0.95), 2)
    
    # Crear un ID único (en un caso real, se guardaría en la DB)
    doc_id = f"ocr_{int(time.time())}"
    
    resultado = ResultadoOCR(
        documento_id=doc_id,
        texto_extraido=texto_simulado,
        metadatos_extraidos=metadatos,
        confianza=confianza
    )
    
    return resultado


@ia.post("/busqueda-semantica", response_model=RespuestaBusquedaSemantica)
async def busqueda_semantica(
    consulta: ConsultaBusquedaSemantica = Body(...),
    token: str = Depends(esquema_oauth)
):
    """
    Realiza una búsqueda semántica en los documentos utilizando procesamiento de lenguaje natural.
    """
    start_time = time.time()
    
    # En un sistema real, aquí procesaríamos la consulta con NLP y vectorizaríamos
    # Por ahora, simplemente buscamos palabras clave en los documentos
    
    # Obtener todos los documentos de la base de datos
    todos_documentos = await conn["documentos"].find().to_list(1000)
    
    # Palabras clave de la consulta (en un sistema real se usaría embedding)
    palabras_clave = consulta.query.lower().split()
    
    resultados = []
    for doc in todos_documentos:
        # Calcular relevancia simulada basada en coincidencias
        relevancia = 0
        titulo = doc.get("titulo", "").lower()
        descripcion = doc.get("descripcion", "").lower()
        
        for palabra in palabras_clave:
            if palabra in titulo:
                relevancia += 0.5
            if palabra in descripcion:
                relevancia += 0.3
                
        # Solo incluir documentos con alguna relevancia
        if relevancia > 0:
            fragmento = f"{descripcion[:100]}..." if len(descripcion) > 100 else descripcion
            
            resultados.append(
                ResultadoBusqueda(
                    documento_id=doc.get("_id"),
                    titulo=doc.get("titulo"),
                    relevancia=round(relevancia, 2),
                    fragmento=fragmento
                )
            )
    
    # Ordenar por relevancia
    resultados.sort(key=lambda x: x.relevancia, reverse=True)
    
    # Limitar al número de resultados solicitados
    resultados = resultados[:consulta.num_resultados]
    
    tiempo_ejecucion = round(time.time() - start_time, 3)
    
    return RespuestaBusquedaSemantica(
        resultados=resultados,
        tiempo_ejecucion=tiempo_ejecucion,
        total_encontrados=len(resultados)
    )


@ia.post("/traducir", response_description="Documento traducido")
async def traducir_documento(
    solicitud: SolicitudTraduccion = Body(...),
    token: str = Depends(esquema_oauth)
):
    """
    Traduce el contenido de un documento a otro idioma.
    """
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": solicitud.documento_id})
    if not documento:
        raise HTTPException(status_code=404, detail=f"Documento con ID {solicitud.documento_id} no encontrado")
    
    # Verificar que el idioma destino es válido
    idiomas_validos = ["es", "en", "fr", "de", "it", "pt", "ru", "zh", "ja"]
    if solicitud.idioma_destino not in idiomas_validos:
        raise HTTPException(
            status_code=400, 
            detail=f"Idioma no soportado. Idiomas válidos: {', '.join(idiomas_validos)}"
        )
    
    # En un sistema real, aquí llamaríamos a un servicio de traducción
    # Por ahora, simulamos la traducción
    
    # Simular tiempo de procesamiento
    tiempo_espera = random.uniform(0.5, 2.0)
    time.sleep(tiempo_espera)
    
    idioma_origen = documento.get("idioma", "es")
    
    # Crear una versión traducida del título y descripción
    titulo_original = documento.get("titulo", "")
    descripcion_original = documento.get("descripcion", "")
    
    # Simular traducción (agregando un prefijo al texto original)
    titulo_traducido = f"[Traducido a {solicitud.idioma_destino}] {titulo_original}"
    descripcion_traducida = f"[Traducido a {solicitud.idioma_destino} desde {idioma_origen}] {descripcion_original}"
    
    return {
        "documento_id": solicitud.documento_id,
        "idioma_origen": idioma_origen,
        "idioma_destino": solicitud.idioma_destino,
        "titulo_original": titulo_original,
        "titulo_traducido": titulo_traducido,
        "descripcion_original": descripcion_original,
        "descripcion_traducida": descripcion_traducida,
        "nota": "Esta es una traducción automática y puede contener errores."
    }


@ia.post("/etiquetar", response_description="Documento etiquetado automáticamente")
async def etiquetar_documento(documento_id: str, token: str = Depends(esquema_oauth)):
    """
    Genera etiquetas automáticamente para un documento utilizando IA.
    """
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": documento_id})
    if not documento:
        raise HTTPException(status_code=404, detail=f"Documento con ID {documento_id} no encontrado")
    
    # Obtener texto y metadatos del documento
    titulo = documento.get("titulo", "")
    descripcion = documento.get("descripcion", "")
    categoria = documento.get("categoria", "")
    autor = documento.get("autor", "")
    
    # Lista de posibles etiquetas basadas en el contenido
    # En un sistema real, aquí se usaría NLP para extraer palabras clave
    posibles_etiquetas = []
    
    # Agregar categoría como etiqueta
    if categoria:
        posibles_etiquetas.append(categoria)
    
    # Agregar autor como etiqueta
    if autor:
        posibles_etiquetas.append(autor)
    
    # Agregar palabras del título (simulación simplificada)
    for palabra in titulo.split():
        if len(palabra) > 4:  # Solo palabras relevantes
            posibles_etiquetas.append(palabra.lower())
    
    # Agregar palabras de la descripción (simulación simplificada)
    for palabra in descripcion.split():
        if len(palabra) > 5 and palabra.lower() not in [p.lower() for p in posibles_etiquetas]:
            posibles_etiquetas.append(palabra.lower())
    
    # Seleccionar un subconjunto aleatorio de etiquetas (3-7)
    num_etiquetas = min(random.randint(3, 7), len(posibles_etiquetas))
    etiquetas_seleccionadas = random.sample(posibles_etiquetas, num_etiquetas)
    
    # Crear objetos EtiquetaIA con nivel de confianza
    etiquetas_ia = []
    for etiqueta in etiquetas_seleccionadas:
        confianza = round(random.uniform(0.70, 0.98), 2)
        etiquetas_ia.append(EtiquetaIA(nombre=etiqueta, confianza=confianza))
    
    # Ordenar por confianza
    etiquetas_ia.sort(key=lambda x: x.confianza, reverse=True)
    
    # Guardar en la base de datos
    etiquetas_doc = {
        "documento_id": documento_id,
        "etiquetas": [{"nombre": e.nombre, "confianza": e.confianza} for e in etiquetas_ia],
        "fecha_generacion": datetime.now().isoformat(),
    }
    
    # Actualizar o insertar
    await conn["etiquetas_ia"].update_one(
        {"documento_id": documento_id},
        {"$set": etiquetas_doc},
        upsert=True
    )
    
    return DocumentoEtiquetas(documento_id=documento_id, etiquetas=etiquetas_ia)
