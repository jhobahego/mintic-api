from pydantic import ConfigDict, BaseModel, Field
from typing import Text, Optional
# from models.Id import PyObjectId


class Documento(BaseModel):
    # documento_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    id: Optional[str] = Field(alias="_id", default=None)
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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "645701810b24c99f29187db0",
                "tipo_documento": "digital",
                "autor": "Robert C. Martin",
                "titulo": "clean code",
                "descripcion": "un libro para aprender codigo",
                "imagen": "https://www.google.com/images/clean_code.jpg",
                "categoria": "desarrollo de software",
                "stock": "12",
                "precio": "40",
                "editorial": "betulia-editoriales",
                "idioma": "ingles",
                "paginas": "125",
            }
        },
    )


class ActualizarDocumento(BaseModel):
    tipo_documento: Optional[str] = None
    autor: Optional[str] = None
    titulo: Optional[str] = None
    descripcion: Optional[Text] = None
    categoria: Optional[str] = None
    stock: Optional[int] = None
    precio: Optional[int] = None
    editorial: Optional[str] = None
    idioma: Optional[str] = None
    paginas: Optional[int] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
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
        },
    )
