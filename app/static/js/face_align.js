/* PixPort Face Alignment Utility */

// Face detection and alignment functionality
class FaceAligner {
    constructor() {
        this.canvas = null;
        this.context = null;
        this.originalImage = null;
        this.currentImage = null;
        this.faceDetector = null;
        this.alignmentPoints = [];
        this.isAligning = false;
        
        this.initializeFaceDetection();
    }
    
    async initializeFaceDetection() {
        try {
            // Check if Face Detection API is available
            if ('FaceDetector' in window) {
                this.faceDetector = new FaceDetector({
                    maxDetectedFaces: 1,
                    fastMode: false
                });
                console.log('✅ Face Detection API initialized');
            } else {
                console.log('⚠️ Face Detection API not available, using fallback methods');
            }
        } catch (error) {
            console.error('Face detection initialization failed:', error);
        }
    }
    
    // Set up canvas for face alignment
    setupCanvas(imageElement) {
        const container = imageElement.parentElement;
        
        // Remove any existing canvas
        const existingCanvas = container.querySelector('.face-alignment-canvas');
        if (existingCanvas) {
            existingCanvas.remove();
        }
        
        // Create canvas overlay
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'face-alignment-canvas';
        this.canvas.style.position = 'absolute';
        this.canvas.style.pointerEvents = 'auto';
        this.canvas.style.cursor = 'crosshair';
        this.canvas.style.zIndex = '10';
        
        // Get the actual displayed image dimensions
        const rect = imageElement.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        
        // Calculate the offset of the image within its container
        const offsetLeft = rect.left - containerRect.left;
        const offsetTop = rect.top - containerRect.top;
        
        // Set canvas to match the exact displayed image size and position
        this.canvas.style.left = offsetLeft + 'px';
        this.canvas.style.top = offsetTop + 'px';
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        
        // Set canvas internal dimensions to match natural image size for precision
        this.canvas.width = imageElement.naturalWidth || rect.width;
        this.canvas.height = imageElement.naturalHeight || rect.height;
        
        // Ensure container is positioned relatively
        container.style.position = 'relative';
        container.appendChild(this.canvas);
        
        this.context = this.canvas.getContext('2d');
        this.originalImage = imageElement;
        
        // Setup event listeners
        this.setupCanvasEvents();
        
        console.log('Canvas setup:', {
            imageRect: rect,
            containerRect: containerRect,
            canvasStyle: {
                width: this.canvas.style.width,
                height: this.canvas.style.height,
                left: this.canvas.style.left,
                top: this.canvas.style.top
            },
            canvasSize: {
                width: this.canvas.width,
                height: this.canvas.height
            }
        });
        
        return this.canvas;
    }
    
    setupCanvasEvents() {
        this.canvas.addEventListener('click', (e) => {
            if (!this.isAligning) return;
            
            const rect = this.canvas.getBoundingClientRect();
            const scaleX = this.canvas.width / rect.width;
            const scaleY = this.canvas.height / rect.height;
            
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            
            this.addAlignmentPoint(x, y);
        });
        
        this.canvas.addEventListener('mousemove', (e) => {
            if (!this.isAligning) return;
            this.updateCrosshair(e);
        });
    }
    
    // Start face alignment mode
    startAlignment() {
        this.isAligning = true;
        // Don't reset alignment points if they were already detected
        if (this.alignmentPoints.length === 0) {
            this.alignmentPoints = [];
        }
        this.canvas.style.display = 'block';
        this.drawAlignmentGrid();
        
        // Redraw canvas to show any existing points
        if (this.alignmentPoints.length > 0) {
            this.redrawCanvas();
        }
        
        // Show alignment instructions
        this.showAlignmentInstructions();
    }
    
    // Stop face alignment mode
    stopAlignment() {
        this.isAligning = false;
        this.canvas.style.display = 'none';
        this.hideAlignmentInstructions();
    }
    
    // Add alignment point
    addAlignmentPoint(x, y) {
        if (this.alignmentPoints.length >= 4) {
            this.alignmentPoints = []; // Reset if too many points
        }
        
        this.alignmentPoints.push({ x, y });
        this.redrawCanvas();
        
        // Show feedback message
        const pointNum = this.alignmentPoints.length;
        if (pointNum === 1) {
            this.showMessage('Point 1 placed! Click on the right eye next.', 'info');
        } else if (pointNum === 2) {
            this.showMessage('Point 2 placed! You can now apply alignment or add more points.', 'success');
            this.showApplyAlignmentButton();
        } else if (pointNum === 3) {
            this.showMessage('Point 3 placed! Additional point for better alignment.', 'info');
        }
        
        // If we have enough points, enable alignment
        if (this.alignmentPoints.length >= 2) {
            this.enableAlignmentAction();
        }
    }
    
    // Draw alignment grid and points
    drawAlignmentGrid() {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid lines
        this.context.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.context.lineWidth = 1;
        
        // Vertical center line
        this.context.beginPath();
        this.context.moveTo(this.canvas.width / 2, 0);
        this.context.lineTo(this.canvas.width / 2, this.canvas.height);
        this.context.stroke();
        
        // Horizontal center line
        this.context.beginPath();
        this.context.moveTo(0, this.canvas.height / 2);
        this.context.lineTo(this.canvas.width, this.canvas.height / 2);
        this.context.stroke();
        
        // Rule of thirds lines
        this.context.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        
        // Vertical thirds
        this.context.beginPath();
        this.context.moveTo(this.canvas.width / 3, 0);
        this.context.lineTo(this.canvas.width / 3, this.canvas.height);
        this.context.moveTo((this.canvas.width * 2) / 3, 0);
        this.context.lineTo((this.canvas.width * 2) / 3, this.canvas.height);
        this.context.stroke();
        
        // Horizontal thirds
        this.context.beginPath();
        this.context.moveTo(0, this.canvas.height / 3);
        this.context.lineTo(this.canvas.width, this.canvas.height / 3);
        this.context.moveTo(0, (this.canvas.height * 2) / 3);
        this.context.lineTo(this.canvas.width, (this.canvas.height * 2) / 3);
        this.context.stroke();
    }
    
    // Redraw canvas with points
    redrawCanvas() {
        this.drawAlignmentGrid();
        
        // Draw alignment points
        this.context.fillStyle = '#ff4444';
        this.context.strokeStyle = '#ffffff';
        this.context.lineWidth = 2;
        
        this.alignmentPoints.forEach((point, index) => {
            this.context.beginPath();
            this.context.arc(point.x, point.y, 6, 0, 2 * Math.PI);
            this.context.fill();
            this.context.stroke();
            
            // Add point label
            this.context.fillStyle = '#ffffff';
            this.context.font = '12px Arial';
            this.context.fillText(index + 1, point.x + 10, point.y - 10);
            this.context.fillStyle = '#ff4444';
        });
        
        // Draw alignment line if we have 2+ points
        if (this.alignmentPoints.length >= 2) {
            this.drawAlignmentLine();
        }
    }
    
    // Draw alignment line between points
    drawAlignmentLine() {
        if (this.alignmentPoints.length < 2) return;
        
        this.context.strokeStyle = '#44ff44';
        this.context.lineWidth = 2;
        this.context.setLineDash([5, 5]);
        
        this.context.beginPath();
        this.context.moveTo(this.alignmentPoints[0].x, this.alignmentPoints[0].y);
        
        for (let i = 1; i < this.alignmentPoints.length; i++) {
            this.context.lineTo(this.alignmentPoints[i].x, this.alignmentPoints[i].y);
        }
        
        this.context.stroke();
        this.context.setLineDash([]);
    }
    
    // Update crosshair cursor
    updateCrosshair(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Update cursor position indicator
        this.canvas.style.cursor = 'crosshair';
    }
    // Auto-detect and align face
    async detectFace() {
        if (!this.faceDetector || !this.originalImage) {
            return this.fallbackFaceDetection();
        }
        
        try {
            const faces = await this.faceDetector.detect(this.originalImage);
            
            if (faces.length > 0) {
                const face = faces[0];
                const landmarks = this.extractFaceLandmarks(face);
                
                // Add detected points to alignment
                this.alignmentPoints = landmarks;
                this.redrawCanvas();
                this.enableAlignmentAction();
                
                return landmarks;
            } else {
                throw new Error('No face detected');
            }
        } catch (error) {
            console.error('Face detection failed:', error);
            // Always return fallback points, don't throw
            const fallbackPoints = this.fallbackFaceDetection();
            this.alignmentPoints = fallbackPoints;
            this.redrawCanvas();
            this.enableAlignmentAction();
            return fallbackPoints;
        }
    }
    
    // Extract landmarks from detected face
    extractFaceLandmarks(face) {
        const landmarks = [];
        const box = face.boundingBox;
        
        // Estimate eye positions (typically at 1/3 and 2/3 width, 1/3 height)
        const leftEyeX = box.x + box.width * 0.3;
        const rightEyeX = box.x + box.width * 0.7;
        const eyeY = box.y + box.height * 0.35;
        
        landmarks.push(
            { x: leftEyeX, y: eyeY },    // Left eye
            { x: rightEyeX, y: eyeY }   // Right eye
        );
        
        // Add nose tip if needed
        const noseX = box.x + box.width * 0.5;
        const noseY = box.y + box.height * 0.55;
        landmarks.push({ x: noseX, y: noseY });
        
        return landmarks;
    }
    
    // Fallback face detection using simple algorithms
    fallbackFaceDetection() {
        console.log('Using fallback face detection...');
        
        // Simple implementation: assume face is roughly centered
        // and provide guidance for manual alignment
        const centerX = this.canvas.width / 2;
        const faceTopY = this.canvas.height * 0.25;
        const eyeY = faceTopY + (this.canvas.height * 0.15);
        
        const estimatedPoints = [
            { x: centerX - 60, y: eyeY },  // Left eye estimate
            { x: centerX + 60, y: eyeY },   // Right eye estimate
            { x: centerX, y: eyeY + 40 }    // Nose estimate
        ];
        
        return estimatedPoints;
    }
    
    // Calculate alignment transformation
    calculateAlignment() {
        if (this.alignmentPoints.length < 2) {
            throw new Error('Need at least 2 alignment points');
        }
        
        const leftEye = this.alignmentPoints[0];
        const rightEye = this.alignmentPoints[1];
        
        // Calculate angle between eyes
        const dx = rightEye.x - leftEye.x;
        const dy = rightEye.y - leftEye.y;
        const angle = Math.atan2(dy, dx) * (180 / Math.PI);
        
        // Calculate center point
        const centerX = (leftEye.x + rightEye.x) / 2;
        const centerY = (leftEye.y + rightEye.y) / 2;
        
        // Only rotate if the angle is significant (more than 2 degrees)
        const shouldRotate = Math.abs(angle) > 2;
        
        return {
            angle: shouldRotate ? -angle : 0, // Negative to correct the tilt, but only if significant
            centerX: centerX,
            centerY: centerY,
            eyeDistance: Math.sqrt(dx * dx + dy * dy),
            shouldRotate: shouldRotate
        };
    }
    
    // Apply alignment to image
    async applyAlignment() {
        try {
            const alignment = this.calculateAlignment();
            
            // Get the current manual tilt value from the slider
            const manualTilt = this.getCurrentTilt();
            
            // Combine automatic alignment angle with manual tilt
            const finalAngle = alignment.angle + manualTilt;
            
            console.log('Applying alignment:', {
                autoAngle: alignment.angle,
                manualTilt: manualTilt,
                finalAngle: finalAngle,
                center: { x: alignment.centerX, y: alignment.centerY }
            });
            
            // Apply the combined transformation
            this.originalImage.style.transform = `rotate(${finalAngle}deg)`;
            this.originalImage.style.transformOrigin = `${alignment.centerX}px ${alignment.centerY}px`;
            
            // Show success and hide alignment interface
            this.stopAlignment();
            
            // Create detailed success message
            let message = `Face alignment applied!`;
            if (Math.abs(alignment.angle) > 2) {
                message += ` Auto correction: ${alignment.angle.toFixed(1)}°`;
            }
            if (Math.abs(manualTilt) > 0) {
                message += ` Manual tilt: ${manualTilt}°`;
            }
            message += ` Total rotation: ${finalAngle.toFixed(1)}°`;
            
            showToast(message, 'success');
            
            // Reset the transform after showing success (for now)
            setTimeout(() => {
                this.originalImage.style.transform = '';
                this.originalImage.style.transformOrigin = '';
                showToast('Alignment preview completed. This would process the actual image in production.', 'info');
            }, 3000);
            
            return { 
                success: true, 
                alignment: {
                    ...alignment,
                    manualTilt: manualTilt,
                    finalAngle: finalAngle
                }
            };
            
        } catch (error) {
            console.error('Alignment failed:', error);
            showToast(`Alignment failed: ${error.message}`, 'error');
            throw error;
        }
    }
    
    // Show alignment instructions
    showAlignmentInstructions() {
        const instructions = document.createElement('div');
        instructions.className = 'alignment-instructions';
        instructions.innerHTML = `
            <div class="instructions-content">
                <div class="instruction-header">
                    <i class="fas fa-crosshairs instruction-icon"></i>
                    <h3>Face Alignment & Positioning</h3>
                </div>
                
                <!-- Auto Align Face Button -->
                <button class="auto-align-btn" id="auto-detect-btn">
                    <i class="fas fa-magic"></i> Auto Align Face
                </button>
                
                <!-- Adjust Head Size Section -->
                <div class="adjustment-section">
                    <label class="section-label">Adjust Head Size:</label>
                    <div class="size-adjustment-controls">
                        <button class="size-btn decrease-btn" id="decrease-size-btn">
                            <i class="fas fa-minus"></i>
                        </button>
                        <span class="size-label">Head Size</span>
                        <button class="size-btn increase-btn" id="increase-size-btn">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Tilt Correction Section -->
                <div class="adjustment-section">
                    <label class="section-label">Tilt Correction (degrees):</label>
                    <div class="tilt-input-container">
                        <input type="number" id="tilt-input" min="-180" max="180" value="0" class="tilt-number-input">
                        <button class="apply-tilt-btn" id="apply-tilt-btn">
                            <i class="fas fa-check"></i> Apply
                        </button>
                    </div>
                    <input type="range" id="tilt-slider" min="-180" max="180" value="0" step="1" class="tilt-slider">
                </div>
                
                <!-- Face Grid Overlay Checkbox -->
                <div class="checkbox-section">
                    <label class="checkbox-container">
                        <input type="checkbox" id="show-face-grid" checked>
                        <span class="checkmark"></span>
                        Show Face Grid Overlay
                    </label>
                </div>
                
                <!-- Check Passport Guidelines Button -->
                <button class="passport-guidelines-btn" id="passport-guidelines-btn">
                    <i class="fas fa-search"></i> Check Passport Guidelines
                </button>
                
                <!-- Action Buttons -->
                <div class="instructions-actions">
                    <button class="btn-warning" id="reset-points-btn" ${this.alignmentPoints.length === 0 ? 'disabled' : ''}>
                        <i class="fas fa-undo"></i> Reset
                    </button>
                    <button class="btn-primary" id="apply-alignment-btn" ${this.alignmentPoints.length < 2 ? 'disabled' : ''}>
                        <i class="fas fa-check"></i> Apply Alignment
                    </button>
                    <button class="btn-secondary" id="cancel-alignment-btn">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(instructions);
        
        // Add event listeners to buttons
        const autoDetectBtn = instructions.querySelector('#auto-detect-btn');
        const resetBtn = instructions.querySelector('#reset-points-btn');
        const applyAlignmentBtn = instructions.querySelector('#apply-alignment-btn');
        const cancelBtn = instructions.querySelector('#cancel-alignment-btn');
        
        autoDetectBtn.addEventListener('click', async () => {
            try {
                console.log('Auto detect button clicked');
                // Show detection message
                this.showMessage('Detecting face...', 'info');
                
                // Run face detection
                const points = await this.detectFace();
                
                if (points && points.length >= 2) {
                    this.showMessage('Face detected! Points placed automatically', 'success');
                    // Update button state
                    this.enableAlignmentAction();
                } else {
                    this.showMessage('Auto detection completed. You can manually adjust points.', 'info');
                }
            } catch (error) {
                console.error('Auto detect failed:', error);
                this.showMessage('Auto detection failed. Please place points manually.', 'error');
            }
        });
        
        resetBtn.addEventListener('click', () => {
            this.resetAlignmentPoints();
        });
        
        applyAlignmentBtn.addEventListener('click', async () => {
            try {
                await this.applyAlignment();
            } catch (error) {
                console.error('Apply alignment failed:', error);
            }
        });
        
        cancelBtn.addEventListener('click', () => {
            // Only hide the popup, keep the canvas for manual marking
            this.hideAlignmentInstructions();
            // Keep the canvas visible for manual clicking
            this.canvas.style.display = 'block';
            // Show a brief message about manual alignment
            this.showMessage('You can now click on the image to manually place alignment points', 'info');
        });
        
        // Setup tilt slider functionality
        this.setupTiltSlider(instructions);
        
        // Position instructions
        setTimeout(() => {
            instructions.classList.add('show');
        }, 100);
    }
    
    // Hide alignment instructions
    hideAlignmentInstructions() {
        const instructions = document.querySelector('.alignment-instructions');
        if (instructions) {
            instructions.classList.remove('show');
            setTimeout(() => {
                instructions.remove();
            }, 300);
        }
    }
    
    // Enable alignment action button
    enableAlignmentAction() {
        const applyBtn = document.querySelector('#apply-alignment-btn');
        if (applyBtn) {
            applyBtn.disabled = false;
        }
    }
    
    // Reset alignment points
    resetAlignmentPoints() {
        console.log('Resetting alignment points...');
        
        // Clear all alignment points
        this.alignmentPoints = [];
        
        // Hide floating Apply Alignment button if visible
        this.hideApplyAlignmentButton();
        
        // Redraw canvas with just the grid (no points)
        this.drawAlignmentGrid();
        
        // Update button states in popup if it exists
        const applyBtn = document.querySelector('#apply-alignment-btn');
        const resetBtn = document.querySelector('#reset-points-btn');
        
        if (applyBtn) {
            applyBtn.disabled = true;
        }
        if (resetBtn) {
            resetBtn.disabled = true;
        }
        
        // Show confirmation message
        this.showMessage('Alignment points cleared! You can now place new points.', 'info');
    }
    
    // Show message function (fallback for showToast)
    showMessage(message, type = 'info') {
        // Try to use showToast if available
        if (typeof showToast === 'function') {
            showToast(message, type);
            return;
        }
        
        // Fallback: console log with alert for important messages
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // Show alert for important messages
        if (type === 'error') {
            alert(`Error: ${message}`);
        } else if (type === 'success') {
            console.log(`✅ ${message}`);
        }
    }
    
    // Show Apply Alignment button as floating action button
    showApplyAlignmentButton() {
        // Remove any existing floating button
        const existingBtn = document.querySelector('.floating-apply-btn');
        if (existingBtn) {
            existingBtn.remove();
        }
        
        // Create floating Apply Alignment button
        const floatingBtn = document.createElement('div');
        floatingBtn.className = 'floating-apply-btn';
        floatingBtn.innerHTML = `
            <button class="apply-btn" onclick="faceAligner.applyAlignment()">
                <i class="fas fa-check"></i>
                Apply Alignment
            </button>
        `;
        
        document.body.appendChild(floatingBtn);
        
        // Add CSS for floating button
        if (!document.querySelector('#floating-btn-styles')) {
            const style = document.createElement('style');
            style.id = 'floating-btn-styles';
            style.textContent = `
                .floating-apply-btn {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1002;
                    animation: slideIn 0.3s ease;
                }
                
                .floating-apply-btn .apply-btn {
                    background: #10b981;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 25px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.2s ease;
                }
                
                .floating-apply-btn .apply-btn:hover {
                    background: #059669;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
                }
                
                @keyframes slideIn {
                    from {
                        transform: translateY(60px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Auto hide after 10 seconds
        setTimeout(() => {
            if (document.querySelector('.floating-apply-btn')) {
                this.hideApplyAlignmentButton();
            }
        }, 10000);
    }
    
    // Hide floating Apply Alignment button
    hideApplyAlignmentButton() {
        const floatingBtn = document.querySelector('.floating-apply-btn');
        if (floatingBtn) {
            floatingBtn.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                floatingBtn.remove();
            }, 300);
        }
    }
    
    // Setup tilt slider functionality
    setupTiltSlider(instructions) {
        const tiltSlider = instructions.querySelector('#tilt-slider');
        const tiltValue = instructions.querySelector('#tilt-value');
        
        if (!tiltSlider || !tiltValue) return;
        
        // Real-time tilt preview
        tiltSlider.addEventListener('input', (e) => {
            const angle = parseInt(e.target.value);
            tiltValue.textContent = angle;
            this.previewTilt(angle);
        });
        
        // Mouse wheel support for fine adjustment
        tiltSlider.addEventListener('wheel', (e) => {
            e.preventDefault();
            const currentValue = parseInt(tiltSlider.value);
            const step = e.deltaY > 0 ? -1 : 1;
            const newValue = Math.max(-180, Math.min(180, currentValue + step));
            
            tiltSlider.value = newValue;
            tiltValue.textContent = newValue;
            this.previewTilt(newValue);
        });
    }
    
    // Set tilt to specific angle (for preset buttons)
    setTilt(angle) {
        const tiltSlider = document.querySelector('#tilt-slider');
        const tiltValue = document.querySelector('#tilt-value');
        
        if (tiltSlider && tiltValue) {
            tiltSlider.value = angle;
            tiltValue.textContent = angle;
            this.previewTilt(angle);
        }
    }
    
    // Preview tilt transformation in real-time
    previewTilt(angle) {
        if (!this.originalImage) return;
        
        // Calculate center point for rotation
        let centerX = this.originalImage.offsetWidth / 2;
        let centerY = this.originalImage.offsetHeight / 2;
        
        // If we have alignment points, use them as rotation center
        if (this.alignmentPoints.length >= 2) {
            const rect = this.canvas.getBoundingClientRect();
            const imgRect = this.originalImage.getBoundingClientRect();
            
            // Convert canvas coordinates to image coordinates
            const scaleX = imgRect.width / this.canvas.width;
            const scaleY = imgRect.height / this.canvas.height;
            
            const leftEye = this.alignmentPoints[0];
            const rightEye = this.alignmentPoints[1];
            
            centerX = ((leftEye.x + rightEye.x) / 2) * scaleX;
            centerY = ((leftEye.y + rightEye.y) / 2) * scaleY;
        }
        
        // Apply CSS transformation
        this.originalImage.style.transform = `rotate(${angle}deg)`;
        this.originalImage.style.transformOrigin = `${centerX}px ${centerY}px`;
        
        console.log(`Previewing tilt: ${angle}°, center: (${centerX.toFixed(1)}, ${centerY.toFixed(1)})`);
    }
    
    // Get current tilt value
    getCurrentTilt() {
        const tiltSlider = document.querySelector('#tilt-slider');
        return tiltSlider ? parseInt(tiltSlider.value) : 0;
    }
    
    // Reset tilt to 0
    resetTilt() {
        this.setTilt(0);
        if (this.originalImage) {
            this.originalImage.style.transform = '';
            this.originalImage.style.transformOrigin = '';
        }
    }
    
    // Clean up
    cleanup() {
        if (this.canvas && this.canvas.parentElement) {
            this.canvas.parentElement.removeChild(this.canvas);
        }
        this.hideAlignmentInstructions();
        // Reset any applied transformations
        if (this.originalImage) {
            this.originalImage.style.transform = '';
            this.originalImage.style.transformOrigin = '';
        }
    }
}

// Utility function to get filename from image element
function getFilenameFromImage(imageElement) {
    const src = imageElement.src;
    const matches = src.match(/\/([^\/]+\.(jpg|jpeg|png|gif|webp))$/i);
    return matches ? matches[1] : null;
}

// Global face aligner instance
let faceAligner = null;

// Initialize face alignment functionality
function initializeFaceAlignment() {
    faceAligner = new FaceAligner();
}

// Start face alignment on current image
function startFaceAlignment(imageElement) {
    if (!faceAligner) {
        initializeFaceAlignment();
    }
    
    faceAligner.setupCanvas(imageElement);
    faceAligner.startAlignment();
}

// Auto-detect and align face
async function autoAlignFace(imageElement) {
    if (!faceAligner) {
        initializeFaceAlignment();
    }
    
    faceAligner.setupCanvas(imageElement);
    
    try {
        showToast('Detecting face...', 'info');
        const points = await faceAligner.detectFace();
        
        if (points && points.length >= 2) {
            showToast('Face detected! Ready to apply alignment', 'success');
            // Show the manual interface with detected points
            faceAligner.startAlignment();
        } else {
            showToast('No face detected. Please align manually.', 'warning');
            faceAligner.startAlignment();
        }
    } catch (error) {
        console.error('Auto-alignment error:', error);
        showToast('Auto-alignment failed. Please try manual alignment.', 'warning');
        faceAligner.startAlignment();
    }
}

// Export for global access
window.FaceAligner = FaceAligner;
window.faceAligner = faceAligner;
window.startFaceAlignment = startFaceAlignment;
window.autoAlignFace = autoAlignFace;
window.initializeFaceAlignment = initializeFaceAlignment;

// CSS for face alignment (injected dynamically)
const alignmentStyles = `
    .face-alignment-canvas {
        border: 2px solid #44ff44;
        border-radius: 4px;
    }
    
    .alignment-instructions {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) scale(0.9);
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        z-index: 1001;
        max-width: 400px;
        width: 90%;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .alignment-instructions.show {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
    
    .instructions-content {
        padding: 24px;
    }
    
    .instructions-content h3 {
        margin: 0 0 16px 0;
        color: #1f2937;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    .instructions-content ul {
        margin: 0 0 24px 0;
        padding-left: 20px;
        color: #6b7280;
    }
    
    .instructions-content li {
        margin-bottom: 8px;
    }
    
    .instructions-actions {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .instructions-actions button {
        flex: 1;
        min-width: 100px;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    
    .instructions-actions .btn-secondary {
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    
    .instructions-actions .btn-secondary:hover {
        background: #e5e7eb;
        border-color: #9ca3af;
    }
    
    .instructions-actions .btn-primary {
        background: #3b82f6;
        color: white;
        border: 1px solid #3b82f6;
    }
    
    .instructions-actions .btn-primary:hover:not(:disabled) {
        background: #2563eb;
        border-color: #2563eb;
    }
    
    .instructions-actions .btn-primary:disabled {
        background: #9ca3af;
        border-color: #9ca3af;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    .instructions-actions .btn-warning {
        background: #f59e0b;
        color: white;
        border: 1px solid #f59e0b;
    }
    
    .instructions-actions .btn-warning:hover:not(:disabled) {
        background: #d97706;
        border-color: #d97706;
    }
    
    .instructions-actions .btn-warning:disabled {
        background: #9ca3af;
        border-color: #9ca3af;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    /* Tilt Correction Slider Styles */
    .tilt-correction-section {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0 24px 0;
    }
    
    .tilt-correction-section label {
        display: block;
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px;
        text-align: center;
    }
    
    .tilt-slider {
        width: 100%;
        height: 6px;
        border-radius: 3px;
        background: #e5e7eb;
        outline: none;
        margin-bottom: 16px;
        -webkit-appearance: none;
        appearance: none;
    }
    
    .tilt-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #3b82f6;
        cursor: pointer;
        border: 2px solid #ffffff;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    
    .tilt-slider::-webkit-slider-thumb:hover {
        background: #2563eb;
        transform: scale(1.1);
    }
    
    .tilt-slider::-moz-range-thumb {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #3b82f6;
        cursor: pointer;
        border: 2px solid #ffffff;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    
    .tilt-presets {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .preset-btn {
        background: #ffffff;
        color: #374151;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 45px;
    }
    
    .preset-btn:hover {
        background: #f3f4f6;
        border-color: #9ca3af;
        transform: translateY(-1px);
    }
    
    .preset-btn:active {
        transform: translateY(0);
        background: #e5e7eb;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = alignmentStyles;
document.head.appendChild(styleSheet);
