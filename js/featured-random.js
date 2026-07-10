// Home-page featured-post randomizer. Progressive enhancement: the server bakes
// the newest post that HAS A FIGURE into the featured slot (so the card is valid
// with JS off and for crawlers). On each visit this swaps in a random
// figure-having post — the TEXT immediately (it all lives in the Latest row, no
// fetch) so the baked default never flashes, then the FIGURE fetched from that
// one post's page and dropped into a reserved slot. Any failure leaves the baked
// default or the text-only card.
//
// The card is held invisible pre-paint by a small inline script in the page head
// (the `feat-pending` class); reveal() clears it once the text is in place.
//
// innerHTML is built only from first-party same-origin content (the site's own
// rows/pages), with all plain-text fields HTML-escaped.
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    function reveal() { document.documentElement.classList.remove('feat-pending'); }

    var featured = document.querySelector('.featured');
    if (!featured) { reveal(); return; }
    var grid = featured.querySelector('.featured-grid');
    var dateEl = featured.querySelector('.featured-date');
    if (!grid) { reveal(); return; }

    var rows = Array.prototype.slice.call(
      document.querySelectorAll('.post-row[data-has-figure]'));
    if (!rows.length) { reveal(); return; }

    var curLink = featured.querySelector('.featured-title a');
    var curUrl = curLink ? curLink.getAttribute('href') : null;

    function pathOf(u) {
      try { return new URL(u, location.href).pathname; } catch (e) { return u || ''; }
    }
    // Hide whichever Latest row is the currently-featured post (class, not the
    // [hidden] attribute, so the topic filter can't un-hide it).
    function reconcile(url) {
      var p = pathOf(url);
      Array.prototype.slice.call(document.querySelectorAll('.post-row'))
        .forEach(function (r) {
          r.classList.toggle('is-featured', pathOf(r.getAttribute('href')) === p);
        });
    }

    // Random eligible row, avoiding the previous pick and the baked default so
    // the card visibly changes.
    var LAST = 'np-featured-last', last = null;
    try { last = sessionStorage.getItem(LAST); } catch (e) {}
    var choices = rows.filter(function (r) {
      var p = pathOf(r.getAttribute('href'));
      return p !== pathOf(last) && p !== pathOf(curUrl);
    });
    if (!choices.length) {
      choices = rows.filter(function (r) {
        return pathOf(r.getAttribute('href')) !== pathOf(curUrl);
      });
    }
    if (!choices.length) { reconcile(curUrl); reveal(); return; }

    var pick = choices[Math.floor(Math.random() * choices.length)];
    var url = pick.getAttribute('href');
    try { sessionStorage.setItem(LAST, url); } catch (e) {}
    var base = new URL(url, location.href);

    function esc(s) { var d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
    function rowText(sel) { var n = pick.querySelector(sel); return n ? n.textContent.trim() : ''; }

    // The picker injects the figure + caption AFTER MathJax's one-time initial
    // typeset has already run, so any \(...\) in a fetched caption stays raw.
    // Re-typeset just the injected subtree once MathJax is ready.
    function typeset(el) {
      var MJ = window.MathJax;
      if (!MJ) return;
      var run = function () { if (MJ.typesetPromise) MJ.typesetPromise([el]).catch(function () {}); };
      if (MJ.startup && MJ.startup.promise) MJ.startup.promise.then(run);
      else run();
    }

    // ---- Synchronous: swap the text column now, reserve the figure, reveal. ----
    var title = rowText('.post-row-title'), desc = rowText('.post-row-desc'),
        topic = rowText('.post-row-topic'), date = rowText('.post-row-date');
    var tags = Array.prototype.slice.call(pick.querySelectorAll('.post-row-tags .row-tag'))
      .map(function (t) { return t.textContent.replace(/^#/, '').trim(); }).filter(Boolean);

    if (dateEl && date) dateEl.textContent = date;

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
        '<div class="figure-body" style="min-height:240px"></div>' +
      '</figure>';

    reconcile(url);
    reveal();

    // ---- Async: fetch the chosen post's figure and drop it into the slot. ----
    fetch(url).then(function (r) {
      if (!r.ok) throw new Error('fetch ' + r.status);
      return r.text();
    }).then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var fig = doc.querySelector('.tikz-figure, .post-body figure');
      if (!fig) throw new Error('no figure');

      // Caption: an <img> figure carries its own <figcaption>; a TikZ div is
      // followed by a "Figure N." paragraph (same pairing the server uses).
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

      // Absolutize asset/link URLs so they resolve from "/".
      Array.prototype.slice.call(fig.querySelectorAll('img[src], a[href]'))
        .forEach(function (el) {
          var attr = el.hasAttribute('src') ? 'src' : 'href';
          try { el.setAttribute(attr, new URL(el.getAttribute(attr), base).href); } catch (e) {}
        });
      var figMarkup = fig.classList.contains('tikz-figure') ? fig.outerHTML : fig.innerHTML;

      var figEl = grid.querySelector('.featured-figure');
      if (!figEl) return;
      var body = figEl.querySelector('.figure-body');
      body.style.minHeight = '';
      body.innerHTML = figMarkup;
      if (capHtml) {
        var cap = document.createElement('figcaption');
        cap.className = 'figure-caption';
        cap.innerHTML = capHtml;
        figEl.appendChild(cap);
      }
      typeset(figEl);
    }).catch(function () {
      // No figure available: drop the empty slot and let the text fill the row.
      var figEl = grid.querySelector('.featured-figure');
      if (figEl) figEl.remove();
      grid.style.gridTemplateColumns = '1fr';
    });
  });
})();
