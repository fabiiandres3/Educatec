from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eventos", "0002_rename_hora_evento_hora_fin_evento_hora_inicio"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evento",
            name="publico",
            field=models.CharField(
                choices=[
                    ("todos", "Todos"),
                    ("alumnos", "Alumnos"),
                    ("docentes", "Docentes"),
                    ("acudientes", "Acudientes"),
                ],
                default="todos",
                max_length=20,
            ),
        ),
    ]
