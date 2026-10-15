const grados = document.querySelectorAll('.grado');

grados.forEach(grado => {

    grado.addEventListener('click', () => {

        grados.forEach(g =>
            g.classList.remove('active')
        );

        grado.classList.add('active');

    });

});

