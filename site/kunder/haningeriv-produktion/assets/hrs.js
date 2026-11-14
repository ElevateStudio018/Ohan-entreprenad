(function () {
  "use strict";

  // Siffrorna: ringarna fylls och talen räknar upp när sektionen kommer in i bild.
  function rakna(el) {
    var till = parseFloat(el.dataset.till), dec = +el.dataset.dec, t0 = null, d = 1600;
    function steg(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / d, 1), v = till * (1 - Math.pow(1 - p, 3));
      el.textContent = dec ? v.toFixed(1).replace(".", ",") : Math.round(v);
      if (p < 1) requestAnimationFrame(steg);
    }
    requestAnimationFrame(steg);
  }
  var anim = document.querySelectorAll(".hb-anim");
  if (anim.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("syns");
        e.target.querySelectorAll("[data-till]").forEach(rakna);
        io.unobserve(e.target);
      });
    }, { threshold: 0.35 });
    anim.forEach(function (s) {
      s.querySelectorAll("[data-till]").forEach(function (el) { el.textContent = "0"; });
      io.observe(s);
    });
  } else {
    anim.forEach(function (s) {
      s.classList.add("syns");
      s.querySelectorAll("[data-till]").forEach(function (el) { el.textContent = el.dataset.slut; });
    });
  }

  // Projektlistan: filterknappar.
  document.querySelectorAll("[data-pf]").forEach(function (sek) {
    var knappar = sek.querySelectorAll(".pf-chips button"), rader = sek.querySelectorAll(".pf-lista li");
    knappar.forEach(function (k) {
      k.addEventListener("click", function () {
        var typ = k.dataset.typ;
        knappar.forEach(function (b) { b.setAttribute("aria-pressed", String(b === k)); });
        rader.forEach(function (r) { r.hidden = !!typ && r.dataset.typ !== typ; });
      });
    });
  });
})();

(function () {
  "use strict";
  // Projektbilderna: filter och bildvisning i helskärm.
  var gal = document.querySelector("[data-galleri]");
  if (!gal) return;
  var figs = [].slice.call(gal.querySelectorAll(".gl-lista li"));
  gal.querySelectorAll(".pf-chips button").forEach(function (k) {
    k.addEventListener("click", function () {
      gal.querySelectorAll(".pf-chips button").forEach(function (b) { b.setAttribute("aria-pressed", String(b === k)); });
      figs.forEach(function (f) { f.hidden = !!k.dataset.typ && f.dataset.typ !== k.dataset.typ; });
    });
  });
  var lb = document.querySelector(".gl-lb"), img = lb.querySelector("img"), txt = lb.querySelector("p"), cur = 0, last = null;
  function synliga() { return figs.filter(function (f) { return !f.hidden; }); }
  function visa(f) {
    var v = synliga(); cur = v.indexOf(f);
    var i = f.querySelector("img"); img.src = i.dataset.full || i.src; img.alt = i.alt; txt.textContent = i.alt;
    lb.hidden = false; document.body.style.overflow = "hidden"; lb.querySelector(".gl-stang").focus();
  }
  function stang() { lb.hidden = true; document.body.style.overflow = ""; if (last) last.focus(); }
  function steg(d) { var v = synliga(); visa(v[(cur + d + v.length) % v.length]); }
  figs.forEach(function (f) {
    var b = f.querySelector("button");
    b.addEventListener("click", function () { last = b; visa(f); });
  });
  lb.querySelector(".gl-stang").addEventListener("click", stang);
  lb.querySelector(".gl-bak").addEventListener("click", function () { steg(-1); });
  lb.querySelector(".gl-fram").addEventListener("click", function () { steg(1); });
  lb.addEventListener("click", function (e) { if (e.target === lb) stang(); });
  document.addEventListener("keydown", function (e) {
    if (lb.hidden) return;
    if (e.key === "Escape") stang();
    if (e.key === "ArrowLeft") steg(-1);
    if (e.key === "ArrowRight") steg(1);
  });
})();
