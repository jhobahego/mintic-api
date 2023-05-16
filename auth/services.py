from fastapi import Depends, HTTPException, status
from models.Usuario import Usuario, Role
from .autenticacion import obtener_usuario_activo_actual

def usuario_rol_requerido(usuario: Usuario = Depends(obtener_usuario_activo_actual)):
    if usuario["rol"] != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="acceso denegado"
        )