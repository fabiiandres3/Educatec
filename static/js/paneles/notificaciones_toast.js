document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".app-toast").forEach((toast) => {
        let timer;
        const dismiss = () => {
            if (toast.classList.contains("is-leaving")) return;
            toast.classList.add("is-leaving");
            window.setTimeout(() => toast.remove(), 220);
        };

        toast.querySelector(".app-toast__close")?.addEventListener("click", dismiss);
        timer = window.setTimeout(dismiss, 5000);
        toast.addEventListener("mouseenter", () => window.clearTimeout(timer));
        toast.addEventListener("mouseleave", () => { timer = window.setTimeout(dismiss, 1500); });
    });
});
