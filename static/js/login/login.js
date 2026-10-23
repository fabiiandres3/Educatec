(() => {
  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    const password = button.closest(".login-password-wrap")?.querySelector("input");
    if (!password) return;

    button.addEventListener("click", () => {
      const show = password.type === "password";
      password.type = show ? "text" : "password";
      button.setAttribute("aria-label", show ? "Ocultar contraseña" : "Mostrar contraseña");
      button.innerHTML = `<i class="fa-regular fa-eye${show ? "-slash" : ""}"></i>`;
    });
  });
})();