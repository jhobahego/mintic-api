import google.generativeai as genai
from typing import Optional
from asyncio import Semaphore
from dotenv import load_dotenv
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini_service")

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API KEY: {GEMINI_API_KEY}")


class GeminiService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"
        self.generation_model = genai.GenerativeModel(self.model_name)
        self.semaphore = Semaphore(5)
        logger.info(f"Usando modelo: {self.model_name}")

    async def get_embedding(self, text: str) -> list[float]:
        async with self.semaphore:
            try:
                # Asegurar que el texto no esté vacío
                text = text.strip() or "contenido vacío"
                response = genai.embed_content(
                    model="models/embedding-001", content=text
                )
                return response["embedding"]
            except Exception as e:
                logger.error(f"Error obteniendo embedding: {str(e)}")
                # Devolver un embedding vacío en caso de error
                return [0.0] * 768  # Dimensión típica de embeddings

    async def semantic_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            logger.warning("Comparando textos vacíos - devolviendo similitud cero")
            return 0.0

        try:
            embedding1 = await self.get_embedding(text1)
            embedding2 = await self.get_embedding(text2)
            similarity = self._cosine_similarity(embedding1, embedding2)
            logger.info(
                f"Similitud calculada: {similarity:.4f} entre textos: '{text1[:30]}...' y '{text2[:30]}...'"
            )
            return similarity
        except Exception as e:
            logger.error(f"Error calculando similitud: {str(e)}")
            return 0.0

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5

            # Evitar división por cero
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)
        except Exception as e:
            logger.error(f"Error en cálculo de similitud del coseno: {str(e)}")
            return 0.0

    async def generate_content(self, query: str, context: Optional[str] = None) -> str:
        """
        Genera una respuesta basada en la consulta y el contexto proporcionado.

        Args:
            query: La consulta o pregunta del usuario
            context: Contexto adicional para informar la respuesta

        Returns:
            La respuesta generada por Gemini
        """
        try:
            # Construir el prompt con instrucciones y contexto
            prompt = "Eres un asistente experto en gestión documental que ayuda a encontrar información."

            if context:
                prompt += f"\n\nContexto de documentos disponibles:\n{context}"

            prompt += f"\n\nConsulta del usuario: {query}\n\nResponde de manera clara, concisa y basándote solo en la información proporcionada en el contexto."

            logger.info(
                f"Enviando prompt a Gemini usando modelo {self.model_name}: {prompt[:100]}..."
            )

            # Llamar a la API de Gemini con manejo de errores mejorado
            try:
                response = self.generation_model.generate_content(prompt)
                return response.text
            except Exception as api_error:
                logger.error(f"Error específico de la API: {str(api_error)}")
                # Si el error es por longitud, intentar con un prompt más corto
                if "length" in str(api_error).lower():
                    # Acortar el contexto si es muy largo
                    logger.info("Intentando con un contexto más corto")
                    shortened_context = (
                        context[:4000] + "..."
                        if context and len(context) > 4000
                        else context
                    )
                    prompt_short = f"Eres un asistente documental. Consulta: {query}"
                    if shortened_context:
                        prompt_short += f"\nContexto resumido: {shortened_context}"

                    response = self.generation_model.generate_content(prompt_short)
                    return response.text
                else:
                    return f"Error al procesar la consulta: {str(api_error)}"

        except Exception as e:
            logger.error(f"Error generando contenido con Gemini: {str(e)}")
            return f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}"


gemini_service = GeminiService()
