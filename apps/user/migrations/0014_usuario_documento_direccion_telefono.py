from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0013_alter_usuario_first_name_alter_usuario_last_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="documento",
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="usuario",
            name="direccion",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="usuario",
            name="telefono",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
