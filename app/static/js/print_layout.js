/**
 * Print Layout Sheet Generator JavaScript
 * Handles the interactive functionality for creating print sheets
 */

class PrintLayoutGenerator {
    constructor() {
        this.filename = null;
        this.currentSheetUrl = null;
        this.init();
    }

    init() {
        this.filename = document.getElementById('current-filename')?.value;
        this.bindEvents();
        this.updatePreview(); // Show initial preview
    }

    bindEvents() {
        // Form change events for live preview
        const formElements = [
            'print-sheet-type',
            'print-num-photos', 
            'print-photo-size',
            'print-margin-size',
            'print-cut-guides'
        ];

        formElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => this.updatePreview());
            }
        });

        // Button events
        const previewBtn = document.getElementById('print-preview-btn');
        const generateBtn = document.getElementById('print-generate-btn');
        const downloadBtn = document.getElementById('print-download-btn');
        const viewBtn = document.getElementById('print-view-btn');

        if (previewBtn) {
            previewBtn.addEventListener('click', () => this.showPreview());
        }

        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generatePrintSheet());
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadSheet());
        }

        if (viewBtn) {
            viewBtn.addEventListener('click', () => this.viewFullSize());
        }
    }

    async updatePreview() {
        if (!this.filename) return;

        try {
            const formData = this.getFormData();
            
            const response = await fetch('/print/api/print-preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                this.displayPreviewInfo(result.preview);
            }
        } catch (error) {
            console.error('Preview update failed:', error);
        }
    }

    async showPreview() {
        const previewSection = document.getElementById('preview-section');
        if (previewSection) {
            previewSection.style.display = 'block';
            previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        await this.updatePreview();
    }

    displayPreviewInfo(preview) {
        const previewInfo = document.getElementById('print-preview-info');
        if (!previewInfo) return;
        
        // Show the preview info section
        previewInfo.style.display = 'block';

        const html = `
            <h4>📋 Print Layout Preview</h4>
            <p><strong>Sheet Type:</strong> ${preview.sheet_name}</p>
            <p><strong>Photo Size:</strong> ${preview.photo_size} passport format</p>
            <p><strong>Requested Photos:</strong> ${preview.requested_photos} copies</p>
            <p><strong>Actual Photos:</strong> <span style="color: #28a745; font-weight: 600;">${preview.actual_photos} copies</span> ${preview.actual_photos < preview.requested_photos ? '(maximum that fits)' : ''}</p>
            <p><strong>Layout:</strong> ${preview.layout} grid arrangement</p>
            <p><strong>Photo Dimensions:</strong> ${preview.photo_dimensions}</p>
            <p><strong>Sheet Dimensions:</strong> ${preview.sheet_dimensions}</p>
            ${preview.actual_photos < preview.requested_photos ? 
                '<p style="color: #856404; background: #fff3cd; padding: 10px; border-radius: 8px; border: 1px solid #ffeaa7;"><strong>Note:</strong> Some photos don\'t fit. Try a larger sheet size or smaller photo size.</p>' 
                : ''}
        `;
        
        previewInfo.innerHTML = html;
    }

    async generatePrintSheet() {
        if (!this.filename) {
            this.showStatus('error', 'No filename available');
            return;
        }

        const generateBtn = document.getElementById('print-generate-btn');
        const progressContainer = document.getElementById('print-progress-container');
        
        // Disable button and show progress
        if (generateBtn) {
            generateBtn.disabled = true;
            generateBtn.textContent = '🔄 Generating...';
        }
        
        if (progressContainer) {
            progressContainer.style.display = 'block';
        }

        this.hideStatus();

        try {
            const formData = this.getFormData();

            const response = await fetch('/print/api/generate-print-sheet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                this.currentSheetUrl = result.download_url;
                this.showResult(result.sheet_filename, result.download_url);
                this.showStatus('success', '✅ Print sheet generated successfully!');
                
                // Scroll to result
                const resultSection = document.getElementById('print-result-section');
                if (resultSection) {
                    setTimeout(() => {
                        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 500);
                }
            } else {
                throw new Error(result.error || 'Failed to generate print sheet');
            }

        } catch (error) {
            console.error('Generation failed:', error);
            this.showStatus('error', `❌ Error: ${error.message}`);
        } finally {
            // Reset button and hide progress
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.textContent = '🖨️ Create Print Sheet';
            }
            
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }
    }

    showResult(filename, downloadUrl) {
        const resultSection = document.getElementById('print-result-section');
        const resultImage = document.getElementById('print-result-image');
        const downloadBtn = document.getElementById('print-download-btn');
        const viewBtn = document.getElementById('print-view-btn');

        if (resultSection) {
            resultSection.style.display = 'block';
        }

        if (resultImage) {
            resultImage.src = downloadUrl;
            resultImage.alt = `Print sheet: ${filename}`;
        }

        // Update download button
        if (downloadBtn) {
            downloadBtn.onclick = () => this.downloadFile(downloadUrl, filename);
        }

        // Update view button  
        if (viewBtn) {
            viewBtn.onclick = () => this.openInNewTab(downloadUrl);
        }
    }

    downloadSheet() {
        if (this.currentSheetUrl) {
            const link = document.createElement('a');
            link.href = this.currentSheetUrl;
            link.download = this.currentSheetUrl.split('/').pop();
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        this.showStatus('success', '📥 Print sheet download started!');
    }

    openInNewTab(url) {
        window.open(url, '_blank');
    }

    viewFullSize() {
        if (this.currentSheetUrl) {
            this.openInNewTab(this.currentSheetUrl);
        }
    }

    getFormData() {
        const cutGuidesElement = document.getElementById('print-cut-guides');
        return {
            filename: this.filename,
            sheet_type: document.getElementById('print-sheet-type')?.value || 'A4',
            num_photos: parseInt(document.getElementById('print-num-photos')?.value || '4'),
            photo_size: document.getElementById('print-photo-size')?.value || 'US',
            margin_size: document.getElementById('print-margin-size')?.value || 'normal',
            add_cut_guides: cutGuidesElement ? cutGuidesElement.checked : true
        };
    }

    showStatus(type, message) {
        const statusElement = document.getElementById('print-status-message');
        if (!statusElement) return;

        statusElement.className = `print-status-message ${type}`;
        statusElement.textContent = message;
        statusElement.style.display = 'block';

        // Auto hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                this.hideStatus();
            }, 5000);
        }
    }

    hideStatus() {
        const statusElement = document.getElementById('print-status-message');
        if (statusElement) {
            statusElement.style.display = 'none';
        }
    }
}

// Utility functions
function addCacheBuster(url) {
    const separator = url.includes('?') ? '&' : '?';
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2);
    return `${url}${separator}_cb=${timestamp}-${random}`;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the print layout generator
    window.printLayoutGenerator = new PrintLayoutGenerator();
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states for buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            // Add subtle click feedback
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // Add form validation
    const form = document.querySelector('.generator-form');
    if (form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                this.classList.add('touched');
                validateForm();
            });
        });
    }

    function validateForm() {
        const filename = document.getElementById('current-filename')?.value;
        const generateBtn = document.getElementById('print-generate-btn');
        
        if (generateBtn) {
            generateBtn.disabled = !filename;
        }
    }

    // Initial validation
    validateForm();
});

// Handle browser back/forward buttons
window.addEventListener('popstate', function(event) {
    // Handle navigation state if needed
    console.log('Navigation state changed');
});

// Performance optimization: Lazy load images
function setupLazyLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Setup lazy loading when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupLazyLoading);
} else {
    setupLazyLoading();
}

// Error handling for images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        console.error('Image failed to load:', e.target.src);
        e.target.style.display = 'none';
        
        // Show placeholder or error message
        const placeholder = document.createElement('div');
        placeholder.className = 'image-error';
        placeholder.innerHTML = `
            <div style="
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                color: #6c757d;
                font-size: 14px;
            ">
                <div style="font-size: 2em; margin-bottom: 10px;">📷</div>
                <div>Image could not be loaded</div>
            </div>
        `;
        e.target.parentNode.insertBefore(placeholder, e.target);
    }
}, true);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const generateBtn = document.getElementById('print-generate-btn');
        if (generateBtn && !generateBtn.disabled) {
            generateBtn.click();
        }
    }
    
    // Ctrl/Cmd + D to download (when sheet is generated)
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        const downloadBtn = document.getElementById('print-download-btn');
        if (downloadBtn && downloadBtn.style.display !== 'none') {
            e.preventDefault();
            downloadBtn.click();
        }
    }
});

// Add tooltip functionality
function setupTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 1000;
        pointer-events: none;
        top: ${e.pageY - 35}px;
        left: ${e.pageX - 50}px;
        opacity: 0;
        transition: opacity 0.2s;
    `;
    
    document.body.appendChild(tooltip);
    
    // Trigger animation
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
    
    e.target.tooltipElement = tooltip;
}

function hideTooltip(e) {
    if (e.target.tooltipElement) {
        e.target.tooltipElement.remove();
        delete e.target.tooltipElement;
    }
}

// Initialize tooltips
setupTooltips();
