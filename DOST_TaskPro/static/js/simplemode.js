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
      for (var i = 0; i < tables.length; i++) {
        tables[i].style.display = isSimple ? 'none' : '';
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
