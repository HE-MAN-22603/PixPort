/**
 * Print Sheet Download Dropdown Handler
 * Manages the dropdown UI for selecting download formats (PNG, JPEG, PDF)
 */

class PrintSheetDropdown {
    constructor() {
        this.dropdown = null;
        this.button = null;
        this.menu = null;
        this.isOpen = false;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        this.setupDropdownElements();
        this.bindEvents();
    }

    setupDropdownElements() {
        // Find existing download button and replace with dropdown
        const existingButton = document.querySelector('.print-btn-success');
        if (!existingButton) {
            console.warn('Print download button not found');
            return;
        }

        // Create dropdown structure
        this.createDropdownHTML(existingButton);
        
        // Cache DOM elements
        this.dropdown = document.querySelector('.print-download-dropdown');
        this.button = document.querySelector('.print-download-btn');
        this.menu = document.querySelector('.print-download-menu');
        
        if (!this.dropdown || !this.button || !this.menu) {
            console.error('Failed to create dropdown elements');
            return;
        }
    }

    createDropdownHTML(existingButton) {
        // Create the dropdown wrapper
        const dropdownHTML = `
            <div class="print-download-dropdown">
                <button class="print-download-btn" type="button">
                    <i class="fas fa-download"></i>
                    <span>Download Print Sheet</span>
                    <i class="fas fa-chevron-down dropdown-arrow"></i>
                </button>
                <div class="print-download-menu">
                    <button class="print-download-item" data-format="png" type="button">
                        <i class="fas fa-file-image"></i>
                        <div class="format-info">
                            <div class="format-name">PNG Format</div>
                            <div class="format-desc">High quality, transparent background</div>
                        </div>
                    </button>
                    <button class="print-download-item" data-format="jpeg" type="button">
                        <i class="fas fa-image"></i>
                        <div class="format-info">
                            <div class="format-name">JPEG Format</div>
                            <div class="format-desc">Smaller file size, white background</div>
                        </div>
                    </button>
                    <button class="print-download-item" data-format="pdf" type="button">
                        <i class="fas fa-file-pdf"></i>
                        <div class="format-info">
                            <div class="format-name">PDF Format</div>
                            <div class="format-desc">Print-ready document</div>
                        </div>
                    </button>
                </div>
            </div>
        `;

        // Replace existing button with dropdown
        existingButton.outerHTML = dropdownHTML;
    }

    bindEvents() {
        if (!this.button || !this.menu) return;

        // Toggle dropdown on button click
        this.button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });

        // Handle format selection
        this.menu.addEventListener('click', (e) => {
            const formatItem = e.target.closest('.print-download-item');
            if (formatItem) {
                e.stopPropagation();
                const format = formatItem.dataset.format;
                this.downloadPrintSheet(format);
                this.closeDropdown();
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeDropdown();
            }
        });
    }

    toggleDropdown() {
        if (this.isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        if (!this.dropdown || !this.menu) return;
        
        this.dropdown.classList.add('open');
        this.isOpen = true;
        
        // Focus first item for accessibility
        const firstItem = this.menu.querySelector('.print-download-item');
        if (firstItem) {
            firstItem.focus();
        }
    }

    closeDropdown() {
        if (!this.dropdown) return;
        
        this.dropdown.classList.remove('open');
        this.isOpen = false;
    }

    async downloadPrintSheet(format) {
        try {
            this.showDownloadProgress();
            
            // Get current form data
            const formData = this.getCurrentFormData();
            formData.format = format;
            
            // Make API request
            const response = await fetch('/api/download-print-sheet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Get the blob and create download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            // Create download link
            const a = document.createElement('a');
            a.href = url;
            a.download = `print_sheet.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showDownloadSuccess(format);
            
        } catch (error) {
            console.error('Download failed:', error);
            this.showDownloadError(error.message);
        } finally {
            this.hideDownloadProgress();
        }
    }

    getCurrentFormData() {
        // Get the current form data from the print layout form
        // First try to get the image from the result page
        const resultImage = document.querySelector('.result-image');
        let imageUrl = '';
        
        if (resultImage && resultImage.src) {
            imageUrl = resultImage.src;
        } else {
            // Fallback to window variable if available
            imageUrl = window.processedImageUrl || '';
        }
        
        const paperSize = document.getElementById('print-sheet-type')?.value || 'A4';
        const numPhotos = parseInt(document.getElementById('print-num-photos')?.value || '4');
        const addCutGuides = document.getElementById('print-cut-guides')?.checked || true;
        
        // Calculate grid layout from number of photos
        // This is a simple approximation - for 4 photos, use 2x2; for 6, use 2x3, etc.
        let imagesPerRow, imagesPerCol;
        
        if (numPhotos <= 4) {
            imagesPerRow = 2;
            imagesPerCol = 2;
        } else if (numPhotos <= 6) {
            imagesPerRow = 2;
            imagesPerCol = 3;
        } else if (numPhotos <= 9) {
            imagesPerRow = 3;
            imagesPerCol = 3;
        } else if (numPhotos <= 12) {
            imagesPerRow = 3;
            imagesPerCol = 4;
        } else {
            imagesPerRow = 4;
            imagesPerCol = Math.ceil(numPhotos / 4);
        }
        
        return {
            image_url: imageUrl,
            paper_size: paperSize,
            images_per_row: imagesPerRow,
            images_per_col: imagesPerCol,
            add_cut_guides: addCutGuides,
            num_photos: numPhotos
        };
    }

    showDownloadProgress() {
        // Disable the dropdown button
        if (this.button) {
            this.button.disabled = true;
            this.button.innerHTML = `
                <i class="fas fa-spinner fa-spin"></i>
                <span>Preparing Download...</span>
            `;
        }
    }

    hideDownloadProgress() {
        // Re-enable the dropdown button
        if (this.button) {
            this.button.disabled = false;
            this.button.innerHTML = `
                <i class="fas fa-download"></i>
                <span>Download Print Sheet</span>
                <i class="fas fa-chevron-down dropdown-arrow"></i>
            `;
        }
    }

    showDownloadSuccess(format) {
        // Show success message
        this.showToast(`Print sheet downloaded successfully as ${format.toUpperCase()}!`, 'success');
    }

    showDownloadError(message) {
        // Show error message
        this.showToast(`Download failed: ${message}`, 'error');
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `download-toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span class="toast-message">${message}</span>
            </div>
        `;

        // Add toast styles if not already present
        this.addToastStyles();

        document.body.appendChild(toast);

        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);

        // Hide and remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    addToastStyles() {
        // Check if styles already exist
        if (document.getElementById('toast-styles')) return;

        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .download-toast {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                transform: translateX(100%);
                transition: transform 0.3s ease;
                z-index: 1000;
                border-left: 4px solid #10b981;
                min-width: 300px;
            }
            
            .download-toast.toast-error {
                border-left-color: #ef4444;
            }
            
            .download-toast.show {
                transform: translateX(0);
            }
            
            .download-toast .toast-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .download-toast .toast-content i {
                color: #10b981;
                font-size: 18px;
            }
            
            .download-toast.toast-error .toast-content i {
                color: #ef4444;
            }
            
            .download-toast .toast-message {
                font-weight: 500;
                color: #374151;
            }
        `;

        document.head.appendChild(style);
    }
}

// Initialize the dropdown when the script loads
new PrintSheetDropdown();
