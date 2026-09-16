from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("docentes", "0003_asignaciondocente"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="docente",
            name="clase",
        ),
        migrations.RemoveField(
            model_name="docente",
            name="curso",
        ),
    ]