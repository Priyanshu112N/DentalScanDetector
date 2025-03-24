import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from model_utils import generate_heatmap, analyze_tooth_color, enhance_dental_image

def preprocess_image(image, target_size=(224, 224)):
    """
    Preprocess the input image for the dental decay detection model.

    Args:
        image: Input image as a numpy array (RGB format)
        target_size: Target size for model input (default: 224x224)

    Returns:
        Preprocessed image ready for model input
    """
    # Convert to RGB if needed
    if len(image.shape) == 3 and image.shape[2] == 3:
        # Already in RGB format
        rgb_image = image
    else:
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize image to target size
    resized_image = cv2.resize(rgb_image, target_size, interpolation=cv2.INTER_AREA)
    
    # Basic preprocessing
    # Use our enhance_dental_image function from model_utils
    enhanced_image = enhance_dental_image(resized_image)
    
    # Normalize pixel values
    normalized_image = enhanced_image.astype(np.float32) / 255.0
    
    return normalized_image

def annotate_image(image, detection_results):
    """
    Annotate the input image with detection results.

    Args:
        image: Original input image
        detection_results: Dictionary containing detection results

    Returns:
        Annotated image with detection highlights
    """
    # Create a copy to avoid modifying the original
    image_copy = np.copy(image)
    
    # Make sure the image is in the right format
    if image_copy.max() <= 1.0:
        image_copy = (image_copy * 255).astype(np.uint8)
    
    # Only process significant issues (> 40% confidence)
    significant_issues = {k: v for k, v in detection_results.items() if v > 40}
    
    # If no significant issues, return the original image
    if not significant_issues:
        return image_copy
    
    # Create a composite image with overlays for each issue
    result_image = image_copy.copy()
    
    # Process each issue type and overlay heatmaps
    for issue, confidence in significant_issues.items():
        if issue == "Decay":
            # Apply decay heatmap
            overlay = generate_heatmap(image_copy, "decay")
            # Blend with original based on confidence
            alpha = confidence / 200  # Scale down to avoid too strong overlay
            result_image = cv2.addWeighted(result_image, 1 - alpha, overlay, alpha, 0)
            
        elif issue == "Plaque":
            # Apply plaque heatmap
            overlay = generate_heatmap(image_copy, "plaque") 
            alpha = confidence / 200
            result_image = cv2.addWeighted(result_image, 1 - alpha, overlay, alpha, 0)
            
        elif issue == "Cavity":
            # Apply cavity heatmap
            overlay = generate_heatmap(image_copy, "cavity")
            alpha = confidence / 200
            result_image = cv2.addWeighted(result_image, 1 - alpha, overlay, alpha, 0)
            
        elif issue == "Gingivitis":
            # Apply gingivitis heatmap
            overlay = generate_heatmap(image_copy, "gingivitis")
            alpha = confidence / 200
            result_image = cv2.addWeighted(result_image, 1 - alpha, overlay, alpha, 0)
    
    # Convert to PIL for adding text labels
    pil_image = Image.fromarray(result_image)
    draw = ImageDraw.Draw(pil_image)
    
    # Add text labels for each issue
    height = 30
    for issue, confidence in significant_issues.items():
        text = f"{issue}: {confidence:.1f}%"
        # Add with black outline for visibility
        draw.text((10, height), text, fill=(0, 0, 0), stroke_width=3, stroke_fill=(255, 255, 255))
        height += 25
    
    # Convert back to numpy array
    return np.array(pil_image)

def detect_teeth_region(image):
    """
    Attempt to detect the region containing teeth in the image.
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Coordinates of the region (x, y, w, h) or None if not detected
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Apply histogram equalization
    gray = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect edges
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size
    min_area = image.shape[0] * image.shape[1] * 0.1  # Minimum 10% of image
    large_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    if large_contours:
        # Find the largest contour
        largest_contour = max(large_contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h)
    
    # If no suitable contour found, return the central region
    h, w = image.shape[:2]
    return (w//4, h//4, w//2, h//2)
