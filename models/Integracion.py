from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ProveedorNube(str, Enum):
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"
    OTRO = "otro"


class EstadoSincronizacion(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"


class ConfiguracionIntegracion(BaseModel):
    proveedor: ProveedorNube
    token_acceso: str
    carpeta_id: Optional[str] = None
    sincronizacion_automatica: bool = False
    intervalo_sincronizacion: Optional[int] = None  # en minutos

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "proveedor": "google_drive",
                "token_acceso": "ya29.a0AfH6SMBgkVV...",
                "carpeta_id": "1x2y3z4...",
                "sincronizacion_automatica": True,
                "intervalo_sincronizacion": 60
            }
        },
    )


class SincronizacionNube(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    usuario_id: str
    proveedor: ProveedorNube
    documento_id: str
    documento_nombre: str
    id_en_nube: Optional[str] = None
    url_en_nube: Optional[str] = None
    estado: EstadoSincronizacion = EstadoSincronizacion.PENDIENTE
    ultima_sincronizacion: Optional[datetime] = None
    proxima_sincronizacion: Optional[datetime] = None
    error: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class DocumentoExportacion(BaseModel):
    documento_id: str
    formato: str  # pdf, docx, txt, etc.

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "documento_id": "645701810b24c99f29187db0",
                "formato": "pdf"
            }
        },
    )


class DatosEstadisticos(BaseModel):
    total_documentos: int
    documentos_por_categoria: Dict[str, int]
    documentos_por_idioma: Dict[str, int]
    documentos_mas_vistos: List[Dict[str, Any]]
    usuarios_mas_activos: List[Dict[str, Any]]
    documentos_recientes: List[Dict[str, Any]]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
