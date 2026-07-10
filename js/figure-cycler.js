// Featured-panel figure cycler. Progressive enhancement: the first real
// figure (extracted from the post body at build time) is server-rendered
// active; with JS the prev/next arrows appear and cycle through all of them.
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var root = document.querySelector('[data-figcycle]');
    if (!root) return;
    var slides = Array.prototype.slice.call(root.querySelectorAll('.fig-slide'));
    if (slides.length < 2) return; // single figure: no nav, counter stays "1 of 1"

    var nav = root.querySelector('[data-fig-nav]');
    var counter = root.querySelector('[data-fig-counter]');
    var i = 0;
    if (nav) nav.hidden = false;

    function show(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); });
      if (counter) counter.textContent = 'Fig. ' + (i + 1) + ' of ' + slides.length;
    }

    root.querySelector('[data-fig-prev]').addEventListener('click', function () { show(i - 1); });
    root.querySelector('[data-fig-next]').addEventListener('click', function () { show(i + 1); });
  });
})();
