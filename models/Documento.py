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
    imagen: str = Field(...)
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
                "imagen": "https://www.google.com/imgres?imgurl=https%3A%2F%2Fimages.cdn2.buscalibre.com%2Ffit-in%2F360x360%2F03%2F1a%2F031af9d7e401bb2d08911c317ecbedad.jpg&tbnid=ivGrcngPn4jHBM&vet=12ahUKEwjm6KqEieL-AhW9lIQIHReWBZsQMygAegUIARDeAQ..i&imgrefurl=https%3A%2F%2Fwww.buscalibre.com.co%2Flibro-the-pragmatic-programmer-your-journey-to-mastery-20th-anniversary-edition-libro-en-ingles%2F9780135957059%2Fp%2F52121486&docid=9ey-sNX8FfSKVM&w=275&h=360&q=the%20pragmatic%20programmer&ved=2ahUKEwjm6KqEieL-AhW9lIQIHReWBZsQMygAegUIARDeAQ",
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