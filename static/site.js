(function () {
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var panel = document.getElementById("site-nav");
  var backdrop = document.querySelector(".nav-backdrop");
  if (header && toggle && panel) {
    function closeNav() {
      header.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
      document.body.classList.remove("nav-lock");
    }
    function openNav() {
      header.classList.add("nav-open");
      toggle.setAttribute("aria-expanded", "true");
      document.body.classList.add("nav-lock");
    }
    toggle.addEventListener("click", function () {
      header.classList.contains("nav-open") ? closeNav() : openNav();
    });
    if (backdrop) backdrop.addEventListener("click", closeNav);
    panel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeNav);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 960) closeNav();
    });
  }

  var form = document.getElementById("contact-form");
  if (!form) return;

  var statusEl = document.getElementById("form-status");
  var submitBtn = form.querySelector('button[type="submit"]');

  function setStatus(text, ok) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.toggle("form-status-ok", !!ok);
    statusEl.classList.toggle("form-status-err", !ok);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (submitBtn) submitBtn.disabled = true;
    setStatus("Sending...", true);

    var payload = {
      name: form.elements.name ? form.elements.name.value : "",
      email: form.elements.email ? form.elements.email.value : "",
      phone: form.elements.phone ? form.elements.phone.value : "",
      message: form.elements.message ? form.elements.message.value : "",
      company: form.elements.company ? form.elements.company.value : "",
    };

    fetch("/api/contact", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (result) {
        if (result.ok) {
          form.reset();
          setStatus("Inquiry sent. Our intake team will respond shortly.", true);
        } else {
          setStatus(result.data.error || "Unable to send inquiry.", false);
        }
      })
      .catch(function () {
        setStatus("Network error. Please try again or call us directly.", false);
      })
      .finally(function () {
        if (submitBtn) submitBtn.disabled = false;
      });
  });
})();
