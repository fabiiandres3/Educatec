(function () {
  const body = document.body;
  if (!body) return;

  const dialog = document.createElement("div");
  dialog.id = "educatec-logout-dialog";
  dialog.className = "logout-dialog-backdrop";
  dialog.hidden = true;
  dialog.innerHTML = `
    <section class="logout-dialog" role="dialog" aria-modal="true" aria-labelledby="logout-dialog-title" aria-describedby="logout-dialog-description" tabindex="-1">
      <div class="logout-dialog-icon"><i class="fa-solid fa-right-from-bracket" aria-hidden="true"></i></div>
      <h2 id="logout-dialog-title">¿Cerrar sesión?</h2>
      <p id="logout-dialog-description">Vas a salir de tu cuenta de Educatec. Podrás volver a ingresar cuando quieras.</p>
      <div class="logout-dialog-error" role="alert" hidden>No se pudo cerrar la sesión. Inténtalo nuevamente.</div>
      <div class="logout-dialog-actions">
        <button type="button" class="logout-dialog-cancel">Seguir aquí</button>
        <button type="button" class="logout-dialog-confirm"><i class="fa-solid fa-arrow-right-from-bracket" aria-hidden="true"></i><span>Cerrar sesión</span></button>
      </div>
    </section>`;
  body.appendChild(dialog);

  const panel = dialog.querySelector(".logout-dialog");
  const cancel = dialog.querySelector(".logout-dialog-cancel");
  const confirm = dialog.querySelector(".logout-dialog-confirm");
  const error = dialog.querySelector(".logout-dialog-error");
  let previousFocus = null;

  function closeDialog() {
    dialog.hidden = true;
    error.hidden = true;
    if (previousFocus && typeof previousFocus.focus === "function") previousFocus.focus();
  }

  function openDialog(trigger) {
    previousFocus = trigger;
    error.hidden = true;
    dialog.hidden = false;
    panel.focus();
  }

  function requestLogout() {
    confirm.disabled = true;
    confirm.querySelector("span").textContent = "Cerrando sesión…";
    const token = body.dataset.csrfToken || "";
    const url = body.dataset.logoutUrl || "/cerrar/";
    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": token,
        "X-Requested-With": "XMLHttpRequest"
      }
    }).then(function (response) {
      if (!response.ok) throw new Error("logout failed");
      window.location.assign(body.dataset.logoutSuccessUrl || "/");
    }).catch(function () {
      error.hidden = false;
      confirm.disabled = false;
      confirm.querySelector("span").textContent = "Cerrar sesión";
    });
  }

  function findLogoutControl(target) {
    if (!(target instanceof Element)) return null;
    return target.closest(
      "#logoutBtn, a[href*='/cerrar/'], form[action*='/cerrar/'] button[type='submit'], form[action*='/cerrar/'] input[type='submit']"
    );
  }

  document.addEventListener("click", function (event) {
    if (dialog.contains(event.target)) return;
    const control = findLogoutControl(event.target);
    if (!control) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    openDialog(control);
  }, true);

  document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.action.includes("/cerrar/")) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    openDialog(form.querySelector("button[type='submit'], input[type='submit']") || form);
  }, true);

  cancel.addEventListener("click", closeDialog);
  confirm.addEventListener("click", requestLogout);
  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) closeDialog();
  });
  document.addEventListener("keydown", function (event) {
    if (dialog.hidden) return;
    if (event.key === "Escape") {
      event.preventDefault();
      closeDialog();
    } else if (event.key === "Tab") {
      event.preventDefault();
      (document.activeElement === cancel ? confirm : cancel).focus();
    }
  });
})();
