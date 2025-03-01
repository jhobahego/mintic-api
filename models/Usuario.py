from typing import Optional, Union
from pydantic import ConfigDict, Field, EmailStr, BaseModel
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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "nombres": "Jane Doe",
                "apellidos": "hernandez gomez",
                "correo": "jdoe@example.com",
                "contra": "pass123",
                "pais": "Colombia",
                "ciudad": "Betulia",
                "inactivo": True,
                "rol": "USER",
            }
        },
    )


class UserResponse(BaseModel):
    usuario_id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombres: str
    apellidos: str
    correo: str
    pais: str
    ciudad: str
    inactivo: bool
    rol: Role

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "nombres": "Jane Doe",
                "apellidos": "Hernandez Gomez",
                "correo": "jdoe@example.com",
                "pais": "Colombia",
                "ciudad": "Betulia",
                "inactivo": False,
                "rol": "USER",
            }
        },
    )


class ActualizarUsuario(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    correo: Optional[EmailStr] = None
    contra: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    inactivo: Optional[bool] = None
    rol: Optional[Role] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "nombres": "Jane Doe",
                "apellidos": "hernandez gomez",
                "correo": "jdoe@example.com",
                "contra": "pass123",
                "pais": "Colombia",
                "ciudad": "Betulia",
                "inactivo": False,
                "rol": "USER",
            }
        },
    )
