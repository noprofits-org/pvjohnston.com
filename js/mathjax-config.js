(function () {
  'use strict';

  // This file is deferred, so the document is available by the time it runs.
  // Most pages have no math; do not download or execute MathJax on those pages.
  // Homepage featured captions can inject math later, so always export
  // window.ensureMathJax for a same-CDN lazy load.
  var ready = null;

  function injectScript() {
    var existing = document.getElementById('MathJax-script');
    if (existing) return existing;
    var script = document.createElement('script');
    script.id = 'MathJax-script';
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js';
    script.integrity = 'sha384-Wuix6BuhrWbjDBs24bXrjf4ZQ5aFeFWBuKkFekO2t8xFU0iNaLQfp2K6/1Nxveei';
    script.crossOrigin = 'anonymous';
    script.async = true;
    document.head.appendChild(script);
    return script;
  }

  function loadMathJax() {
    if (ready) return ready;
    if (!window.MathJax || !window.MathJax.tex) {
      window.MathJax = {
        tex: {
            // Pandoc emits real math as \(…\) / \[…\], never bare $…$ — so the
            // dollar delimiters add nothing but cause currency ("$300K … $559K")
            // to be paired into math at render time. Use only the brace forms.
            inlineMath: [['\\(', '\\)']],
            displayMath: [['\\[', '\\]']],
            processEscapes: true,
            packages: {'[+]': ['base', 'ams', 'noerrors', 'noundefined', '[tex]/mhchem']},
            tags: 'ams'
        },
        options: {
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
        },
        loader: {
            load: ['[tex]/mhchem']
        }
      };
    }
    ready = new Promise(function (resolve) {
      function waitStartup() {
        var MJ = window.MathJax;
        if (MJ && MJ.startup && MJ.startup.promise) MJ.startup.promise.then(resolve);
        else resolve();
      }
      var s = injectScript();
      if (window.MathJax && window.MathJax.typesetPromise) {
        waitStartup();
        return;
      }
      s.addEventListener('load', waitStartup);
    });
    return ready;
  }

  window.ensureMathJax = function (root) {
    loadMathJax().then(function () {
      var MJ = window.MathJax;
      if (!MJ || !MJ.typesetPromise) return;
      MJ.typesetPromise(root ? [root] : undefined).catch(function () {});
    });
  };

  if (document.querySelector('.math')) loadMathJax();
})();
