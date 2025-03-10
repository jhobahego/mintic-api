import google.generativeai as genai
from decouple import config
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gemini_service")

class GeminiService:
    def __init__(self):
        genai.configure(api_key=config("GEMINI_API_KEY"))

    async def get_embedding(self, text: str) -> list[float]:
        try:
            # Asegurar que el texto no esté vacío
            text = text.strip() or "contenido vacío"
            response = genai.embed_content(model="models/embedding-001", content=text)
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
            logger.info(f"Similitud calculada: {similarity:.4f} entre textos: '{text1[:30]}...' y '{text2[:30]}...'")
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

gemini_service = GeminiService()
