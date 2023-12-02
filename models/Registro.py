from pydantic import ConfigDict, BaseModel, Field
from typing import Optional

# from models.Id import PyObjectId


class Registro(BaseModel):
    # registro_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    id: Optional[str] = Field(alias="_id", default=None)
    id_cliente: str = Field(...)
    nombre_cliente: str = Field(...)
    id_documento: str = Field(...)
    titulo_documento: str = Field(...)
    imagen: str = Field(...)
    tipo_de_adquisicion: str = Field(...)
    cantidad: int = Field(...)
    activo: bool = Field(...)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id_cliente": "63afc7da089fe226352a222",
                "nombre_cliente": "Jhon Hernandez",
                "id_documento": "a9f63fc7d4a089fe22635224",
                "titulo_documento": "Clean code",
                "imagen": "https:/img/clean_code.png",
                "tipo_de_adquisicion": "prestamo",
                "cantidad": 1,
                "activo": True,
            }
        },
    )
