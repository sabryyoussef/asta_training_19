(function () {
  'use strict';
  
  // Check if console tap is explicitly enabled (default: disabled to avoid connection errors)
  if (window.__CONSOLE_TAP_ENABLED__ !== true) {
    return; // Exit early if not explicitly enabled
  }
  
  // Configuration
  const CONSOLE_TAP_PORT = window.__CONSOLE_TAP_PORT__ || 5055;
  const CONSOLE_TAP_URL = window.__CONSOLE_TAP_URL__ || `${location.protocol}//${location.hostname}:${CONSOLE_TAP_PORT}/__console_tap__`;
  
  // Utility function to safely stringify objects
  function safeStringify(obj) {
    try {
      return JSON.stringify(obj);
    } catch (e) {
      return String(obj);
    }
  }
  
  // Send data to console tap server (only if server is available)
  // This is a development tool - fails silently if server is not running
  let serverAvailable = null;
  
  function post(data) {
    // Check if console tap is disabled or server unavailable
    if (window.__CONSOLE_TAP_DISABLED__ === true) {
      return; // Console tap is explicitly disabled
    }
    
    try {
      const payload = JSON.stringify({
        ...data,
        timestamp: Date.now(),
        url: location.href,
        userAgent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      });
      
      // Use fetch with proper error handling to avoid connection refused errors
      if (navigator.sendBeacon) {
        try {
          const sent = navigator.sendBeacon(CONSOLE_TAP_URL, new Blob([payload], { type: 'application/json' }));
          if (!sent) {
            // If sendBeacon fails, don't retry - server likely not available
            return;
          }
        } catch (e) {
          // Silent fail - server not available
          return;
        }
      } else {
        fetch(CONSOLE_TAP_URL, { 
          method: 'POST', 
          headers: { 'Content-Type': 'application/json' }, 
          body: payload, 
          keepalive: true,
          mode: 'no-cors' // Prevents CORS errors, but also hides connection errors
        }).catch(() => {
          // Silent fail - server not available
        });
      }
    } catch (e) {
      // Silent fail - don't break the app
    }
  }
  
  // Capture window errors
  window.addEventListener('error', function(e) {
    post({
      level: 'error',
      type: 'window.error',
      message: e.message,
      filename: e.filename,
      lineno: e.lineno,
      colno: e.colno,
      stack: e.error ? e.error.stack : null
    });
  });
  
  // Capture unhandled promise rejections
  window.addEventListener('unhandledrejection', function(e) {
    const reason = e.reason || {};
    post({
      level: 'error',
      type: 'unhandledrejection',
      reason: String(reason.message || reason),
      stack: reason.stack || null
    });
  });
  
  // Capture console methods
  const originalMethods = {
    error: console.error,
    warn: console.warn,
    info: console.info,
    log: console.log,
    debug: console.debug
  };
  
  Object.keys(originalMethods).forEach(function(method) {
    console[method] = function() {
      // Call original method
      originalMethods[method].apply(console, arguments);
      
      // Send to tap server
      post({
        level: method,
        type: 'console.' + method,
        args: Array.prototype.slice.call(arguments).map(function(arg) {
          return typeof arg === 'string' ? arg : safeStringify(arg);
        })
      });
    };
  });
  
  // Capture network errors (if fetch is available)
  if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = function() {
      return originalFetch.apply(this, arguments)
        .catch(function(error) {
          post({
            level: 'error',
            type: 'fetch.error',
            message: error.message,
            stack: error.stack
          });
          throw error;
        });
    };
  }
  
  // Send initialization message (only if server is available)
  // Note: This will only run if __CONSOLE_TAP_ENABLED__ is set to true
  try {
    post({
      level: 'info',
      type: 'console_tap.initialized',
      message: 'Console tap initialized'
    });
  } catch (e) {
    // Silent fail - server not available
  }
  
})();
