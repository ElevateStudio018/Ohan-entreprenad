(function () {
  "use strict";

  // Quote form: checked here, e-mailed through FormSubmit, then a thank-you in its place.
  var form = document.getElementById("qform");
  if (!form) return;
  var done = document.getElementById("qdone");
  var sendErr = document.getElementById("send-err");
  var f = {
    namn: document.getElementById("f-namn"),
    tel: document.getElementById("f-tel"),
    epost: document.getElementById("f-epost"),
    typ: document.getElementById("f-typ"),
    start: document.getElementById("f-start"),
    adress: document.getElementById("f-adress"),
    besk: document.getElementById("f-besk"),
    web: document.getElementById("f-web")
  };

  // Ett formulär för båda bolagen: valet styr vilka uppdragstyper som visas och vart förfrågan skickas.
  var NAMN = { hrs: "Haninge Riv & Sanering", hb: "Haninge Byggteam", bada: "Båda bolagen" };
  var radios = form.querySelectorAll("input[name=bolag]");
  function bolag() { return (form.querySelector("input[name=bolag]:checked") || {}).value || "hrs"; }
  function filtrera() {
    var b = bolag();
    form.querySelectorAll("#f-typ optgroup").forEach(function (g) {
      var visa = b === "bada" || g.dataset.bolag === b;
      g.hidden = !visa; g.disabled = !visa;
    });
    var valt = f.typ.selectedOptions[0];
    if (valt && valt.parentNode.disabled) f.typ.value = "";
  }
  radios.forEach(function (r) { r.addEventListener("change", filtrera); });
  // Väljer man en typ som hör till det andra bolaget (vid "Båda") behålls valet; annars följer listan bolaget.
  filtrera();

  // "Begär offert" on a service page arrives with ?typ=… and that type chosen.
  var typ = new URLSearchParams(location.search).get("typ");
  if (typ) {
    for (var i = 0; i < f.typ.options.length; i++) if (f.typ.options[i].text === typ) {
      var g = f.typ.options[i].parentNode.dataset ? f.typ.options[i].parentNode.dataset.bolag : null;
      if (g) { form.querySelector("input[name=bolag][value=" + g + "]").checked = true; filtrera(); }
      f.typ.selectedIndex = i;
    }
  }

  function mark(key, input, bad) {
    document.getElementById("e-" + key).hidden = !bad;
    input.setAttribute("aria-invalid", bad ? "true" : "false");
    if (bad) input.setAttribute("aria-describedby", "e-" + key); else input.removeAttribute("aria-describedby");
  }
  function validate() {
    var bad = [];
    var tel = f.tel.value.trim(), ep = f.epost.value.trim();
    var namnBad = !f.namn.value.trim();
    var contactBad = !tel && !ep;
    var epBad = !!ep && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(ep);
    mark("namn", f.namn, namnBad); if (namnBad) bad.push(f.namn);
    mark("tel", f.tel, contactBad); if (contactBad) bad.push(f.tel);
    mark("epost", f.epost, epBad); if (epBad) bad.push(f.epost);
    return bad;
  }
  form.addEventListener("input", function (e) {
    if (e.target.getAttribute("aria-invalid") === "true" || e.target === f.tel || e.target === f.epost) validate();
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var bad = validate();
    if (bad.length) { bad[0].focus(); return; }
    var submit = form.querySelector("button[type=submit]");
    submit.disabled = true;
    submit.textContent = "Skickar …";
    sendErr.hidden = true;
    var payload = {
      _subject: "Offertförfrågan – " + NAMN[bolag()] + " – " + f.namn.value.trim(),
      _template: "table",
      _captcha: "false",
      _honey: f.web.value,
      Namn: f.namn.value.trim(),
      Telefon: f.tel.value.trim() || "–",
      "E-post": f.epost.value.trim() || "–",
      Bolag: NAMN[bolag()],
      "Typ av uppdrag": f.typ.value || "–",
      "Önskad start": f.start.value || "–",
      "Adress/ort": f.adress.value.trim() || "–",
      Beskrivning: f.besk.value.trim() || "–",
      Sida: location.pathname
    };
    if (f.epost.value.trim()) payload._replyto = f.epost.value.trim();
    var b = bolag(), till = b === "bada" ? ["hrs", "hb"] : [b];
    var sand = till.map(function (k) { return form.getAttribute("data-endpoint-" + k); })
      .filter(function (u, i, a) { return a.indexOf(u) === i; });  // samma adress två gånger: skicka en gång
    Promise.all(sand.map(function (url) {
      return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload)
      }).then(function (r) {
        return r.json().catch(function () { return null; }).then(function (j) {
          if (!r.ok || !j || String(j.success) !== "true") throw new Error("not sent");
        });
      });
    })).then(function () {
      document.getElementById("qdone-txt").textContent = b === "bada"
        ? "Förfrågan har gått till både Haninge Riv & Sanering och Haninge Byggteam. Vi hör av oss så snart vi kan."
        : "Förfrågan har gått till " + NAMN[b] + ". Vi hör av oss så snart vi kan.";
      form.reset();
      filtrera();
      form.hidden = true;
      done.hidden = false;
      done.focus();
    }).catch(function () {
      // Kept as typed, so it can be sent again or read out over the phone.
      sendErr.hidden = false;
    }).then(function () {
      submit.disabled = false;
      submit.textContent = "Skicka offertförfrågan";
    });
  });

  document.getElementById("qagain").addEventListener("click", function () {
    done.hidden = true;
    form.hidden = false;
    f.namn.focus();
  });
})();
