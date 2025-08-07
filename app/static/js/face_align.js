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
        
        // Create canvas overlay
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'face-alignment-canvas';
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.pointerEvents = 'auto';
        this.canvas.style.cursor = 'crosshair';
        this.canvas.style.zIndex = '10';
        
        // Set canvas dimensions
        const rect = imageElement.getBoundingClientRect();
        this.canvas.width = imageElement.naturalWidth;
        this.canvas.height = imageElement.naturalHeight;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        
        container.style.position = 'relative';
        container.appendChild(this.canvas);
        
        this.context = this.canvas.getContext('2d');
        this.originalImage = imageElement;
        
        // Setup event listeners
        this.setupCanvasEvents();
        
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
        this.alignmentPoints = [];
        this.canvas.style.display = 'block';
        this.drawAlignmentGrid();
        
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
    
    // Automatic face detection
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
            return this.fallbackFaceDetection();
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
            { x: centerX + 60, y: eyeY }   // Right eye estimate
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
        
        return {
            angle: -angle, // Negative to correct the tilt
            centerX: centerX,
            centerY: centerY,
            eyeDistance: Math.sqrt(dx * dx + dy * dy)
        };
    }
    
    // Apply alignment to image
    async applyAlignment() {
        try {
            const alignment = this.calculateAlignment();
            
            // Send alignment data to backend
            const response = await fetch('/api/align-face', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: getFilenameFromImage(this.originalImage),
                    alignment: alignment,
                    points: this.alignmentPoints
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Update image with aligned version
                this.originalImage.src = result.aligned_image_url + '?t=' + Date.now();
                this.stopAlignment();
                
                showToast('Face alignment applied successfully!', 'success');
                
                return result;
            } else {
                throw new Error(result.message || 'Alignment failed');
            }
            
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
                <h3>Face Alignment</h3>
                <ul>
                    <li>Click on the left eye, then the right eye</li>
                    <li>Add additional points for better alignment (nose, mouth)</li>
                    <li>Use the grid lines to ensure proper positioning</li>
                    <li>Click "Apply Alignment" when ready</li>
                </ul>
                <div class="instructions-actions">
                    <button class="btn-secondary" onclick="faceAligner.detectFace()">
                        <i class="fas fa-search"></i> Auto Detect
                    </button>
                    <button class="btn-primary" onclick="faceAligner.applyAlignment()" ${this.alignmentPoints.length < 2 ? 'disabled' : ''}>
                        <i class="fas fa-check"></i> Apply Alignment
                    </button>
                    <button class="btn-secondary" onclick="faceAligner.stopAlignment()">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(instructions);
        
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
        const applyBtn = document.querySelector('.alignment-instructions button[onclick*="applyAlignment"]');
        if (applyBtn) {
            applyBtn.disabled = false;
        }
    }
    
    // Clean up
    cleanup() {
        if (this.canvas && this.canvas.parentElement) {
            this.canvas.parentElement.removeChild(this.canvas);
        }
        this.hideAlignmentInstructions();
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
            showToast('Face detected! Applying alignment...', 'info');
            await faceAligner.applyAlignment();
        } else {
            showToast('No face detected. Please align manually.', 'warning');
            faceAligner.startAlignment();
        }
    } catch (error) {
        showToast(`Auto-alignment failed: ${error.message}`, 'error');
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
        background: var(--bg-color);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        z-index: 1000;
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
        color: var(--text-color);
        font-size: 1.25rem;
    }
    
    .instructions-content ul {
        margin: 0 0 24px 0;
        padding-left: 20px;
        color: var(--text-secondary);
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
        min-width: 120px;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = alignmentStyles;
document.head.appendChild(styleSheet);
