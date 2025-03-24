import os
import numpy as np
import cv2
import matplotlib.pyplot as plt

def generate_heatmap(image, region_type="decay"):
    """
    Generate a simple heatmap visualization for dental issues.
    
    Args:
        image: Input image
        region_type: Type of dental issue to visualize
        
    Returns:
        Image with overlay heatmap
    """
    # Make sure image is in the right format
    if image.max() > 1.0:
        normalized_image = image / 255.0
    else:
        normalized_image = image.copy()
    
    # Create a blank heatmap of the same size as the image
    heatmap = np.zeros((image.shape[0], image.shape[1]), dtype=np.float32)
    
    # Different regions for different issues
    h, w = image.shape[:2]
    
    if region_type == "decay":
        # Simulate decay in certain areas (e.g., centers of teeth)
        cx, cy = w // 2, h // 2
        for i in range(3):
            # Add some random spots
            x = np.random.randint(w//4, 3*w//4)
            y = np.random.randint(h//4, 3*h//4)
            radius = np.random.randint(5, 15)
            
            # Create a circular heatmap
            y_indices, x_indices = np.ogrid[:h, :w]
            dist = np.sqrt((x_indices - x)**2 + (y_indices - y)**2)
            mask = dist <= radius
            heatmap[mask] = np.maximum(heatmap[mask], 1 - dist[mask]/radius)
    
    elif region_type == "plaque":
        # Simulate plaque around gum lines
        for i in range(5):
            x = np.random.randint(w//4, 3*w//4)
            y = h // 2 + np.random.randint(-10, 10)
            width = np.random.randint(20, 40)
            height = np.random.randint(5, 10)
            
            # Create a rectangular region
            y_indices, x_indices = np.ogrid[:h, :w]
            mask = ((x_indices > x - width//2) & (x_indices < x + width//2) & 
                   (y_indices > y - height//2) & (y_indices < y + height//2))
            heatmap[mask] = 1.0
    
    elif region_type == "cavity":
        # Simulate small cavity spots
        for i in range(2):
            x = np.random.randint(w//4, 3*w//4)
            y = np.random.randint(h//4, 3*h//4)
            radius = np.random.randint(3, 8)
            
            # Create a small circular spot
            y_indices, x_indices = np.ogrid[:h, :w]
            dist = np.sqrt((x_indices - x)**2 + (y_indices - y)**2)
            mask = dist <= radius
            heatmap[mask] = 1.0
    
    else:  # gingivitis
        # Simulate inflammation along gum line
        gum_y = h // 2
        thickness = h // 10
        
        # Create a band along the center
        y_indices, x_indices = np.ogrid[:h, :w]
        mask = (y_indices > gum_y - thickness//2) & (y_indices < gum_y + thickness//2)
        
        # Add some randomness to the intensity
        heatmap[mask] = np.random.uniform(0.5, 1.0, size=(np.sum(mask),))
    
    # Resize heatmap to match the image size if needed
    heatmap = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
    
    # Apply colormap
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    
    # Convert image to uint8 if it's float
    if normalized_image.dtype != np.uint8:
        img_uint8 = (normalized_image * 255).astype(np.uint8)
    else:
        img_uint8 = normalized_image
    
    # Make sure the image is RGB
    if len(img_uint8.shape) == 2:
        img_rgb = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2RGB)
    else:
        img_rgb = img_uint8
    
    # Superimpose heatmap on original image
    return cv2.addWeighted(img_rgb, 0.7, heatmap_colored, 0.3, 0)

def analyze_tooth_color(image):
    """
    Analyze the color distribution in the image to identify potential dental issues.
    
    Args:
        image: Input image
        
    Returns:
        Dictionary with tooth color analysis results
    """
    # Convert to HSV for better color analysis
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Extract channels
    h, s, v = cv2.split(hsv)
    
    # Calculate statistics
    avg_hue = np.mean(h)
    avg_saturation = np.mean(s)
    avg_value = np.mean(v)
    
    # Detect yellow tint (potential plaque/tartar)
    # Yellow in HSV has hue values around 20-40
    yellow_mask = ((h > 20) & (h < 40) & (s > 100))
    yellow_ratio = np.sum(yellow_mask) / (image.shape[0] * image.shape[1])
    
    # Detect dark spots (potential cavities)
    dark_mask = (v < 80)
    dark_ratio = np.sum(dark_mask) / (image.shape[0] * image.shape[1])
    
    # Detect redness (potential gingivitis)
    # Red in HSV has hue values around 0-10 or 170-180
    red_mask = (((h < 10) | (h > 170)) & (s > 100))
    red_ratio = np.sum(red_mask) / (image.shape[0] * image.shape[1])
    
    return {
        "yellow_ratio": yellow_ratio,
        "dark_ratio": dark_ratio,
        "red_ratio": red_ratio,
        "avg_brightness": avg_value
    }

def enhance_dental_image(image):
    """
    Enhance a dental image for better visibility.
    
    Args:
        image: Input image
        
    Returns:
        Enhanced image
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    
    # Split channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge channels
    merged = cv2.merge((cl, a, b))
    
    # Convert back to RGB
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    
    return enhanced
