document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("adminEmailButton");
    const panel = document.getElementById("adminEmailPanel");
    const closeButton = document.getElementById("adminEmailClose");
    const refreshButton = document.getElementById("adminEmailRefresh");
    const countBadge = document.getElementById("adminEmailCount");
    const summaryCount = document.getElementById("adminEmailSummaryCount");
    const status = document.getElementById("adminEmailStatus");
    const list = document.getElementById("adminEmailList");
    const gmailLink = document.getElementById("adminEmailOpenGmail");
    if (!button || !panel || !countBadge || !status || !list) return;

    function setEmpty(icon, message) {
        const empty = document.createElement("div");
        empty.className = "admin-email-empty";
        const iconElement = document.createElement("i");
        iconElement.className = "fas " + icon;
        iconElement.setAttribute("aria-hidden", "true");
        const text = document.createElement("span");
        text.textContent = message;
        empty.append(iconElement, text);
        list.replaceChildren(empty);
    }

    function formatDate(value) {
        if (!value) return "";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        const sameDay = date.toDateString() === new Date().toDateString();
        return new Intl.DateTimeFormat("es-CO", sameDay
            ? { hour: "numeric", minute: "2-digit" }
            : { day: "numeric", month: "short" }).format(date);
    }

    function senderInitial(sender) {
        const cleanSender = (sender || "").replace(/<[^>]*>/g, "").replace(/"/g, "").trim();
        return cleanSender ? cleanSender.charAt(0).toLocaleUpperCase("es-CO") : "?";
    }

    function renderEmails(data) {
        const count = Number(data.unread_count || 0);
        if (gmailLink && data.gmail_url) {
            gmailLink.href = data.gmail_url;
            gmailLink.removeAttribute("aria-disabled");
        }
        countBadge.textContent = count > 99 ? "99+" : String(count);
        countBadge.hidden = count === 0;
        button.setAttribute("aria-label", count ? count + " correos sin leer" : "No hay correos sin leer");
        if (summaryCount) summaryCount.textContent = count ? count + (count === 1 ? " mensaje" : " mensajes") : "Todo al día";
        status.classList.toggle("is-connected", Boolean(data.connected));
        status.classList.toggle("is-error", !data.connected);
        if (!data.connected) {
            status.textContent = "No se pudo conectar con Gmail";
            setEmpty("fa-plug-circle-xmark", "Revisa la conexión y que IMAP esté habilitado en el buzón configurado.");
            if (gmailLink) { gmailLink.href = "#"; gmailLink.setAttribute("aria-disabled", "true"); }
            return;
        }
        status.textContent = "Conectado a Gmail";
        const emails = Array.isArray(data.emails) ? data.emails : [];
        if (!emails.length) {
            setEmpty("fa-circle-check", "No hay correos de soporte recientes en el buzón configurado.");
            return;
        }
        list.replaceChildren();
        emails.forEach(function (email) {
            const item = document.createElement("article");
            item.className = "admin-email-item";
            const avatar = document.createElement("span");
            avatar.className = "admin-email-sender-avatar";
            avatar.setAttribute("aria-hidden", "true");
            avatar.textContent = senderInitial(email.sender);
            const copy = document.createElement("div");
            copy.className = "admin-email-item-copy";
            const top = document.createElement("div");
            top.className = "admin-email-item-top";
            const sender = document.createElement("span");
            sender.className = "admin-email-sender";
            sender.textContent = email.sender || "Remitente desconocido";
            const date = document.createElement("time");
            date.textContent = formatDate(email.date);
            top.append(sender, date);
            const subject = document.createElement("strong");
            subject.textContent = email.subject || "Sin asunto";
            const note = document.createElement("div");
            note.className = "admin-email-item-note";
            note.textContent = email.unread ? "No leído · Soporte Educatec" : "Soporte Educatec";
            if (email.unread) item.classList.add("admin-email-item--unread");
            copy.append(top, subject, note);
            item.append(avatar, copy);
            list.appendChild(item);
        });
    }

    async function refreshInbox() {
        if (refreshButton) refreshButton.classList.add("is-loading");
        try {
            const response = await fetch(button.dataset.inboxUrl, {
                method: "GET",
                credentials: "same-origin",
                headers: { "X-Requested-With": "XMLHttpRequest" },
                cache: "no-store"
            });
            if (!response.ok) throw new Error("No se pudo consultar Gmail");
            renderEmails(await response.json());
        } catch (error) {
            renderEmails({ connected: false, unread_count: 0, emails: [] });
        } finally {
            if (refreshButton) refreshButton.classList.remove("is-loading");
        }
    }

    function setOpen(open) {
        panel.hidden = !open;
        button.setAttribute("aria-expanded", String(open));
        if (open) refreshInbox();
    }

    button.addEventListener("click", function () { setOpen(panel.hidden); });
    refreshButton?.addEventListener("click", refreshInbox);
    gmailLink?.addEventListener("click", function (event) {
        if (gmailLink.getAttribute("aria-disabled") === "true") event.preventDefault();
    });
    closeButton?.addEventListener("click", function () { setOpen(false); });
    document.addEventListener("click", function (event) {
        if (!panel.hidden && !event.target.closest(".admin-email-notification")) setOpen(false);
    });
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") setOpen(false);
    });
    refreshInbox();
    window.setInterval(refreshInbox, 60000);
});
