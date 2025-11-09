# Proyecto EV3: Sistema de Gestión "Dulcería Lilis"

[cite_start]Aplicación web desarrollada en Django para la asignatura "Programación Back End" (T13041), basada en el proyecto de "Proyecto Integrado"[cite: 552].

## [cite_start]Descripción Breve del Proyecto [cite: 567]

Este sistema es un panel de gestión interna (backend) para la "Dulcería Lilis". Permite a los administradores autenticados gestionar todos los módulos maestros y transaccionales del negocio.

**Módulos Implementados:**
* Autenticación (Login, Logout, Reseteo de Contraseña)
* CRUD de Productos (con pestañas)
* CRUD de Proveedores (con pestañas)
* CRUD de Usuarios (con roles y permisos)
* CRUD de Categorías y Marcas
* Módulo de Movimientos de Inventario (con pestañas)

## [cite_start]Instrucciones de Instalación y Ejecución [cite: 568]

1.  **Clonar/Descargar:** Obtener el código fuente.
2.  **Entorno Virtual:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Base de Datos (MySQL):**
    * Asegurarse de tener un servidor MySQL (WAMP/XAMPP) corriendo.
    * Crear una base de datos vacía (ej. `dulceria_db`).
    * Verificar que `dulceria_project/settings.py` tenga las credenciales correctas.
5.  **Migraciones:**
    ```bash
    python manage.py makemigrations catalogo gestion
    python manage.py migrate
    ```
6.  **Crear Superusuario:**
    ```bash
    python manage.py createsuperuser
    ```
7.  **(¡Importante!) Asignar Rol de Administrador:**
    ```bash
    python manage.py shell
    >>> from gestion.models import CustomUser
    >>> u = CustomUser.objects.get(username='tu_usuario_creado')
    >>> u.rol = CustomUser.Roles.ROOT
    >>> u.save()
    >>> exit()
    ```
8.  **Ejecutar Servidor[cite: 569]:**
    ```bash
    python manage.py runserver
    ```

## [cite_start]Credenciales de Prueba del Sistema [cite: 568]

* **Usuario:** `lilis`
* **Contraseña:** `Ventana#123`