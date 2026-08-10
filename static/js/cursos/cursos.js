document.addEventListener('DOMContentLoaded', function () {

    const filtroCurso = document.getElementById('filtroCurso');
    const filasAlumnos = document.querySelectorAll('#listaAlumnos tr');

    if (!filtroCurso) {
        return;
    }

    filtroCurso.addEventListener('change', function () {

        const cursoSeleccionado = this.value;

        filasAlumnos.forEach(function (fila) {

            const cursoAlumno = fila.dataset.curso;

            if (
                cursoSeleccionado === '' ||
                cursoAlumno === cursoSeleccionado
            ) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }

        });

    });

});