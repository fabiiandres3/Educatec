(() => {
  const button = document.querySelector(".student-nav-toolbar .nav-toggle-button");
  const sidebar = document.querySelector("#panel-navigation");
  const overlay = document.querySelector(".nav-menu-overlay");
  if (!button || !sidebar || !overlay) return;

  const icon = button.querySelector("i");
  const mobileQuery = window.matchMedia("(max-width: 768px)");
  const storageKey = "educatec-alumno-sidebar-collapsed";

  function setMenuOpen(open) {
    sidebar.classList.toggle("is-open", open);
    document.body.classList.toggle("nav-open", open);
    button.setAttribute("aria-expanded", String(open));
    button.setAttribute("aria-label", open ? "Cerrar menu de navegacion" : "Abrir menu de navegacion");
    button.title = open ? "Cerrar menu" : "Abrir menu";
    if (icon) {
      icon.classList.toggle("fa-bars-staggered", !open);
      icon.classList.toggle("fa-xmark", open);
      icon.classList.remove("fa-angles-right", "fa-bars");
    }
  }

  function setCollapsed(collapsed) {
    document.body.classList.toggle("alumno-sidebar-collapsed", collapsed);
    sidebar.querySelectorAll(".nav-link-admin, .sidebar-footer a").forEach((item) => {
      if (!item.dataset.navTitle) item.dataset.navTitle = item.textContent.trim().replace(/\s+/g, " ");
      if (collapsed) item.title = item.dataset.navTitle;
      else item.removeAttribute("title");
    });
    button.setAttribute("aria-expanded", String(!collapsed));
    button.setAttribute("aria-label", collapsed ? "Expandir menu de navegacion" : "Contraer menu de navegacion");
    button.title = collapsed ? "Expandir menu" : "Contraer menu";
    if (icon) {
      icon.classList.toggle("fa-bars-staggered", !collapsed);
      icon.classList.toggle("fa-angles-right", collapsed);
      icon.classList.remove("fa-xmark", "fa-bars");
    }
    try { localStorage.setItem(storageKey, String(collapsed)); } catch (error) {}
  }

  function syncViewport() {
    if (mobileQuery.matches) {
      document.body.classList.remove("alumno-sidebar-collapsed");
      setMenuOpen(sidebar.classList.contains("is-open"));
    } else {
      setMenuOpen(false);
      let collapsed = false;
      try { collapsed = localStorage.getItem(storageKey) === "true"; } catch (error) {}
      setCollapsed(collapsed);
    }
  }

  button.addEventListener("click", () => {
    if (mobileQuery.matches) setMenuOpen(!sidebar.classList.contains("is-open"));
    else setCollapsed(!document.body.classList.contains("alumno-sidebar-collapsed"));
  });
  overlay.addEventListener("click", () => setMenuOpen(false));
  sidebar.querySelectorAll("a, .menu li, button[type='submit']").forEach((item) => {
    item.addEventListener("click", () => {
      if (mobileQuery.matches) setMenuOpen(false);
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && mobileQuery.matches) setMenuOpen(false);
  });
  mobileQuery.addEventListener("change", syncViewport);
  syncViewport();
})();
