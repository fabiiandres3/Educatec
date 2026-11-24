from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tareas", "0012_actividadcalificacion_periodo_and_fecha"),
    ]

    operations = [
        migrations.AddField(
            model_name="calificacion",
            name="actualizado_en",
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
        migrations.AddField(
            model_name="calificacionactividad",
            name="actualizado_en",
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
    ]
