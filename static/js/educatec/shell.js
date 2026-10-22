/* =========================================================
   EDUCATEC · COMPORTAMIENTO DEL SHELL
   Menú lateral: colapsable en escritorio, deslizable en móvil.
   ========================================================= */

(function () {
    "use strict";

    var CLAVE = "educatec-sidebar-colapsado";
    var app = document.querySelector("[data-edc-app]");

    if (!app) {
        return;
    }

    var botonColapsar = app.querySelector("[data-edc-colapsar]");
    var botonMenu = app.querySelector("[data-edc-menu]");
    var velo = app.querySelector("[data-edc-velo]");

    // -----------------------------------------------------
    // ESCRITORIO: recordar estado colapsado
    // -----------------------------------------------------

    var colapsado = false;

    try {
        colapsado = window.localStorage.getItem(CLAVE) === "1";
    } catch (error) {
        colapsado = false;
    }

    if (colapsado) {
        app.classList.add("is-collapsed");
    }

    function alternarColapsado() {
        var activo = app.classList.toggle("is-collapsed");

        try {
            window.localStorage.setItem(CLAVE, activo ? "1" : "0");
        } catch (error) {
            /* almacenamiento no disponible */
        }
    }

    if (botonColapsar) {
        botonColapsar.addEventListener("click", alternarColapsado);
    }

    // -----------------------------------------------------
    // MÓVIL: abrir y cerrar el menú
    // -----------------------------------------------------

    function abrirMenu() {
        app.classList.add("is-open");
        if (botonMenu) {
            botonMenu.setAttribute("aria-expanded", "true");
        }
    }

    function cerrarMenu() {
        app.classList.remove("is-open");
        if (botonMenu) {
            botonMenu.setAttribute("aria-expanded", "false");
        }
    }

    if (botonMenu) {
        botonMenu.addEventListener("click", function () {
            if (app.classList.contains("is-open")) {
                cerrarMenu();
            } else {
                abrirMenu();
            }
        });
    }

    if (velo) {
        velo.addEventListener("click", cerrarMenu);
    }

    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrarMenu();
        }
    });

    // Cerrar al navegar dentro del menú en móvil.
    app.querySelectorAll(".edc-nav__enlace").forEach(function (enlace) {
        enlace.addEventListener("click", function () {
            if (window.matchMedia("(max-width: 991px)").matches) {
                cerrarMenu();
            }
        });
    });
})();
