(function () {
    const button = document.querySelector(".nav-toggle-button");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.querySelector(".nav-menu-overlay");
    if (!button || !sidebar || !overlay) return;

    const icon = button.querySelector("i");
    const mobileQuery = window.matchMedia("(max-width: 768px)");
    const supportsDesktopCollapse = Boolean(document.querySelector(".main-content"));
    const storageKey = "educatec-admin-sidebar-collapsed";

    function setMenuOpen(open) {
        sidebar.classList.toggle("is-open", open);
        document.body.classList.toggle("nav-open", open);
        button.setAttribute("aria-expanded", String(open));
        button.setAttribute("aria-label", open ? "Cerrar menú de navegación" : "Abrir menú de navegación");
        button.title = open ? "Cerrar menú" : "Abrir menú";
        if (icon) {
            icon.classList.toggle("fa-bars-staggered", !open);
            icon.classList.toggle("fa-xmark", open);
            icon.classList.remove("fa-bars", "fa-angles-right");
        }
    }

    function setCollapsed(collapsed) {
        document.body.classList.toggle("sidebar-collapsed", collapsed);
        sidebar.querySelectorAll(".nav-link-admin, .menu-link, .sidebar .menu li, .sidebar-footer a").forEach(function (link) {
            if (!link.dataset.navTitle) link.dataset.navTitle = link.textContent.trim().replace(/\s+/g, " ");
            if (collapsed) link.title = link.dataset.navTitle;
            else link.removeAttribute("title");
        });
        button.setAttribute("aria-expanded", String(!collapsed));
        button.setAttribute("aria-label", collapsed ? "Expandir menú de navegación" : "Contraer menú de navegación");
        button.title = collapsed ? "Expandir menú" : "Contraer menú";
        if (icon) {
            icon.classList.toggle("fa-bars-staggered", !collapsed);
            icon.classList.toggle("fa-angles-right", collapsed);
            icon.classList.remove("fa-bars", "fa-xmark");
        }
        try { localStorage.setItem(storageKey, String(collapsed)); } catch (error) {}
    }

    function syncViewport() {
        if (mobileQuery.matches) {
            document.body.classList.remove("sidebar-collapsed");
            setMenuOpen(sidebar.classList.contains("is-open"));
        } else {
            setMenuOpen(false);
            if (supportsDesktopCollapse) {
                let collapsed = false;
                try { collapsed = localStorage.getItem(storageKey) === "true"; } catch (error) {}
                setCollapsed(collapsed);
            } else {
                document.body.classList.remove("sidebar-collapsed");
                button.setAttribute("aria-expanded", "false");
            }
        }
    }

    window.toggleAdminSidebar = function () {
        if (mobileQuery.matches) {
            setMenuOpen(!sidebar.classList.contains("is-open"));
            return;
        }
        setCollapsed(!document.body.classList.contains("sidebar-collapsed"));
    };

    if (!button.hasAttribute("onclick")) {
        button.addEventListener("click", function () {
            if (mobileQuery.matches) setMenuOpen(!sidebar.classList.contains("is-open"));
        });
    }

    overlay.addEventListener("click", function () { setMenuOpen(false); });
    sidebar.querySelectorAll("a, .menu li, button[type='submit']").forEach(function (item) {
        item.addEventListener("click", function () {
            if (mobileQuery.matches) setMenuOpen(false);
        });
    });
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && mobileQuery.matches) setMenuOpen(false);
    });
    mobileQuery.addEventListener("change", syncViewport);
    syncViewport();
})();