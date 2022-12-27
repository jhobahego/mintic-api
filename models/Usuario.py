from typing import Optional, Union
from pydantic import Field, EmailStr, BaseModel
from bson import ObjectId
from models.Id import PyObjectId


class Usuario(BaseModel):
    usuario_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombres: str = Field(...)
    apellidos: str = Field(...)
    correo: EmailStr = Field(...)
    contra: str = Field(...)
    pais: str = Field(...)
    ciudad: str = Field(...)
    inactivo: Union[bool, None] = Field(default=False)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "nombres": "Jane Doe",
                "apellidos": "hernandez gomez",
                "correo": "jdoe@example.com",
                "contra": "pass123",
                "pais": "Colombia",
                "ciudad": "Betulia",
                "inactivo": True
            }
        }


class ActualizarUsuario(BaseModel):
    nombres: Optional[str]
    apellidos: Optional[str]
    correo: Optional[EmailStr]
    contra: Optional[str]
    pais: Optional[str]
    ciudad: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "nombres": "Jane Doe",
                "apellidos": "hernandez gomez",
                "correo": "jdoe@example.com",
                "contra": "pass123",
                "pais": "Colombia",
                "ciudad": "Betulia",
            }
        }
