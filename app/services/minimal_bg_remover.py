"""
Minimal Memory Background Removal Service
Uses <100MB memory with OpenCV and computer vision techniques
Ultimate fallback for Railway 512MB deployment when AI models fail
"""

import os
import gc
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class MinimalBgRemover:
    """Ultra-lightweight background remover using only OpenCV and PIL"""
    
    def __init__(self):
        logger.info("MinimalBgRemover initialized (CPU-only, <100MB memory)")
    
    def remove_background(self, input_path: str, output_path: str) -> bool:
        """
        Remove background using computer vision techniques
        Memory usage: <100MB
        """
        try:
            # Validate input
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            file_size = os.path.getsize(input_path)
            logger.info(f"Processing with minimal memory CV: {input_path} ({file_size} bytes)")
            
            # Load image with OpenCV
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError(f"Could not read image: {input_path}")
            
            # Resize if too large (memory constraint)
            height, width = img.shape[:2]
            max_dimension = 1200  # Conservative for minimal memory
            
            if max(width, height) > max_dimension:
                scale = max_dimension / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized to {new_width}x{new_height} for minimal memory processing")
            
            # Apply advanced background removal
            result = self._advanced_bg_removal(img)
            
            # Save result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, result)
            
            logger.info(f"✅ Minimal CV background removal completed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Minimal background removal failed: {e}")
            return False
        finally:
            # Force cleanup
            gc.collect()
    
    def _advanced_bg_removal(self, img: np.ndarray) -> np.ndarray:
        """Advanced computer vision background removal"""
        try:
            height, width = img.shape[:2]
            
            # Method 1: GrabCut algorithm (most effective)
            result = self._grabcut_removal(img.copy())
            if result is not None:
                logger.info("✅ GrabCut background removal successful")
                return result
            
            # Method 2: Color-based segmentation
            result = self._color_segmentation_removal(img.copy())
            if result is not None:
                logger.info("✅ Color segmentation removal successful") 
                return result
            
            # Method 3: Edge-based removal (fallback)
            result = self._edge_based_removal(img.copy())
            logger.info("✅ Edge-based removal applied (fallback)")
            return result
            
        except Exception as e:
            logger.error(f"Advanced removal failed: {e}")
            # Ultimate fallback - return with basic transparency
            return self._basic_transparency(img)
    
    def _grabcut_removal(self, img: np.ndarray) -> Optional[np.ndarray]:
        """GrabCut algorithm for background removal"""
        try:
            height, width = img.shape[:2]
            
            # Create mask
            mask = np.zeros((height, width), np.uint8)
            
            # Define rectangle around the probable foreground
            # Use central 70% of image as probable foreground
            margin_w = int(width * 0.15)
            margin_h = int(height * 0.15)
            rect = (margin_w, margin_h, width - 2*margin_w, height - 2*margin_h)
            
            # Initialize foreground and background models
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # Apply GrabCut
            cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
            
            # Create binary mask
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # Apply mask to create transparency
            result = img.copy()
            
            # Convert to RGBA
            result_rgba = cv2.cvtColor(result, cv2.COLOR_BGR2RGBA)
            result_rgba[:, :, 3] = mask2 * 255
            
            return result_rgba
            
        except Exception as e:
            logger.warning(f"GrabCut failed: {e}")
            return None
    
    def _color_segmentation_removal(self, img: np.ndarray) -> Optional[np.ndarray]:
        """Color-based background segmentation"""
        try:
            # Convert to HSV for better color segmentation
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            height, width = img.shape[:2]
            
            # Sample corner pixels to estimate background color
            corner_samples = [
                hsv[0:10, 0:10],           # top-left
                hsv[0:10, width-10:width], # top-right
                hsv[height-10:height, 0:10], # bottom-left
                hsv[height-10:height, width-10:width] # bottom-right
            ]
            
            # Calculate average background color
            corner_pixels = np.concatenate([sample.reshape(-1, 3) for sample in corner_samples])
            bg_color = np.mean(corner_pixels, axis=0)
            
            # Create mask based on color similarity
            tolerance = 40
            lower_bg = np.array([
                max(0, int(bg_color[0]) - tolerance),
                max(0, int(bg_color[1]) - tolerance//2),
                max(0, int(bg_color[2]) - tolerance)
            ])
            upper_bg = np.array([
                min(179, int(bg_color[0]) + tolerance),
                min(255, int(bg_color[1]) + tolerance//2),
                min(255, int(bg_color[2]) + tolerance)
            ])
            
            # Create background mask
            mask = cv2.inRange(hsv, lower_bg, upper_bg)
            
            # Apply morphological operations to clean mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Invert mask (keep foreground)
            mask_inv = cv2.bitwise_not(mask)
            
            # Apply Gaussian blur to soften edges
            mask_inv = cv2.GaussianBlur(mask_inv, (3, 3), 0)
            
            # Convert to RGBA and apply mask
            result_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            result_rgba[:, :, 3] = mask_inv
            
            return result_rgba
            
        except Exception as e:
            logger.warning(f"Color segmentation failed: {e}")
            return None
    
    def _edge_based_removal(self, img: np.ndarray) -> np.ndarray:
        """Edge-based background removal"""
        try:
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Dilate edges to create connected regions
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create mask from largest contour (assumed to be main subject)
            mask = np.zeros(gray.shape, dtype=np.uint8)
            if contours:
                # Find largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                cv2.fillPoly(mask, [largest_contour], 255)
                
                # Apply morphological closing to fill gaps
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            else:
                # Fallback: assume center region is foreground
                h, w = mask.shape
                cv2.ellipse(mask, (w//2, h//2), (w//3, h//3), 0, 0, 360, 255, -1)
            
            # Smooth mask edges
            mask = cv2.GaussianBlur(mask, (5, 5), 0)
            
            # Apply mask to create RGBA image
            result_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            result_rgba[:, :, 3] = mask
            
            return result_rgba
            
        except Exception as e:
            logger.error(f"Edge-based removal failed: {e}")
            return self._basic_transparency(img)
    
    def _basic_transparency(self, img: np.ndarray) -> np.ndarray:
        """Basic transparency application (ultimate fallback)"""
        try:
            # Convert to RGBA
            result_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            
            # Apply basic transparency to edges
            height, width = img.shape[:2]
            alpha = result_rgba[:, :, 3]
            
            # Make edges more transparent
            edge_margin = min(width, height) // 20
            alpha[:edge_margin, :] = alpha[:edge_margin, :] * 0.3
            alpha[-edge_margin:, :] = alpha[-edge_margin:, :] * 0.3
            alpha[:, :edge_margin] = alpha[:, :edge_margin] * 0.3
            alpha[:, -edge_margin:] = alpha[:, -edge_margin:] * 0.3
            
            result_rgba[:, :, 3] = alpha
            return result_rgba
            
        except Exception as e:
            logger.error(f"Basic transparency failed: {e}")
            # Return original with full alpha
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    
    def change_background_color(self, input_path: str, output_path: str, bg_color: Tuple[int, int, int]) -> bool:
        """Remove background and change color in minimal memory"""
        temp_path = None
        
        try:
            # Remove background first
            temp_path = output_path.replace('.jpg', '_temp_nobg.png').replace('.jpeg', '_temp_nobg.png')
            
            if not self.remove_background(input_path, temp_path):
                return False
            
            # Apply background color
            return self._apply_background_color_cv(temp_path, output_path, bg_color)
            
        finally:
            # Cleanup
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def _apply_background_color_cv(self, transparent_path: str, output_path: str, bg_color: Tuple[int, int, int]) -> bool:
        """Apply background color using OpenCV"""
        try:
            # Load transparent image
            img = cv2.imread(transparent_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                return False
            
            if img.shape[2] == 4:  # Has alpha channel
                # Extract alpha channel
                alpha = img[:, :, 3] / 255.0
                
                # Create background
                bg_bgr = (bg_color[2], bg_color[1], bg_color[0])  # RGB to BGR
                background = np.full(img.shape[:3], bg_bgr, dtype=np.uint8)
                
                # Blend foreground with background using alpha
                for c in range(3):
                    img[:, :, c] = alpha * img[:, :, c] + (1 - alpha) * background[:, :, c]
                
                # Remove alpha channel
                result = img[:, :, :3]
            else:
                result = img
            
            # Save result
            cv2.imwrite(output_path, result, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            logger.info(f"Background color applied with CV: {bg_color}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying background color with CV: {e}")
            return False
    
    def get_memory_usage(self) -> dict:
        """Get memory usage (always minimal)"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent(),
                'model_loaded': False,  # No AI model
                'model_name': 'opencv_cv'
            }
        except Exception as e:
            return {'error': str(e)}

# Global instance  
minimal_bg_remover = MinimalBgRemover()
