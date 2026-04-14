document.addEventListener('DOMContentLoaded', function () {
  // Buttons placed inside each module should use this class
  const helpTriggers = document.querySelectorAll('.module-howto-btn');
  const helpModal = document.getElementById('helpModal');
  const helpCloseBtn = document.getElementById('helpCloseBtn');
  const helpGotIt = document.getElementById('helpGotIt');
  const helpModalContent = document.getElementById('helpModalContent');
  const helpTemplate = document.getElementById('module-help-template');
  const simpleToggle = document.getElementById('simple-toggle');
  const simpleIcon = document.getElementById('simple-toggle-icon');

  // Utility: set cookie
  function setCookie(name, value, days) {
    let expires = '';
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = '; expires=' + date.toUTCString();
    }
    document.cookie = name + '=' + (value || '') + expires + '; path=/';
  }

  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  function applySimpleMode(enabled) {
    if (enabled) {
      document.body.classList.add('simple-mode');
      simpleToggle && simpleToggle.setAttribute('aria-pressed', 'true');
      simpleIcon && (simpleIcon.textContent = 'format_size');
      // store preference in localStorage for quick client-side persistence
      try { localStorage.setItem('simple_mode', '1'); } catch (e) {}
    } else {
      document.body.classList.remove('simple-mode');
      simpleToggle && simpleToggle.setAttribute('aria-pressed', 'false');
      simpleIcon && (simpleIcon.textContent = 'format_size');
      try { localStorage.removeItem('simple_mode'); } catch (e) {}
    }
  }

  function setSimpleMode(enabled, persistCookie = true) {
    applySimpleMode(enabled);
    if (persistCookie) setCookie('simple_mode', enabled ? '1' : '0', 365);
  }

  // Initialize simple mode state from cookie or localStorage
  (function initSimpleMode() {
    let enabled = false;
    // check template-provided context first (server-side). If not available, fall back.
    try {
      // window.__SIMPLE_MODE might be injected by server later; fallback to cookie/localStorage
      if (typeof window.__SIMPLE_MODE !== 'undefined') {
        enabled = !!window.__SIMPLE_MODE;
      }
    } catch (e) {}

    if (!enabled) {
      const cookieVal = getCookie('simple_mode');
      if (cookieVal && (cookieVal === '1' || cookieVal.toLowerCase() === 'true')) enabled = true;
    }
    if (!enabled) {
      try { enabled = !!localStorage.getItem('simple_mode'); } catch (e) {}
    }
    setSimpleMode(enabled, false);
  })();

  if (simpleToggle) {
    simpleToggle.addEventListener('click', function () {
      const isActive = document.body.classList.contains('simple-mode');
      setSimpleMode(!isActive, true);
    });
  }

  // Note: We intentionally do NOT create a global floating FAB here.
  // Instead, each module should include a local "How to use" button with
  // the `module-howto-btn` class. This keeps help contextual to each module.

  // openHelp: accepts optional HTML content. If content is not provided,
  // it falls back to the server-provided `#module-help-template` block.
  function openHelp(contentHtml) {
    if (contentHtml) {
      helpModalContent.innerHTML = contentHtml;
    } else if (helpTemplate) {
      helpModalContent.innerHTML = helpTemplate.innerHTML.trim() || '<p class="text-sm text-gray-700 dark:text-gray-300">No help available for this module.</p>';
    } else {
      helpModalContent.innerHTML = '<p class="text-sm text-gray-700 dark:text-gray-300">No help available for this module.</p>';
    }
    helpModal.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
    // focus the modal close for accessibility
    helpCloseBtn && helpCloseBtn.focus();
  }

  function closeHelp() {
    helpModal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }

  if (helpTriggers && helpTriggers.length) {
    helpTriggers.forEach(function(el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        // Strategy: look for contextual help inside the nearest .module container
        let content = null;
        try {
          // If the button has a data-help-target attribute, use that element's HTML
          const targetId = el.getAttribute('data-help-target');
          if (targetId) {
            const targetEl = document.getElementById(targetId);
            if (targetEl) content = targetEl.innerHTML.trim();
          }
          // Otherwise, search for an inline .module-help element within the same module
          if (!content) {
            const moduleAncestor = el.closest('.module');
            if (moduleAncestor) {
              const localHelp = moduleAncestor.querySelector('.module-help');
              if (localHelp) content = localHelp.innerHTML.trim();
            }
          }
          // Fallback: if button has data-help-content, use it (HTML-encoded)
          if (!content) {
            const inline = el.getAttribute('data-help-content');
            if (inline) content = inline;
          }
        } catch (err) {
          console.error('help.js error locating module help content', err);
        }
        openHelp(content);
      });
    });
  }
  if (helpCloseBtn) {
    helpCloseBtn.addEventListener('click', closeHelp);
  }
  if (helpGotIt) {
    helpGotIt.addEventListener('click', closeHelp);
  }

  // Close on ESC
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeHelp();
  });

  // Close when clicking outside the modal content
  helpModal && helpModal.addEventListener('click', function (e) {
    if (e.target === helpModal) closeHelp();
  });
});
