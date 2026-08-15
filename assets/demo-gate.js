/* Elevate Aura - gated demo modal
   Captures a lead (name, org, phone, email) and emails it to you via Web3Forms,
   then opens the requested live demo.

   SETUP (one step): paste your Web3Forms access key below.
   Get a free key at https://web3forms.com  (it emails submissions to the address
   you register with). The access key is safe to expose in the browser - it only
   allows sending to your verified email, nothing else. */
(function () {
  "use strict";

  var WEB3FORMS_KEY = "fdd6ab41-01f5-497f-8cb3-daea26afbdbd"; // Web3Forms access key (elevateauraofficial@gmail.com)

  var DEMOS = {
    hospital: { url: "/demo/hospital.html", label: "Hospital HIMS + AuraPACS" },
    dental:   { url: "/demo/dental.html",   label: "Dental Clinic HIMS" },
    lms:      { url: "/demo/lms.html",      label: "Aura Learn (LMS)" },
    aurapacs: { url: "https://demo.elevateaura.co.in/api/demo-login", label: "AuraPACS (medical imaging)" }
  };

  var state = { product: "", url: "" };

  // ---- build modal DOM ----
  var ov = document.createElement("div");
  ov.className = "ead-ov";
  ov.innerHTML =
    '<div class="ead-card" role="dialog" aria-modal="true" aria-label="Open the live demo">' +
      '<button class="ead-x" type="button" aria-label="Close">&times;</button>' +
      '<div class="ead-top">' +
        '<span class="ead-pill"><span class="d"></span>Live demo</span>' +
        '<h3 data-el="title">See it working, live.</h3>' +
        '<p data-el="sub">Real, running software with sample data. Tell us who you are and it opens right away.</p>' +
      '</div>' +
      '<div class="ead-body">' +
        // choose step (HIMS only)
        '<div data-step="choose" class="ead-choose ead-hide">' +
          '<button class="ead-opt" type="button" data-pick="hospital">' +
            '<span class="ic">&#127973;</span><span><b>Hospital HIMS</b><small>OP/IP, EMR, pharmacy, lab, billing + imaging</small></span><span class="ar">&rarr;</span>' +
          '</button>' +
          '<button class="ead-opt" type="button" data-pick="dental">' +
            '<span class="ic">&#129463;</span><span><b>Dental clinic HIMS</b><small>Appointments, charting, treatment &amp; billing</small></span><span class="ar">&rarr;</span>' +
          '</button>' +
        '</div>' +
        // form step
        '<form data-step="form" class="ead-hide" novalidate>' +
          '<button type="button" class="ead-back ead-hide" data-el="back">&larr; Choose a different version</button>' +
          '<div class="ead-err" data-el="err"></div>' +
          '<div class="ead-field"><label>Full name</label><input name="name" autocomplete="name" required></div>' +
          '<div class="ead-field"><label>Organisation / clinic</label><input name="organisation" autocomplete="organization" required></div>' +
          '<div class="ead-row">' +
            '<div class="ead-field"><label>Phone / WhatsApp</label><input name="phone" type="tel" inputmode="tel" autocomplete="tel" required></div>' +
            '<div class="ead-field"><label>City</label><input name="city" autocomplete="address-level2"></div>' +
          '</div>' +
          '<div class="ead-field"><label>Email</label><input name="email" type="email" autocomplete="email" required></div>' +
          '<label class="ead-consent"><input type="checkbox" name="consent" required><span>I agree to be contacted by Elevate Aura about this demo.</span></label>' +
          '<button type="submit" class="ead-submit" data-el="submit"><span data-el="btnlabel">Open the live demo</span></button>' +
          '<p class="ead-fine">We only use these details to show you the demo and follow up. No spam.</p>' +
        '</form>' +
        // success step
        '<div data-step="done" class="ead-done ead-hide">' +
          '<div class="tick">&#10003;</div>' +
          '<h4>You\'re in.</h4>' +
          '<p>Opening your demo now. If it doesn\'t open, use the button below.</p>' +
          '<a class="ead-open" data-el="open" href="#" target="_blank" rel="noopener">Open the live demo &rarr;</a>' +
        '</div>' +
      '</div>' +
    '</div>';
  document.body.appendChild(ov);

  var card    = ov.querySelector(".ead-card");
  var elTitle = ov.querySelector('[data-el="title"]');
  var elSub   = ov.querySelector('[data-el="sub"]');
  var stChoose= ov.querySelector('[data-step="choose"]');
  var stForm  = ov.querySelector('[data-step="form"]');
  var stDone  = ov.querySelector('[data-step="done"]');
  var elBack  = ov.querySelector('[data-el="back"]');
  var elErr   = ov.querySelector('[data-el="err"]');
  var elSubmit= ov.querySelector('[data-el="submit"]');
  var elBtnLbl= ov.querySelector('[data-el="btnlabel"]');
  var elOpen  = ov.querySelector('[data-el="open"]');

  function showStep(name) {
    stChoose.classList.toggle("ead-hide", name !== "choose");
    stForm.classList.toggle("ead-hide", name !== "form");
    stDone.classList.toggle("ead-hide", name !== "done");
  }
  function open(mode) {
    elErr.classList.remove("on"); elErr.textContent = "";
    stForm.reset && stForm.reset();
    if (mode === "hims") {
      elTitle.textContent = "Which HIMS would you like to see?";
      elSub.textContent = "Pick the version closest to you. The demo opens after a quick sign-in.";
      elBack.classList.remove("ead-hide");
      showStep("choose");
    } else {
      var d = DEMOS[mode] || DEMOS.lms;
      state.product = d.label; state.url = d.url;
      elTitle.textContent = "See " + d.label + ", live.";
      elSub.textContent = "Real software with sample data. Tell us who you are and it opens right away.";
      elBack.classList.add("ead-hide");
      showStep("form");
    }
    ov.classList.add("on");
    document.documentElement.style.overflow = "hidden";
  }
  function close() {
    ov.classList.remove("on");
    document.documentElement.style.overflow = "";
    showStep("choose"); // reset for next time (hidden anyway)
  }

  // ---- events ----
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-demo]");
    if (t) { e.preventDefault(); open(t.getAttribute("data-demo")); }
  });
  ov.querySelector(".ead-x").addEventListener("click", close);
  ov.addEventListener("mousedown", function (e) { if (e.target === ov) close(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && ov.classList.contains("on")) close(); });

  ov.querySelectorAll("[data-pick]").forEach(function (b) {
    b.addEventListener("click", function () {
      var key = b.getAttribute("data-pick");
      state.product = DEMOS[key].label; state.url = DEMOS[key].url;
      elTitle.textContent = "Sign in to open the demo";
      elSub.textContent = state.product + " - real software with sample data.";
      showStep("form");
    });
  });
  elBack.addEventListener("click", function () {
    elTitle.textContent = "Which HIMS would you like to see?";
    elSub.textContent = "Pick the version closest to you. The demo opens after a quick sign-in.";
    showStep("choose");
  });

  function launch() {
    elOpen.setAttribute("href", state.url);
    showStep("done");
    try { window.open(state.url, "_blank", "noopener"); } catch (e) {}
  }

  stForm.addEventListener("submit", function (e) {
    e.preventDefault();
    elErr.classList.remove("on");
    var fd = new FormData(stForm);
    var name = (fd.get("name") || "").toString().trim();
    var org  = (fd.get("organisation") || "").toString().trim();
    var phone= (fd.get("phone") || "").toString().trim();
    var email= (fd.get("email") || "").toString().trim();
    if (!name || !org || !phone || !email || !fd.get("consent")) {
      elErr.textContent = "Please fill in your name, organisation, phone, email and tick the box.";
      elErr.classList.add("on"); return;
    }
    elSubmit.setAttribute("disabled", "disabled");
    elBtnLbl.textContent = "Opening…";

    var payload = {
      access_key: WEB3FORMS_KEY,
      subject: "New demo signup: " + state.product,
      from_name: "Elevate Aura - Demo gate",
      product: state.product,
      name: name, organisation: org, phone: phone,
      city: (fd.get("city") || "").toString().trim(),
      email: email,
      page: location.href
    };

    // Send the lead in the background (keepalive so it completes even if the
    // page navigates). We never block the demo on the network: open on the
    // first of "email confirmed" or a short timeout, so the button can't hang.
    var launched = false;
    function openOnce() { if (launched) return; launched = true; launch(); }
    var failsafe = setTimeout(openOnce, 3500);

    fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
      keepalive: true
    })
    .then(function (r) { return r.json(); })
    .then(function () { clearTimeout(failsafe); openOnce(); })
    .catch(function () { clearTimeout(failsafe); openOnce(); });
  });
})();
