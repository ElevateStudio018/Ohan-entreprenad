/* Bildspelets bild 2 och 3 laddas först när sidan har visats, så att första bilden och texten kommer fram snabbare. */
addEventListener("load", function () { setTimeout(function () {
  document.querySelectorAll("img[data-src]").forEach(function (i) {
    if (i.dataset.srcset) i.srcset = i.dataset.srcset;
    i.src = i.dataset.src; i.removeAttribute("data-src"); i.removeAttribute("data-srcset");
  });
}, 300); });
