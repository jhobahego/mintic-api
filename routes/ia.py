from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from datetime import datetime
from typing import Optional
import random  # Simulación - en producción usar bibliotecas de ML/AI
import time
import os

from services.gemini_service import gemini_service

from config.db import conn
from models.IA import (
    ConsultaBusquedaSemantica,
    RespuestaAsistente,
    RespuestaBusquedaSemantica,
    ResultadoBusqueda,
    SolicitudAsistente,
    SolicitudTraduccion,
    ResultadoOCR,
    DocumentoEtiquetas,
    EtiquetaIA,
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
        raise HTTPException(
            status_code=404, detail=f"Documento con ID {documento_id} no encontrado"
        )

    # Categorías predefinidas para clasificación
    categorias = [
        "tecnología",
        "ciencia",
        "literatura",
        "negocios",
        "arte",
        "medicina",
        "derecho",
        "ingeniería",
        "educación",
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
        "metodo": "auto-IA",
    }

    await conn["clasificaciones"].insert_one(clasificacion_doc)

    # Si la confianza es alta, actualizar la categoría del documento
    if confianza > 0.85:
        await conn["documentos"].update_one(
            {"_id": documento_id}, {"$set": {"categoria": clasificacion}}
        )

    return {
        "documento_id": documento_id,
        "clasificacion": clasificacion,
        "confianza": confianza,
    }


@ia.post("/ocr", response_description="Texto extraído del documento")
async def extraer_texto_documento(
    archivo: UploadFile = File(...), token: str = Depends(esquema_oauth)
):
    """
    Extrae texto de un documento utilizando OCR (Reconocimiento Óptico de Caracteres).
    """
    # Verificar que es un tipo de archivo permitido
    extensiones_permitidas = [".pdf", ".jpg", ".jpeg", ".png", ".tiff"]

    if archivo.filename is None:
        raise HTTPException(
            status_code=400, detail="No se proporcionó un nombre de archivo"
        )

    ext = os.path.splitext(archivo.filename)[1].lower()

    if ext not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado. Extensiones permitidas: {', '.join(extensiones_permitidas)}",
        )

    # En un sistema real, aquí se procesaría el archivo con una biblioteca de OCR
    # Por ahora, simulamos la respuesta
    tiempo_espera = random.uniform(1.0, 3.0)  # Simular tiempo de procesamiento
    time.sleep(tiempo_espera)

    # Generar texto simulado basado en el tipo de documento
    if ext == ".pdf":
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
        confianza=confianza,
    )

    return resultado


@ia.post("/busqueda-semantica", response_model=RespuestaBusquedaSemantica)
async def busqueda_semantica(
    consulta: ConsultaBusquedaSemantica = Body(...),
    token: str = Depends(esquema_oauth),
    umbral_manual: Optional[float] = None,  # Umbral manual opcional
):
    start_time = time.time()

    # Validar que la consulta no esté vacía
    if not consulta.query.strip():
        raise HTTPException(
            status_code=400, detail="La consulta de búsqueda no puede estar vacía"
        )

    # Validar umbral manual si se proporciona
    if umbral_manual is not None and (umbral_manual < 0.0 or umbral_manual > 1.0):
        raise HTTPException(
            status_code=400, detail="El umbral de relevancia debe estar entre 0 y 1"
        )

    # Obtener todos los documentos de la base de datos
    todos_documentos = await conn["documentos"].find().to_list(1000)

    # Calcular similitud semántica usando Gemini para todos los documentos primero
    documentos_con_relevancia = []

    for doc in todos_documentos:
        # Verificar que el documento tiene contenido para comparar
        titulo = doc.get("titulo", "").strip()
        descripcion = doc.get("descripcion", "").strip()

        if not titulo and not descripcion:
            continue  # Saltar documentos sin contenido textual

        texto_documento = f"{titulo} {descripcion}"

        # Calcular relevancia semántica
        relevancia = await gemini_service.semantic_similarity(
            consulta.query, texto_documento
        )

        documentos_con_relevancia.append(
            {
                "doc": doc,
                "titulo": titulo,
                "descripcion": descripcion,
                "relevancia": relevancia,
            }
        )

    # Si no hay documentos, devolver respuesta vacía
    if not documentos_con_relevancia:
        return RespuestaBusquedaSemantica(
            resultados=[],
            tiempo_ejecucion=round(time.time() - start_time, 3),
            total_encontrados=0,
            mensaje="No se encontraron documentos para evaluar",
        )

    # Ordenar documentos por relevancia de mayor a menor
    documentos_con_relevancia.sort(key=lambda x: x["relevancia"], reverse=True)

    # Aplicar umbral inteligente basado en análisis de brecha si no se proporciona umbral manual
    if umbral_manual is None:
        # Calcular brechas entre relevancia de documentos adyacentes
        brechas = []
        for i in range(1, len(documentos_con_relevancia)):
            brecha = (
                documentos_con_relevancia[i - 1]["relevancia"]
                - documentos_con_relevancia[i]["relevancia"]
            )
            brechas.append({"indice": i, "brecha": brecha})

        # Si hay documentos suficientes para analizar brechas
        if brechas:
            # Ordenar brechas por tamaño (de mayor a menor)
            brechas.sort(key=lambda x: x["brecha"], reverse=True)

            # Encontrar la brecha más significativa entre los primeros n documentos
            # Limitamos la búsqueda a los primeros 5 documentos o el 30% de los resultados
            limite_busqueda = min(5, max(2, int(len(documentos_con_relevancia) * 0.3)))

            brechas_relevantes = [b for b in brechas if b["indice"] <= limite_busqueda]

            if brechas_relevantes:
                # Si se encuentra una brecha significativa (>= 0.05), usarla como punto de corte
                brecha_mayor = brechas_relevantes[0]
                if brecha_mayor["brecha"] >= 0.05:
                    indice_corte = brecha_mayor["indice"]
                    documentos_con_relevancia = documentos_con_relevancia[:indice_corte]
                else:
                    # Si no hay brecha significativa, usar solo el top document con un nivel mínimo de relevancia
                    if documentos_con_relevancia[0]["relevancia"] > 0.7:
                        documentos_con_relevancia = [documentos_con_relevancia[0]]
                    else:
                        # Si ni siquiera el top document es suficientemente relevante, usar 0.65 como umbral
                        documentos_con_relevancia = [
                            d
                            for d in documentos_con_relevancia
                            if d["relevancia"] > 0.65
                        ]
    else:
        # Usar umbral manual si se proporciona
        documentos_con_relevancia = [
            d for d in documentos_con_relevancia if d["relevancia"] > umbral_manual
        ]

    # Convertir a ResultadoBusqueda
    resultados = []
    for doc_info in documentos_con_relevancia:
        doc = doc_info["doc"]
        descripcion = doc_info["descripcion"]
        fragmento = f"{descripcion[:100]}..." if len(descripcion) > 100 else descripcion

        resultados.append(
            ResultadoBusqueda(
                documento_id=doc.get("_id"),
                titulo=doc_info["titulo"],
                relevancia=round(doc_info["relevancia"], 2),
                fragmento=fragmento,
            )
        )

    # Limitar al número de resultados solicitados
    resultados = resultados[: consulta.num_resultados]

    tiempo_ejecucion = round(time.time() - start_time, 3)

    mensaje = None
    if len(resultados) == 0:
        mensaje = "No se encontraron documentos que coincidan con su consulta. Intente con términos más generales."

    return RespuestaBusquedaSemantica(
        resultados=resultados,
        tiempo_ejecucion=tiempo_ejecucion,
        total_encontrados=len(resultados),
        mensaje=mensaje,
    )


@ia.post("/traducir", response_description="Documento traducido")
async def traducir_documento(
    solicitud: SolicitudTraduccion = Body(...), token: str = Depends(esquema_oauth)
):
    """
    Traduce el contenido de un documento a otro idioma.
    """
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": solicitud.documento_id})
    if not documento:
        raise HTTPException(
            status_code=404,
            detail=f"Documento con ID {solicitud.documento_id} no encontrado",
        )

    # Verificar que el idioma destino es válido
    idiomas_validos = ["es", "en", "fr", "de", "it", "pt", "ru", "zh", "ja"]
    if solicitud.idioma_destino not in idiomas_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Idioma no soportado. Idiomas válidos: {', '.join(idiomas_validos)}",
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
        "nota": "Esta es una traducción automática y puede contener errores.",
    }


@ia.post("/etiquetar", response_description="Documento etiquetado automáticamente")
async def etiquetar_documento(documento_id: str, token: str = Depends(esquema_oauth)):
    """
    Genera etiquetas automáticamente para un documento utilizando IA.
    """
    # Verificar que el documento existe
    documento = await conn["documentos"].find_one({"_id": documento_id})
    if not documento:
        raise HTTPException(
            status_code=404, detail=f"Documento con ID {documento_id} no encontrado"
        )

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
        if len(palabra) > 5 and palabra.lower() not in [
            p.lower() for p in posibles_etiquetas
        ]:
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
        "etiquetas": [
            {"nombre": e.nombre, "confianza": e.confianza} for e in etiquetas_ia
        ],
        "fecha_generacion": datetime.now().isoformat(),
    }

    # Actualizar o insertar
    await conn["etiquetas_ia"].update_one(
        {"documento_id": documento_id}, {"$set": etiquetas_doc}, upsert=True
    )

    return DocumentoEtiquetas(documento_id=documento_id, etiquetas=etiquetas_ia)


@ia.post("/asistente", response_model=RespuestaAsistente)
async def consultar_asistente(
    solicitud: SolicitudAsistente = Body(...), token: str = Depends(esquema_oauth)
):
    """
    Consulta al asistente IA que puede responder preguntas basándose en los documentos disponibles.
    """
    start_time = time.time()

    # Validar consulta
    if not solicitud.consulta.strip():
        raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")

    # 1. Buscar documentos relevantes utilizando la búsqueda semántica
    consulta_busqueda = ConsultaBusquedaSemantica(
        query=solicitud.consulta, num_resultados=solicitud.max_documentos_contexto
    )

    resultados_busqueda = await busqueda_semantica(
        consulta=consulta_busqueda,
        token=token,
        umbral_manual=solicitud.umbral_relevancia,
    )

    # 2. Obtener información completa de los documentos relevantes
    documentos_contexto = []
    ids_documentos = []

    for resultado in resultados_busqueda.resultados:
        try:
            documento = await conn["documentos"].find_one(
                {"_id": resultado.documento_id}
            )
            if documento:
                # Extraer información relevante del documento
                info_documento = (
                    f"ID: {documento.get('_id', 'N/A')}\n"
                    f"Título: {documento.get('titulo', 'Sin título')}\n"
                    f"Autor: {documento.get('autor', 'Desconocido')}\n"
                    f"Categoría: {documento.get('categoria', 'Sin categoría')}\n"
                    f"Descripción: {documento.get('descripcion', 'Sin descripción')}\n"
                    f"Editorial: {documento.get('editorial', 'N/A')}\n"
                    f"Idioma: {documento.get('idioma', 'N/A')}\n"
                    f"Páginas: {documento.get('paginas', 'N/A')}\n"
                    f"Relevancia: {resultado.relevancia}\n"
                )
                documentos_contexto.append(info_documento)
                ids_documentos.append(documento.get("_id", "N/A"))
        except Exception as e:
            print(f"Error obteniendo detalles del documento: {str(e)}")

    # 3. Formar el contexto para Gemini
    if documentos_contexto:
        contexto_completo = "=== DOCUMENTOS RELEVANTES ===\n\n" + "\n\n---\n\n".join(
            documentos_contexto
        )
    else:
        contexto_completo = (
            "No se encontraron documentos relevantes para esta consulta."
        )

    # 4. Enviar la consulta a Gemini junto con el contexto
    respuesta = await gemini_service.generate_content(
        query=solicitud.consulta, context=contexto_completo
    )

    tiempo_ejecucion = round(time.time() - start_time, 3)

    return RespuestaAsistente(
        respuesta=respuesta,
        documentos_consultados=ids_documentos,
        tiempo_ejecucion=tiempo_ejecucion,
    )
