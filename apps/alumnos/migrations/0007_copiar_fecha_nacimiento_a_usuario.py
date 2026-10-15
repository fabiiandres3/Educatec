from django.conf import settings
from django.db import migrations


def copiar_fecha_nacimiento_a_usuario(apps, schema_editor):
    Alumnos = apps.get_model("alumnos", "Alumnos")
    Usuario = apps.get_model(*settings.AUTH_USER_MODEL.split("."))
    database = schema_editor.connection.alias

    registros = (
        Alumnos.objects.using(database)
        .exclude(fecha_nacimiento__isnull=True)
        .values_list("usuario_id", "fecha_nacimiento")
        .iterator()
    )
    for usuario_id, fecha_nacimiento in registros:
        Usuario.objects.using(database).filter(
            pk=usuario_id,
            fecha_nacimiento__isnull=True,
        ).update(fecha_nacimiento=fecha_nacimiento)


class Migration(migrations.Migration):

    dependencies = [
        ("alumnos", "0006_remove_alumnos_codigo"),
        ("user", "0015_usuario_fecha_nacimiento"),
    ]

    operations = [
        migrations.RunPython(
            copiar_fecha_nacimiento_a_usuario,
            migrations.RunPython.noop,
        ),
    ]
