/* PixPort General JavaScript Functions */

// Global app state
const PixPort = {
    currentImage: null,
    processing: false,
    settings: {
        selectedColor: 'white',
        selectedCountry: 'US',
        selectedQuality: 'high'
    }
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize Application
function initializeApp() {
    setupNavigation();
    setupToastSystem();
    setupGlobalEventListeners();
    
    // Initialize page-specific functionality
    if (document.querySelector('.hero')) {
        initializeHomePage();
    }
    
    console.log('🎯 PixPort initialized successfully');
}

// Navigation Setup
function setupNavigation() {
    const hamburger = document.getElementById('nav-hamburger');
    const navMenu = document.getElementById('nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            hamburger.classList.toggle('active');
            
            // Animate hamburger lines
            const lines = hamburger.querySelectorAll('.nav-hamburger-line');
            lines.forEach((line, index) => {
                if (hamburger.classList.contains('active')) {
                    if (index === 0) line.style.transform = 'rotate(45deg) translate(5px, 5px)';
                    if (index === 1) line.style.opacity = '0';
                    if (index === 2) line.style.transform = 'rotate(-45deg) translate(7px, -6px)';
                } else {
                    line.style.transform = '';
                    line.style.opacity = '';
                }
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                hamburger.classList.remove('active');
                
                // Reset hamburger animation
                const lines = hamburger.querySelectorAll('.nav-hamburger-line');
                lines.forEach(line => {
                    line.style.transform = '';
                    line.style.opacity = '';
                });
            }
        });
    }
}

// Toast Notification System
function setupToastSystem() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
}

function showToast(message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="closeToast(this)">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            closeToast(toast.querySelector('.toast-close'));
        }
    }, duration);
    
    // Add click to close
    toast.addEventListener('click', function() {
        closeToast(toast.querySelector('.toast-close'));
    });
}

function getToastIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

function closeToast(closeBtn) {
    const toast = closeBtn.parentElement;
    toast.style.animation = 'slideOut 0.3s ease-in forwards';
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Global Event Listeners
function setupGlobalEventListeners() {
    // Handle loading overlay
    setupLoadingSystem();
    
    // Handle form submissions
    document.addEventListener('submit', handleFormSubmissions);
    
    // Handle API calls
    setupApiHandlers();
}

// Loading System
function setupLoadingSystem() {
    // Create loading overlay if it doesn't exist
    if (!document.getElementById('loading-overlay')) {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay hidden';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Processing your image...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
}

function showLoading(message = 'Processing your image...') {
    const overlay = document.getElementById('loading-overlay');
    const text = overlay.querySelector('p');
    
    if (text) text.textContent = message;
    overlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('hidden');
    document.body.style.overflow = '';
}

// Form Submission Handler
function handleFormSubmissions(e) {
    if (e.target.tagName === 'FORM') {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.6';
            
            // Re-enable after 3 seconds to prevent indefinite disable
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.style.opacity = '';
            }, 3000);
        }
    }
}

// API Handlers
function setupApiHandlers() {
    // Set up CSRF token if available
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        // Set default headers for fetch requests
        window.fetch = new Proxy(window.fetch, {
            apply(target, thisArg, argumentsList) {
                const [url, config = {}] = argumentsList;
                
                if (config.method && config.method.toUpperCase() !== 'GET') {
                    config.headers = {
                        'X-CSRF-Token': csrfToken.getAttribute('content'),
                        ...config.headers
                    };
                }
                
                return Reflect.apply(target, thisArg, [url, config]);
            }
        });
    }
}

// API Functions
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(endpoint, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Image Processing Functions
async function uploadImage(file) {
    if (!file) {
        throw new Error('No file selected');
    }
    
    // Validate file
    if (!isValidImageFile(file)) {
        throw new Error('Please select a valid image file (JPG, PNG, HEIC)');
    }
    
    if (file.size > 16 * 1024 * 1024) {
        throw new Error('File size too large. Maximum 16MB allowed.');
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading('Uploading your image...');
    
    try {
        const response = await fetch('/process/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Upload failed');
        }
        
        hideLoading();
        return data;
    } catch (error) {
        hideLoading();
        throw error;
    }
}

async function processImage(action, filename, options = {}) {
    const endpoints = {
        remove_background: '/process/remove_background',
        change_background: '/process/change_background',
        enhance: '/process/enhance',
        resize: '/process/resize'
    };
    
    const endpoint = endpoints[action];
    if (!endpoint) {
        throw new Error('Invalid processing action');
    }
    
    const payload = { filename, ...options };
    
    showLoading(getProcessingMessage(action));
    
    try {
        const data = await apiCall(endpoint, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        hideLoading();
        return data;
    } catch (error) {
        hideLoading();
        throw error;
    }
}

function getProcessingMessage(action) {
    const messages = {
        remove_background: 'Removing background with AI...',
        change_background: 'Changing background color...',
        enhance: 'Enhancing image quality...',
        resize: 'Resizing to passport dimensions...'
    };
    
    return messages[action] || 'Processing image...';
}

// File Validation
function isValidImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/heic', 'image/webp'];
    return allowedTypes.includes(file.type.toLowerCase());
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        } catch (err) {
            document.body.removeChild(textArea);
            return Promise.reject(err);
        }
    }
}

// Home Page Initialization
function initializeHomePage() {
    console.log('🏠 Initializing home page...');
    
    // Any home page specific initialization
    setupScrollAnimations();
}

function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.step, .feature-card, .testimonial').forEach(el => {
        observer.observe(el);
    });
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    
    // Show user-friendly error for critical errors
    if (e.error && e.error.message) {
        showToast('Something went wrong. Please refresh the page and try again.', 'error');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    
    // Show user-friendly error for unhandled promises
    if (e.reason && typeof e.reason === 'string') {
        showToast(e.reason, 'error');
    } else {
        showToast('An unexpected error occurred. Please try again.', 'error');
    }
});

// Export functions for use in other scripts
window.PixPort = PixPort;
window.showToast = showToast;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.apiCall = apiCall;
window.uploadImage = uploadImage;
window.processImage = processImage;
window.formatFileSize = formatFileSize;
window.isValidImageFile = isValidImageFile;
window.copyToClipboard = copyToClipboard;
