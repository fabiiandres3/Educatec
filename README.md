# Django Starter

Plantilla base para proyectos Django.

## 1. Clonar el proyecto

```bash
git clone <url-del-repositorio>
cd mi_parte
```

## 2. Crear entorno virtual

```bash
python -m venv env
```

## 3. Activar entorno virtual

### Windows

```bash
env\Scripts\activate
```

### Linux / Mac

```bash
source env/bin/activate
```

## 4. Instalar dependencias

Si existe el archivo requirements.txt:

```bash
pip install -r requirements.txt
```

O instalar manualmente.:

```bash
pip install django
pip install django-allauth
pip install PyJWT
pip install cryptography
pip install django-embed-video
pip install pillow
pip install reportlab
pip install openpyxl
pip install django-extensions
pip install pydotplus
```

## 5. Instalar Graphviz (requerido por django-extensions)

`django-extensions` usa el comando `graph_models` para generar diagramas del
modelo de datos, y este necesita el programa **Graphviz** instalado en el
sistema (no se instala con pip).

1. Descarga la versión ZIP desde el sitio oficial:
   👉 https://graphviz.org/download/
2. Extrae el contenido en una carpeta de tu preferencia (evita nombres con
   espacios o caracteres especiales, ejemplo: `C:\Graphviz`).
3. Agrega Graphviz al PATH (solo para la sesión actual de la terminal):

   **Windows (CMD):**
   ```bash
   set PATH=C:\Graphviz\bin;%PATH%
   ```
   Ajusta la ruta según la ubicación donde hayas descomprimido Graphviz.

4. Verifica la instalación:
   ```bash
   dot -V
   ```
   Deberías ver algo como `dot - graphviz version 15.0.0 (...)`.

> Nota: si cierras la terminal, la variable PATH configurada con `set` se
> pierde y debes repetir el paso 3. Si quieres que sea permanente, agrégala
> desde "Variables de entorno del sistema" en Windows.

## 6. Agregar `django_extensions` a `INSTALLED_APPS`

En `settings.py`, agrega la app (una sola vez, sin duplicarla):

```python
INSTALLED_APPS = [
    ...
    'django_extensions',
]
```

## 7. Crear migraciones

```bash
python manage.py makemigrations
```

## 8. Aplicar migraciones

```bash
python manage.py migrate
```

## 9. Crear superusuario

```bash
python manage.py createsuperuser
```

## 10. Ejecutar servidor

```bash
python manage.py runserver
```

Abrir en el navegador:

```text
http://127.0.0.1:8000/
```

## Dependencias utilizadas

- Django
- django-allauth
- django-embed-video
- Pillow
- ReportLab
- OpenPyXL
- django-extensions
- pydotplus
- Graphviz (programa externo, no se instala con pip)

## Generar requirements.txt

Después de instalar todas las librerías:

```bash
pip freeze > requirements.txt
```

## Actualizar requirements.txt

Cada vez que instales una nueva librería:

```bash
pip freeze > requirements.txt
```

## Reporte de notas (Excel y PDF)

Para que funcionen los reportes:

```bash
pip install reportlab openpyxl
```

o

```bash
pip install -r requirements.txt
```

## Generar diagrama del modelo de datos

Una vez instalado Graphviz y `django-extensions` (ver pasos 5 y 6):

```bash
python manage.py graph_models -a -o diagrama.png
```

Esto genera una imagen `diagrama.png` con el diagrama de todos los modelos
de la aplicación.

## Documentacion Final del proyecto

```bash
https://docs.google.com/document/d/1IvvAGxMQbhCuh6kNDvXS1nsNnK6QicE6Iild1zFYRLI/edit?usp=sharing
```