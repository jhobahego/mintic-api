# Documentación de la API de MINTIC

## 1. Descripción General

La API de MINTIC es una aplicación web que permite a los usuarios gestionar sus proyectos de manera eficiente. Permite a los usuarios crear, editar y eliminar proyectos, asi como tambien a los usuarios gestionar sus tareas dentro de los proyectos.

### 1. Instalación

Para instalar la API de MINTIC, sigue estos pasos:

```bash
# Navegar al directorio del proyecto
cd /ruta/al/proyecto/mintic-api


# Ejecutar el comando de instalación
pip install -r requirements.txt

# Ejecutar la aplicación
uvicorn main:app --reload
```

# Gestión de Usuarios Administradores

Este documento explica las diferentes formas de crear y gestionar usuarios administradores en el sistema.

## Métodos para Crear Usuarios Administradores

### 1. Creación Automática al Iniciar la Aplicación

La aplicación puede crear automáticamente un usuario administrador si no existe ninguno, utilizando variables de entorno:

```bash
# Agregar estas variables a tu archivo .env o exportarlas en el entorno
INIT_ADMIN=true
ADMIN_EMAIL=admin@miempresa.com
ADMIN_PASSWORD=MiContraseñaSegura123
```

Al iniciar la aplicación con `INIT_ADMIN=true`, se verificará si existe algún administrador. Si no existe, se creará uno con las credenciales especificadas (o valores por defecto si no se proporcionan).

### 2. Usando el Script de Inicialización

Se proporciona un script para crear un administrador predeterminado:

```bash
# Navegar al directorio del proyecto
cd /ruta/al/proyecto/mintic-api

# Ejecutar el script de inicialización
python scripts/init_admin.py
```

Este script verifica si ya existe un administrador y, si no, crea uno con credenciales predeterminadas.

### 3. Creación de Administrador Personalizado

Para crear un administrador con datos personalizados:

```bash
# Navegar al directorio del proyecto
cd /ruta/al/proyecto/mintic-api

# Ejecutar el script con parámetros
python scripts/create_admin.py --nombres "Juan" --apellidos "Pérez" --correo "juan@empresa.com" --contra "ContraseñaSegura123" --pais "Colombia" --ciudad "Medellín"
```
