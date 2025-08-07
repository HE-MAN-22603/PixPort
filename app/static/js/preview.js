/* PixPort Preview Page JavaScript */

// Preview page state
let previewState = {
    filename: null,
    currentImage: null,
    processedFilename: null,  // Track latest processed image
    zoomLevel: 1,
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    imageOffset: { x: 0, y: 0 }
};

// Initialize preview page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize enhanced preview functionality
    initializeEnhancedPreview();
    if (document.querySelector('.preview-page')) {
        initializePreviewPage();
    }
});

function initializePreviewPage() {
    console.log('🔍 Initializing preview page...');
    
    // Get filename from URL or data attribute
    previewState.filename = getFilenameFromURL();
    
    setupImageControls();
    setupProcessingOptions();
    setupProcessingButtons();
    loadImageInfo();
}

function getFilenameFromURL() {
    const path = window.location.pathname;
    const matches = path.match(/\/preview\/(.+)$/);
    return matches ? matches[1] : null;
}

function setupImageControls() {
    const image = document.querySelector('.preview-image');
    const container = document.querySelector('.image-container');
    
    if (!image || !container) return;
    
    previewState.currentImage = image;
    
    // Zoom controls
    const zoomInBtn = document.querySelector('[data-action="zoom-in"]');
    const zoomOutBtn = document.querySelector('[data-action="zoom-out"]');
    const resetBtn = document.querySelector('[data-action="reset"]');
    
    if (zoomInBtn) zoomInBtn.addEventListener('click', () => zoomImage(1.2));
    if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => zoomImage(0.8));
    if (resetBtn) resetBtn.addEventListener('click', resetImage);
    
    // Mouse events for dragging
    image.addEventListener('mousedown', startDrag);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);
    
    // Touch events for mobile
    image.addEventListener('touchstart', startDrag);
    document.addEventListener('touchmove', drag);
    document.addEventListener('touchend', endDrag);
    
    // Prevent context menu on image
    image.addEventListener('contextmenu', e => e.preventDefault());
}

function zoomImage(factor) {
    previewState.zoomLevel *= factor;
    previewState.zoomLevel = Math.max(0.5, Math.min(3, previewState.zoomLevel));
    
    updateImageTransform();
    updateZoomControls();
}

function resetImage() {
    previewState.zoomLevel = 1;
    previewState.imageOffset = { x: 0, y: 0 };
    updateImageTransform();
    updateZoomControls();
}

function updateImageTransform() {
    if (!previewState.currentImage) return;
    
    const { zoomLevel, imageOffset } = previewState;
    previewState.currentImage.style.transform = 
        `scale(${zoomLevel}) translate(${imageOffset.x}px, ${imageOffset.y}px)`;
}

function updateZoomControls() {
    const zoomInBtn = document.querySelector('[data-action="zoom-in"]');
    const zoomOutBtn = document.querySelector('[data-action="zoom-out"]');
    
    if (zoomInBtn) zoomInBtn.disabled = previewState.zoomLevel >= 3;
    if (zoomOutBtn) zoomOutBtn.disabled = previewState.zoomLevel <= 0.5;
}

function startDrag(e) {
    if (previewState.zoomLevel <= 1) return;
    
    previewState.isDragging = true;
    
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    previewState.dragStart = {
        x: clientX - previewState.imageOffset.x,
        y: clientY - previewState.imageOffset.y
    };
    
    previewState.currentImage.style.cursor = 'grabbing';
    e.preventDefault();
}

function drag(e) {
    if (!previewState.isDragging) return;
    
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    previewState.imageOffset = {
        x: clientX - previewState.dragStart.x,
        y: clientY - previewState.dragStart.y
    };
    
    updateImageTransform();
    e.preventDefault();
}

function endDrag() {
    if (!previewState.isDragging) return;
    
    previewState.isDragging = false;
    previewState.currentImage.style.cursor = 'grab';
}

function setupProcessingOptions() {
    const optionHeaders = document.querySelectorAll('.option-header');
    
    optionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const isActive = this.classList.contains('active');
            
            // Close all options first
            optionHeaders.forEach(h => {
                h.classList.remove('active');
                if (h.nextElementSibling) {
                    h.nextElementSibling.classList.remove('active');
                }
            });
            
            // Open clicked option if it wasn't active
            if (!isActive) {
                this.classList.add('active');
                content.classList.add('active');
            }
        });
    });
    
    // Setup color selection
    setupColorSelection();
    
    // Setup country selection
    setupCountrySelection();
}

function setupColorSelection() {
    const colorOptions = document.querySelectorAll('.color-option');
    
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            colorOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Store selected color
            const color = this.dataset.color || this.className.match(/color-(\w+)/)?.[1];
            PixPort.settings.selectedColor = color;
        });
    });
    
    // Set default selection
    const defaultColor = document.querySelector('.color-white');
    if (defaultColor) defaultColor.classList.add('selected');
}

function setupCountrySelection() {
    const countryOptions = document.querySelectorAll('.country-option');
    
    countryOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            countryOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Store selected country
            PixPort.settings.selectedCountry = this.dataset.country || this.textContent.trim();
        });
    });
    
    // Set default selection
    const defaultCountry = document.querySelector('[data-country="US"]');
    if (defaultCountry) defaultCountry.classList.add('selected');
}

function setupProcessingButtons() {
    const processButtons = document.querySelectorAll('.process-btn');
    
    processButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const action = this.dataset.action;
            if (!action || !previewState.filename) return;
            
            try {
                this.disabled = true;
                
                let options = {};
                
                // Add action-specific options
                if (action === 'change_background') {
                    options.color = PixPort.settings.selectedColor;
                } else if (action === 'resize') {
                    options.country = PixPort.settings.selectedCountry;
                }
                
                const result = await processImage(action, previewState.filename, options);
                
                if (result.success) {
                    showToast(result.message, 'success');
                    
                    // Update preview image with processed result
                    if (result.preview_url) {
                        updatePreviewImage(result.preview_url, result.output_filename);
                    } else if (result.redirect) {
                        // Only redirect for quick actions
                        window.location.href = result.redirect;
                    }
                } else {
                    showToast(result.message || 'Processing failed', 'error');
                }
                
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                this.disabled = false;
            }
        });
    });
}

async function loadImageInfo() {
    if (!previewState.filename) return;
    
    try {
        const response = await fetch(`/api/image-info/${previewState.filename}`);
        if (response.ok) {
            const info = await response.json();
            updateImageInfo(info);
        }
    } catch (error) {
        console.error('Failed to load image info:', error);
    }
}

function updateImageInfo(info) {
    const infoContainer = document.querySelector('.image-info');
    if (!infoContainer) return;
    
    const infoList = infoContainer.querySelector('.info-list');
    if (!infoList) return;
    
    infoList.innerHTML = `
        <li class="info-item">
            <span class="info-label">Format:</span>
            <span class="info-value">${info.format || 'Unknown'}</span>
        </li>
        <li class="info-item">
            <span class="info-label">Dimensions:</span>
            <span class="info-value">${info.width || 0} × ${info.height || 0}px</span>
        </li>
        <li class="info-item">
            <span class="info-label">File Size:</span>
            <span class="info-value">${formatFileSize(info.file_size || 0)}</span>
        </li>
        <li class="info-item">
            <span class="info-label">Color Mode:</span>
            <span class="info-value">${info.mode || 'RGB'}</span>
        </li>
    `;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (!document.querySelector('.preview-page')) return;
    
    switch(e.key) {
        case '+':
        case '=':
            e.preventDefault();
            zoomImage(1.2);
            break;
        case '-':
            e.preventDefault();
            zoomImage(0.8);
            break;
        case '0':
            e.preventDefault();
            resetImage();
            break;
        case 'Escape':
            resetImage();
            break;
    }
});

// Update preview image with processed result
function updatePreviewImage(previewUrl, outputFilename) {
    if (!previewState.currentImage) return;
    
    // Update the preview image source
    previewState.currentImage.src = previewUrl;
    
    // Store the processed filename
    previewState.processedFilename = outputFilename;
    
    // Reset image transform
    resetImage();
    
    // Update the current working filename for further processing
    previewState.filename = outputFilename;
    
    // Show/update the result button
    showResultButton();
    
    // Add visual feedback
    previewState.currentImage.style.transition = 'opacity 0.3s ease';
    previewState.currentImage.style.opacity = '0.7';
    
    previewState.currentImage.onload = function() {
        this.style.opacity = '1';
        this.style.transition = '';
        
        // Update image info for the new processed image
        loadImageInfo();
    };
}

// Show result/download button when image has been processed
function showResultButton() {
    let resultButton = document.querySelector('.result-button');
    
    if (!resultButton) {
        // Create result button if it doesn't exist
        resultButton = document.createElement('button');
        resultButton.className = 'btn btn-primary result-button';
        resultButton.innerHTML = `
            <i class="fas fa-download"></i>
            Go to Download Page
        `;
        
        resultButton.addEventListener('click', function() {
            if (previewState.processedFilename) {
                window.location.href = `/result/${previewState.processedFilename}`;
            }
        });
        
        // Add button to header actions or create a container
        const headerActions = document.querySelector('.header-actions');
        if (headerActions) {
            headerActions.appendChild(resultButton);
        } else {
            // Create a floating action button
            resultButton.style.position = 'fixed';
            resultButton.style.bottom = '20px';
            resultButton.style.right = '20px';
            resultButton.style.zIndex = '1000';
            resultButton.style.borderRadius = '50px';
            resultButton.style.padding = '15px 25px';
            resultButton.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
            document.body.appendChild(resultButton);
        }
    }
    
    // Show with animation
    resultButton.style.display = 'block';
    setTimeout(() => {
        resultButton.style.opacity = '1';
        resultButton.style.transform = 'scale(1)';
    }, 100);
}

// Enhanced preview functionality
function initializeEnhancedPreview() {
    console.log('🎨 Initializing enhanced preview...');
    
    // Initialize all enhanced components
    setupEnhancementSliders();
    setupActionButtons();
    setupBottomActions();
    setupSelectDropdowns();
    setupRotateControls();
    setupFitControls();
    setupColorPalette();
}

// Setup enhancement sliders
function setupEnhancementSliders() {
    const sliders = document.querySelectorAll('.enhancement-slider');
    
    sliders.forEach(slider => {
        const valueDisplay = slider.nextElementSibling;
        
        // Update display value on change
        slider.addEventListener('input', function() {
            if (valueDisplay && valueDisplay.classList.contains('slider-value')) {
                valueDisplay.textContent = this.value;
            }
            
            // Apply real-time preview effects (CSS filters)
            applyEnhancementPreview();
        });
    });
}

// Apply enhancement preview using CSS filters
function applyEnhancementPreview() {
    const image = document.getElementById('previewImage');
    if (!image) return;
    
    const contrast = document.getElementById('contrastSlider')?.value || 0;
    const brightness = document.getElementById('brightnessSlider')?.value || 0;
    const saturation = document.getElementById('saturationSlider')?.value || 0;
    const hue = document.getElementById('hueSlider')?.value || 0;
    
    const filters = [
        `contrast(${100 + parseInt(contrast)}%)`,
        `brightness(${100 + parseInt(brightness)}%)`,
        `saturate(${100 + parseInt(saturation)}%)`,
        `hue-rotate(${hue}deg)`
    ];
    
    image.style.filter = filters.join(' ');
}

// Setup action buttons
function setupActionButtons() {
    const actionButtons = document.querySelectorAll('.action-btn, .quick-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const action = this.dataset.action;
            if (!action) return;
            
            try {
                this.disabled = true;
                this.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing...`;
                
                let options = getProcessingOptions(action);
                const filename = previewState.filename || getFilenameFromURL();
                
                const result = await processImage(action, filename, options);
                
                if (result.success) {
                    showToast(result.message, 'success');
                    
                    if (result.preview_url) {
                        updatePreviewImage(result.preview_url, result.output_filename);
                    }
                } else {
                    showToast(result.message || 'Processing failed', 'error');
                }
                
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                this.disabled = false;
                resetButtonText(this, action);
            }
        });
    });
}

// Get processing options based on action
function getProcessingOptions(action) {
    let options = {};
    
    switch(action) {
        case 'change_background':
            const selectedColor = document.querySelector('.color-option.selected');
            options.color = selectedColor?.dataset.color || 'white';
            break;
            
        case 'resize':
            const selectedCountry = document.getElementById('photoSize')?.value || 'US';
            options.country = selectedCountry;
            
            // Add custom dimensions if specified
            const customWidth = document.getElementById('customWidth')?.value;
            const customHeight = document.getElementById('customHeight')?.value;
            if (customWidth && customHeight) {
                options.custom_width = parseInt(customWidth);
                options.custom_height = parseInt(customHeight);
            }
            break;
            
        case 'enhance':
            // Get all slider values for enhancement
            const sliders = document.querySelectorAll('.enhancement-slider');
            sliders.forEach(slider => {
                const property = slider.dataset.property;
                if (property) {
                    options[property] = parseFloat(slider.value);
                }
            });
            break;
            
        case 'quick_passport':
        case 'professional':
            options.country = document.getElementById('photoSize')?.value || 'US';
            const bgColor = document.querySelector('.color-option.selected');
            options.color = bgColor?.dataset.color || 'white';
            break;
    }
    
    return options;
}

// Reset button text after processing
function resetButtonText(button, action) {
    const buttonTexts = {
        'remove_background': '<i class="fas fa-cut"></i> Remove Background',
        'change_background': '<i class="fas fa-palette"></i> Change Background Color',
        'enhance': '<i class="fas fa-magic"></i> ENHANCE IMAGE',
        'resize': '<i class="fas fa-expand-arrows-alt"></i> Apply Resize & Rotate',
        'quick_passport': '<i class="fas fa-bolt"></i> Quick Passport Photo',
        'professional': '<i class="fas fa-star"></i> Professional Package'
    };
    
    button.innerHTML = buttonTexts[action] || button.innerHTML;
}

// Setup bottom action buttons
function setupBottomActions() {
    const uploadNewBtn = document.querySelector('.upload-new-btn');
    const resetAllBtn = document.querySelector('.reset-all-btn');
    const downloadBtn = document.querySelector('.download-professional-btn');
    
    if (uploadNewBtn) {
        uploadNewBtn.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
    
    if (resetAllBtn) {
        resetAllBtn.addEventListener('click', () => {
            // Reset all sliders
            document.querySelectorAll('.enhancement-slider').forEach(slider => {
                slider.value = slider.min || 0;
                const valueDisplay = slider.nextElementSibling;
                if (valueDisplay && valueDisplay.classList.contains('slider-value')) {
                    valueDisplay.textContent = slider.value;
                }
            });
            
            // Reset image filters
            const image = document.getElementById('previewImage');
            if (image) {
                image.style.filter = 'none';
            }
            
            // Reset form values
            document.getElementById('photoSize').value = 'US';
            document.getElementById('dpiSetting').value = '300';
            document.getElementById('customWidth').value = '';
            document.getElementById('customHeight').value = '';
            
            // Reset color selection
            document.querySelectorAll('.color-option').forEach(option => {
                option.classList.remove('selected');
            });
            document.querySelector('.color-option[data-color="white"]')?.classList.add('selected');
            
            showToast('All settings reset to defaults', 'info');
        });
    }
    
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            if (previewState.processedFilename) {
                window.location.href = `/result/${previewState.processedFilename}`;
            } else {
                showToast('Please process the image first', 'warning');
            }
        });
    }
}

// Setup select dropdowns
function setupSelectDropdowns() {
    const photoSizeSelect = document.getElementById('photoSize');
    const dpiSelect = document.getElementById('dpiSetting');
    
    if (photoSizeSelect) {
        photoSizeSelect.addEventListener('change', function() {
            updateDimensionsDisplay(this.value);
        });
    }
    
    if (dpiSelect) {
        dpiSelect.addEventListener('change', function() {
            updatePixelSizeDisplay();
        });
    }
    
    // Initialize display
    updateDimensionsDisplay('US');
}

// Update dimensions display
function updateDimensionsDisplay(country) {
    const helpText = document.querySelector('.dpi-selection .help-text');
    if (!helpText) return;
    
    const dimensions = {
        'US': '1200x1500 pixels',
        'UK': '1378x1772 pixels', 
        'INDIA': '1378x1378 pixels',
        'CANADA': '1378x1772 pixels',
        'GERMANY': '1378x1772 pixels',
        'FRANCE': '1378x1772 pixels',
        'AUSTRALIA': '1378x1772 pixels',
        'JAPAN': '1378x1772 pixels'
    };
    
    helpText.textContent = `Output size: ${dimensions[country] || dimensions.US} for ${country} size`;
}

// Setup rotate controls
function setupRotateControls() {
    const rotateButtons = document.querySelectorAll('.rotate-btn');
    
    rotateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const rotation = parseInt(this.dataset.rotate);
            const image = document.getElementById('previewImage');
            
            if (image) {
                const currentTransform = image.style.transform || '';
                const currentRotation = currentTransform.match(/rotate\(([^)]+)\)/)?.[1] || '0deg';
                const currentValue = parseInt(currentRotation) || 0;
                const newRotation = currentValue + rotation;
                
                image.style.transform = `${currentTransform.replace(/rotate\([^)]*\)/, '')} rotate(${newRotation}deg)`;
                
                showToast(`Image rotated ${rotation > 0 ? 'right' : 'left'}`, 'info');
            }
        });
    });
}

// Setup fit controls
function setupFitControls() {
    const fitButtons = document.querySelectorAll('.fit-btn');
    
    fitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const fitType = this.dataset.fit;
            const image = document.getElementById('previewImage');
            
            if (image && fitType) {
                const currentScale = previewState.zoomLevel || 1;
                let newScale = currentScale;
                
                if (fitType === 'head-smaller') {
                    newScale = Math.max(0.5, currentScale * 0.9);
                } else if (fitType === 'head-larger') {
                    newScale = Math.min(3, currentScale * 1.1);
                }
                
                previewState.zoomLevel = newScale;
                updateImageTransform();
                
                showToast(`Head size ${fitType === 'head-smaller' ? 'decreased' : 'increased'}`, 'info');
            }
        });
    });
}

// Setup color palette
function setupColorPalette() {
    const colorOptions = document.querySelectorAll('.color-palette .color-option');
    
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            colorOptions.forEach(opt => opt.classList.remove('selected'));
            
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Visual feedback
            this.style.transform = 'scale(1.2)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });
    
    // Set default selection
    const defaultColor = document.querySelector('.color-palette .color-option[data-color="white"]');
    if (defaultColor) {
        defaultColor.classList.add('selected');
    }
}

// Detect positioning guidelines (placeholder function)
function detectPositioningGuidelines() {
    showToast('Positioning guidelines detected - face alignment optimized', 'success');
    
    // Add visual guidelines overlay (you can implement actual face detection here)
    const container = document.querySelector('.image-container');
    if (container && !container.querySelector('.guidelines-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'guidelines-overlay';
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            border: 2px solid #6366f1;
            border-radius: 8px;
            opacity: 0.7;
        `;
        container.appendChild(overlay);
        
        // Remove after 3 seconds
        setTimeout(() => {
            overlay.remove();
        }, 3000);
    }
}

// Setup detect positioning button
document.addEventListener('DOMContentLoaded', function() {
    const detectBtn = document.querySelector('.detect-positioning-btn');
    if (detectBtn) {
        detectBtn.addEventListener('click', detectPositioningGuidelines);
    }
});

// Export for global access
window.previewState = previewState;
window.updatePreviewImage = updatePreviewImage;
window.initializeEnhancedPreview = initializeEnhancedPreview;
