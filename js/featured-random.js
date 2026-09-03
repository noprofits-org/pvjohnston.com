// Home-page featured-note reel. Progressive enhancement: the server bakes the
// newest post that HAS A FIGURE into the featured slot (so the card is valid
// with JS off and for crawlers). With JS, the slot becomes a small carousel of
// the N most recent figure-having notes (N = 5, or fewer if the site has
// fewer). The reel itself is newest-first so the dots have a stable meaning;
// the initial slide is a random member of that reel, avoiding the previous
// sessionStorage pick when another choice exists. No autoplay.
//
// Text comes from the reel source (or a Latest row as fallback). The figure
// prefers the front-matter hero carried as `template.row-featured-figure` —
// the compact landscape PNG the server already bakes. Fall back to fetching
// the post body only for TikZ-only posts. Body SVGs with wrapping panels
// (`.fig-levels`) must not enter the hero: they stack in the half-width
// column. Any failure leaves the baked default or the text-only card.
//
// The card is held invisible pre-paint by a small inline script in the page
// head (the `feat-pending` class); reveal() clears it once the first slide
// is in place.
//
// innerHTML is built only from first-party same-origin content (the site's
// own rows/pages), with all plain-text fields HTML-escaped.
(function () {
  'use strict';

  var LIMIT = 5;
  var LAST = 'np-featured-last';

  document.addEventListener('DOMContentLoaded', function () {
    function reveal() { document.documentElement.classList.remove('feat-pending'); }

    var featured = document.querySelector('.featured');
    if (!featured) { reveal(); return; }
    var inner = featured.querySelector('.featured-inner');
    var grid = featured.querySelector('.featured-grid');
    var dateEl = featured.querySelector('.featured-date');
    if (!inner || !grid) { reveal(); return; }

    var curLink = featured.querySelector('.featured-title a');
    var curUrl = curLink ? curLink.getAttribute('href') : null;

    function pathOf(u) {
      try { return new URL(u, location.href).pathname; } catch (e) { return u || ''; }
    }
    function itemUrl(el) {
      return el.getAttribute('data-href') || el.getAttribute('href');
    }

    // Hide whichever Latest row is the currently-shown featured post (class,
    // not the [hidden] attribute, so the topic filter can't un-hide it).
    function reconcile(url) {
      var p = pathOf(url);
      Array.prototype.slice.call(document.querySelectorAll('.post-row'))
        .forEach(function (r) {
          r.classList.toggle('is-featured', pathOf(r.getAttribute('href')) === p);
        });
    }

    // Newest-first: the dedicated reel source is already take-N of the
    // figure-having pool. Latest rows are a fallback if that island is missing
    // (older HTML) — they are also newest-first, but only among the Latest
    // window, which may have fewer than N figured notes.
    var src = featured.querySelector('.featured-reel-src')
           || document.querySelector('.featured-reel-src');
    var rows = src
      ? Array.prototype.slice.call(src.querySelectorAll('.featured-reel-item'))
      : [];
    if (!rows.length) {
      rows = Array.prototype.slice.call(
        document.querySelectorAll('.latest .post-row[data-has-figure]'));
    }
    var reel = rows.slice(0, LIMIT);
    if (!reel.length) { reconcile(curUrl); reveal(); return; }

    function esc(s) {
      var d = document.createElement('div');
      d.textContent = s || '';
      return d.innerHTML;
    }
    function rowText(row, sel) {
      var n = row.querySelector(sel);
      return n ? n.textContent.trim() : '';
    }
    function rowTags(row) {
      return Array.prototype.slice.call(row.querySelectorAll('.post-row-tags .row-tag'))
        .map(function (t) { return t.textContent.replace(/^#/, '').trim(); })
        .filter(Boolean);
    }

    // The picker injects the figure + caption AFTER MathJax's one-time initial
    // typeset has already run, so any math delimiters in a fetched caption stay raw.
    // Homepage skips MathJax (no .math in the baked document); lazy-load the
    // same CDN only when injected HTML actually contains math.
    function looksLikeMath(html) {
      return typeof html === 'string' && /\\\(|\\\[|\.math\b/.test(html);
    }
    function typeset(el) {
      if (!el || typeof window.ensureMathJax !== 'function') return;
      window.ensureMathJax(el);
    }
    function typesetIfMath(el, html) {
      if (!el) return;
      var blob = html;
      if (blob == null) blob = el.innerHTML || '';
      if (!looksLikeMath(blob) &&
          !(el.querySelector && (el.querySelector('.math') || el.querySelector('mjx-container')))) {
        return;
      }
      typeset(el);
    }

    function dropFigure() {
      var figEl = grid.querySelector('.featured-figure');
      if (figEl) figEl.remove();
      grid.style.gridTemplateColumns = '1fr';
    }

    // Caption slot is always in the figure (see renderSlide). Fill or clear
    // it in place so a missing caption cannot drop the reserved line.
    function setCaption(figEl, opts) {
      var cap = figEl.querySelector('figcaption.figure-caption');
      if (!cap) {
        cap = document.createElement('figcaption');
        cap.className = 'figure-caption';
        figEl.appendChild(cap);
      }
      if (opts && opts.html) cap.innerHTML = opts.html;
      else cap.textContent = (opts && opts.text) || '';
    }

    // Prefer the front-matter hero already on the reel item / Latest row. It
    // is the same markup the server bakes into `$figure$` — a landscape PNG
    // when the post declares one — so the featured slot stays compact.
    function applyRowHero(row) {
      var tpl = row.querySelector('template.row-featured-figure');
      if (!tpl) return false;
      var srcFig = tpl.content;
      var figSrc = srcFig.querySelector('[data-figure]');
      if (!figSrc || !figSrc.innerHTML.trim()) return false;
      var figEl = grid.querySelector('.featured-figure');
      if (!figEl) return false;
      var body = figEl.querySelector('.figure-body');
      body.innerHTML = figSrc.innerHTML;
      var labelSrc = srcFig.querySelector('[data-figlabel]');
      var label = figEl.querySelector('.figure-label');
      if (label && labelSrc) {
        var lab = labelSrc.textContent.trim();
        label.textContent = lab ? 'Fig. 1 — ' + lab : 'Fig. 1';
      }
      var capText = '';
      var capSrc = srcFig.querySelector('[data-figcaption]');
      if (capSrc) capText = capSrc.textContent.trim();
      setCaption(figEl, { text: capText });
      typesetIfMath(figEl, (body.innerHTML || '') + capText);
      return true;
    }

    // TikZ-only fallback: take a compact figure from the post body. Skip
    // `.fig-levels` — those two-panel SVGs wrap into a double-tall tower in
    // the half-width column and must not replace a hero.
    function pickBodyFigure(doc) {
      var tikz = doc.querySelector('.tikz-figure');
      if (tikz) return tikz;
      var figs = doc.querySelectorAll('.post-body figure');
      for (var i = 0; i < figs.length; i++) {
        if (figs[i].classList.contains('fig-levels')) continue;
        if (figs[i].querySelector('.fig-levels')) continue;
        return figs[i];
      }
      return null;
    }

    function applyFetched(cached) {
      var figEl = grid.querySelector('.featured-figure');
      if (!figEl) return;
      var body = figEl.querySelector('.figure-body');
      body.innerHTML = cached.markup;
      setCaption(figEl, cached.capHtml ? { html: cached.capHtml } : { text: '' });
      typesetIfMath(figEl, (cached.markup || '') + (cached.capHtml || ''));
    }

    var figCache = Object.create(null);

    function fetchFigure(url, token) {
      var key = pathOf(url);
      var base = new URL(url, location.href);
      fetch(url).then(function (r) {
        if (!r.ok) throw new Error('fetch ' + r.status);
        return r.text();
      }).then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var fig = pickBodyFigure(doc);
        if (!fig) throw new Error('no figure');

        // Caption: an <img> figure carries its own <figcaption>; a TikZ div
        // is followed by a "Figure N." paragraph (same pairing the server uses).
        var capHtml = '', innerCap = fig.querySelector('figcaption');
        if (innerCap) { capHtml = innerCap.innerHTML; innerCap.remove(); }
        else {
          var sib = fig.nextElementSibling;
          if (sib && sib.tagName === 'P' && /^\s*(<(strong|em)>)?\s*Figure\b/i.test(sib.innerHTML)) {
            capHtml = sib.innerHTML;
          }
        }
        capHtml = capHtml.replace(/^\s*<(strong|em)>\s*Figure\s+\d+\.?\s*<\/\1>\s*/i, '')
                         .replace(/^\s*Figure\s+\d+\.?\s*/i, '');

        Array.prototype.slice.call(fig.querySelectorAll('img[src], a[href]'))
          .forEach(function (el) {
            var attr = el.hasAttribute('src') ? 'src' : 'href';
            try { el.setAttribute(attr, new URL(el.getAttribute(attr), base).href); } catch (e) {}
          });
        var cached = {
          markup: fig.classList.contains('tikz-figure') ? fig.outerHTML : fig.innerHTML,
          capHtml: capHtml
        };
        figCache[key] = cached;
        if (token !== gen) return;
        applyFetched(cached);
      }).catch(function () {
        figCache[key] = { none: true };
        if (token !== gen) return;
        dropFigure();
      });
    }

    var idx = 0;
    var gen = 0;
    var dots = [];

    function renderSlide(row) {
      var url = itemUrl(row);
      var title = rowText(row, '.post-row-title');
      var desc = rowText(row, '.post-row-desc');
      var topic = rowText(row, '.post-row-topic');
      var date = rowText(row, '.post-row-date');
      var tags = rowTags(row);

      if (dateEl && date) dateEl.textContent = date;
      grid.style.gridTemplateColumns = '';
      grid.innerHTML =
        '<div class="featured-text">' +
          (topic ? '<span class="featured-topic">' + esc(topic) + '</span>' : '') +
          '<h2 class="featured-title"><a href="' + esc(url) + '">' + esc(title) + '</a></h2>' +
          (desc ? '<p class="featured-desc">' + esc(desc) + '</p>' : '') +
          (tags.length ? '<div class="tag-chips">' + tags.map(function (t) {
            return '<span class="tag-chip">' + esc(t) + '</span>'; }).join('') + '</div>' : '') +
          '<a class="featured-readmore" href="' + esc(url) + '">Read the note →</a>' +
        '</div>' +
        '<figure class="featured-figure">' +
          '<div class="figure-label">Fig. 1</div>' +
          '<div class="figure-body"></div>' +
          '<figcaption class="figure-caption"></figcaption>' +
        '</figure>';
    }

    function updateDots(focusDot) {
      dots.forEach(function (btn, k) {
        var current = k === idx;
        if (current) btn.setAttribute('aria-current', 'true');
        else btn.removeAttribute('aria-current');
        btn.tabIndex = current ? 0 : -1;
        if (current && focusDot) btn.focus();
      });
    }

    function show(n, opts) {
      if (!reel.length) return;
      idx = ((n % reel.length) + reel.length) % reel.length;
      var row = reel[idx];
      var url = itemUrl(row);
      try { sessionStorage.setItem(LAST, url); } catch (e) {}
      var token = ++gen;

      renderSlide(row);
      reconcile(url);
      updateDots(opts && opts.focusDot);

      if (applyRowHero(row)) return;

      var cached = figCache[pathOf(url)];
      if (cached) {
        if (cached.none) dropFigure();
        else applyFetched(cached);
        return;
      }
      fetchFigure(url, token);
    }

    function pickInitial() {
      var last = null;
      try { last = sessionStorage.getItem(LAST); } catch (e) {}
      var lastPath = pathOf(last);
      var choices = [];
      for (var i = 0; i < reel.length; i++) {
        if (pathOf(itemUrl(reel[i])) !== lastPath) choices.push(i);
      }
      if (!choices.length) {
        for (var j = 0; j < reel.length; j++) choices.push(j);
      }
      return choices[Math.floor(Math.random() * choices.length)];
    }

    function mountChrome() {
      if (reel.length < 2) return;

      featured.tabIndex = 0;

      var nav = document.createElement('nav');
      nav.className = 'featured-reel';
      nav.setAttribute('aria-label', 'Featured notes');

      function makeStep(dir, label) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'featured-reel-btn';
        b.setAttribute('aria-label', label);
        b.tabIndex = -1;
        b.textContent = dir < 0 ? '‹' : '›';
        b.addEventListener('click', function () { show(idx + dir); });
        return b;
      }

      nav.appendChild(makeStep(-1, 'Previous featured note'));

      var group = document.createElement('div');
      group.className = 'featured-dots';
      group.setAttribute('role', 'group');
      group.setAttribute('aria-label', 'Choose a featured note');

      reel.forEach(function (row, k) {
        var title = rowText(row, '.post-row-title') || 'Untitled';
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'featured-dot';
        btn.setAttribute('aria-label',
          'Featured note ' + (k + 1) + ' of ' + reel.length + ': ' + title);
        btn.addEventListener('click', function () { show(k); });
        group.appendChild(btn);
        dots.push(btn);
      });

      nav.appendChild(group);
      nav.appendChild(makeStep(1, 'Next featured note'));
      inner.appendChild(nav);

      var hint = document.createElement('p');
      hint.className = 'np-visually-hidden';
      hint.textContent = 'Arrow keys move between featured notes.';
      inner.appendChild(hint);

      featured.addEventListener('keydown', function (e) {
        if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
        if (e.altKey || e.ctrlKey || e.metaKey) return;
        var t = e.target;
        var onDot = t.classList && t.classList.contains('featured-dot');
        var onBtn = t.classList && t.classList.contains('featured-reel-btn');
        if (t !== featured && !onDot && !onBtn) return;
        e.preventDefault();
        show(idx + (e.key === 'ArrowRight' ? 1 : -1), { focusDot: onDot });
      });
    }

    mountChrome();
    show(pickInitial());
    reveal();
  });
})();
