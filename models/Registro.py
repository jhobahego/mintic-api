from pydantic import BaseModel, Field
from bson import ObjectId

from models.Id import PyObjectId

class Registro(BaseModel):
    registro_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    id_cliente: str = Field(...)
    id_documento: str = Field(...)
    titulo_documento: str = Field(...)
    tipo_de_adquisicion: str = Field(...)
    cantidad: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "cliente_id": "12352252",
                "documento_id": "12425266353",
                "titulo_documento": "hernandez gomez",
                "tipo_de_adquisicion": "prestamo",
                "cantidad": "124",
            }
        }
