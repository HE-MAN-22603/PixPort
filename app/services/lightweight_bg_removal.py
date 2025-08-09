"""
Lightweight Background Removal Service
Uses OpenCV and computer vision techniques instead of heavy AI models
Optimized for Railway's 512MB memory constraint
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import logging

logger = logging.getLogger(__name__)

class LightweightBackgroundRemover:
    """Memory-efficient background removal using traditional CV techniques"""
    
    def __init__(self):
        self.initialized = True
        logger.info("Lightweight Background Remover initialized")
    
    def remove_background(self, input_path: str, output_path: str, method: str = 'auto') -> bool:
        """
        Remove background using lightweight computer vision techniques
        
        Args:
            input_path: Path to input image
            output_path: Path to save output image
            method: 'auto', 'grabcut', 'contour', 'edge', 'threshold'
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info(f"Processing {input_path} with method: {method}")
            
            # Load image with OpenCV
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError(f"Could not load image: {input_path}")
            
            # Convert to RGB (OpenCV uses BGR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width = img_rgb.shape[:2]
            
            # Choose best method based on image characteristics
            if method == 'auto':
                method = self._select_best_method(img_rgb)
                logger.info(f"Auto-selected method: {method}")
            
            # Apply selected background removal method
            mask = self._create_mask(img_rgb, method)
            
            # Apply mask to create transparent background
            result = self._apply_mask(img_rgb, mask)
            
            # Save result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self._save_with_transparency(result, output_path)
            
            logger.info(f"Background removal completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Lightweight background removal failed: {e}")
            return False
    
    def _select_best_method(self, img: np.ndarray) -> str:
        """Select the best method based on image characteristics"""
        height, width = img.shape[:2]
        
        # Analyze image to choose best method
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Check edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (height * width)
        
        # Check color distribution
        hist_r = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([img], [2], None, [256], [0, 256])
        
        # Check if background is likely uniform (high peak in histograms)
        r_peak = np.max(hist_r) / (height * width)
        g_peak = np.max(hist_g) / (height * width)
        b_peak = np.max(hist_b) / (height * width)
        avg_peak = (r_peak + g_peak + b_peak) / 3
        
        # Decision logic
        if avg_peak > 0.3:  # Uniform background
            return 'threshold'
        elif edge_density > 0.1:  # High edge density
            return 'grabcut'
        else:
            return 'contour'
    
    def _create_mask(self, img: np.ndarray, method: str) -> np.ndarray:
        """Create mask using specified method"""
        height, width = img.shape[:2]
        
        if method == 'grabcut':
            return self._grabcut_mask(img)
        elif method == 'contour':
            return self._contour_mask(img)
        elif method == 'edge':
            return self._edge_mask(img)
        elif method == 'threshold':
            return self._threshold_mask(img)
        else:
            # Default to threshold method
            return self._threshold_mask(img)
    
    def _grabcut_mask(self, img: np.ndarray) -> np.ndarray:
        """GrabCut algorithm for background removal"""
        height, width = img.shape[:2]
        
        # Create initial mask (assume center contains foreground)
        mask = np.zeros((height, width), np.uint8)
        
        # Define rectangle around likely foreground (center 60% of image)
        margin_h = int(height * 0.2)
        margin_w = int(width * 0.2)
        rect = (margin_w, margin_h, width - 2*margin_w, height - 2*margin_h)
        
        # Initialize background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        # Apply GrabCut
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 3, cv2.GC_INIT_WITH_RECT)
        
        # Create final mask
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        
        return mask2 * 255
    
    def _contour_mask(self, img: np.ndarray) -> np.ndarray:
        """Contour-based background removal"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 30, 80)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create mask
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        if contours:
            # Find largest contour (likely the main subject)
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.fillPoly(mask, [largest_contour], 255)
        
        return mask
    
    def _edge_mask(self, img: np.ndarray) -> np.ndarray:
        """Edge-based background removal"""
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Edge detection
        edges = cv2.Canny(filtered, 50, 150, apertureSize=3)
        
        # Dilate edges to close gaps
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Fill enclosed areas
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter small contours
                cv2.fillPoly(mask, [contour], 255)
        
        return mask
    
    def _threshold_mask(self, img: np.ndarray) -> np.ndarray:
        """Threshold-based background removal (good for uniform backgrounds)"""
        # Convert to HSV for better color separation
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        
        # Calculate background color (assume corners are background)
        height, width = img.shape[:2]
        corner_size = min(50, height//10, width//10)
        
        # Sample corner pixels
        corners = [
            hsv[:corner_size, :corner_size],  # Top-left
            hsv[:corner_size, -corner_size:],  # Top-right
            hsv[-corner_size:, :corner_size],  # Bottom-left
            hsv[-corner_size:, -corner_size:]  # Bottom-right
        ]
        
        # Calculate average background color
        bg_colors = []
        for corner in corners:
            avg_color = np.mean(corner, axis=(0, 1))
            bg_colors.append(avg_color)
        
        bg_color = np.mean(bg_colors, axis=0)
        
        # Create mask based on distance from background color
        distances = np.sqrt(np.sum((hsv - bg_color) ** 2, axis=2))
        
        # Threshold (adjust based on image characteristics)
        threshold = np.std(distances) * 1.5
        mask = (distances > threshold).astype(np.uint8) * 255
        
        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def _apply_mask(self, img: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Apply mask to image with smooth edges"""
        # Smooth the mask for better edge quality
        mask_smooth = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Normalize mask to 0-1 range
        mask_norm = mask_smooth.astype(np.float32) / 255.0
        
        # Create RGBA image
        result = np.zeros((*img.shape[:2], 4), dtype=np.uint8)
        result[:, :, :3] = img  # RGB channels
        result[:, :, 3] = (mask_norm * 255).astype(np.uint8)  # Alpha channel
        
        return result
    
    def _save_with_transparency(self, img_rgba: np.ndarray, output_path: str):
        """Save image with transparency"""
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(img_rgba, 'RGBA')
        
        # Save as PNG (supports transparency)
        pil_image.save(output_path, 'PNG', optimize=True)

# Global instance
lightweight_remover = LightweightBackgroundRemover()
