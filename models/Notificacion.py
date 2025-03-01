from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum
from datetime import datetime


class TipoNotificacion(str, Enum):
    INFO = "info"
    ALERTA = "alerta"
    ERROR = "error"
    EXITO = "exito"


class EstadoNotificacion(str, Enum):
    NO_LEIDA = "no_leida"
    LEIDA = "leida"
    ARCHIVADA = "archivada"


class Notificacion(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    usuario_id: str
    tipo: TipoNotificacion
    titulo: str
    mensaje: str
    documento_id: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    estado: EstadoNotificacion = EstadoNotificacion.NO_LEIDA
    fecha_lectura: Optional[datetime] = None
    icono: Optional[str] = None
    accion_url: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class ConfiguracionRecordatorio(BaseModel):
    documento_id: str
    titulo_recordatorio: str
    fecha_recordatorio: datetime
    repetir: bool = False
    intervalo_repeticion: Optional[int] = None  # en días
    mensaje: Optional[str] = None
    enviar_email: bool = False
    email_destino: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "documento_id": "645701810b24c99f29187db0",
                "titulo_recordatorio": "Revisar documento",
                "fecha_recordatorio": "2023-12-31T10:00:00",
                "repetir": True,
                "intervalo_repeticion": 7,
                "mensaje": "Es necesario revisar este documento semanalmente",
                "enviar_email": True,
                "email_destino": "usuario@ejemplo.com"
            }
        },
    )


class Recordatorio(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    usuario_id: str
    documento_id: str
    titulo: str
    mensaje: Optional[str] = None
    fecha_programada: datetime
    repetir: bool = False
    intervalo_repeticion: Optional[int] = None  # en días
    proxima_ejecucion: Optional[datetime] = None
    ultima_ejecucion: Optional[datetime] = None
    enviado: bool = False
    activo: bool = True
    enviar_email: bool = False
    email_destino: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
