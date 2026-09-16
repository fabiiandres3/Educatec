from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("docentes", "0005_alter_asignaciondocente_options_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="asignaciondocente",
                    unique_together=set(),
                ),
            ],
        ),
    ]