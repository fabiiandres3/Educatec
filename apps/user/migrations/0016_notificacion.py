from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0015_usuario_fecha_nacimiento"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notificacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=180)),
                ("mensaje", models.TextField()),
                ("url", models.CharField(blank=True, max_length=500)),
                ("tipo", models.CharField(default="general", max_length=30)),
                ("leida", models.BooleanField(default=False)),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificaciones", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-creada_en"]},
        ),
        migrations.AddIndex(
            model_name="notificacion",
            index=models.Index(fields=["usuario", "leida"], name="user_notif_read_idx"),
        ),
    ]
