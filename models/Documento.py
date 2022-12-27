from pydantic import BaseModel, Field
from typing import Text, Optional
from models.Id import PyObjectId
from bson import ObjectId

class Documento(BaseModel):
    documento_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    tipo_documento: str = Field(...)
    autor: str = Field(...)
    titulo: str = Field(...)
    descripcion: Text = Field(...)
    categoria: str = Field(...)
    stock: int = Field(...)
    precio: int = Field(...)
    editorial: str = Field(...)
    idioma: str = Field(...)
    paginas: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "tipo_documento": "digital",
                "autor": "Robert C. Martin",
                "titulo": "clean code",
                "descripcion": "un libro para aprender codigo",
                "categoria": "desarrollo de software",
                "stock": "12",
                "precio": "40",
                "editorial": "betulia-editoriales",
                "idioma": "ingles",
                "paginas": "125",
            }
        }


class ActualizarDocumento(BaseModel):
    tipo_documento: Optional[str]
    autor: Optional[str]
    titulo: Optional[str]
    descripcion: Optional[Text]
    categoria: Optional[str]
    stock: Optional[int]
    precio: Optional[int]
    editorial: Optional[str]
    idioma: Optional[str]
    paginas: Optional[int]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "tipo_documento": "digital",
                "autor": "Robert C. Martin",
                "titulo": "clean code",
                "descripcion": "un libro para aprender codigo",
                "categoria": "desarrollo de software",
                "stock": "12",
                "precio": "40",
                "editorial": "betulia-editoriales",
                "idioma": "ingles",
                "paginas": "125",
            }
        }