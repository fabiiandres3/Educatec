from django.db import migrations, models


def copiar_curso_actual_a_relacion_muchos(apps, schema_editor):
    Clases = apps.get_model("clases", "Clases")
    db_alias = schema_editor.connection.alias
    campo_cursos = Clases._meta.get_field("cursos")
    tabla_intermedia = campo_cursos.remote_field.through
    campo_clase = campo_cursos.m2m_field_name()
    campo_curso = campo_cursos.m2m_reverse_field_name()
    attname_clase = tabla_intermedia._meta.get_field(campo_clase).attname
    attname_curso = tabla_intermedia._meta.get_field(campo_curso).attname

    asignaciones = Clases.objects.using(db_alias).exclude(
        curso_id__isnull=True
    ).values_list("pk", "curso_id").iterator()

    lote = []
    for clase_id, curso_id in asignaciones:
        lote.append(tabla_intermedia(**{
            attname_clase: clase_id,
            attname_curso: curso_id,
        }))
        if len(lote) == 1000:
            tabla_intermedia.objects.using(db_alias).bulk_create(lote)
            lote = []

    if lote:
        tabla_intermedia.objects.using(db_alias).bulk_create(lote)


def restaurar_un_curso_por_clase(apps, schema_editor):
    Clases = apps.get_model("clases", "Clases")
    db_alias = schema_editor.connection.alias
    campo_cursos = Clases._meta.get_field("cursos")
    tabla_intermedia = campo_cursos.remote_field.through
    campo_clase = campo_cursos.m2m_field_name()
    campo_curso = campo_cursos.m2m_reverse_field_name()
    attname_clase = tabla_intermedia._meta.get_field(campo_clase).attname
    attname_curso = tabla_intermedia._meta.get_field(campo_curso).attname

    for clase_id in Clases.objects.using(db_alias).values_list("pk", flat=True).iterator():
        curso_id = tabla_intermedia.objects.using(db_alias).filter(
            **{attname_clase: clase_id}
        ).order_by(attname_curso).values_list(attname_curso, flat=True).first()
        if curso_id:
            Clases.objects.using(db_alias).filter(pk=clase_id).update(curso_id=curso_id)


class Migration(migrations.Migration):

    dependencies = [
        ("clases", "0003_alter_clases_options_alter_clases_curso_and_more"),
        ("cursos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="clases",
            name="cursos",
            field=models.ManyToManyField(blank=True, related_name="clases", to="cursos.cursos"),
        ),
        migrations.RunPython(
            copiar_curso_actual_a_relacion_muchos,
            restaurar_un_curso_por_clase,
        ),
        migrations.RemoveField(
            model_name="clases",
            name="curso",
        ),
    ]
