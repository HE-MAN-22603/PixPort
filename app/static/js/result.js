/* PixPort Result Page JavaScript */

// Result page state with better management
const resultState = {
    filename: null,
    downloadCount: parseInt(localStorage.getItem('downloadCount') || '0'),
    shareCount: parseInt(localStorage.getItem('shareCount') || '0'),
    comparisonMode: false,
    imageMetadata: null,
    isDownloading: false,
    retryCount: 0,
    maxRetries: 3
};

// State management with persistence
const updateState = (key, value) => {
    resultState[key] = value;
    // Persist certain state to localStorage
    if (['downloadCount', 'shareCount'].includes(key)) {
        localStorage.setItem(key, value.toString());
    }
    // Dispatch custom event for state changes
    window.dispatchEvent(new CustomEvent('resultStateChanged', { 
        detail: { key, value, state: resultState } 
    }));
};

// Use global debounce and throttle functions from script.js if available
const debounceResult = window.debounce || ((func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
});

const throttleResult = window.throttle || ((func, limit) => {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
});

// Initialize result page
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.result-page')) {
        initializeResultPage();
    }
});

function initializeResultPage() {
    console.log('📋 Initializing result page...');
    
    // Get filename from URL
    resultState.filename = getFilenameFromURL();
    
    setupDownloadButtons();
    setupImageControls();
    setupComparisonMode();
    setupSharingFeatures();
    loadImageMetadata();
    
    // Show success animation
    showSuccessAnimation();
    
    // Dispatch event to signal result page is ready
    document.dispatchEvent(new CustomEvent('resultPageReady', { 
        detail: { state: resultState } 
    }));
}

function getFilenameFromURL() {
    const path = window.location.pathname;
    const matches = path.match(/\/result\/(.+)$/);
    return matches ? matches[1] : null;
}

function setupDownloadButtons() {
    const downloadBtns = document.querySelectorAll('.download-btn');
    
    downloadBtns.forEach(btn => {
        btn.addEventListener('click', async function() {
            const format = this.dataset.format;
            const quality = this.dataset.quality || '95';
            
            // Prevent multiple downloads
            if (this.disabled) return;
            
            // Show loading state
            const originalContent = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i> <span>Downloading...</span>';
            
            // Show progress
            showDownloadProgress();
            
            try {
                await downloadImage(format, quality);
                resultState.downloadCount++;
                updateDownloadCount();
                
                // Show success feedback
                showToast(`Image downloaded as ${format.toUpperCase()}!`, 'success');
                
            } catch (error) {
                console.error('Download error:', error);
                showToast(`Download failed: ${error.message || 'Unknown error occurred'}`, 'error');
            } finally {
                // Reset button state
                this.disabled = false;
                this.innerHTML = originalContent;
                hideDownloadProgress();
            }
        });
    });
    
    // Setup format selector
    const formatSelector = document.querySelector('#download-format');
    const qualitySlider = document.querySelector('#quality-slider');
    const qualityValue = document.querySelector('#quality-value');
    
    if (formatSelector) {
        formatSelector.addEventListener('change', function() {
            const format = this.value;
            
            // Show/hide quality slider based on format
            if (qualitySlider && qualityValue) {
                const showQuality = ['JPEG', 'JPG', 'WEBP'].includes(format.toUpperCase());
                qualitySlider.style.display = showQuality ? 'block' : 'none';
            }
            
            // Update download button
            updateDownloadButton();
        });
    }
    
    if (qualitySlider) {
        qualitySlider.addEventListener('input', function() {
            if (qualityValue) qualityValue.textContent = this.value + '%';
            updateDownloadButton();
        });
    }
}

function updateDownloadButton() {
    const mainDownloadBtn = document.querySelector('.download-btn-main');
    const formatSelector = document.querySelector('#download-format');
    const qualitySlider = document.querySelector('#quality-slider');
    
    if (!mainDownloadBtn || !formatSelector) return;
    
    const format = formatSelector.value;
    const quality = qualitySlider ? qualitySlider.value : '95';
    
    mainDownloadBtn.dataset.format = format;
    mainDownloadBtn.dataset.quality = quality;
    
    // Update button text
    const formatText = format.toUpperCase();
    const qualityText = ['JPEG', 'JPG', 'WEBP'].includes(formatText) ? ` (${quality}%)` : '';
    mainDownloadBtn.innerHTML = `
        <i class="fas fa-download" aria-hidden="true"></i>
        <span class="download-text">Download ${formatText}${qualityText}</span>
    `;
    
    // Update aria-label for accessibility
    mainDownloadBtn.setAttribute('aria-label', `Download as ${format} ${qualityText ? 'with ' + quality + '% quality' : ''}`);
}

// Input sanitization utility
const sanitizeInput = {
    filename: (filename) => {
        if (!filename || typeof filename !== 'string') return null;
        // Remove dangerous characters and normalize
        return filename.replace(/[^a-zA-Z0-9._-]/g, '').substring(0, 255);
    },
    
    format: (format) => {
        const allowedFormats = ['JPEG', 'PNG', 'WEBP', 'PDF'];
        return allowedFormats.includes(format.toUpperCase()) ? format.toUpperCase() : 'JPEG';
    },
    
    quality: (quality) => {
        const num = parseInt(quality, 10);
        return isNaN(num) ? 95 : Math.max(60, Math.min(100, num));
    }
};

// Retry mechanism with exponential backoff
async function retryOperation(operation, maxRetries = 3, baseDelay = 1000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await operation();
        } catch (error) {
            if (attempt === maxRetries) throw error;
            
            // Don't retry on certain error types
            if (error.name === 'AbortError' || error.message.includes('404') || error.message.includes('400')) {
                throw error;
            }
            
            const delay = baseDelay * Math.pow(2, attempt - 1) + Math.random() * 1000;
            console.warn(`Attempt ${attempt} failed, retrying in ${delay}ms:`, error.message);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

// Enhanced download with retry and better error handling
async function downloadImage(format = 'JPEG', quality = '95') {
    // Prevent concurrent downloads
    if (resultState.isDownloading) {
        throw new Error('Download already in progress');
    }
    
    const sanitizedFilename = sanitizeInput.filename(resultState.filename);
    if (!sanitizedFilename) {
        throw new Error('No valid image filename available');
    }
    
    const sanitizedFormat = sanitizeInput.format(format);
    const sanitizedQuality = sanitizeInput.quality(quality);
    
    updateState('isDownloading', true);
    
    try {
        return await retryOperation(async () => {
            const params = new URLSearchParams({
                format: sanitizedFormat,
                quality: sanitizedQuality.toString()
            });
            
            // Add timeout for fetch request
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            try {
                const response = await fetch(`/api/download/${encodeURIComponent(sanitizedFilename)}?${params}`, {
                    signal: controller.signal,
                    headers: {
                        'Accept': 'application/octet-stream, image/*, application/pdf',
                        'Cache-Control': 'no-cache'
                    }
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    let errorMessage = 'Download failed';
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.message || errorData.error || errorMessage;
                    } catch {
                        errorMessage = `Server returned ${response.status}: ${response.statusText}`;
                    }
                    throw new Error(errorMessage);
                }
                
                // Get filename from response headers or generate one
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = `passport_photo_${Date.now()}.${sanitizedFormat.toLowerCase()}`;
                
                if (contentDisposition) {
                    const matches = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/); 
                    if (matches && matches[1]) {
                        filename = matches[1].replace(/["']/g, '');
                        // Sanitize filename
                        filename = filename.replace(/[^a-zA-Z0-9._-]/g, '_');
                    }
                }
                
                // Validate response is actually a file
                const contentType = response.headers.get('Content-Type');
                if (!contentType || (!contentType.startsWith('image/') && !contentType.startsWith('application/'))) {
                    throw new Error('Invalid file format received from server');
                }
                
                // Create download link with better error handling
                const blob = await response.blob();
                
                if (blob.size === 0) {
                    throw new Error('Received empty file');
                }
                
                const url = window.URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.style.display = 'none';
                document.body.appendChild(a);
                
                // Trigger download
                a.click();
                
                // Clean up
                setTimeout(() => {
                    if (document.body.contains(a)) {
                        document.body.removeChild(a);
                    }
                    window.URL.revokeObjectURL(url);
                }, 100);
                
                return { filename, size: blob.size, type: contentType };
                
            } catch (error) {
                clearTimeout(timeoutId);
                
                if (error.name === 'AbortError') {
                    throw new Error('Download timed out. Please try again.');
                }
                
                throw error;
            }
        }, resultState.maxRetries, 1000);
    } finally {
        updateState('isDownloading', false);
    }
}

function setupImageControls() {
    const resultImage = document.querySelector('.result-image');
    const zoomControls = document.querySelector('.zoom-controls');
    
    if (!resultImage) return;
    
    // Image zoom functionality
    let zoomLevel = 1;
    let isDragging = false;
    let dragStart = { x: 0, y: 0 };
    let imageOffset = { x: 0, y: 0 };
    
    const zoomInBtn = zoomControls?.querySelector('[data-action="zoom-in"]');
    const zoomOutBtn = zoomControls?.querySelector('[data-action="zoom-out"]');
    const resetBtn = zoomControls?.querySelector('[data-action="reset"]');
    
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            zoomLevel = Math.min(3, zoomLevel * 1.2);
            updateImageTransform();
        });
    }
    
    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            zoomLevel = Math.max(0.5, zoomLevel * 0.8);
            updateImageTransform();
        });
    }
    
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            zoomLevel = 1;
            imageOffset = { x: 0, y: 0 };
            updateImageTransform();
        });
    }
    
    function updateImageTransform() {
        resultImage.style.transform = `scale(${zoomLevel}) translate(${imageOffset.x}px, ${imageOffset.y}px)`;
        
        if (zoomInBtn) zoomInBtn.disabled = zoomLevel >= 3;
        if (zoomOutBtn) zoomOutBtn.disabled = zoomLevel <= 0.5;
    }
    
    // Drag functionality
    resultImage.addEventListener('mousedown', (e) => {
        if (zoomLevel <= 1) return;
        isDragging = true;
        dragStart = {
            x: e.clientX - imageOffset.x,
            y: e.clientY - imageOffset.y
        };
        resultImage.style.cursor = 'grabbing';
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        imageOffset = {
            x: e.clientX - dragStart.x,
            y: e.clientY - dragStart.y
        };
        updateImageTransform();
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
        resultImage.style.cursor = 'grab';
    });
}

function setupComparisonMode() {
    const toggleBtn = document.querySelector('.comparison-toggle');
    const container = document.querySelector('.comparison-container');
    
    if (!toggleBtn || !container) return;
    
    toggleBtn.addEventListener('click', function() {
        resultState.comparisonMode = !resultState.comparisonMode;
        
        if (resultState.comparisonMode) {
            container.classList.add('active');
            // Remove aria-hidden when showing the comparison
            container.setAttribute('aria-hidden', 'false');
            this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            loadComparisonImages();
        } else {
            container.classList.remove('active');
            // Add aria-hidden when hiding the comparison
            container.setAttribute('aria-hidden', 'true');
            this.innerHTML = '<i class="fas fa-eye"></i>';
        }
    });
}

async function loadComparisonImages() {
    const originalImg = document.querySelector('.comparison-original');
    const processedImg = document.querySelector('.comparison-processed');
    
    if (!originalImg || !processedImg || !resultState.filename) return;
    
    try {
        // Get original filename from API
        const response = await fetch(`/api/comparison/${resultState.filename}`);
        const data = await response.json();
        
        if (data.success) {
            originalImg.src = `/static/uploads/${data.original_filename}`;
            processedImg.src = `/static/processed/${resultState.filename}`;
        }
    } catch (error) {
        console.error('Failed to load comparison images:', error);
    }
}

function setupSharingFeatures() {
    const shareBtn = document.querySelector('.share-btn');
    const copyLinkBtn = document.querySelector('.copy-link-btn');
    
    if (shareBtn) {
        shareBtn.addEventListener('click', async function() {
            // Prevent multiple clicks
            if (this.disabled) return;
            
            this.disabled = true;
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i>';
            
            try {
                if (navigator.share && navigator.canShare) {
                    const shareData = {
                        title: 'PixPort - AI Passport Photo',
                        text: 'Check out my passport photo created with PixPort AI!',
                        url: window.location.href
                    };
                    
                    if (navigator.canShare(shareData)) {
                        await navigator.share(shareData);
                        resultState.shareCount++;
                        showToast('Shared successfully!', 'success');
                    } else {
                        throw new Error('Cannot share this content');
                    }
                } else {
                    // Fallback: copy to clipboard
                    await copyToClipboard(window.location.href);
                    showToast('Link copied to clipboard!', 'success');
                }
            } catch (error) {
                if (error.name !== 'AbortError') {
                    console.warn('Share failed, falling back to clipboard:', error);
                    try {
                        await copyToClipboard(window.location.href);
                        showToast('Link copied to clipboard!', 'success');
                    } catch (clipboardError) {
                        console.error('Clipboard fallback failed:', clipboardError);
                        showToast('Unable to share or copy link', 'error');
                    }
                }
            } finally {
                this.disabled = false;
                this.innerHTML = originalContent;
            }
        });
    }
    
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', async function() {
            if (this.disabled) return;
            
            this.disabled = true;
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i> <div class="action-content"><span class="action-title">Copying...</span></div>';
            
            try {
                await copyToClipboard(window.location.href);
                showToast('Link copied to clipboard!', 'success');
            } catch (error) {
                console.error('Copy to clipboard failed:', error);
                showToast('Unable to copy link to clipboard', 'error');
            } finally {
                this.disabled = false;
                this.innerHTML = originalContent;
            }
        });
    }
}

async function loadImageMetadata() {
    if (!resultState.filename) {
        console.warn('No filename available for metadata loading');
        return;
    }
    
    const loadingElement = document.querySelector('.loading-stats');
    const statsContainer = document.querySelector('.image-stats');
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
        
        const response = await fetch(`/api/image-info/${resultState.filename}`, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.width && data.height) {
            resultState.imageMetadata = data;
            updateImageStats();
        } else {
            throw new Error(data.message || 'Invalid metadata received');
        }
        
    } catch (error) {
        console.error('Failed to load image metadata:', error);
        
        // Show error state in UI
        if (statsContainer && loadingElement) {
            statsContainer.innerHTML = `
                <div class="error-stats">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Unable to load image details</span>
                </div>
            `;
        }
    }
}

function updateImageStats() {
    const statsContainer = document.querySelector('.image-stats');
    if (!statsContainer || !resultState.imageMetadata) {
        console.warn('Cannot update stats: missing container or metadata');
        return;
    }
    
    const info = resultState.imageMetadata;
    
    // Validate required data
    if (!info.width || !info.height) {
        console.error('Invalid metadata: missing dimensions');
        return;
    }
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <span class="stat-label">Format</span>
            <span class="stat-value">${info.format || 'JPEG'}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Dimensions</span>
            <span class="stat-value">${info.width} × ${info.height}px</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">File Size</span>
            <span class="stat-value">${formatFileSize(info.file_size || 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">DPI</span>
            <span class="stat-value">${info.dpi || '300'} DPI</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Color Space</span>
            <span class="stat-value">${info.color_space || 'sRGB'}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Modified</span>
            <span class="stat-value">${formatDate(info.modified)}</span>
        </div>
    `;
    
    // Add animation
    statsContainer.style.opacity = '0';
    setTimeout(() => {
        statsContainer.style.transition = 'opacity 0.3s ease';
        statsContainer.style.opacity = '1';
    }, 50);
}

function updateDownloadCount() {
    const countElement = document.querySelector('.download-count');
    if (countElement) {
        countElement.textContent = resultState.downloadCount;
        
        // Add animation
        countElement.classList.add('updated');
        setTimeout(() => countElement.classList.remove('updated'), 500);
    }
}

function showSuccessAnimation() {
    const successHeader = document.querySelector('.success-header');
    const resultImage = document.querySelector('.result-image');
    
    if (successHeader) {
        // Animate success header
        successHeader.style.opacity = '0';
        successHeader.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            successHeader.style.transition = 'all 0.6s ease';
            successHeader.style.opacity = '1';
            successHeader.style.transform = 'translateY(0)';
        }, 200);
    }
    
    if (resultImage) {
        // Animate result image
        resultImage.style.opacity = '0';
        resultImage.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            resultImage.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            resultImage.style.opacity = '1';
            resultImage.style.transform = 'scale(1)';
        }, 400);
    }
    
    // Animate download panel
    const downloadPanel = document.querySelector('.download-panel');
    if (downloadPanel) {
        downloadPanel.style.opacity = '0';
        downloadPanel.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            downloadPanel.style.transition = 'all 0.6s ease';
            downloadPanel.style.opacity = '1';
            downloadPanel.style.transform = 'translateY(0)';
        }, 600);
    }
}

// Additional actions
function setupAdditionalActions() {
    const processAgainBtn = document.querySelector('.process-again-btn');
    const newPhotoBtn = document.querySelector('.new-photo-btn');
    
    if (processAgainBtn) {
        processAgainBtn.addEventListener('click', function() {
            // Go back to preview page with same image
            const originalFilename = getOriginalFilename();
            if (originalFilename) {
                window.location.href = `/preview/${originalFilename}`;
            } else {
                window.location.href = '/';
            }
        });
    }
    
    if (newPhotoBtn) {
        newPhotoBtn.addEventListener('click', function() {
            window.location.href = '/';
        });
    }
}

function getOriginalFilename() {
    // Try to extract original filename from result filename
    // This would depend on your naming convention
    const filename = resultState.filename;
    if (!filename) return null;
    
    // Remove processing suffixes
    return filename.replace(/_processed|_bg_removed|_bg_changed|_resized|_enhanced/g, '');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (!document.querySelector('.result-page')) return;
    
    // Only process if not in an input field or textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.contentEditable === 'true') return;
    
    // Check if user has text selected for copy operations
    const selection = window.getSelection();
    const selectedText = selection ? selection.toString().trim() : '';
    
    switch(e.key.toLowerCase()) {
        case 'd':
            // Don't interfere if user is trying to copy selected text with Ctrl+C/D combinations
            if (!e.ctrlKey && !e.altKey && !e.metaKey && selectedText.length === 0) {
                e.preventDefault();
                document.querySelector('.download-btn-main')?.click();
            }
            break;
        case 's':
            // Don't interfere if user is trying to copy selected text
            if (!e.ctrlKey && !e.altKey && !e.metaKey && selectedText.length === 0) {
                e.preventDefault();
                document.querySelector('.share-btn')?.click();
            }
            break;
        case 'c':
            // Only trigger comparison if it's Shift+C (to avoid conflict with Ctrl+C copy)
            if (e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey && selectedText.length === 0) {
                e.preventDefault();
                document.querySelector('.comparison-toggle')?.click();
            }
            // Don't interfere with normal Ctrl+C copy functionality - let it work naturally
            break;
    }
});

// Initialize additional actions when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.result-page')) {
        setupAdditionalActions();
    }
});

// Utility Functions
function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    } catch (error) {
        console.warn('Invalid date format:', dateString);
        return 'Unknown';
    }
}

async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            // Use modern clipboard API
            await navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            textArea.style.pointerEvents = 'none';
            document.body.appendChild(textArea);
            textArea.select();
            textArea.setSelectionRange(0, 99999);
            
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            
            if (!successful) {
                throw new Error('Failed to copy using fallback method');
            }
        }
    } catch (error) {
        console.error('Copy to clipboard failed:', error);
        throw new Error('Unable to copy to clipboard');
    }
}

function showDownloadProgress() {
    const progressElement = document.querySelector('.download-progress');
    if (progressElement) {
        progressElement.classList.add('active');
        
        // Simulate progress for better UX
        const progressBar = progressElement.querySelector('.progress-bar-fill');
        const progressText = progressElement.querySelector('.progress-text');
        
        if (progressBar && progressText) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 90) progress = 90;
                
                progressBar.style.width = progress + '%';
                progressText.textContent = `Preparing download... ${Math.round(progress)}%`;
                
                if (progress >= 90) {
                    clearInterval(interval);
                }
            }, 200);
            
            progressElement.dataset.intervalId = interval;
        }
    }
}

function hideDownloadProgress() {
    const progressElement = document.querySelector('.download-progress');
    if (progressElement) {
        // Clear any running intervals
        const intervalId = progressElement.dataset.intervalId;
        if (intervalId) {
            clearInterval(parseInt(intervalId));
            delete progressElement.dataset.intervalId;
        }
        
        // Complete the progress bar
        const progressBar = progressElement.querySelector('.progress-bar-fill');
        const progressText = progressElement.querySelector('.progress-text');
        
        if (progressBar && progressText) {
            progressBar.style.width = '100%';
            progressText.textContent = 'Download complete!';
            
            setTimeout(() => {
                progressElement.classList.remove('active');
                progressBar.style.width = '0%';
                progressText.textContent = '';
            }, 1000);
        } else {
            progressElement.classList.remove('active');
        }
    }
}

// Enhanced showToast function with better error handling
function showToast(message, type = 'info', duration = 5000) {
    // Remove existing toasts of the same type
    const existingToasts = document.querySelectorAll(`.toast.${type}`);
    existingToasts.forEach(toast => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
    
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="${icon}" aria-hidden="true"></i>
        <span>${escapeHtml(message)}</span>
        <button class="toast-close" onclick="closeToast(this)" aria-label="Close notification">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    // Auto-remove after duration
    const timeoutId = setTimeout(() => {
        if (toast.parentNode) {
            closeToast(toast.querySelector('.toast-close'));
        }
    }, duration);
    
    // Store timeout ID for potential cleanup
    toast.dataset.timeoutId = timeoutId;
    
    // Add click to close
    toast.addEventListener('click', function(e) {
        if (e.target !== toast.querySelector('.toast-close')) {
            closeToast(toast.querySelector('.toast-close'));
        }
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 350px;
    `;
    document.body.appendChild(container);
    return container;
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
    if (!closeBtn) return;
    
    const toast = closeBtn.parentElement;
    if (!toast) return;
    
    // Clear timeout if exists
    const timeoutId = toast.dataset.timeoutId;
    if (timeoutId) {
        clearTimeout(parseInt(timeoutId));
    }
    
    toast.classList.remove('show');
    toast.style.animation = 'slideOut 0.3s ease-in forwards';
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred. Please refresh the page and try again.', 'error');
});

// Initialize error handling for general errors
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    // Only show toast for critical errors, not every minor issue
    if (event.error && event.error.stack && event.error.stack.includes('result.js')) {
        showToast('A page error occurred. Some features may not work correctly.', 'warning');
    }
});

// Export for global access
window.resultState = resultState;
window.showToast = showToast;
window.closeToast = closeToast;
