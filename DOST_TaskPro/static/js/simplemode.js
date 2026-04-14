(function() {
  'use strict';
  var syncTimeout = null;
  var isProcessing = false;

  function isSimpleModeActive() {
    return document.documentElement.classList.contains('simple-mode');
  }

  function syncTables() {
    if (isProcessing) return;
    isProcessing = true;
    try {
      var tables = document.querySelectorAll('.table-section');
      var isSimple = isSimpleModeActive();
      var body = document.body;
      var isReversed = body && body.classList.contains('simple-mode-reversed');
      var isExcluded = body && body.classList.contains('no-simple-mode');
      var hasCharts = !!document.querySelector('.chart-section');

      for (var i = 0; i < tables.length; i++) {
        var tableEl = tables[i];

        if (!isSimple || isExcluded) {
          tableEl.style.removeProperty('display');
          continue;
        }

        if (isReversed) {
          tableEl.style.setProperty('display', 'block', 'important');
          continue;
        }

        // If a page has no chart section, keep table visible to avoid blank screens.
        if (hasCharts) {
          tableEl.style.setProperty('display', 'none', 'important');
        } else {
          tableEl.style.setProperty('display', 'block', 'important');
        }
      }
    } catch (e) {
      console.error('SimpleModeHelper error:', e);
    }
    isProcessing = false;
  }

  function debouncedSync() {
    clearTimeout(syncTimeout);
    syncTimeout = setTimeout(syncTables, 100);
  }

  function init() {
    syncTables();
    var observer = new MutationObserver(function(mutations) {
      for (var i = 0; i < mutations.length; i++) {
        if (mutations[i].attributeName === 'class') {
          debouncedSync();
          break;
        }
      }
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.SimpleModeHelper = {
    isActive: isSimpleModeActive,
    sync: syncTables
  };
})();
