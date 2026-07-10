// Home-page "Latest" topic filter. Progressive enhancement: the full list is
// server-rendered, and this only hides/shows rows client-side. Topics come from
// each row's data-topic (derived from the post's first tag in Blog.Context).
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var pills = Array.prototype.slice.call(document.querySelectorAll('.topic-pill'));
    if (!pills.length) return;
    var rows = Array.prototype.slice.call(document.querySelectorAll('.post-row[data-topic]'));
    var empty = document.querySelector('.topic-empty');

    function apply(filter) {
      var shown = 0;
      rows.forEach(function (row) {
        var match = filter === 'all' || row.getAttribute('data-topic') === filter;
        row.hidden = !match;
        if (match) shown++;
      });
      if (empty) empty.hidden = shown !== 0;
    }

    pills.forEach(function (pill) {
      pill.addEventListener('click', function () {
        pills.forEach(function (p) {
          var active = p === pill;
          p.classList.toggle('is-active', active);
          p.setAttribute('aria-pressed', String(active));
        });
        apply(pill.getAttribute('data-topic-filter'));
      });
    });
  });
})();
