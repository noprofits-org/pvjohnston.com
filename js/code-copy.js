document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('pre code').forEach((block) => {
        const pre = block.parentNode;
        if (!pre || pre.tagName !== 'PRE') return;

        // The button must anchor to a wrapper, NOT to the pre itself. The pre
        // is both the scroll container (overflow-x: auto) and, previously, the
        // positioning context, so an absolutely-positioned child was part of
        // the scrollable content and slid away with the code on wide blocks.
        // Wrapping moves the positioning context off the scrolling element.
        let wrapper = pre.parentNode;
        if (!wrapper || !wrapper.classList.contains('code-block')) {
            wrapper = document.createElement('div');
            wrapper.className = 'code-block';
            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(pre);
        }

        // Guard against a second run (bfcache restore, re-injected script)
        // leaving two buttons on the same block.
        if (wrapper.querySelector(':scope > .copy-button')) return;

        const button = document.createElement('button');
        // Without an explicit type a <button> defaults to submit, which would
        // post an enclosing form if a code block ever appeared inside one.
        button.type = 'button';
        button.className = 'copy-button';
        button.textContent = 'Copy';
        wrapper.appendChild(button);

        button.addEventListener('click', async () => {
            try {
                const text = block.textContent || '';

                // Try the modern clipboard API first.
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(text);
                } else {
                    // Fallback for browsers without the async clipboard API.
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    textarea.style.position = 'fixed';  // avoid scrolling to bottom
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                }

                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
                button.textContent = 'Error';
            }
        });
    });
});
