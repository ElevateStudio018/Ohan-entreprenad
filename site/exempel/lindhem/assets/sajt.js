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

  // Innehåll som glider in när det syns.
  var els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("syns"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("syns"); });
  }

  document.querySelectorAll("[data-year]").forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();
