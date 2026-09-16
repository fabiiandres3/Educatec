from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("docentes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="docente",
            name="telefono",
            field=models.IntegerField(
                "telefono",
                blank=True,
                null=True,
            ),
        ),
    ]