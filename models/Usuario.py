from typing import Optional, Union
from pydantic import Field, EmailStr, BaseModel
from bson import ObjectId
from models.Id import PyObjectId

from enum import Enum


class Role(str, Enum):
    USUARIO = "USER"
    ADMIN = "ADMIN"


class Usuario(BaseModel):
    usuario_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombres: str = Field(...)
    apellidos: str = Field(...)
    correo: EmailStr = Field(...)
    contra: str = Field(...)
    pais: str = Field(...)
    ciudad: str = Field(...)
    inactivo: Union[bool, None] = Field(default=False)
    rol: Optional[Role] = Field(default=Role.USUARIO)

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
                "inactivo": True,
                "rol": "USER"
            }
        }


class ActualizarUsuario(BaseModel):
    nombres: Optional[str]
    apellidos: Optional[str]
    correo: Optional[EmailStr]
    contra: Optional[str]
    pais: Optional[str]
    ciudad: Optional[str]
    inactivo: Optional[bool]
    rol: Optional[Role]

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
                "inactivo": False,
                "rol": "USER"
            }
        }
