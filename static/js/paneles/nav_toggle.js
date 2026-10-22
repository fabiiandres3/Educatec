(function () {
    const button = document.querySelector(".nav-toggle-button");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".nav-menu-overlay");
    if (!button || !sidebar || !overlay) return;

    const icon = button.querySelector("i");
    const mobileQuery = window.matchMedia("(max-width: 768px)");
    const storageKey = "educatec-admin-sidebar-collapsed";

    function setMenuOpen(open) {
        sidebar.classList.toggle("is-open", open);
        document.body.classList.toggle("nav-open", open);
        button.setAttribute("aria-expanded", String(open));
        button.setAttribute("aria-label", open ? "Cerrar menú de navegación" : "Abrir menú de navegación");
        if (icon) {
            icon.classList.toggle("fa-bars", !open);
            icon.classList.toggle("fa-xmark", open);
        }
    }

    function setCollapsed(collapsed) {
        document.body.classList.toggle("sidebar-collapsed", collapsed);
        sidebar.querySelectorAll(".nav-link-admin, .sidebar-footer a").forEach(function (link) {
            if (!link.dataset.navTitle) link.dataset.navTitle = link.textContent.trim().replace(/\s+/g, " ");
            if (collapsed) link.title = link.dataset.navTitle;
            else link.removeAttribute("title");
        });
        button.setAttribute("aria-expanded", String(!collapsed));
        button.setAttribute("aria-label", collapsed ? "Expandir menú de navegación" : "Contraer menú de navegación");
        button.title = collapsed ? "Expandir menú" : "Contraer menú";
        if (icon) {
            icon.classList.toggle("fa-bars", !collapsed);
            icon.classList.toggle("fa-angles-right", collapsed);
        }
        try { localStorage.setItem(storageKey, String(collapsed)); } catch (error) {}
    }

    function syncViewport() {
        if (mobileQuery.matches) {
            document.body.classList.remove("sidebar-collapsed");
            button.setAttribute("aria-expanded", String(sidebar.classList.contains("is-open")));
            button.setAttribute("aria-label", sidebar.classList.contains("is-open") ? "Cerrar menú de navegación" : "Abrir menú de navegación");
            if (icon) {
                icon.classList.toggle("fa-bars", !sidebar.classList.contains("is-open"));
                icon.classList.toggle("fa-xmark", sidebar.classList.contains("is-open"));
            }
        } else {
            document.body.classList.remove("nav-open");
            sidebar.classList.remove("is-open");
            let collapsed = false;
            try { collapsed = localStorage.getItem(storageKey) === "true"; } catch (error) {}
            setCollapsed(collapsed);
        }
    }

    window.toggleAdminSidebar = function () {
        setCollapsed(!document.body.classList.contains("sidebar-collapsed"));
    };

    overlay.addEventListener("click", function () { setMenuOpen(false); });
    sidebar.querySelectorAll("a, .menu li, button[type='submit']").forEach(function (item) {
        item.addEventListener("click", function () {
            if (mobileQuery.matches) setMenuOpen(false);
        });
    });
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") setMenuOpen(false);
    });
    mobileQuery.addEventListener("change", syncViewport);
    syncViewport();
})();