(function () {
  "use strict";
  var head = document.getElementById("head");
  var btn = document.getElementById("menyKnapp");
  var meny = document.getElementById("meny");

  // Menyn: öppnas under headern, stängs med Esc, klick på länk eller krysset.
  if (btn && meny) {
    var setOpen = function (open) {
      meny.hidden = !open;
      btn.setAttribute("aria-expanded", String(open));
      btn.setAttribute("aria-label", open ? "Stäng menyn" : "Öppna menyn");
      if (head) head.classList.toggle("fast", open || window.scrollY > 40);
    };
    btn.addEventListener("click", function () { setOpen(meny.hidden); });
    meny.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !meny.hidden) { setOpen(false); btn.focus(); } });
  }

  // Transparent header över heron blir solid när man scrollar.
  if (head) {
    var onScroll = function () { head.classList.toggle("fast", window.scrollY > 40 || (meny && !meny.hidden)); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Bildspel i heron: byter bild var 7:e sekund, prickar och nästa-knapp. Pausar när man håller muspekaren över.
  document.querySelectorAll("[data-bildspel]").forEach(function (spel) {
    var slides = spel.querySelectorAll(".bild-slide");
    var prickar = spel.querySelectorAll(".spel-prickar button");
    var nasta = spel.querySelector(".spel-nasta");
    if (slides.length < 2) return;
    var i = 0, timer = null, reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var visa = function (n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle("aktiv", k === i); s.setAttribute("aria-hidden", String(k !== i)); });
      prickar.forEach(function (p, k) { p.setAttribute("aria-current", String(k === i)); });
    };
    var start = function () { if (!reduce) { clearInterval(timer); timer = setInterval(function () { visa(i + 1); }, 7000); } };
    prickar.forEach(function (p, k) { p.addEventListener("click", function () { visa(k); start(); }); });
    if (nasta) nasta.addEventListener("click", function () { visa(i + 1); start(); });
    spel.addEventListener("mouseenter", function () { clearInterval(timer); });
    spel.addEventListener("mouseleave", start);
    visa(0);
    start();
  });

  // Projektkarusellen: pilknappar scrollar en bredd i taget.
  document.querySelectorAll("[data-karusell]").forEach(function (k) {
    var lista = document.getElementById(k.getAttribute("data-karusell"));
    if (!lista) return;
    k.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () { lista.scrollBy({ left: (b.classList.contains("bak") ? -1 : 1) * lista.clientWidth * 0.9, behavior: "smooth" }); });
    });
  });

  // Innehåll som glider in när det syns.
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("syns"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -6% 0px" });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("syns"); });
  }

  document.querySelectorAll("[data-year]").forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();
