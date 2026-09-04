const items = document.querySelectorAll('.carousel-item');
let current = 0;

function goTo(index) {
    items[current].classList.add('d-none');
    items[current].classList.remove('active');

    current = (index + items.length) % items.length;

    items[current].classList.remove('d-none');
    items[current].classList.add('active');
}

document.getElementById('btnPrev')
    .addEventListener('click', () => goTo(current - 1));

document.getElementById('btnNext')
    .addEventListener('click', () => goTo(current + 1));




document.addEventListener("DOMContentLoaded", function () {

    const track = document.getElementById("eventosTrack");
    const carousel = document.getElementById("eventosCarousel");

    const btnPrev = document.getElementById("btnPrev");
    const btnNext = document.getElementById("btnNext");

    const indicatorsContainer =
        document.getElementById("eventosIndicators");


    if (!track || !carousel) {
        return;
    }


    const cards = Array.from(
        track.querySelectorAll(".evento-card")
    );


    if (cards.length === 0) {
        return;
    }


    let currentIndex = 0;


    /* =====================================================
       CALCULAR CUÁNTAS TARJETAS SE MUESTRAN
    ===================================================== */

    function getCardsPerView() {

        if (window.innerWidth <= 767) {
            return 1;
        }

        if (window.innerWidth <= 991) {
            return 2;
        }

        return 3;
    }


    /* =====================================================
       CALCULAR MÁXIMO ÍNDICE
    ===================================================== */

    function getMaxIndex() {

        const cardsPerView = getCardsPerView();

        return Math.max(
            0,
            cards.length - cardsPerView
        );
    }


    /* =====================================================
       CREAR INDICADORES
    ===================================================== */

    function createIndicators() {

        indicatorsContainer.innerHTML = "";

        const cardsPerView = getCardsPerView();

        const totalSlides =
            Math.max(
                1,
                Math.ceil(
                    (cards.length - cardsPerView + 1)
                )
            );


        for (let i = 0; i < totalSlides; i++) {

            const indicator =
                document.createElement("button");

            indicator.type = "button";

            indicator.className =
                "eventos-indicator";


            if (i === currentIndex) {
                indicator.classList.add("active");
            }


            indicator.addEventListener(
                "click",
                function () {

                    currentIndex = i;

                    updateCarousel();

                }
            );


            indicatorsContainer.appendChild(
                indicator
            );
        }
    }


    /* =====================================================
       ACTUALIZAR CARRUSEL
    ===================================================== */

    function updateCarousel() {

        const cardsPerView =
            getCardsPerView();

        const maxIndex =
            getMaxIndex();


        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
        }


        /*
         * Calculamos el ancho real de la tarjeta
         * más el espacio entre tarjetas.
         */

        const cardWidth =
            cards[0].getBoundingClientRect().width;


        const gap = 24;


        const movement =
            currentIndex *
            (cardWidth + gap);


        track.style.transform =
            `translateX(-${movement}px)`;


        /* =================================================
           BOTONES
        ================================================= */

        btnPrev.disabled =
            currentIndex === 0;


        btnNext.disabled =
            currentIndex >= maxIndex;


        /* =================================================
           INDICADORES
        ================================================= */

        const indicators =
            indicatorsContainer.querySelectorAll(
                ".eventos-indicator"
            );


        indicators.forEach(
            (indicator, index) => {

                indicator.classList.toggle(
                    "active",
                    index === currentIndex
                );

            }
        );
    }


    /* =====================================================
       SIGUIENTE
    ===================================================== */

    btnNext.addEventListener(
        "click",
        function () {

            const maxIndex =
                getMaxIndex();


            if (currentIndex < maxIndex) {

                currentIndex++;

                updateCarousel();

            }

        }
    );


    /* =====================================================
       ANTERIOR
    ===================================================== */

    btnPrev.addEventListener(
        "click",
        function () {

            if (currentIndex > 0) {

                currentIndex--;

                updateCarousel();

            }

        }
    );


    /* =====================================================
       RESPONSIVE
    ===================================================== */

    window.addEventListener(
        "resize",
        function () {

            createIndicators();

            updateCarousel();

        }
    );


    /* =====================================================
       INICIALIZAR
    ===================================================== */

    createIndicators();

    updateCarousel();

});