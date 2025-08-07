/* PixPort Result Page JavaScript */

// Result page state
let resultState = {
    filename: null,
    downloadCount: 0,
    shareCount: 0,
    comparisonMode: false,
    imageMetadata: null
};

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
            
            try {
                await downloadImage(format, quality);
                resultState.downloadCount++;
                updateDownloadCount();
                
                // Show success feedback
                showToast(`Image downloaded as ${format.toUpperCase()}!`, 'success');
                
            } catch (error) {
                showToast(`Download failed: ${error.message}`, 'error');
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
        <i class="fas fa-download"></i>
        Download ${formatText}${qualityText}
    `;
}

async function downloadImage(format = 'JPEG', quality = '95') {
    if (!resultState.filename) throw new Error('No image available');
    
    const params = new URLSearchParams({
        format: format,
        quality: quality
    });
    
    const response = await fetch(`/api/download/${resultState.filename}?${params}`);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Download failed');
    }
    
    // Get filename from response headers or generate one
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `passport_photo.${format.toLowerCase()}`;
    
    if (contentDisposition) {
        const matches = contentDisposition.match(/filename="?(.+)"?/);
        if (matches) filename = matches[1];
    }
    
    // Create download link
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    window.URL.revokeObjectURL(url);
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
            this.innerHTML = '<i class="fas fa-eye-slash"></i> Hide Comparison';
            loadComparisonImages();
        } else {
            container.classList.remove('active');
            this.innerHTML = '<i class="fas fa-eye"></i> Show Comparison';
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
            originalImg.src = `/uploads/${data.original_filename}`;
            processedImg.src = `/processed/${resultState.filename}`;
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
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'PixPort - AI Passport Photo',
                        text: 'Check out my passport photo created with PixPort AI!',
                        url: window.location.href
                    });
                    resultState.shareCount++;
                } catch (error) {
                    console.log('Share cancelled or failed');
                }
            } else {
                // Fallback: copy to clipboard
                copyToClipboard(window.location.href);
                showToast('Link copied to clipboard!', 'success');
            }
        });
    }
    
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', function() {
            copyToClipboard(window.location.href);
            showToast('Link copied to clipboard!', 'success');
        });
    }
}

async function loadImageMetadata() {
    if (!resultState.filename) return;
    
    try {
        const response = await fetch(`/api/image-info/${resultState.filename}`);
        const data = await response.json();
        
        if (data.success) {
            resultState.imageMetadata = data;
            updateImageStats();
        }
    } catch (error) {
        console.error('Failed to load image metadata:', error);
    }
}

function updateImageStats() {
    const statsContainer = document.querySelector('.image-stats');
    if (!statsContainer || !resultState.imageMetadata) return;
    
    const info = resultState.imageMetadata;
    
    statsContainer.innerHTML = `
        <div class="stat-item">
            <span class="stat-label">Format</span>
            <span class="stat-value">${info.format || 'JPEG'}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Dimensions</span>
            <span class="stat-value">${info.width || 0} × ${info.height || 0}px</span>
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
            <span class="stat-label">Processing Time</span>
            <span class="stat-value">${info.processing_time || '0.0'}s</span>
        </div>
    `;
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
    
    switch(e.key) {
        case 'd':
        case 'D':
            e.preventDefault();
            document.querySelector('.download-btn-main')?.click();
            break;
        case 's':
        case 'S':
            e.preventDefault();
            document.querySelector('.share-btn')?.click();
            break;
        case 'c':
        case 'C':
            e.preventDefault();
            document.querySelector('.comparison-toggle')?.click();
            break;
    }
});

// Initialize additional actions when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.result-page')) {
        setupAdditionalActions();
    }
});

// Export for global access
window.resultState = resultState;
