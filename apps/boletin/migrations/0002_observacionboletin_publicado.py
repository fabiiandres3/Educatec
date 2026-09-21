from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("boletin", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="observacionboletin",
            name="publicado",
            field=models.BooleanField(default=False, help_text="Visible para el alumno dentro de su boletín consolidado."),
        ),
        migrations.AddField(
            model_name="observacionboletin",
            name="publicado_en",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
