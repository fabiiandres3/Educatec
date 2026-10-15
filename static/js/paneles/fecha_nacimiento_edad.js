(function () {
  function edadDesdeFecha(valor) {
    if (!valor) return null;
    const partes = valor.split("-").map(Number);
    if (partes.length !== 3 || partes.some(Number.isNaN)) return null;

    const [anio, mes, dia] = partes;
    const hoy = new Date();
    let edad = hoy.getFullYear() - anio;
    const cumpleEsteAnio = new Date(hoy.getFullYear(), mes - 1, dia);
    if (hoy < cumpleEsteAnio) edad -= 1;
    return edad >= 0 ? edad : null;
  }

  function conectarCampo(campo) {
    if (campo.dataset.edadConectada === "true") return;
    campo.dataset.edadConectada = "true";

    const resultado = document.createElement("div");
    resultado.className = "birth-age-preview";
    resultado.setAttribute("role", "status");
    resultado.setAttribute("aria-live", "polite");
    resultado.style.cssText = "margin-top:6px;color:#64748b;font-size:12px;line-height:1.45";
    campo.insertAdjacentElement("afterend", resultado);

    function actualizar() {
      const edad = edadDesdeFecha(campo.value);
      if (edad === null) {
        resultado.textContent = campo.value
          ? "La fecha debe ser válida y anterior a hoy."
          : "Selecciona una fecha para calcular la edad.";
        resultado.style.color = campo.value ? "#c2414b" : "#64748b";
        return;
      }
      resultado.textContent = "Edad calculada: " + edad + (edad === 1 ? " año" : " años");
      resultado.style.color = "#16805a";
    }

    campo.addEventListener("input", actualizar);
    campo.addEventListener("change", actualizar);
    actualizar();
  }

  function iniciar() {
    document.querySelectorAll('input[type="date"][name="fecha_nacimiento"]').forEach(conectarCampo);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
