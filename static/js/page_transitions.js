(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    // Modern browsers keep the named sidebar in place during page navigation.
    // Older browsers animate only the content region; the nav remains untouched.
    if (!document.startViewTransition) {
        document.documentElement.classList.add("page-transition-fallback");
    }
})();
