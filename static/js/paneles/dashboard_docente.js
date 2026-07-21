const grados = document.querySelectorAll('.grado');

grados.forEach(grado => {

    grado.addEventListener('click', () => {

        grados.forEach(g =>
            g.classList.remove('active')
        );

        grado.classList.add('active');

    });

});

const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {

    logoutBtn.addEventListener("click", (e) => {

        e.preventDefault();

        const confirmar = confirm(
            "¿Deseas cerrar sesión?"
        );

        if (confirmar) {

            localStorage.removeItem("rol");

            window.location.href = "/cerrar/";

        }

    });

}