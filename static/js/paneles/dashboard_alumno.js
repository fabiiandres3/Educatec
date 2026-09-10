// MENÚ ACTIVO

const menuItems = document.querySelectorAll('.menu li');

menuItems.forEach(item => {

    item.addEventListener('click', () => {

        menuItems.forEach(i =>
            i.classList.remove('active')
        );

        item.classList.add('active');

    });

});

// NOTIFICACIÓN

const notification = document.querySelector('.notification');

notification.addEventListener('click', () => {

    alert(
        'Tienes 3 notificaciones nuevas:\n\n' +
        '- Nueva tarea de Matemáticas\n' +
        '- Examen de Biología programado\n' +
        '- Nuevo mensaje del docente'
    );

});

// EFECTO TARJETAS

const cards = document.querySelectorAll(
    '.stat-card, .subject-card'
);

cards.forEach(card => {

    card.addEventListener('mouseenter', () => {

        card.style.transform =
            'translateY(-5px)';

    });

    card.addEventListener('mouseleave', () => {

        card.style.transform =
            'translateY(0px)';

    });

});

// BIENVENIDA

window.addEventListener('load', () => {

    console.log(
        'Portal estudiantil Educatec cargado'
    );

});

const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {

    logoutBtn.addEventListener("click", () => {

        const confirmar = confirm(
            "¿Deseas cerrar sesión?"
        );

        if (confirmar) {

            localStorage.removeItem("rol");

            window.location.href = "/cerrar/";
        }

    });

}