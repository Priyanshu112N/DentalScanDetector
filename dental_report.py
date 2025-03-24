import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64

def generate_health_score(detection_results):
    """
    Generate an overall dental health score based on detection results.
    
    Args:
        detection_results: Dictionary with detection results
        
    Returns:
        score: 0-100 health score
        status: Text status of dental health
        color: Color representing the health status
    """
    if not detection_results:
        return None, None, None
    
    # Calculate base score (100 - average of issues)
    issue_values = list(detection_results.values())
    base_score = 100 - np.mean(issue_values)
    
    # Adjust score based on severity of specific issues
    decay_penalty = 0.5 * detection_results.get("Decay", 0)
    cavity_penalty = 0.7 * detection_results.get("Cavity", 0)
    plaque_penalty = 0.3 * detection_results.get("Plaque", 0)
    
    # Calculate final score
    final_score = max(0, min(100, base_score - (decay_penalty + cavity_penalty + plaque_penalty) / 3))
    final_score = round(final_score, 1)
    
    # Determine status and color based on score
    if final_score >= 85:
        status = "Excellent"
        color = "#2ecc71"  # Green
    elif final_score >= 70:
        status = "Good"
        color = "#3498db"  # Blue
    elif final_score >= 50:
        status = "Fair"
        color = "#f39c12"  # Orange
    else:
        status = "Needs Attention"
        color = "#e74c3c"  # Red
    
    return final_score, status, color


def create_trend_chart(history_data):
    """
    Create a chart showing dental health trend over time.
    
    Args:
        history_data: List of history entries with timestamps and results
        
    Returns:
        HTML img tag with the embedded chart image
    """
    if not history_data or len(history_data) < 2:
        return None
    
    # Collect data points
    dates = []
    scores = []
    
    for entry in history_data:
        # Convert timestamp string to datetime
        date = datetime.strptime(entry.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
        dates.append(date)
        
        # Calculate health score
        results = entry.get('results', {})
        score, _, _ = generate_health_score(results)
        scores.append(score if score is not None else 0)
    
    # Create plot
    plt.figure(figsize=(10, 4))
    plt.plot(dates, scores, marker='o', linestyle='-', color='#3498db')
    plt.axhline(y=70, color='#f39c12', linestyle='--', alpha=0.7)
    plt.axhline(y=85, color='#2ecc71', linestyle='--', alpha=0.7)
    
    # Format the plot
    plt.xlabel('Date')
    plt.ylabel('Dental Health Score')
    plt.title('Your Dental Health Trend')
    plt.ylim(0, 100)
    plt.grid(axis='y', alpha=0.3)
    
    # Add annotations for the threshold lines
    plt.text(dates[0], 86, 'Excellent', color='#2ecc71', fontsize=9)
    plt.text(dates[0], 71, 'Good', color='#f39c12', fontsize=9)
    
    # Convert plot to base64 encoded image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    encoded = base64.b64encode(image_png).decode('utf-8')
    html_img = f'<img src="data:image/png;base64,{encoded}" alt="Dental Health Trend">'
    
    return html_img


def generate_recommendations(detection_results):
    """
    Generate personalized recommendations based on detection results.
    
    Args:
        detection_results: Dictionary with detection results
        
    Returns:
        recommendations_html: HTML formatted recommendations
    """
    if not detection_results:
        return None
    
    recommendations = []
    
    decay_score = detection_results.get("Decay", 0)
    cavity_score = detection_results.get("Cavity", 0)
    plaque_score = detection_results.get("Plaque", 0)
    
    # Core recommendations based on detected issues
    if decay_score > 50:
        recommendations.append({
            "title": "Decay Treatment Needed",
            "description": "Significant tooth decay detected. We recommend seeing a dentist within the next 2 weeks.",
            "actions": [
                "Visit a dentist for professional treatment",
                "Use fluoride toothpaste twice daily",
                "Consider a prescribed fluoride mouthwash"
            ],
            "urgency": "high"
        })
    elif decay_score > 30:
        recommendations.append({
            "title": "Early Decay Signs",
            "description": "Early signs of tooth decay detected. Take preventive actions now.",
            "actions": [
                "Improve brushing technique, focusing on problem areas",
                "Use fluoride toothpaste and mouthwash",
                "Schedule a dental checkup within a month"
            ],
            "urgency": "medium"
        })
    
    if cavity_score > 50:
        recommendations.append({
            "title": "Cavity Treatment Required",
            "description": "Potential cavity detected. Professional treatment is recommended.",
            "actions": [
                "See a dentist promptly for evaluation and treatment",
                "Avoid sweet and acidic foods in the affected area",
                "Use sensitive teeth toothpaste until your appointment"
            ],
            "urgency": "high"
        })
    
    if plaque_score > 40:
        recommendations.append({
            "title": "Plaque Buildup Detected",
            "description": "Significant plaque buildup observed. Improved oral hygiene needed.",
            "actions": [
                "Brush teeth for full 2 minutes, twice daily",
                "Use dental floss or interdental brushes daily",
                "Consider an anti-plaque mouthwash",
                "Schedule a professional cleaning"
            ],
            "urgency": "medium"
        })
    
    # General recommendations if no specific issues detected
    if not recommendations:
        recommendations.append({
            "title": "Maintain Good Oral Health",
            "description": "Your dental health looks good. Keep up the good habits!",
            "actions": [
                "Continue regular brushing (2 minutes, twice daily)",
                "Floss daily to maintain gum health",
                "Visit your dentist for checkups twice a year"
            ],
            "urgency": "low"
        })
    
    # Format recommendations as HTML
    recommendations_html = ""
    
    for rec in recommendations:
        # Set color based on urgency
        if rec["urgency"] == "high":
            color = "#e74c3c"  # Red
        elif rec["urgency"] == "medium":
            color = "#f39c12"  # Orange
        else:
            color = "#2ecc71"  # Green
            
        # Build HTML for this recommendation
        rec_html = f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 5px solid {color}; background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);">
            <h4 style="color: {color};">{rec["title"]}</h4>
            <p>{rec["description"]}</p>
            <ul>
        """
        
        for action in rec["actions"]:
            rec_html += f"<li>{action}</li>"
        
        rec_html += "</ul></div>"
        recommendations_html += rec_html
    
    return recommendations_html


def calculate_next_checkup(detection_results):
    """
    Calculate recommended next dental checkup date based on detection results.
    
    Args:
        detection_results: Dictionary with detection results
        
    Returns:
        next_date: Recommended next checkup date
        urgency: Urgency level (text)
    """
    if not detection_results:
        return datetime.now() + timedelta(days=180), "Regular"  # 6 months
    
    # Calculate base score
    score, status, _ = generate_health_score(detection_results)
    
    # Determine next checkup date based on health score
    if score is None:
        next_date = datetime.now() + timedelta(days=180)  # 6 months
        urgency = "Regular"
    elif score < 50:
        next_date = datetime.now() + timedelta(days=14)  # 2 weeks
        urgency = "Urgent"
    elif score < 70:
        next_date = datetime.now() + timedelta(days=90)  # 3 months
        urgency = "Soon"
    else:
        next_date = datetime.now() + timedelta(days=180)  # 6 months
        urgency = "Regular"
    
    return next_date, urgency