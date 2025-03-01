from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Text


class DocumentoClasificacion(BaseModel):
    documento_id: str
    contenido: Text
    clasificacion_sugerida: Optional[str] = None
    confianza: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class EtiquetaIA(BaseModel):
    nombre: str
    confianza: float


class DocumentoEtiquetas(BaseModel):
    documento_id: str
    etiquetas: List[EtiquetaIA] = []

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class ConsultaBusquedaSemantica(BaseModel):
    query: str
    num_resultados: int = 5

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "documentos sobre programación que hablen de Python",
                "num_resultados": 5
            }
        },
    )


class ResultadoBusqueda(BaseModel):
    documento_id: str
    titulo: str
    relevancia: float
    fragmento: Optional[str] = None


class RespuestaBusquedaSemantica(BaseModel):
    resultados: List[ResultadoBusqueda] = []
    tiempo_ejecucion: float
    total_encontrados: int

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class SolicitudTraduccion(BaseModel):
    documento_id: str
    idioma_destino: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "documento_id": "645701810b24c99f29187db0",
                "idioma_destino": "es"
            }
        },
    )


class ResultadoOCR(BaseModel):
    documento_id: str
    texto_extraido: Text
    metadatos_extraidos: dict = {}
    confianza: float

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
