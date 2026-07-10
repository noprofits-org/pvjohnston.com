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