document.addEventListener("DOMContentLoaded", function () {

    console.log("EVENTOS JS CARGADO");

    const contenedor = document.getElementById("eventosCarousel");

    if (!contenedor) {
        console.error("NO EXISTE eventosCarousel");
        return;
    }

    fetch("/eventos-home/")
        .then(response => {

            console.log("RESPUESTA:", response);

            return response.json();
        })
        .then(eventos => {

            console.log("EVENTOS RECIBIDOS:", eventos);

            contenedor.innerHTML = "";

            eventos.forEach(evento => {

                const div = document.createElement("div");

                div.className = "col-md-4 mb-4";

                div.innerHTML = `
                    <div class="card h-100 shadow">

                        ${
                            evento.imagen
                            ? `
                                <img
                                    src="${evento.imagen}"
                                    class="card-img-top"
                                    style="height:220px; object-fit:cover;"
                                >
                            `
                            : ""
                        }

                        <div class="card-body">

                            <span class="badge bg-primary">
                                ${evento.tipo || "Evento"}
                            </span>

                            <h3 class="mt-3">
                                ${evento.titulo}
                            </h3>

                            <p>
                                ${evento.descripcion || ""}
                            </p>

                            <p>
                                📅 ${evento.fecha}
                            </p>

                            <p>
                                🕐 ${evento.hora}
                            </p>

                        </div>

                    </div>
                `;

                contenedor.appendChild(div);

            });

        })
        .catch(error => {

            console.error(
                "ERROR CARGANDO EVENTOS:",
                error
            );

        });

});