from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cursos", "0001_initial"),
        ("docentes", "0004_remove_docente_clase_remove_docente_curso"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="asignaciondocente",
            options={},
        ),

        migrations.AlterModelOptions(
            name="docente",
            options={},
        ),

        migrations.AddField(
            model_name="asignaciondocente",
            name="curso",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="asignaciones_docentes",
                to="cursos.cursos",
            ),
        ),

        migrations.AlterField(
            model_name="docente",
            name="direccion",
            field=models.CharField(
                max_length=255
            ),
        ),

        migrations.AlterField(
            model_name="docente",
            name="telefono",
            field=models.IntegerField(
                blank=True,
                null=True
            ),
        ),

        migrations.RemoveField(
            model_name="asignaciondocente",
            name="clase",
        ),
    ]