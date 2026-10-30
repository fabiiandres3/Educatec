from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("docentes", "0007_alter_asignaciondocente_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="docente",
            name="telefono",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
