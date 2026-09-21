# Generated manually to match the project's current migration graph.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("alumnos", "0006_remove_alumnos_codigo"),
        ("docentes", "0007_alter_asignaciondocente_options_and_more"),
        ("horario", "0004_remove_horario_activo_horario_clase_horario_curso_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContenidoPedagogico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("competencias", models.TextField(blank=True)),
                ("contenidos", models.TextField(blank=True)),
                ("logros", models.TextField(blank=True)),
                ("dificultades_generales", models.TextField(blank=True)),
                ("recomendaciones", models.TextField(blank=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("asignacion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contenidos_boletin", to="docentes.asignaciondocente")),
                ("periodo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contenidos_boletin", to="horario.periodo")),
            ],
            options={"verbose_name": "Contenido pedagógico", "verbose_name_plural": "Contenidos pedagógicos", "ordering": ["periodo__anio", "periodo__numero", "asignacion__id"]},
        ),
        migrations.CreateModel(
            name="ObservacionBoletin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("observacion", models.TextField(blank=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("alumno", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="observaciones_boletin", to="alumnos.alumnos")),
                ("contenido", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="observaciones", to="boletin.contenidopedagogico")),
            ],
            options={"verbose_name": "Observación de boletín", "verbose_name_plural": "Observaciones de boletín"},
        ),
        migrations.AddConstraint(model_name="contenidopedagogico", constraint=models.UniqueConstraint(fields=("asignacion", "periodo"), name="contenido_boletin_unico_por_asignacion_periodo")),
        migrations.AddConstraint(model_name="observacionboletin", constraint=models.UniqueConstraint(fields=("contenido", "alumno"), name="observacion_boletin_unica_por_alumno_contenido")),
    ]
