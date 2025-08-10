/**
 * Performance Enhancement Script for PixPort
 * Handles loading states, retries, and user experience improvements
 */

// Performance monitoring
const PixPortPerformance = {
    startTime: null,
    metrics: {},
    retryAttempts: {}
};

// Initialize performance monitoring
document.addEventListener('DOMContentLoaded', function() {
    initializePerformanceEnhancements();
});

function initializePerformanceEnhancements() {
    setupRetryMechanism();
    setupProgressIndicators();
    setupConnectionCheck();
    preloadCriticalAssets();
    console.log('📊 Performance enhancements loaded');
}

// Retry mechanism for failed requests
function setupRetryMechanism() {
    window.pixportRetry = function(url, options = {}, maxRetries = 3) {
        const retryKey = url + JSON.stringify(options);
        
        if (!PixPortPerformance.retryAttempts[retryKey]) {
            PixPortPerformance.retryAttempts[retryKey] = 0;
        }
        
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                // Reset retry count on success
                PixPortPerformance.retryAttempts[retryKey] = 0;
                return response;
            })
            .catch(error => {
                const currentAttempt = PixPortPerformance.retryAttempts[retryKey];
                
                if (currentAttempt < maxRetries) {
                    PixPortPerformance.retryAttempts[retryKey]++;
                    
                    // Progressive delay: 1s, 3s, 5s
                    const delay = Math.min(1000 * (currentAttempt * 2 + 1), 5000);
                    
                    console.log(`🔄 Retrying request (${currentAttempt + 1}/${maxRetries}) in ${delay}ms...`);
                    
                    return new Promise(resolve => setTimeout(resolve, delay))
                        .then(() => pixportRetry(url, options, maxRetries));
                } else {
                    console.error(`❌ Request failed after ${maxRetries} retries:`, error);
                    throw error;
                }
            });
    };
}

// Enhanced progress indicators
function setupProgressIndicators() {
    // Create enhanced loading overlay
    const existingOverlay = document.getElementById('loading-overlay');
    if (existingOverlay) {
        existingOverlay.innerHTML = `
            <div class="loading-spinner enhanced">
                <div class="ai-icon">🤖</div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill"></div>
                    </div>
                    <div class="progress-text">
                        <p id="loading-message">Initializing AI models...</p>
                        <small id="loading-detail">This may take a moment on first use</small>
                    </div>
                </div>
                <div class="loading-tips">
                    <p id="loading-tip">💡 Tip: Your first image may take longer as we warm up the AI models</p>
                </div>
            </div>
        `;
    }
    
    // Enhanced loading function
    window.showEnhancedLoading = function(stage = 'init', progress = 0) {
        const overlay = document.getElementById('loading-overlay');
        const fill = document.getElementById('progress-fill');
        const message = document.getElementById('loading-message');
        const detail = document.getElementById('loading-detail');
        const tip = document.getElementById('loading-tip');
        
        if (!overlay) return;
        
        // Update progress bar
        if (fill) {
            fill.style.width = `${Math.min(progress, 100)}%`;
        }
        
        // Stage-specific messages
        const stages = {
            init: {
                message: 'Initializing AI models...',
                detail: 'This may take a moment on first use',
                tip: '💡 Tip: Your first image may take longer as we warm up the AI models'
            },
            upload: {
                message: 'Uploading your image...',
                detail: 'Preparing for AI processing',
                tip: '📤 Tip: We support JPG, PNG, HEIC, and WebP formats'
            },
            processing: {
                message: 'AI is processing your image...',
                detail: 'Removing background with advanced algorithms',
                tip: '🎨 Tip: High-quality processing ensures professional results'
            },
            background: {
                message: 'Applying new background...',
                detail: 'Optimizing colors and lighting',
                tip: '✨ Tip: We automatically adjust colors for the best look'
            },
            finalizing: {
                message: 'Finalizing your passport photo...',
                detail: 'Adding finishing touches',
                tip: '📏 Tip: Photos are automatically sized for your selected country'
            }
        };
        
        const currentStage = stages[stage] || stages.init;
        
        if (message) message.textContent = currentStage.message;
        if (detail) detail.textContent = currentStage.detail;
        if (tip) tip.textContent = currentStage.tip;
        
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    };
}

// Connection quality check
function setupConnectionCheck() {
    window.checkConnection = function() {
        return pixportRetry('/health', { method: 'GET' }, 1)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'healthy') {
                    return {
                        status: 'good',
                        modelsReady: data.models_ready || false,
                        coldStart: !data.models_ready
                    };
                }
                return { status: 'poor', modelsReady: false, coldStart: true };
            })
            .catch(() => ({ status: 'offline', modelsReady: false, coldStart: true }));
    };
    
    // Check on page load
    checkConnection().then(result => {
        if (result.coldStart) {
            console.log('🥶 Cold start detected - first request may be slower');
            showToast('AI models are warming up - first processing may take longer', 'info', 8000);
        }
    });
}

// Preload critical assets
function preloadCriticalAssets() {
    const criticalAssets = [
        '/static/css/style.css',
        '/static/js/script.js'
    ];
    
    criticalAssets.forEach(asset => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = asset.endsWith('.css') ? 'style' : 'script';
        link.href = asset;
        document.head.appendChild(link);
    });
}

// Enhanced error handling
window.handlePixPortError = function(error, context = '') {
    console.error(`PixPort Error ${context}:`, error);
    
    let userMessage = 'Something went wrong. Please try again.';
    let shouldRetry = true;
    
    // Parse different error types
    if (error.message) {
        if (error.message.includes('404')) {
            userMessage = 'The image processing failed. Please try uploading your image again.';
        } else if (error.message.includes('413') || error.message.includes('too large')) {
            userMessage = 'Your image is too large. Please use an image smaller than 16MB.';
            shouldRetry = false;
        } else if (error.message.includes('timeout')) {
            userMessage = 'Processing is taking longer than expected. This often happens on the first use.';
        } else if (error.message.includes('network')) {
            userMessage = 'Network connection issue. Please check your internet and try again.';
        }
    }
    
    hideLoading();
    
    // Show error with retry option
    if (shouldRetry) {
        showToast(`${userMessage} <button onclick="location.reload()" class="retry-btn">Retry</button>`, 'error', 10000);
    } else {
        showToast(userMessage, 'error', 8000);
    }
    
    return { userMessage, shouldRetry };
};

// Performance measurement
window.measurePerformance = function(operation, startTime) {
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    PixPortPerformance.metrics[operation] = {
        duration,
        timestamp: endTime
    };
    
    console.log(`⏱️ ${operation} took ${duration}ms`);
    
    // Show performance hints
    if (duration > 30000) { // 30 seconds
        showToast('Processing took longer than usual - this is normal for the first image', 'info');
    }
    
    return duration;
};

// Smart retry for form submissions
window.smartSubmit = function(form, maxRetries = 2) {
    const formData = new FormData(form);
    const startTime = Date.now();
    
    showEnhancedLoading('upload', 10);
    
    return pixportRetry(form.action, {
        method: form.method || 'POST',
        body: formData
    }, maxRetries)
    .then(response => {
        showEnhancedLoading('processing', 50);
        return response;
    })
    .catch(error => {
        measurePerformance('form_submission_failed', startTime);
        throw error;
    });
};

// CSS injection for enhanced UI
const performanceStyles = `
.loading-spinner.enhanced {
    text-align: center;
    max-width: 400px;
    margin: 0 auto;
}

.ai-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    animation: bounce 2s infinite;
}

.progress-container {
    margin: 2rem 0;
}

.progress-bar {
    background: rgba(255,255,255,0.2);
    border-radius: 10px;
    height: 6px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.progress-fill {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    height: 100%;
    width: 0%;
    transition: width 0.5s ease;
}

.progress-text p {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.progress-text small {
    opacity: 0.8;
    font-size: 0.875rem;
}

.loading-tips {
    margin-top: 2rem;
    padding: 1rem;
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    font-size: 0.875rem;
}

.retry-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    margin-left: 0.5rem;
    cursor: pointer;
    font-size: 0.875rem;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = performanceStyles;
document.head.appendChild(styleSheet);
