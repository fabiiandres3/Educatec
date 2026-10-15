(function () {
  const refreshUrl = "/csrf/refresh/";
  let refreshInFlight = null;
  const resumedForms = new WeakSet();

  function applyToken(token) {
    if (!token) return;
    document.querySelectorAll('input[name="csrfmiddlewaretoken"]').forEach(function (input) {
      input.value = token;
    });
    document.querySelectorAll('meta[name="csrf-token"]').forEach(function (meta) {
      meta.content = token;
    });
    if (document.body) document.body.dataset.csrfToken = token;
  }

  function refreshToken() {
    if (refreshInFlight) return refreshInFlight;
    refreshInFlight = fetch(refreshUrl, {
      method: "GET",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    }).then(function (response) {
      if (!response.ok) throw new Error("Could not refresh CSRF token");
      return response.json();
    }).then(function (data) {
      applyToken(data.csrfToken);
      return data.csrfToken;
    }).catch(function () {
      return null;
    }).finally(function () {
      refreshInFlight = null;
    });
    return refreshInFlight;
  }

  window.addEventListener("pageshow", function (event) {
    const navigation = performance.getEntriesByType("navigation")[0];
    if (event.persisted || (navigation && navigation.type === "back_forward")) {
      refreshToken();
    }
  });

  document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || form.method.toLowerCase() !== "post") return;
    if (resumedForms.has(form)) {
      resumedForms.delete(form);
      return;
    }
    event.preventDefault();
    const submitter = event.submitter;
    refreshToken().then(function (token) {
      if (!form.isConnected) return;
      resumedForms.add(form);
      if (submitter && submitter.form === form) form.requestSubmit(submitter);
      else form.requestSubmit();
    });
  }, true);

  window.educatecRefreshCsrfToken = refreshToken;
})();
