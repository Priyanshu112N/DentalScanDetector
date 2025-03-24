import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

def generate_3d_tooth_model(decay_areas=None):
    """
    Generate a 3D model of a tooth with optional decay areas highlighted.
    
    Args:
        decay_areas: List of dictionaries with decay coordinates and severity
        
    Returns:
        A plotly figure object with the 3D tooth model
    """
    # Create parameters for a tooth shape
    u = np.linspace(0, 2*np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    
    # Base tooth shape (similar to molar)
    root_height = 1.5
    crown_height = 1.0
    
    # Generate points for crown (top part of tooth)
    crown_x = 0.8 * np.outer(np.cos(u), np.sin(v))
    crown_y = 0.8 * np.outer(np.sin(u), np.sin(v))
    crown_z = crown_height * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Adjust the crown to have a flat biting surface with slight indentation
    for i in range(len(crown_z)):
        for j in range(len(crown_z[0])):
            if crown_z[i][j] > 0.5:
                # Create indentation on the biting surface
                dist_from_center = np.sqrt(crown_x[i][j]**2 + crown_y[i][j]**2)
                if dist_from_center < 0.4:
                    crown_z[i][j] = 0.5 - 0.3 * (0.4 - dist_from_center) 
    
    # Generate points for root (bottom part of tooth)
    root_x = 0.5 * np.outer(np.cos(u), np.sin(v))
    root_y = 0.5 * np.outer(np.sin(u), np.sin(v))
    root_z = -root_height * np.outer(np.ones(np.size(u)), np.cos(v))
    
    # Adjust the roots to have a more realistic shape
    for i in range(len(root_z)):
        for j in range(len(root_z[0])):
            if root_z[i][j] < -0.8:
                # Make roots taper at the end
                tapering = (-root_z[i][j] - 0.8) / root_height
                root_x[i][j] *= (1 - 0.7 * tapering)
                root_y[i][j] *= (1 - 0.7 * tapering)
    
    # Create figure
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'surface'}]])
    
    # Add crown surface
    fig.add_trace(
        go.Surface(
            x=crown_x, 
            y=crown_y, 
            z=crown_z,
            colorscale='Blues',
            opacity=0.9,
            showscale=False,
            name="Crown"
        )
    )
    
    # Add root surface
    fig.add_trace(
        go.Surface(
            x=root_x, 
            y=root_y, 
            z=root_z,
            colorscale='Greys',
            opacity=0.85,
            showscale=False,
            name="Root"
        )
    )
    
    # Add decay areas if provided
    if decay_areas:
        for area in decay_areas:
            x, y, z = area['position']
            size = area['size']
            severity = area['severity']
            
            # Color based on severity
            if severity > 75:
                color = 'red'
            elif severity > 50:
                color = 'orange'
            else:
                color = 'yellow'
            
            # Add decay marker
            fig.add_trace(
                go.Scatter3d(
                    x=[x], 
                    y=[y], 
                    z=[z],
                    mode='markers',
                    marker=dict(
                        size=size,
                        color=color,
                        opacity=0.8,
                        symbol='circle'
                    ),
                    name=f"Decay ({severity}%)"
                )
            )
    
    # Update layout
    fig.update_layout(
        title='3D Tooth Model',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=1)
        )
    )
    
    return fig


def generate_decay_visualization(detection_results):
    """
    Generate decay areas for 3D visualization based on detection results.
    
    Args:
        detection_results: Dictionary with detection results
        
    Returns:
        List of decay areas for the 3D model
    """
    decay_areas = []
    
    if not detection_results:
        return decay_areas
    
    # Create decay areas based on detection results
    decay_score = detection_results.get("Decay", 0)
    cavity_score = detection_results.get("Cavity", 0)
    plaque_score = detection_results.get("Plaque", 0)
    
    # Add decay markers based on scores
    if decay_score > 20:
        # Add 1-3 decay spots based on severity
        num_spots = 1
        if decay_score > 40:
            num_spots = 2
        if decay_score > 70:
            num_spots = 3
            
        for _ in range(num_spots):
            # Position on the crown surface
            x = random.uniform(-0.6, 0.6)
            y = random.uniform(-0.6, 0.6)
            # Adjust z to be on the surface
            z = 0.5 + 0.3 * (1 - min(1, (x**2 + y**2) / 0.36))
            
            decay_areas.append({
                'position': [x, y, z],
                'size': 8 + (decay_score / 10),
                'severity': decay_score
            })
    
    if cavity_score > 30:
        # Add cavity on the biting surface
        decay_areas.append({
            'position': [random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0.5],
            'size': 12 + (cavity_score / 8),
            'severity': cavity_score
        })
    
    if plaque_score > 25:
        # Add plaque near the gumline
        for _ in range(min(3, int(plaque_score / 25))):
            angle = random.uniform(0, 2*np.pi)
            decay_areas.append({
                'position': [
                    0.7 * np.cos(angle), 
                    0.7 * np.sin(angle), 
                    0.1  # Near the gumline
                ],
                'size': 7 + (plaque_score / 12),
                'severity': plaque_score
            })
    
    return decay_areas