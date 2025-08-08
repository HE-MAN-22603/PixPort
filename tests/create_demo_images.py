#!/usr/bin/env python3
"""
Create placeholder demo images for PixPort
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_demo_image(filename, text, color, size=(200, 200)):
    """Create a demo image with text"""
    # Create a new image
    image = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill='white', font=font)
    
    # Save image
    image.save(filename, 'JPEG', quality=95)
    print(f"Created: {filename}")

def main():
    """Create demo images"""
    images_dir = os.path.join('app', 'static', 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Create demo images
    demo_images = [
        ('demo1.jpg', 'Demo Photo 1\nPerson Portrait', (70, 130, 180)),  # Blue
        ('demo2.jpg', 'Demo Photo 2\nPassport Style', (220, 20, 60)),    # Red
        ('demo3.jpg', 'Demo Photo 3\nProfessional', (60, 179, 113))      # Green
    ]
    
    for filename, text, color in demo_images:
        filepath = os.path.join(images_dir, filename)
        create_demo_image(filepath, text, color, (200, 250))
    
    print("✅ Demo images created successfully!")

if __name__ == '__main__':
    main()
