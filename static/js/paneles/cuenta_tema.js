(function () {
  const key = "educatec-theme";
  const root = document.documentElement;
  const apply = (theme) => {
    root.dataset.theme = theme === "dark" ? "dark" : "light";
    const toggle = document.getElementById("theme-switch");
    if (toggle) toggle.checked = root.dataset.theme === "dark";
  };
  let saved = "light";
  try { saved = localStorage.getItem(key) || "light"; } catch (_) {}
  apply(saved);
  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("theme-switch");
    if (!toggle) return;
    toggle.addEventListener("change", function () {
      const theme = toggle.checked ? "dark" : "light";
      try { localStorage.setItem(key, theme); } catch (_) {}
      apply(theme);
    });
  });
})();
