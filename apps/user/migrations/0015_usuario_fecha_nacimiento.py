from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0014_usuario_documento_direccion_telefono"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="fecha_nacimiento",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="fecha de nacimiento",
            ),
        ),
    ]
