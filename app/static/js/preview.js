/* =============================================
   PIXPORT PREVIEW PAGE - FRESH JAVASCRIPT
   ============================================= */

/* PixPort Preview - Error Handler and Fallback Functions */

// Ensure showToast function is available
if (typeof showToast === 'undefined') {
    window.showToast = function(message, type = 'info', duration = 3000) {
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Remove existing notifications to prevent stacking
        const existingNotifications = document.querySelectorAll('.toast-notification');
        existingNotifications.forEach(notification => {
            notification.remove();
        });
        
        // Simple notification fallback
        const notification = document.createElement('div');
        notification.className = 'toast-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10001;
            font-size: 14px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInFromRight 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Add animation styles if not present
        if (!document.querySelector('#toast-animations')) {
            const style = document.createElement('style');
            style.id = 'toast-animations';
            style.textContent = `
                @keyframes slideInFromRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutToRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutToRight 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    };
}

// Ensure face alignment functions are available
if (typeof autoAlignFace === 'undefined') {
    window.autoAlignFace = function(imageElement) {
        console.log('Auto align face called on:', imageElement);
        showToast('Face alignment feature is loading...', 'info');
    };
}

if (typeof startFaceAlignment === 'undefined') {
    window.startFaceAlignment = function(imageElement) {
        console.log('Start face alignment called on:', imageElement);
        showToast('Manual face alignment feature is loading...', 'info');
    };
}

// Global state management
const previewState = {
    currentImage: null,
    originalImage: null,
    zoom: 1,
    rotation: 0,
    selectedColors: [],
    customColor: '#ffffff',
    isProcessing: false,
    sliderValues: {
        brightness: 0,
        contrast: 0,
        saturation: 0,
        sharpness: 0,
        vibrance: 0,
        warmth: 0,
        shadows: 0,
        highlights: 0
    }
};

// Configuration
const CONFIG = {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedFormats: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
};

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

// Get current filename from URL
function getCurrentFilename() {
    const pathArray = window.location.pathname.split('/');
    return pathArray[pathArray.length - 1];
}

// Extract original filename by removing all processing suffixes
function getOriginalFilename(processedFilename) {
    if (!processedFilename) return 'Unknown';
    
    let originalName = processedFilename;
    
    // Remove common processing suffixes
    const suffixes = [
        /_bg_hex_[a-fA-F0-9]+/g,    // hex colors like _bg_hex_ffffff
        /_bg_(white|light_blue|light_gray|red|cream)/g,  // preset colors
        /_enhanced/g,
        /_passport_[a-z]+/g,
        /_passport_photo/g,
        /_resized/g,
        /_no_bg/g,
        /_temp_[a-zA-Z0-9_]+/g
    ];
    
    suffixes.forEach(suffix => {
        originalName = originalName.replace(suffix, '');
    });
    
    // Extract only the user-friendly part (remove UUID prefix)
    // Format: uuid_originalname.ext -> originalname.ext
    const parts = originalName.split('_');
    if (parts.length >= 2) {
        // Remove UUID part (first part) and join the rest
        const nameWithoutUuid = parts.slice(1).join('_');
        if (nameWithoutUuid) {
            originalName = nameWithoutUuid;
        }
    }
    
    return originalName;
}

// Generate user-friendly current filename for display
function generateFriendlyCurrentName(processedFilename) {
    if (!processedFilename) return 'Unknown';
    
    // Get the original name first
    const originalName = getOriginalFilename(processedFilename);
    const baseNameWithoutExt = originalName.replace(/\.[^/.]+$/, ''); // Remove extension
    const extension = originalName.match(/\.[^/.]+$/) ? originalName.match(/\.[^/.]+$/)[0] : '.jpg';
    
    // Determine processing type and version
    let processType = '';
    let version = 1;
    
    // Check what type of processing was applied
    if (processedFilename.includes('_bg_')) {
        if (processedFilename.includes('_bg_white')) {
            processType = 'white_bg';
        } else if (processedFilename.includes('_bg_light_blue')) {
            processType = 'blue_bg';
        } else if (processedFilename.includes('_bg_light_gray')) {
            processType = 'gray_bg';
        } else if (processedFilename.includes('_bg_red')) {
            processType = 'red_bg';
        } else if (processedFilename.includes('_bg_cream')) {
            processType = 'cream_bg';
        } else if (processedFilename.includes('_bg_hex_')) {
            processType = 'custom_bg';
        }
    } else if (processedFilename.includes('_no_bg')) {
        processType = 'no_bg';
    } else if (processedFilename.includes('_enhanced')) {
        processType = 'enhanced';
    } else if (processedFilename.includes('_passport')) {
        processType = 'passport';
    } else if (processedFilename.includes('_resized')) {
        processType = 'resized';
    } else {
        // For original uploaded files (no processing detected)
        // Check if filename contains UUID pattern (indicates it's an uploaded file)
        if (isUuidBasedFilename(processedFilename)) {
            processType = 'pixport';
        } else {
            // If no UUID detected, just return the original name as-is
            return originalName;
        }
    }
    
    // Generate a simple incremental version number for cleaner names
    // Use a hash of the filename for consistent versioning
    version = Math.abs(hashCode(processedFilename)) % 99 + 1;
    
    // Create friendly name: originalname_processtype_version.ext
    return `${baseNameWithoutExt}_${processType}_${version}${extension}`;
}

// Check if filename follows UUID pattern (indicates uploaded file)
function isUuidBasedFilename(filename) {
    // UUID pattern: 8-4-4-4-12 characters separated by hyphens
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_/i;
    return uuidPattern.test(filename);
}

// Simple hash function for consistent version numbers
function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

// Get clean display name (remove file extension for display)
function getDisplayName(filename) {
    if (!filename) return 'Unknown';
    const lastDotIndex = filename.lastIndexOf('.');
    return lastDotIndex > 0 ? filename.substring(0, lastDotIndex) : filename;
}

/* ============================================
   INITIALIZATION
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('PixPort Preview: Initializing...');
        initializePreviewPage();
    } catch (error) {
        console.error('Initialization error:', error);
        showErrorMessage('Failed to initialize preview page');
    }
});

function initializePreviewPage() {
    // Initialize all components
    initializeImageHandling();
    initializeColorSelection();
    initializeSliders();
    initializeControls();
    initializeFormHandling();
    
    // Load existing image if available
    loadExistingImage();
    
    console.log('PixPort Preview: Initialization complete');
}

/* ============================================
   IMAGE HANDLING
   ============================================ */

function initializeImageHandling() {
    const imageContainer = document.querySelector('.image-container');
    const previewImage = document.querySelector('.preview-image');
    
    if (!imageContainer || !previewImage) return;
    
    // Add drag and drop functionality
    setupImageDragAndDrop(imageContainer);
    
    // Add zoom and pan functionality
    setupImageZoomAndPan(previewImage);
    
    // Add image controls event listeners
    setupImageControls();
}

function setupImageDragAndDrop(container) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        container.addEventListener(eventName, () => {
            container.classList.add('drag-over');
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, () => {
            container.classList.remove('drag-over');
        });
    });
    
    container.addEventListener('drop', handleImageDrop);
}

function handleImageDrop(e) {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleImageFile(files[0]);
    }
}

function setupImageZoomAndPan(image) {
    let isDragging = false;
    let startX, startY, currentX = 0, currentY = 0;
    
    image.addEventListener('mousedown', (e) => {
        if (previewState.zoom > 1) {
            isDragging = true;
            startX = e.clientX - currentX;
            startY = e.clientY - currentY;
            image.style.cursor = 'grabbing';
        }
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        currentX = e.clientX - startX;
        currentY = e.clientY - startY;
        
        image.style.transform = `translate(${currentX}px, ${currentY}px) scale(${previewState.zoom}) rotate(${previewState.rotation}deg)`;
    });
    
    document.addEventListener('mouseup', () => {
        isDragging = false;
        image.style.cursor = previewState.zoom > 1 ? 'grabbing' : 'default';
    });
    
    // Zoom with mouse wheel
    image.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        updateZoom(previewState.zoom + delta);
    });
}

function setupImageControls() {
    // Zoom controls
    const zoomInBtn = document.querySelector('[data-action="zoom-in"]');
    const zoomOutBtn = document.querySelector('[data-action="zoom-out"]');
    const zoomResetBtn = document.querySelector('[data-action="zoom-reset"]');
    const zoomFitBtn = document.querySelector('[data-action="zoom-fit"]');
    
    if (zoomInBtn) zoomInBtn.addEventListener('click', () => updateZoom(previewState.zoom + 0.25));
    if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => updateZoom(previewState.zoom - 0.25));
    if (zoomResetBtn) zoomResetBtn.addEventListener('click', () => updateZoom(1));
    if (zoomFitBtn) zoomFitBtn.addEventListener('click', fitImageToContainer);
    
    // Handle zoom-reset action for the Reset View button
    const resetViewBtn = document.querySelector('[data-action="zoom-reset"]');
    if (resetViewBtn) resetViewBtn.addEventListener('click', () => {
        updateZoom(1);
        resetImagePosition();
    });
    
    // Alignment controls
    const alignButtons = document.querySelectorAll('[data-align]');
    alignButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const alignment = btn.getAttribute('data-align');
            alignImage(alignment);
        });
    });
}

function updateZoom(newZoom) {
    const minZoom = 0.25;
    const maxZoom = 3;
    
    previewState.zoom = Math.max(minZoom, Math.min(maxZoom, newZoom));
    
    const image = document.querySelector('.preview-image');
    if (image) {
        image.style.transform = `scale(${previewState.zoom}) rotate(${previewState.rotation}deg)`;
        image.style.cursor = previewState.zoom > 1 ? 'grab' : 'default';
    }
    
    // Update zoom display
    const zoomDisplay = document.querySelector('.zoom-level');
    if (zoomDisplay) {
        zoomDisplay.textContent = `${Math.round(previewState.zoom * 100)}%`;
    }
    
    // Update control buttons
    updateZoomControls();
}

function updateZoomControls() {
    const zoomInBtn = document.querySelector('[data-action="zoom-in"]');
    const zoomOutBtn = document.querySelector('[data-action="zoom-out"]');
    
    if (zoomInBtn) {
        zoomInBtn.disabled = previewState.zoom >= 3;
    }
    
    if (zoomOutBtn) {
        zoomOutBtn.disabled = previewState.zoom <= 0.25;
    }
}

function fitImageToContainer() {
    const container = document.querySelector('.image-container');
    const image = document.querySelector('.preview-image');
    
    if (!container || !image) return;
    
    const containerRect = container.getBoundingClientRect();
    const imageRect = image.getBoundingClientRect();
    
    const scaleX = containerRect.width / imageRect.width;
    const scaleY = containerRect.height / imageRect.height;
    const scale = Math.min(scaleX, scaleY) * 0.9; // 90% of container
    
    updateZoom(scale);
}

function alignImage(alignment) {
    const container = document.querySelector('.image-container');
    if (!container) return;
    
    const alignmentClasses = {
        'left': 'justify-start',
        'center': 'justify-center',
        'right': 'justify-end',
        'top': 'items-start',
        'middle': 'items-center',
        'bottom': 'items-end'
    };
    
    // Remove all alignment classes
    Object.values(alignmentClasses).forEach(cls => {
        container.classList.remove(cls);
    });
    
    // Add new alignment class
    if (alignmentClasses[alignment]) {
        container.classList.add(alignmentClasses[alignment]);
    }
}

// Reset image position and zoom
function resetImagePosition() {
    const image = document.querySelector('.preview-image');
    if (image) {
        // Reset transform to default
        image.style.transform = 'scale(1) rotate(0deg)';
        image.style.cursor = 'default';
    }
    
    // Reset state values
    previewState.zoom = 1;
    previewState.rotation = 0;
    
    // Update zoom display if it exists
    const zoomDisplay = document.querySelector('.zoom-level');
    if (zoomDisplay) {
        zoomDisplay.textContent = '100%';
    }
    
    // Update control buttons
    updateZoomControls();
    
    showSuccessMessage('View reset to default');
}

function loadExistingImage() {
    const previewImage = document.querySelector('.preview-image');
    if (previewImage && previewImage.src && previewImage.src !== window.location.href) {
        console.log('🖼️ Loading existing image:', previewImage.src);
        previewState.currentImage = previewImage.src;
        
        // Try to determine if this is the original image or processed
        const src = previewImage.src;
        let originalSrc = src;
        
        // If this looks like a processed image, try to find the original
        if (src.includes('/static/processed/')) {
            // Extract filename and clean it from processing suffixes
            let filename = src.split('/').pop();
            console.log('🔍 Original processed filename:', filename);
            
            // Strip all processing suffixes to get the original filename
            const suffixesToRemove = [
                /_bg_hex_[a-fA-F0-9]+/g,           // hex colors like _bg_hex_ffffff
                /_bg_(white|light_blue|light_gray|red|cream|blue|gray)/g,  // preset colors
                /_enhanced/g,
                /_passport_[a-z]+/g,
                /_passport_photo/g,
                /_resized/g,
                /_no_bg/g,
                /_temp_[a-zA-Z0-9_]+/g,
                /_\d+x\d+/g                        // dimensions like _600x600
            ];
            
            // Apply all suffix removals
            suffixesToRemove.forEach(suffix => {
                filename = filename.replace(suffix, '');
            });
            
            console.log('🔍 Cleaned original filename:', filename);
            originalSrc = `/static/uploads/${filename}`;
            console.log('🔍 Detected processed image, original should be:', originalSrc);
        }
        
        // Store both current and original references
        previewState.originalImage = originalSrc;
        previewImage.setAttribute('data-original-src', originalSrc);
        
        console.log('✅ Image state initialized:', {
            current: previewState.currentImage,
            original: previewState.originalImage
        });
        
        updateImageInfo();
    }
}

/* ============================================
   COLOR SELECTION
   ============================================ */

function initializeColorSelection() {
    // Preset color circles
    const colorCircles = document.querySelectorAll('.color-circle');
    colorCircles.forEach(circle => {
        circle.addEventListener('click', handleColorSelection);
    });
    
    // Custom color inputs
    const hexInput = document.querySelector('.hex-input');
    const colorPicker = document.querySelector('.color-picker');
    
    if (hexInput) {
        hexInput.addEventListener('input', handleCustomColorInput);
        hexInput.addEventListener('blur', (e) => {
            // Only validate if the input actually had content and user was interacting with it
            if (e.target === document.activeElement || e.relatedTarget) {
                validateHexColor(e);
            }
        });
    }
    
    if (colorPicker) {
        colorPicker.addEventListener('change', handleColorPickerChange);
    }
    
    // Colors are now hardcoded in the HTML template
}


function handleColorSelection(e) {
    const color = e.target.getAttribute('data-color');
    if (!color) return;
    
    // Remove selection from all color circles
    document.querySelectorAll('.color-circle').forEach(circle => {
        circle.classList.remove('selected');
    });
    
    // Add selection to clicked circle
    e.target.classList.add('selected');
    
    // Update state
    previewState.selectedColors = [color];
    previewState.customColor = color;
    
    // Update custom color input
    const hexInput = document.querySelector('.hex-input');
    if (hexInput) {
        hexInput.value = color;
    }
    
    const colorPicker = document.querySelector('.color-picker');
    if (colorPicker) {
        colorPicker.value = color;
    }
}

function handleCustomColorInput(e) {
    let value = e.target.value.trim();
    
    // Add # if missing
    if (value && !value.startsWith('#')) {
        value = '#' + value;
        e.target.value = value;
    }
    
    if (isValidHexColor(value)) {
        previewState.customColor = value;
        
        const colorPicker = document.querySelector('.color-picker');
        if (colorPicker) {
            colorPicker.value = value;
        }
        
        // Clear preset selections
        document.querySelectorAll('.color-circle').forEach(circle => {
            circle.classList.remove('selected');
        });
    }
}

function handleColorPickerChange(e) {
    const color = e.target.value;
    previewState.customColor = color;
    
    const hexInput = document.querySelector('.hex-input');
    if (hexInput) {
        hexInput.value = color;
    }
    
    // Clear preset selections
    document.querySelectorAll('.color-circle').forEach(circle => {
        circle.classList.remove('selected');
    });
}

function validateHexColor(e) {
    const value = e.target.value.trim();
    // Only validate if there's actually content and it's not valid
    // Don't validate empty values or placeholder values
    if (value && value !== '#ffffff' && value !== '' && !isValidHexColor(value)) {
        showErrorMessage('Please enter a valid hex color (e.g., #FF0000)');
        e.target.focus();
    }
}

function isValidHexColor(hex) {
    return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex);
}

/* ============================================
   ENHANCEMENT SLIDERS
   ============================================ */

function initializeSliders() {
    const sliders = document.querySelectorAll('.enhancement-slider');
    
    sliders.forEach(slider => {
        const sliderType = slider.getAttribute('data-slider');
        if (sliderType && previewState.sliderValues.hasOwnProperty(sliderType)) {
            slider.value = previewState.sliderValues[sliderType];
            updateSliderValue(slider, sliderType);
        }
        
        slider.addEventListener('input', (e) => {
            const type = e.target.getAttribute('data-slider');
            if (type) {
                previewState.sliderValues[type] = parseInt(e.target.value);
                updateSliderValue(e.target, type);
            }
        });
    });
}

function updateSliderValue(slider, type) {
    const value = parseInt(slider.value);
    const valueDisplay = slider.parentElement.querySelector('.slider-value');
    
    if (valueDisplay) {
        const sign = value > 0 ? '+' : '';
        valueDisplay.textContent = `${sign}${value}`;
    }
    
    // Update slider track color based on value
    const percentage = ((value + 100) / 200) * 100;
    slider.style.background = `linear-gradient(to top, #3b82f6 0%, #3b82f6 ${percentage}%, #e5e7eb ${percentage}%, #e5e7eb 100%)`;
}

/* ============================================
   BUTTON CONTROLS
   ============================================ */

function initializeControls() {
    // Background removal
    const removeBgBtn = document.querySelector('.remove-bg-btn');
    if (removeBgBtn) {
        removeBgBtn.addEventListener('click', handleRemoveBackground);
    }
    
    // Background change
    const changeBgBtn = document.querySelector('.change-bg-btn');
    if (changeBgBtn) {
        changeBgBtn.addEventListener('click', handleChangeBackground);
    }
    
    // Resize application
    const applyResizeBtn = document.querySelector('.apply-resize-btn');
    if (applyResizeBtn) {
        applyResizeBtn.addEventListener('click', handleApplyResize);
    }
    
    // Face alignment
    const autoAlignBtn = document.querySelector('.auto-align-btn');
    if (autoAlignBtn) {
        autoAlignBtn.addEventListener('click', handleAutoAlign);
    }
    
    // Detect positioning
    const detectPositioningBtn = document.querySelector('.detect-positioning-btn');
    if (detectPositioningBtn) {
        detectPositioningBtn.addEventListener('click', handleDetectPositioning);
    }
    
    // Enhancement
    const enhanceBtn = document.querySelector('.enhance-btn');
    if (enhanceBtn) {
        enhanceBtn.addEventListener('click', handleEnhancement);
    }
    
    // Head size controls
    const sizeBtns = document.querySelectorAll('.size-btn');
    sizeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const fit = e.target.getAttribute('data-fit');
            handleHeadSizeAdjustment(fit);
        });
    });
    
    // Tilt controls
    const tiltApplyBtn = document.querySelector('.tilt-apply-btn');
    if (tiltApplyBtn) {
        tiltApplyBtn.addEventListener('click', handleTiltAdjustment);
    }
    
    // Quick action buttons
    const passportBtn = document.querySelector('.quick-btn.passport');
    const professionalBtn = document.querySelector('.quick-btn.professional');
    
    if (passportBtn) {
        passportBtn.addEventListener('click', () => handleQuickAction('passport'));
    }
    
    if (professionalBtn) {
        professionalBtn.addEventListener('click', () => handleQuickAction('professional'));
    }
    
    // Bottom action buttons (Upload New, Reset All, Go Download Professional)
    console.log('🔍 Searching for bottom action buttons...');
    
    // Multiple selectors for Reset All button to ensure we find it
    const resetAllSelectors = [
        '.reset-all-btn',
        'button.reset-all-btn',
        '.action-btn.secondary:nth-child(2)', // Second button in the grid
        'button[class*="reset-all"]',
        'button:contains("Reset All")',
        '.bottom-actions button:nth-of-type(2)',
        '.action-buttons-grid button:nth-child(2)'
    ];
    
    let resetAllBtn = null;
    let uploadNewBtn = null;
    let downloadProfessionalBtn = null;
    
    // Try each selector until we find the reset button
    for (const selector of resetAllSelectors) {
        try {
            if (selector.includes('contains')) {
                // Handle text-based selection manually
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    if (btn.textContent && btn.textContent.trim().includes('Reset All')) {
                        resetAllBtn = btn;
                        console.log(`✅ Found Reset All button using text content: "${btn.textContent.trim()}"`); 
                        break;
                    }
                }
            } else {
                resetAllBtn = document.querySelector(selector);
            }
            if (resetAllBtn) {
                console.log(`✅ Found Reset All button using selector: ${selector}`);
                break;
            }
        } catch (e) {
            console.log(`❌ Selector failed: ${selector} - ${e.message}`);
        }
    }
    
    // Find other buttons
    uploadNewBtn = document.querySelector('.upload-new-btn') || 
                  document.querySelector('button[class*="upload-new"]') ||
                  document.querySelector('.action-buttons-grid button:first-child');
                  
    downloadProfessionalBtn = document.querySelector('.download-professional-btn') || 
                             document.querySelector('button[class*="download-professional"]') ||
                             document.querySelector('.action-buttons-grid button:last-child');
    
    console.log('🔍 Debug: Bottom action buttons found:', {
        uploadNewBtn: !!uploadNewBtn,
        resetAllBtn: !!resetAllBtn,
        downloadProfessionalBtn: !!downloadProfessionalBtn
    });
    
    // Add event listeners
    if (uploadNewBtn) {
        uploadNewBtn.addEventListener('click', handleUploadNewPhoto);
        console.log('✅ Upload New button event listener added');
    } else {
        console.error('❌ Upload New button not found');
    }
    
    if (resetAllBtn) {
        resetAllBtn.addEventListener('click', handleResetAll);
        console.log('✅ Reset All button event listener added to:', resetAllBtn);
        
        // Add additional debugging - log what happens when button is clicked
        resetAllBtn.addEventListener('click', function(event) {
            console.log('🔥 Reset All button clicked! Event:', event);
            console.log('🔥 Button element:', this);
        });
        
        // Test the button immediately
        console.log('🧪 Testing Reset All button click programmatically...');
        setTimeout(() => {
            if (resetAllBtn.click && typeof resetAllBtn.click === 'function') {
                console.log('✅ Button.click() method available');
            } else {
                console.error('❌ Button.click() method not available');
            }
        }, 1000);
        
    } else {
        console.error('❌ Reset All button not found with any selector!');
        
        // Last resort: find all buttons and list them
        const allButtons = document.querySelectorAll('button');
        console.log('🔍 All buttons found on page:');
        allButtons.forEach((btn, index) => {
            console.log(`  Button ${index + 1}: Classes="${btn.className}", Text="${btn.textContent?.trim()}", ID="${btn.id}"`);
        });
        
        // Try to find by text content as final fallback
        const resetBtnByText = Array.from(allButtons).find(btn => 
            btn.textContent && btn.textContent.toLowerCase().includes('reset')
        );
        
        if (resetBtnByText) {
            console.log('🎯 Found reset button by text content:', resetBtnByText);
            resetBtnByText.addEventListener('click', handleResetAll);
            console.log('✅ Event listener added to reset button found by text');
        }
    }
    
    if (downloadProfessionalBtn) {
        downloadProfessionalBtn.addEventListener('click', handleGoDownloadProfessional);
        console.log('✅ Download Professional button event listener added');
    } else {
        console.error('❌ Download Professional button not found');
    }
    
    // Legacy action buttons - REMOVED to prevent conflicts with new handlers
    // The .action-btn.primary and .action-btn.secondary classes are now handled by:
    // - .upload-new-btn -> handleUploadNewPhoto()
    // - .reset-all-btn -> handleResetAll() 
    // - .download-professional-btn -> handleGoDownloadProfessional()
}

/* ============================================
   ACTION HANDLERS
   ============================================ */

async function handleRemoveBackground() {
    try {
        showLoadingOverlay('Removing background...');
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        const response = await fetch(`/process/remove_background/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage('Background removed successfully!');
            // Update the preview image with the processed result
            if (result.output_filename) {
                const newImageUrl = `/static/processed/${result.output_filename}`;
                updatePreviewImage(newImageUrl);
                previewState.currentImage = newImageUrl;
                // Update the URL to reflect the new file
                window.history.pushState({}, '', `/preview/${result.output_filename}`);
            }
        } else {
            throw new Error(result.error || 'Failed to remove background');
        }
        
    } catch (error) {
        console.error('Background removal error:', error);
        showErrorMessage('Failed to remove background: ' + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

async function handleChangeBackground() {
    console.log('🎨 Background change clicked!');
    
    // Get selected color from various sources
    let selectedColor = null;
    
    // Check for selected preset color
    const selectedCircle = document.querySelector('.color-circle.selected');
    console.log('Selected circle:', selectedCircle);
    if (selectedCircle) {
        selectedColor = selectedCircle.getAttribute('data-color');
        console.log('Color from selected circle:', selectedColor);
    }
    
    // Check for custom color input
    if (!selectedColor) {
        const hexInput = document.querySelector('.hex-input');
        console.log('Hex input:', hexInput?.value);
        if (hexInput && hexInput.value.trim()) {
            selectedColor = hexInput.value.trim();
            console.log('Color from hex input:', selectedColor);
        }
    }
    
    // Check for color picker value
    if (!selectedColor) {
        const colorPicker = document.querySelector('.color-picker');
        console.log('Color picker value:', colorPicker?.value);
        if (colorPicker && colorPicker.value !== '#ffffff') {
            selectedColor = colorPicker.value;
            console.log('Color from color picker:', selectedColor);
        }
    }
    
    // Fallback to state values
    if (!selectedColor) {
        selectedColor = previewState.customColor || previewState.selectedColors[0];
        console.log('Color from state:', selectedColor);
    }
    
    // Ensure we have a valid color - use white as default
    if (!selectedColor) {
        selectedColor = '#ffffff';
        console.log('Using default white color');
    }
    
    console.log('Final selected color for background change:', selectedColor);
    
    // Show user notification about the color being used
    showInfoMessage(`Changing background to ${selectedColor}...`);
    
    try {
        showLoadingOverlay('Changing background...');
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        const response = await fetch(`/process/change_background/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ color: selectedColor })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(`Background changed to ${selectedColor}!`);
            // Update the preview image with the processed result
            if (result.output_filename) {
                // Force a complete page refresh to ensure the new image loads
                setTimeout(() => {
                    window.location.href = `/preview/${result.output_filename}`;
                }, 1000);
            }
        } else {
            throw new Error(result.error || 'Failed to change background');
        }
        
    } catch (error) {
        console.error('Background change error:', error);
        showErrorMessage('Failed to change background: ' + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

async function handleApplyResize() {
    const widthInput = document.querySelector('#resize-width');
    const heightInput = document.querySelector('#resize-height');
    
    if (!widthInput || !heightInput) {
        showErrorMessage('Resize controls not found');
        return;
    }
    
    const width = parseInt(widthInput.value);
    const height = parseInt(heightInput.value);
    
    if (!width || !height || width <= 0 || height <= 0) {
        showErrorMessage('Please enter valid dimensions');
        return;
    }
    
    try {
        showLoadingOverlay('Resizing image...');
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        const response = await fetch(`/process/resize/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                country: 'US', // Default for now
                width: width,
                height: height
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(`Image resized to ${width}x${height}!`);
            // Update the preview image with the processed result
            if (result.output_filename) {
                const newImageUrl = `/static/processed/${result.output_filename}`;
                updatePreviewImage(newImageUrl);
                previewState.currentImage = newImageUrl;
                // Update the URL to reflect the new file
                window.history.pushState({}, '', `/preview/${result.output_filename}`);
            }
        } else {
            throw new Error(result.error || 'Failed to resize image');
        }
        
    } catch (error) {
        console.error('Resize error:', error);
        showErrorMessage('Failed to resize image: ' + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

async function handleAutoAlign() {
    if (!previewState.currentImage) {
        showErrorMessage('Please select an image first');
        return;
    }
    
    // Auto-align face feature is not yet implemented in the backend
    showInfoMessage('Auto-align face feature is coming soon!');
    console.log('Auto-align face feature requested but not yet implemented');
}

async function handleDetectPositioning() {
    // Show passport photo guidelines popup
    showPassportGuidelines();
}

async function handleEnhancement() {
    // Check if any slider values have been changed from default (0)
    const hasChanges = Object.values(previewState.sliderValues).some(value => value !== 0);
    
    if (!hasChanges) {
        showWarningMessage('Please adjust at least one enhancement slider before applying changes.');
        return;
    }
    
    // Log the values being sent for debugging
    console.log('Enhancement values to apply:', previewState.sliderValues);
    
    try {
        showLoadingOverlay('Enhancing image...');
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        const response = await fetch(`/process/enhance/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(previewState.sliderValues)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage('Image enhanced successfully!');
            // Update the preview image with the processed result
            if (result.output_filename) {
                const newImageUrl = `/static/processed/${result.output_filename}`;
                updatePreviewImage(newImageUrl);
                previewState.currentImage = newImageUrl;
                // Update the URL to reflect the new file
                window.history.pushState({}, '', `/preview/${result.output_filename}`);
            }
        } else {
            throw new Error(result.error || 'Failed to enhance image');
        }
        
    } catch (error) {
        console.error('Enhancement error:', error);
        showErrorMessage('Failed to enhance image: ' + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

function handleHeadSizeAdjustment(fit) {
    if (!previewState.currentImage) {
        showErrorMessage('Please select an image first');
        return;
    }
    
    console.log('Adjusting head size:', fit);
    showInfoMessage(`Head size adjusted: ${fit}`);
}

function handleTiltAdjustment() {
    const tiltInput = document.querySelector('.tilt-input');
    if (!tiltInput) return;
    
    const degrees = parseInt(tiltInput.value) || 0;
    
    if (degrees < -360 || degrees > 360) {
        showErrorMessage('Tilt angle must be between -360 and 360 degrees');
        return;
    }
    
    previewState.rotation += degrees;
    
    const image = document.querySelector('.preview-image');
    if (image) {
        image.style.transform = `scale(${previewState.zoom}) rotate(${previewState.rotation}deg)`;
    }
    
    showSuccessMessage(`Image tilted by ${degrees} degrees`);
    tiltInput.value = '0';
}

async function handleQuickAction(type) {
    try {
        showLoadingOverlay(`Applying ${type} preset...`);
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        // Map the action types to correct endpoint names
        let endpoint = '';
        if (type === 'passport') {
            endpoint = 'quick_passport';
        } else if (type === 'professional') {
            endpoint = 'professional';
        } else {
            endpoint = type;
        }
        
        const response = await fetch(`/process/${endpoint}/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(`${type.charAt(0).toUpperCase() + type.slice(1)} preset applied!`);
            // Update the preview image with the processed result
            if (result.output_filename) {
                const newImageUrl = `/static/processed/${result.output_filename}`;
                updatePreviewImage(newImageUrl);
                previewState.currentImage = newImageUrl;
                // Update the URL to reflect the new file
                window.history.pushState({}, '', `/preview/${result.output_filename}`);
            }
        } else {
            throw new Error(result.error || `Failed to apply ${type} preset`);
        }
        
    } catch (error) {
        console.error('Quick action error:', error);
        showErrorMessage(`Failed to apply ${type} preset: ` + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

async function handleSaveImage() {
    if (!previewState.currentImage) {
        showErrorMessage('No image to save');
        return;
    }
    
    try {
        showLoadingOverlay('Saving image...');
        
        const formData = new FormData();
        formData.append('action', 'save_image');
        formData.append('image_data', previewState.currentImage);
        
        const response = await fetch('/api/save-image', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage('Image saved successfully!');
            if (result.saved_path) {
                console.log('Image saved to:', result.saved_path);
            }
        } else {
            throw new Error(result.error || 'Failed to save image');
        }
        
    } catch (error) {
        console.error('Save error:', error);
        showErrorMessage('Failed to save image: ' + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

function handleDownloadImage() {
    if (!previewState.currentImage) {
        showErrorMessage('No image to download');
        return;
    }
    
    try {
        const link = document.createElement('a');
        link.href = previewState.currentImage;
        link.download = `pixport-processed-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showSuccessMessage('Image download started!');
        
    } catch (error) {
        console.error('Download error:', error);
        showErrorMessage('Failed to download image: ' + error.message);
    }
}

/* ============================================
   MAIN ACTION BUTTON HANDLERS
   ============================================ */

// Handler for "Upload New Photo" button
function handleUploadNewPhoto() {
    console.log('Upload New Photo clicked');
    
    try {
        // Show confirmation if user has been working on an image
        if (previewState.currentImage && previewState.currentImage !== previewState.originalImage) {
            const confirmUpload = confirm('You have unsaved changes. Are you sure you want to upload a new photo? Your current work will be lost.');
            if (!confirmUpload) {
                return;
            }
        }
        
        showInfoMessage('Redirecting to upload page...');
        
        // Redirect to home page for new upload (no download activity)
        setTimeout(() => {
            window.location.href = '/';
        }, 500);
        
    } catch (error) {
        console.error('Upload new photo error:', error);
        showErrorMessage('Failed to redirect to upload page');
    }
}

// Handler for "Reset All" button  
function handleResetAll() {
    console.log('Reset All clicked');
    
    try {
        // Show confirmation dialog
        const confirmReset = confirm('This will reset all changes and return to the original image. Are you sure?');
        if (!confirmReset) {
            return;
        }
        
        showInfoMessage('Resetting all changes...');
        
        // Reset all state values
        previewState.zoom = 1;
        previewState.rotation = 0;
        previewState.selectedColors = [];
        previewState.customColor = '#ffffff';
        
        // Reset all slider values
        Object.keys(previewState.sliderValues).forEach(key => {
            previewState.sliderValues[key] = 0;
        });
        
        // Reset UI elements
        resetUIElements();
        
        // Restore the original image
        console.log('🔄 Current previewState.originalImage:', previewState.originalImage);
        console.log('🔄 Current previewState.currentImage:', previewState.currentImage);
        
        const previewImage = document.querySelector('.preview-image');
        if (!previewImage) {
            console.error('❌ Preview image element not found');
            throw new Error('Preview image element not found');
        }
        
        let originalImageUrl = null;
        
        // Try to find original image in multiple ways
        if (previewState.originalImage && previewState.originalImage.includes('/static/uploads/')) {
            // Use stored original image if available
            originalImageUrl = previewState.originalImage;
            console.log('✅ Using stored original image:', originalImageUrl);
        } else {
            // Try to construct original URL from current filename
            const currentFilename = getCurrentFilename();
            console.log('🔍 Current filename from URL:', currentFilename);
            
            if (currentFilename) {
                // Strip all processing suffixes to get the original filename
                let originalFilename = currentFilename;
                
                // Remove all processing suffixes in order
                const suffixesToRemove = [
                    /_bg_hex_[a-fA-F0-9]+/g,           // hex colors like _bg_hex_ffffff
                    /_bg_(white|light_blue|light_gray|red|cream|blue|gray)/g,  // preset colors
                    /_enhanced/g,
                    /_passport_[a-z]+/g,
                    /_passport_photo/g,
                    /_resized/g,
                    /_no_bg/g,
                    /_temp_[a-zA-Z0-9_]+/g,
                    /_\d+x\d+/g                        // dimensions like _600x600
                ];
                
                // Apply all suffix removals
                suffixesToRemove.forEach(suffix => {
                    originalFilename = originalFilename.replace(suffix, '');
                });
                
                console.log('🔍 Processed filename:', currentFilename);
                console.log('🔍 Cleaned original filename:', originalFilename);
                
                // Try different URL patterns with the cleaned filename
                const possibleUrls = [
                    `/static/uploads/${originalFilename}`,
                    `/uploads/${originalFilename}`,
                    previewImage.getAttribute('data-original-src') // Check if original src is stored as data attribute
                ];
                
                // Try to find a working URL
                for (const url of possibleUrls) {
                    if (url) {
                        originalImageUrl = url;
                        console.log('🔍 Trying original URL:', url);
                        break;
                    }
                }
            }
        }
        
        if (!originalImageUrl) {
            // Last resort: try to extract from current image src
            const currentSrc = previewImage.src;
            console.log('🔍 Current image src:', currentSrc);
            
            if (currentSrc && currentSrc.includes('/static/')) {
                // If current src looks like a processed image, try to clean it up
                let cleanUrl = currentSrc;
                
                // Remove common processing parameters and suffixes
                cleanUrl = cleanUrl.split('?')[0]; // Remove query parameters
                
                // Try to find base upload URL pattern
                if (cleanUrl.includes('/static/')) {
                    originalImageUrl = cleanUrl;
                }
            }
        }
        
        if (originalImageUrl) {
            console.log('✅ Restoring to original image:', originalImageUrl);
            
            // Store original in data attribute for future resets
            if (!previewImage.getAttribute('data-original-src')) {
                previewImage.setAttribute('data-original-src', originalImageUrl);
            }
            
            // Update state and UI
            previewState.currentImage = originalImageUrl;
            previewState.originalImage = originalImageUrl;
            
            // Reset image display
            previewImage.src = originalImageUrl;
            previewImage.style.transform = 'scale(1) rotate(0deg)';
            previewImage.style.filter = 'none'; // Reset any CSS filters
            
            console.log('✅ Image reset successfully to:', originalImageUrl);
        } else {
            console.error('❌ Could not determine original image URL for reset');
            throw new Error('Could not find original image to reset to');
        }
        
        showSuccessMessage('All changes have been reset!');
        
        // Update image info
        setTimeout(() => {
            updateImageInfo();
        }, 500);
        
    } catch (error) {
        console.error('Reset all error:', error);
        showErrorMessage('Failed to reset changes: ' + error.message);
    }
}

// Handler for "Go Download Professional" button
function handleGoDownloadProfessional() {
    console.log('Go Download Professional clicked');
    
    try {
        if (!previewState.currentImage) {
            showErrorMessage('Please process an image first before going to results page');
            return;
        }
        
        showInfoMessage('Redirecting to results page...');
        
        // Extract filename from current image URL or use current URL
        const currentFilename = getCurrentFilename();
        
        // Redirect to result page with current filename (singular "result", not "results")
        setTimeout(() => {
            window.location.href = `/result/${currentFilename}`;
        }, 500);
        
    } catch (error) {
        console.error('Go download professional error:', error);
        showErrorMessage('Failed to redirect to results page: ' + error.message);
    }
}

// Helper function to reset UI elements
function resetUIElements() {
    console.log('🔄 Resetting UI elements...');
    
    // Reset color selections
    document.querySelectorAll('.color-circle').forEach(circle => {
        circle.classList.remove('selected');
    });
    
    // Reset hex input
    const hexInput = document.querySelector('.hex-input');
    if (hexInput) {
        hexInput.value = '#ffffff';
    }
    
    // Reset color picker
    const colorPicker = document.querySelector('.color-picker');
    if (colorPicker) {
        colorPicker.value = '#ffffff';
    }
    
    // Reset resize inputs
    const widthInput = document.querySelector('#resize-width');
    const heightInput = document.querySelector('#resize-height');
    if (widthInput) widthInput.value = '';
    if (heightInput) heightInput.value = '';
    
    // Reset rotation input
    const rotateInput = document.querySelector('#rotateInput');
    if (rotateInput) {
        rotateInput.value = '0';
    }
    
    // Reset tilt input (alternative selector)
    const tiltInput = document.querySelector('.tilt-input');
    if (tiltInput) {
        tiltInput.value = '0';
    }
    
    // Reset dropdown selections to default values
    const photoSizeSelect = document.querySelector('#photoSize');
    if (photoSizeSelect) {
        photoSizeSelect.selectedIndex = 0;
        console.log('✅ Photo size dropdown reset');
    }
    
    const dpiSettingSelect = document.querySelector('#dpiSetting');
    if (dpiSettingSelect) {
        dpiSettingSelect.selectedIndex = 0;
        console.log('✅ DPI setting dropdown reset');
    }
    
    // Reset other form selects if they exist
    const outputFormatSelect = document.querySelector('#output-format');
    if (outputFormatSelect) {
        outputFormatSelect.selectedIndex = 0;
    }
    
    const outputSizeSelect = document.querySelector('#output-size');
    if (outputSizeSelect) {
        outputSizeSelect.selectedIndex = 0;
    }
    
    // Reset all enhancement sliders
    document.querySelectorAll('.enhancement-slider').forEach(slider => {
        slider.value = 0;
        const valueDisplay = slider.parentElement.querySelector('.slider-value');
        if (valueDisplay) {
            valueDisplay.textContent = '0';
        }
        // Reset slider background
        slider.style.background = 'linear-gradient(to top, #3b82f6 0%, #3b82f6 50%, #e5e7eb 50%, #e5e7eb 100%)';
    });
    
    // Reset zoom display
    const zoomDisplay = document.querySelector('.zoom-level');
    if (zoomDisplay) {
        zoomDisplay.textContent = '100%';
    }
    
    // Reset any custom file inputs
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.value = '';
    });
    
    // Reset any text inputs that might contain user data
    const textInputs = document.querySelectorAll('input[type="text"]:not(.hex-input)');
    textInputs.forEach(input => {
        if (!input.classList.contains('hex-input')) {
            input.value = '';
        }
    });
    
    console.log('✅ All UI elements reset successfully');
}

/* ============================================
   FORM HANDLING
   ============================================ */

function initializeFormHandling() {
    // Size/format select changes
    const formatSelect = document.querySelector('#output-format');
    const sizeSelect = document.querySelector('#output-size');
    
    // Photo Size and DPI settings
    const photoSizeSelect = document.querySelector('#photoSize');
    const dpiSettingSelect = document.querySelector('#dpiSetting');
    
    if (formatSelect) {
        formatSelect.addEventListener('change', handleFormatChange);
    }
    
    if (sizeSelect) {
        sizeSelect.addEventListener('change', handleSizeChange);
    }
    
    // Add Photo Size change handler
    if (photoSizeSelect) {
        photoSizeSelect.addEventListener('change', handlePhotoSizeChange);
    }
    
    // Add DPI setting change handler
    if (dpiSettingSelect) {
        dpiSettingSelect.addEventListener('change', handleDpiSettingChange);
    }
    
    // Numeric input validations
    const numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(input => {
        input.addEventListener('input', validateNumericInput);
    });
}

function handleFormatChange(e) {
    const format = e.target.value;
    console.log('Output format changed to:', format);
    
    // Update any format-specific options
    updateFormatOptions(format);
}

function handleSizeChange(e) {
    const size = e.target.value;
    console.log('Output size changed to:', size);
    
    // Auto-fill width/height inputs based on preset
    updateSizeInputs(size);
}

// Photo Size dropdown change handler (for passport/ID photo sizes)
async function handlePhotoSizeChange(e) {
    const photoSize = e.target.value;
    console.log('Photo size changed to:', photoSize);
    
    if (!photoSize) return;
    
    try {
        showLoadingOverlay(`Applying ${photoSize} photo format...`);
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        // Map photo sizes to backend endpoints or parameters
        let country = photoSize;
        let dimensions = null;
        
        // Define standard dimensions for different photo sizes
        const photoDimensions = {
            'india': { width: 600, height: 600 },
            'us': { width: 600, height: 600 }, // 2x2 inches at 300 DPI
            'uk': { width: 413, height: 531 }, // 45x35mm
            'canada': { width: 590, height: 826 }, // 50x70mm
            'australia': { width: 413, height: 531 }, // Same as UK
            'schengen': { width: 413, height: 531 } // Same as UK
        };
        
        if (photoDimensions[photoSize.toLowerCase()]) {
            dimensions = photoDimensions[photoSize.toLowerCase()];
        }
        
        // Use the passport/quick resize endpoint
        let endpoint = 'quick_passport';
        let requestData = { country: country };
        
        // If we have specific dimensions, use the resize endpoint instead
        if (dimensions) {
            endpoint = 'resize';
            requestData = {
                country: country,
                width: dimensions.width,
                height: dimensions.height
            };
        }
        
        const response = await fetch(`/process/${endpoint}/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(`Photo resized for ${photoSize.toUpperCase()} format!`);
            // Update the preview image with the processed result
            if (result.output_filename) {
                const newImageUrl = `/static/processed/${result.output_filename}`;
                updatePreviewImage(newImageUrl);
                previewState.currentImage = newImageUrl;
                // Update the URL to reflect the new file
                window.history.pushState({}, '', `/preview/${result.output_filename}`);
                
                // Auto-fill the custom resize inputs with the applied dimensions
                if (dimensions) {
                    const widthInput = document.querySelector('#resize-width');
                    const heightInput = document.querySelector('#resize-height');
                    if (widthInput) widthInput.value = dimensions.width;
                    if (heightInput) heightInput.value = dimensions.height;
                }
            }
        } else {
            throw new Error(result.error || `Failed to apply ${photoSize} format`);
        }
        
    } catch (error) {
        console.error('Photo size change error:', error);
        showErrorMessage(`Failed to apply ${photoSize} format: ` + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

// DPI Setting dropdown change handler
async function handleDpiSettingChange(e) {
    const dpiValue = e.target.value;
    console.log('DPI setting changed to:', dpiValue);
    
    if (!dpiValue) return;
    
    // Get current dimensions from resize inputs or use defaults
    const widthInput = document.querySelector('#resize-width');
    const heightInput = document.querySelector('#resize-height');
    
    let width = widthInput ? parseInt(widthInput.value) : null;
    let height = heightInput ? parseInt(heightInput.value) : null;
    
    // If no dimensions are set, use standard passport photo dimensions
    if (!width || !height) {
        width = 600;
        height = 600;
        
        // Update the input fields with these values
        if (widthInput) widthInput.value = width;
        if (heightInput) heightInput.value = height;
        
        showInfoMessage(`Using standard passport dimensions (${width}x${height}px) with ${dpiValue} DPI`);
    }
    
    try {
        showLoadingOverlay(`Applying ${dpiValue} DPI setting...`);
        
        // Get current filename from URL
        const filename = getCurrentFilename();
        
        // Use the resize endpoint with DPI parameter
        const requestData = {
            country: 'US', // Default country
            width: width,
            height: height,
            dpi: parseInt(dpiValue)
        };
        
        const response = await fetch(`/process/resize/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(`Image processed with ${dpiValue} DPI setting!`);
            // Update the preview image with the processed result
            if (result.output_filename) {
                const newImageUrl = `/static/processed/${result.output_filename}`;
                updatePreviewImage(newImageUrl);
                previewState.currentImage = newImageUrl;
                // Update the URL to reflect the new file
                window.history.pushState({}, '', `/preview/${result.output_filename}`);
            }
        } else {
            throw new Error(result.error || `Failed to apply ${dpiValue} DPI setting`);
        }
        
    } catch (error) {
        console.error('DPI setting change error:', error);
        showErrorMessage(`Failed to apply ${dpiValue} DPI setting: ` + error.message);
    } finally {
        hideLoadingOverlay();
    }
}

function updateFormatOptions(format) {
    // Add format-specific handling if needed
    const qualityOptions = document.querySelector('.quality-options');
    
    if (qualityOptions) {
        // Show quality options for JPEG, hide for PNG
        qualityOptions.style.display = format === 'jpeg' ? 'block' : 'none';
    }
}

function updateSizeInputs(size) {
    const widthInput = document.querySelector('#resize-width');
    const heightInput = document.querySelector('#resize-height');
    
    if (!widthInput || !heightInput) return;
    
    const presets = {
        'passport': { width: 600, height: 600 },
        'visa': { width: 600, height: 600 },
        'id': { width: 480, height: 600 },
        'resume': { width: 300, height: 400 },
        'linkedin': { width: 400, height: 400 },
        'custom': { width: '', height: '' }
    };
    
    if (presets[size]) {
        widthInput.value = presets[size].width;
        heightInput.value = presets[size].height;
    }
}

function validateNumericInput(e) {
    const input = e.target;
    const value = parseInt(input.value);
    
    // Skip validation for resize inputs - allow unlimited values
    if (input.id === 'resize-width' || input.id === 'resize-height') {
        // Only check for negative values
        if (value < 0) {
            input.value = 0;
            showWarningMessage('Size cannot be negative');
        }
        return;
    }
    
    const min = parseInt(input.getAttribute('min')) || 0;
    const max = parseInt(input.getAttribute('max')) || 9999;
    
    if (isNaN(value)) return;
    
    if (value < min) {
        input.value = min;
        showWarningMessage(`Minimum value is ${min}`);
    } else if (value > max) {
        input.value = max;
        showWarningMessage(`Maximum value is ${max}`);
    }
}

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

function updatePreviewImage(imageData) {
    const previewImage = document.querySelector('.preview-image');
    if (previewImage) {
        previewImage.src = imageData;
        previewState.currentImage = imageData;
        updateImageInfo();
    }
}

async function updateImageInfo() {
    const previewImage = document.querySelector('.preview-image');
    if (!previewImage || !previewImage.src) {
        console.log('No preview image found or no source');
        return;
    }
    
    console.log('Updating image info for:', previewImage.src);
    
    // Get filename from current URL or image src
    const filename = getCurrentFilename();
    console.log('Getting image info for filename:', filename);
    
    try {
        // First fetch detailed image info from API
        const response = await fetch(`/api/image-info/${filename}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                // Update all info items with API data
                const originalName = getOriginalFilename(data.filename);
                const friendlyName = generateFriendlyCurrentName(data.filename);
                
                console.log('🔍 Debug Info:');
                console.log('  Raw filename:', data.filename);
                console.log('  Original name:', originalName);
                console.log('  Friendly name:', friendlyName);
                console.log('  UUID detected:', isUuidBasedFilename(data.filename));
                
                updateInfoItem('original name', originalName);
                updateInfoItem('current name', friendlyName);
                updateInfoItem('dimensions', `${data.width} × ${data.height}px`);
                updateInfoItem('aspect ratio', calculateAspectRatio(data.width, data.height));
                updateInfoItem('format', data.format || 'JPEG');
                console.log('✅ Updated image info from API');
                return;
            }
        }
    } catch (error) {
        console.error('Failed to fetch image info from API:', error);
    }
    
    // Fallback to loading image directly and getting basic info
    const img = new Image();
    
    img.onload = function() {
        console.log('Image loaded successfully (fallback):', this.naturalWidth, 'x', this.naturalHeight);
        
        // Update with fallback data
        updateInfoItem('original name', getOriginalFilename(filename));
        updateInfoItem('current name', generateFriendlyCurrentName(filename));
        updateInfoItem('dimensions', `${this.naturalWidth} × ${this.naturalHeight}px`);
        updateInfoItem('aspect ratio', calculateAspectRatio(this.naturalWidth, this.naturalHeight));
        
        // Determine format from URL
        let format = 'JPEG';
        if (previewImage.src.includes('.png')) {
            format = 'PNG';
        } else if (previewImage.src.includes('.webp')) {
            format = 'WebP';
        }
        updateInfoItem('format', format);
        console.log('Updated image info (fallback)');
    };
    
    img.onerror = function() {
        console.error('Failed to load image for info update:', previewImage.src);
        // Show error state
        updateInfoItem('original name', 'Error loading');
        updateInfoItem('current name', 'Error loading');
        updateInfoItem('dimensions', 'Error loading');
        updateInfoItem('aspect ratio', 'Error loading');
        updateInfoItem('format', 'Error loading');
    };
    
    // Set crossOrigin to handle potential CORS issues
    img.crossOrigin = 'anonymous';
    img.src = previewImage.src;
}

// Helper function to update individual info items
function updateInfoItem(labelText, value) {
    const infoItems = document.querySelectorAll('.info-item');
    infoItems.forEach(item => {
        const label = item.querySelector('.info-label');
        const valueElement = item.querySelector('.info-value');
        
        if (label && valueElement && label.textContent.toLowerCase().includes(labelText.toLowerCase())) {
            valueElement.textContent = value;
            console.log(`Updated ${labelText}:`, value);
        }
    });
}

function calculateAspectRatio(width, height) {
    const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
    const divisor = gcd(width, height);
    return `${width / divisor}:${height / divisor}`;
}

function displayPositioningInfo(info) {
    // Create or update positioning info display
    let infoDiv = document.querySelector('.positioning-info');
    
    if (!infoDiv) {
        infoDiv = document.createElement('div');
        infoDiv.className = 'positioning-info';
        infoDiv.style.cssText = `
            background: #f3f4f6;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            font-size: 14px;
            line-height: 1.5;
        `;
        
        const alignmentCard = document.querySelector('.control-card:has(.auto-align-btn)');
        if (alignmentCard) {
            alignmentCard.querySelector('.card-body').appendChild(infoDiv);
        }
    }
    
    infoDiv.innerHTML = `
        <h4 style="margin: 0 0 12px 0; color: #374151; font-weight: 600;">Face Positioning Analysis</h4>
        <div style="display: grid; gap: 8px;">
            <div style="display: flex; justify-content: space-between;">
                <span>Face Position:</span>
                <strong>${info.position || 'Centered'}</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Head Tilt:</span>
                <strong>${info.tilt || '0°'}</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Face Size:</span>
                <strong>${info.size || 'Optimal'}</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Eye Level:</span>
                <strong>${info.eye_level || 'Aligned'}</strong>
            </div>
        </div>
    `;
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleImageFile(file) {
    if (!file || !file.type.startsWith('image/')) {
        showErrorMessage('Please select a valid image file');
        return;
    }
    
    if (file.size > CONFIG.maxFileSize) {
        showErrorMessage('File size too large. Maximum size is 10MB');
        return;
    }
    
    if (!CONFIG.allowedFormats.includes(file.type)) {
        showErrorMessage('Unsupported file format. Please use JPEG, PNG, or WebP');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        updatePreviewImage(e.target.result);
        previewState.originalImage = e.target.result;
    };
    reader.readAsDataURL(file);
}

/* ============================================
   PASSPORT GUIDELINES POPUP
   ============================================ */

function showPassportGuidelines() {
    // Remove any existing guidelines popup
    const existingPopup = document.querySelector('.passport-guidelines-popup');
    if (existingPopup) {
        existingPopup.remove();
    }
    
    // Create the guidelines popup
    const popup = document.createElement('div');
    popup.className = 'passport-guidelines-popup';
    popup.innerHTML = `
        <div class="guidelines-overlay"></div>
        <div class="guidelines-content">
            <div class="guidelines-header">
                <h2><i class="fas fa-id-card"></i> Passport Photo Guidelines</h2>
                <button class="guidelines-close-btn" onclick="closePassportGuidelines()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="guidelines-body">
                <div class="guidelines-tabs">
                    <button class="tab-btn active" onclick="showGuidelinesTab('general')">General Rules</button>
                    <button class="tab-btn" onclick="showGuidelinesTab('composition')">Composition</button>
                    <button class="tab-btn" onclick="showGuidelinesTab('quality')">Photo Quality</button>
                    <button class="tab-btn" onclick="showGuidelinesTab('countries')">Country Specific</button>
                </div>
                
                <!-- General Rules Tab -->
                <div class="tab-content active" id="general-tab">
                    <div class="guidelines-section">
                        <h3><i class="fas fa-user"></i> Face & Expression</h3>
                        <div class="guidelines-grid">
                            <div class="guideline-item">
                                <div class="guideline-icon">✅</div>
                                <div class="guideline-text">
                                    <strong>Neutral Expression:</strong> Keep a natural, neutral expression with mouth closed
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">✅</div>
                                <div class="guideline-text">
                                    <strong>Eyes Open:</strong> Both eyes must be clearly visible and open
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">✅</div>
                                <div class="guideline-text">
                                    <strong>Look Straight:</strong> Look directly at the camera
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">❌</div>
                                <div class="guideline-text">
                                    <strong>No Smiling:</strong> Avoid smiling or showing teeth
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="guidelines-section">
                        <h3><i class="fas fa-eye"></i> Head Position</h3>
                        <div class="guidelines-grid">
                            <div class="guideline-item">
                                <div class="guideline-icon">✅</div>
                                <div class="guideline-text">
                                    <strong>Head Straight:</strong> Keep your head straight and level
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">✅</div>
                                <div class="guideline-text">
                                    <strong>Face the Camera:</strong> Face directly towards the camera
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">❌</div>
                                <div class="guideline-text">
                                    <strong>No Tilting:</strong> Don't tilt your head to any side
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Composition Tab -->
                <div class="tab-content" id="composition-tab">
                    <div class="guidelines-section">
                        <h3><i class="fas fa-crop-alt"></i> Photo Dimensions</h3>
                        <div class="guidelines-grid">
                            <div class="guideline-item">
                                <div class="guideline-icon">📏</div>
                                <div class="guideline-text">
                                    <strong>Standard Size:</strong> 2x2 inches (51x51mm) for most countries
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">📏</div>
                                <div class="guideline-text">
                                    <strong>Head Size:</strong> Head should be 1-1.375 inches (25-35mm) from bottom of chin to top of head
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">🎯</div>
                                <div class="guideline-text">
                                    <strong>Centering:</strong> Head should be centered in the frame
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="guidelines-section">
                        <h3><i class="fas fa-palette"></i> Background</h3>
                        <div class="guidelines-grid">
                            <div class="guideline-item">
                                <div class="guideline-icon">⚪</div>
                                <div class="guideline-text">
                                    <strong>White/Light Background:</strong> Use plain white or off-white background
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">✅</div>
                                <div class="guideline-text">
                                    <strong>No Patterns:</strong> Background must be plain, no textures or patterns
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">❌</div>
                                <div class="guideline-text">
                                    <strong>No Shadows:</strong> Avoid shadows on face or background
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Photo Quality Tab -->
                <div class="tab-content" id="quality-tab">
                    <div class="guidelines-section">
                        <h3><i class="fas fa-camera"></i> Technical Requirements</h3>
                        <div class="guidelines-grid">
                            <div class="guideline-item">
                                <div class="guideline-icon">🔍</div>
                                <div class="guideline-text">
                                    <strong>High Resolution:</strong> Minimum 600x600 pixels, 300 DPI recommended
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">🌟</div>
                                <div class="guideline-text">
                                    <strong>Sharp Focus:</strong> Photo must be in sharp focus, not blurry
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">💡</div>
                                <div class="guideline-text">
                                    <strong>Good Lighting:</strong> Even lighting on face, no harsh shadows
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">🎨</div>
                                <div class="guideline-text">
                                    <strong>Natural Colors:</strong> Accurate skin tone, no color casts
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="guidelines-section">
                        <h3><i class="fas fa-file-image"></i> File Format</h3>
                        <div class="guidelines-grid">
                            <div class="guideline-item">
                                <div class="guideline-icon">📄</div>
                                <div class="guideline-text">
                                    <strong>JPEG Format:</strong> Save as JPEG with high quality (90% or higher)
                                </div>
                            </div>
                            <div class="guideline-item">
                                <div class="guideline-icon">💾</div>
                                <div class="guideline-text">
                                    <strong>File Size:</strong> Keep file size between 240KB - 1MB
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Country Specific Tab -->
                <div class="tab-content" id="countries-tab">
                    <div class="guidelines-section">
                        <h3><i class="fas fa-flag"></i> Different Country Requirements</h3>
                        <div class="country-requirements">
                            <div class="country-item">
                                <div class="country-flag">🇺🇸</div>
                                <div class="country-details">
                                    <strong>United States:</strong>
                                    <ul>
                                        <li>2x2 inches (51x51mm)</li>
                                        <li>Head 1-1.375 inches tall</li>
                                        <li>White/off-white background</li>
                                        <li>Taken within last 6 months</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="country-item">
                                <div class="country-flag">🇬🇧</div>
                                <div class="country-details">
                                    <strong>United Kingdom:</strong>
                                    <ul>
                                        <li>45x35mm (1.77x1.38 inches)</li>
                                        <li>Head 29-34mm tall</li>
                                        <li>Plain light grey or cream background</li>
                                        <li>No shadows on face or background</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="country-item">
                                <div class="country-flag">🇮🇳</div>
                                <div class="country-details">
                                    <strong>India:</strong>
                                    <ul>
                                        <li>35x35mm square format</li>
                                        <li>Head 25-30mm from chin to crown</li>
                                        <li>White background preferred</li>
                                        <li>Matt finish, not glossy</li>
                                    </ul>
                                </div>
                            </div>
                            
                            <div class="country-item">
                                <div class="country-flag">🇨🇦</div>
                                <div class="country-details">
                                    <strong>Canada:</strong>
                                    <ul>
                                        <li>50x70mm (2x2.75 inches)</li>
                                        <li>Head 31-36mm from chin to crown</li>
                                        <li>Plain white or light colored background</li>
                                        <li>Neutral expression, mouth closed</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="guidelines-footer">
                <div class="footer-note">
                    <i class="fas fa-info-circle"></i>
                    <span>Always check with the specific embassy or consulate for the most current requirements as they may change.</span>
                </div>
                <button class="guidelines-btn primary" onclick="closePassportGuidelines()">
                    <i class="fas fa-check"></i> Got it, Thanks!
                </button>
            </div>
        </div>
    `;
    
    // Add styles for the popup
    const styles = `
        <style>
        .passport-guidelines-popup {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease-out;
        }
        
        .guidelines-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(4px);
        }
        
        .guidelines-content {
            position: relative;
            background: white;
            border-radius: 16px;
            width: 90%;
            max-width: 900px;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.3s ease-out;
        }
        
        .guidelines-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 24px;
            border-bottom: 1px solid #e5e7eb;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 16px 16px 0 0;
        }
        
        .guidelines-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .guidelines-header h2 i {
            margin-right: 12px;
        }
        
        .guidelines-close-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        
        .guidelines-close-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .guidelines-body {
            padding: 24px;
        }
        
        .guidelines-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            padding: 12px 20px;
            border: 2px solid #e5e7eb;
            background: white;
            color: #6b7280;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
            flex: 1;
            min-width: 120px;
        }
        
        .tab-btn:hover {
            border-color: #3b82f6;
            color: #3b82f6;
        }
        
        .tab-btn.active {
            background: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .guidelines-section {
            margin-bottom: 32px;
        }
        
        .guidelines-section h3 {
            color: #1f2937;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
        }
        
        .guidelines-section h3 i {
            margin-right: 12px;
            color: #3b82f6;
        }
        
        .guidelines-grid {
            display: grid;
            gap: 16px;
        }
        
        .guideline-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }
        
        .guideline-icon {
            font-size: 1.25rem;
            flex-shrink: 0;
            margin-top: 2px;
        }
        
        .guideline-text {
            color: #374151;
            line-height: 1.5;
        }
        
        .guideline-text strong {
            color: #1f2937;
            font-weight: 600;
        }
        
        .country-requirements {
            display: grid;
            gap: 20px;
        }
        
        .country-item {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }
        
        .country-flag {
            font-size: 2rem;
            flex-shrink: 0;
        }
        
        .country-details strong {
            color: #1f2937;
            font-size: 1.1rem;
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
        }
        
        .country-details ul {
            margin: 0;
            padding-left: 20px;
            color: #6b7280;
        }
        
        .country-details li {
            margin-bottom: 4px;
        }
        
        .guidelines-footer {
            padding: 24px;
            border-top: 1px solid #e5e7eb;
            background: #f9fafb;
            border-radius: 0 0 16px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .footer-note {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #6b7280;
            font-size: 0.9rem;
            flex: 1;
            min-width: 300px;
        }
        
        .footer-note i {
            color: #3b82f6;
            flex-shrink: 0;
        }
        
        .guidelines-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .guidelines-btn.primary {
            background: #3b82f6;
            color: white;
        }
        
        .guidelines-btn.primary:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        @media (max-width: 768px) {
            .guidelines-content {
                width: 95%;
                margin: 10px;
            }
            
            .guidelines-header,
            .guidelines-body,
            .guidelines-footer {
                padding: 16px;
            }
            
            .guidelines-tabs {
                flex-direction: column;
            }
            
            .tab-btn {
                min-width: auto;
            }
            
            .guidelines-footer {
                flex-direction: column;
                align-items: stretch;
            }
            
            .footer-note {
                min-width: auto;
                text-align: center;
            }
        }
        </style>
    `;
    
    // Add styles to head if not already present
    if (!document.querySelector('#passport-guidelines-styles')) {
        const styleSheet = document.createElement('div');
        styleSheet.id = 'passport-guidelines-styles';
        styleSheet.innerHTML = styles;
        document.head.appendChild(styleSheet);
    }
    
    // Add popup to body
    document.body.appendChild(popup);
    
    // Close popup when clicking overlay
    popup.querySelector('.guidelines-overlay').addEventListener('click', closePassportGuidelines);
    
    // Prevent body scroll when popup is open
    document.body.style.overflow = 'hidden';
}

function closePassportGuidelines() {
    const popup = document.querySelector('.passport-guidelines-popup');
    if (popup) {
        popup.style.animation = 'fadeOut 0.3s ease-in';
        setTimeout(() => {
            popup.remove();
            // Restore body scroll
            document.body.style.overflow = '';
        }, 300);
    }
}

function showGuidelinesTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Make functions globally available
window.showPassportGuidelines = showPassportGuidelines;
window.closePassportGuidelines = closePassportGuidelines;
window.showGuidelinesTab = showGuidelinesTab;

/* ============================================
   UI FEEDBACK FUNCTIONS
   ============================================ */

function showLoadingOverlay(message = 'Processing...') {
    let overlay = document.querySelector('.loading-overlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">${message}</div>
                <div class="loading-subtext">Please wait while we process your image</div>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        const loadingText = overlay.querySelector('.loading-text');
        if (loadingText) {
            loadingText.textContent = message;
        }
        overlay.style.display = 'flex';
    }
    
    previewState.isProcessing = true;
    updateButtonStates();
}

function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    previewState.isProcessing = false;
    updateButtonStates();
}

function updateButtonStates() {
    const buttons = document.querySelectorAll('button:not(.control-btn)');
    buttons.forEach(btn => {
        btn.disabled = previewState.isProcessing;
    });
}

function showSuccessMessage(message) {
    showNotification(message, 'success');
}

function showErrorMessage(message) {
    showNotification(message, 'error');
}

function showWarningMessage(message) {
    showNotification(message, 'warning');
}

function showInfoMessage(message) {
    showNotification(message, 'info');
}

function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        max-width: 400px;
        font-size: 14px;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
    
    // Add CSS animations if not already present
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/* ============================================
   ERROR HANDLING
   ============================================ */

// Improved selective error handling to avoid interfering with normal page functionality
let errorCount = 0;
const MAX_ERRORS_PER_MINUTE = 3;
let errorTimestamps = [];

function shouldShowError(error) {
    // Filter out common non-critical errors
    const ignoredErrors = [
        'showToast',
        'Non-Error promise rejection captured',
        'ResizeObserver loop limit exceeded',
        'Script error',
        'Network request failed',
        'Load failed',
        'Loading chunk'
    ];
    
    if (!error || !error.message) return false;
    
    const errorMessage = error.message.toLowerCase();
    if (ignoredErrors.some(ignored => errorMessage.includes(ignored.toLowerCase()))) {
        return false;
    }
    
    // Rate limiting to prevent spam
    const now = Date.now();
    errorTimestamps = errorTimestamps.filter(timestamp => now - timestamp < 60000); // Last minute
    
    if (errorTimestamps.length >= MAX_ERRORS_PER_MINUTE) {
        return false;
    }
    
    errorTimestamps.push(now);
    return true;
}

window.addEventListener('error', (event) => {
    console.error('Global error:', {
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
        error: event.error
    });
    
    // Only show user-friendly error message for critical application errors
    if (shouldShowError(event.error) && 
        event.error && 
        (event.error.name === 'ReferenceError' || 
         event.error.name === 'SyntaxError' ||
         (event.error.name === 'TypeError' && event.error.message.includes('Cannot read')))) {
        
        // Show a generic error message instead of technical details
        setTimeout(() => {
            showErrorMessage('Something went wrong with the image processing. Please refresh the page and try again.');
        }, 100);
    }
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Only handle promise rejections related to fetch/API calls
    if (event.reason && 
        (event.reason.name === 'TypeError' && event.reason.message.includes('fetch')) ||
        (event.reason.toString().includes('Failed to fetch'))) {
        
        setTimeout(() => {
            showErrorMessage('Network error occurred. Please check your connection and try again.');
        }, 100);
        
        // Prevent the default unhandled rejection behavior
        event.preventDefault();
    }
});

/* ============================================
   BROWSER CONSOLE TESTING
   ============================================ */

// Test function for browser console
window.testFriendlyNaming = function(testFilename) {
    console.log('\n🧪 Testing Friendly Naming Function');
    console.log('=' .repeat(50));
    
    const filename = testFilename || getCurrentFilename();
    console.log('Input filename:', filename);
    
    const originalName = getOriginalFilename(filename);
    console.log('Original name:', originalName);
    
    const friendlyName = generateFriendlyCurrentName(filename);
    console.log('Friendly name:', friendlyName);
    
    const isUuid = isUuidBasedFilename(filename);
    console.log('UUID detected:', isUuid);
    
    const hash = hashCode(filename);
    console.log('Hash code:', hash);
    console.log('Version number:', Math.abs(hash) % 99 + 1);
    
    console.log('\n📋 Summary:');
    console.log(`"${filename}" → "${friendlyName}"`);
    console.log('=' .repeat(50));
    
    return {
        input: filename,
        original: originalName,
        friendly: friendlyName,
        isUuid: isUuid,
        hash: hash
    };
};

// Test with multiple examples
window.testMultipleFilenames = function() {
    const testCases = [
        '12345678-1234-1234-1234-123456789012_imggg.jpg',
        'abcd1234-5678-9abc-def0-123456789012_photo.png',
        'test-image.jpg',
        '12345678-1234-1234-1234-123456789012_photo_bg_white.jpg',
        '12345678-1234-1234-1234-123456789012_portrait_enhanced.png'
    ];
    
    console.log('\n🎯 Testing Multiple Filename Examples');
    console.log('=' .repeat(60));
    
    testCases.forEach((filename, index) => {
        console.log(`\nTest Case ${index + 1}:`);
        testFriendlyNaming(filename);
    });
};

/* ============================================
   EXPORT FOR TESTING
   ============================================ */

// Export functions for testing purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        previewState,
        CONFIG,
        isValidHexColor,
        calculateAspectRatio,
        updateZoom,
        handleColorSelection,
        getOriginalFilename,
        generateFriendlyCurrentName,
        isUuidBasedFilename,
        hashCode
    };
}
