/* PixPort Cache Buster Utility */

// Comprehensive cache busting for all JavaScript requests
(function() {
    'use strict';
    
    // Generate cache busting parameter
    function getCacheBuster() {
        return Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    }
    
    // Override fetch to add cache busting
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        let modifiedUrl = url;
        
        // Add cache buster to all non-external URLs
        if (typeof url === 'string' && !url.startsWith('http') && !url.startsWith('//')) {
            const separator = url.includes('?') ? '&' : '?';
            modifiedUrl = `${url}${separator}_cb=${getCacheBuster()}`;
        }
        
        // Add cache control headers
        const modifiedOptions = {
            ...options,
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                ...options.headers
            }
        };
        
        return originalFetch.call(this, modifiedUrl, modifiedOptions);
    };
    
    // Override XMLHttpRequest for older code
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        let modifiedUrl = url;
        
        // Add cache buster to all non-external URLs
        if (typeof url === 'string' && !url.startsWith('http') && !url.startsWith('//')) {
            const separator = url.includes('?') ? '&' : '?';
            modifiedUrl = `${url}${separator}_cb=${getCacheBuster()}`;
        }
        
        return originalXHROpen.call(this, method, modifiedUrl, async, user, password);
    };
    
    // Force reload specific elements on page load
    function forceReloadResources() {
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        const scripts = document.querySelectorAll('script[src]');
        
        // Reload stylesheets
        stylesheets.forEach(link => {
            if (link.href && !link.href.includes('cdnjs.cloudflare.com') && !link.href.includes('fonts.googleapis.com')) {
                const href = link.href;
                const separator = href.includes('?') ? '&' : '?';
                link.href = `${href}${separator}_cb=${getCacheBuster()}`;
            }
        });
    }
    
    // Disable back/forward cache (bfcache)
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Page was loaded from cache, force reload
            window.location.reload();
        }
    });
    
    // Clear browser caches when possible
    function clearCaches() {
        // Clear localStorage cache markers if they exist
        try {
            const cacheKeys = Object.keys(localStorage).filter(key => key.startsWith('pixport_cache_'));
            cacheKeys.forEach(key => localStorage.removeItem(key));
        } catch (e) {
            console.debug('Could not clear localStorage cache');
        }
        
        // Clear sessionStorage cache markers
        try {
            const sessionCacheKeys = Object.keys(sessionStorage).filter(key => key.startsWith('pixport_cache_'));
            sessionCacheKeys.forEach(key => sessionStorage.removeItem(key));
        } catch (e) {
            console.debug('Could not clear sessionStorage cache');
        }
        
        // Force clear Service Worker cache if available
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistrations().then(registrations => {
                registrations.forEach(registration => {
                    registration.update(); // Update SW
                });
            });
        }
        
        // Clear Cache API if available
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => {
                    if (name.includes('pixport')) {
                        caches.delete(name);
                    }
                });
            });
        }
    }
    
    // Add meta refresh as fallback
    function addMetaRefresh() {
        const metaRefresh = document.createElement('meta');
        metaRefresh.setAttribute('http-equiv', 'refresh');
        metaRefresh.setAttribute('content', '0');
        
        // Only add if not already present
        if (!document.querySelector('meta[http-equiv="refresh"]')) {
            document.head.appendChild(metaRefresh);
            setTimeout(() => document.head.removeChild(metaRefresh), 100);
        }
    }
    
    // Initialize cache busting
    function initCacheBuster() {
        clearCaches();
        
        // Force reload on first load
        if (!sessionStorage.getItem('pixport_cache_busted')) {
            sessionStorage.setItem('pixport_cache_busted', 'true');
            forceReloadResources();
        }
        
        // Add cache buster to all form submissions
        document.addEventListener('submit', function(event) {
            const form = event.target;
            if (form.tagName === 'FORM') {
                const cacheBusterInput = document.createElement('input');
                cacheBusterInput.type = 'hidden';
                cacheBusterInput.name = '_cb';
                cacheBusterInput.value = getCacheBuster();
                form.appendChild(cacheBusterInput);
            }
        });
        
        // Periodically clear caches
        setInterval(clearCaches, 30000); // Every 30 seconds
    }
    
    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCacheBuster);
    } else {
        initCacheBuster();
    }
    
    // Export utilities for global use
    window.PixPortCache = {
        bust: getCacheBuster,
        clear: clearCaches,
        reload: forceReloadResources
    };
    
    console.log('🚫 PixPort Cache Buster initialized - Browser caching disabled');
})();
