# Perfil del proyecto Educatec

## Descripción

Educatec es una aplicación web de gestión educativa desarrollada con Django. Reúne herramientas para administrar la comunidad escolar, organizar cursos y clases, asignar docentes, gestionar actividades académicas y consultar información de asistencia y desempeño.

## Propósito

Centralizar procesos académicos y de gestión escolar en una plataforma con acceso según el tipo de usuario. La aplicación contempla espacios y funcionalidades para alumnos, docentes y administración.

## Funcionalidades principales

- Gestión de usuarios y autenticación, incluido el inicio de sesión con Google.
- Administración de alumnos y docentes.
- Organización de cursos y clases.
- Gestión de tareas y actividades.
- Registro y consulta de asistencia.
- Manejo de horarios y eventos.
- Registro de calificaciones y generación de boletines.
- Paneles para presentar información según el área de uso.
- Módulo de soporte.
- Generación de reportes en PDF y Excel (ReportLab y OpenPyXL).

## Tecnologías

- **Backend:** Python y Django.
- **Autenticación social:** django-allauth y proveedor Google.
- **Base de datos configurada:** SQLite.
- **Frontend:** plantillas de Django y archivos estáticos.
- **Procesamiento de documentos y datos:** ReportLab, OpenPyXL y pandas.
- **Recursos multimedia:** Pillow y django-embed-video.
- **Extensiones de desarrollo:** django-extensions y pydotplus; Graphviz se requiere para generar diagramas de modelos.
- **Archivos estáticos en despliegue:** WhiteNoise.

## Aplicaciones Django

`alumnos`, `user`, `soporte`, `paneles`, `clases`, `cursos`, `tareas`, `docentes`, `asistencia`, `eventos`, `horario`, `calificaciones` y `boletin`.

## Configuración regional

- **Idioma:** español (`es`).
- **Zona horaria:** `America/Bogota`.
- **Zona horaria activa:** sí (`USE_TZ`).

## Componentes de configuración

- Usuario personalizado: `apps.user.Usuario`.
- Autenticación Google configurada mediante django-allauth.
- Archivos cargados por usuarios en el directorio `media/`.
- Archivos estáticos recopilados en `staticfiles/`.
- Correo SMTP configurado para Gmail; las credenciales deben mantenerse en variables de entorno y fuera de archivos versionados.

## Comandos habituales

Desde la carpeta que contiene `manage.py`:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Para generar el diagrama de modelos (con django-extensions y Graphviz instalados):

```bash
python manage.py graph_models -a -o diagrama.png
```

## Estado de la información

Este perfil resume la estructura y configuración visibles en el proyecto. La configuración de despliegue, los roles exactos y los permisos de cada tipo de usuario deben documentarse según las reglas implementadas y el entorno donde se publique la aplicación.
