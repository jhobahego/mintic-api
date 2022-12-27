from pydantic import BaseModel, EmailStr
from typing import Union

class Token(BaseModel):
    access_token: str
    tipo_token: str


class TokenData(BaseModel):
    correo: Union[EmailStr, None] = None