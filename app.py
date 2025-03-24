import streamlit as st
import cv2
import numpy as np
import os
import tempfile
from PIL import Image
from datetime import datetime
import pandas as pd
import atexit
import plotly.graph_objects as go
import base64
import json
import re

from dental_detector import DentalDecayDetector
from image_processing import preprocess_image, annotate_image
from tooth_visualization import generate_3d_tooth_model, generate_decay_visualization
from dental_report import generate_health_score, create_trend_chart, generate_recommendations, calculate_next_checkup
from language_support import translator
from reminder_system import reminder_system

# Set page configuration
st.set_page_config(
    page_title="Dental Decay Detector",
    page_icon="🦷",
    layout="wide"
)

# Initialize session state variables
if "detection_results" not in st.session_state:
    st.session_state.detection_results = None
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "history" not in st.session_state:
    st.session_state.history = []
if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False
if "decay_detector" not in st.session_state:
    st.session_state.decay_detector = DentalDecayDetector()
    st.session_state.model_loaded = True
if "camera_on" not in st.session_state:
    st.session_state.camera_on = False
if "language" not in st.session_state:
    st.session_state.language = "english"
if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": "",
        "age": "",
        "last_dental_visit": "",
    }

# Initialize reminder system variables
if "reminders_enabled" not in st.session_state:
    st.session_state.reminders_enabled = False
if "reminder_frequency" not in st.session_state:
    st.session_state.reminder_frequency = "monthly"
if "next_checkup_date" not in st.session_state:
    st.session_state.next_checkup_date = None
if "reminder_email" not in st.session_state:
    st.session_state.reminder_email = ""

# Set the current language
translator.set_language(st.session_state.language)

# Function to clean up resources when app exits
def cleanup_resources():
    # Release camera resources if they were being used
    if st.session_state.camera_on:
        st.session_state.camera_on = False
        # No direct way to release camera in Streamlit, but we can mark it as off
        print("Camera resources released")

# Register the cleanup function to run when the app exits
atexit.register(cleanup_resources)

# Function to translate text
def t(key):
    """Shorthand for translator.translate"""
    return translator.translate(key)

# Main function
def main():
    # App title and introduction
    st.title(t("app_title"))
    
    # Sidebar for language selection and user profile
    with st.sidebar:
        # Language selector
        st.subheader("🌐 " + t("language"))
        languages = translator.get_supported_languages()
        language_names = {
            "english": "English 🇺🇸",
            "spanish": "Español 🇪🇸",
            "french": "Français 🇫🇷",
            "chinese": "中文 🇨🇳",
            "arabic": "العربية 🇦🇪"
        }
        selected_language = st.selectbox(
            "",
            languages,
            format_func=lambda x: language_names.get(x, x),
            index=languages.index(st.session_state.language)
        )
        
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            translator.set_language(selected_language)
            st.rerun()
        
        # User profile section
        st.subheader("👤 User Profile")
        
        with st.form("user_profile_form"):
            name = st.text_input("Name", value=st.session_state.user_info["name"])
            age = st.number_input("Age", min_value=0, max_value=120, value=int(st.session_state.user_info["age"] or 0))
            last_visit = st.date_input("Last Dental Visit", value=None)
            
            submitted = st.form_submit_button("Save Profile")
            if submitted:
                st.session_state.user_info["name"] = name
                st.session_state.user_info["age"] = age
                if last_visit:
                    st.session_state.user_info["last_dental_visit"] = last_visit.strftime("%Y-%m-%d")
                st.success("Profile updated!")
        
        # Reminder system UI
        reminder_system.display_reminder_ui()

    # Main content area
    st.markdown(f"""
    📱 {t("app_description")}
    {t("app_subtitle")}
    """)

    # Create tabs for navigation
    tabs = st.tabs([t("tab_scan"), t("tab_results"), t("tab_report"), t("tab_history")])
    
    with tabs[0]:
        scan_tab()
    
    with tabs[1]:
        results_tab()
    
    with tabs[2]:
        report_tab()
    
    with tabs[3]:
        history_tab()

def scan_tab():
    st.header(t("scan_header"))
    
    # Instructions
    st.markdown(f"""
    ### {t("instructions_title")}
    1. {t("instruction_1")}
    2. {t("instruction_2")}
    3. {t("instruction_3")}
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Camera controls
        camera_options = st.radio(
            t("camera_options"),
            [t("turn_on_camera"), t("use_last_image")],
            index=0 if not st.session_state.camera_on else 1,
            horizontal=True
        )
        
        if camera_options == t("turn_on_camera"):
            st.session_state.camera_on = True
            # Camera input
            img_file = st.camera_input(t("take_picture"), key="camera")
            
            if img_file is not None:
                # Read and display the image
                bytes_data = img_file.getvalue()
                img_array = np.frombuffer(bytes_data, np.uint8)
                image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Store the captured image in session state
                st.session_state.captured_image = image_rgb
                
                # Preprocess the image
                processed_image = preprocess_image(image_rgb)
                
                # Run dental issue detection
                if st.session_state.model_loaded:
                    with st.spinner(t("analyzing")):
                        results = st.session_state.decay_detector.detect(processed_image)
                        st.session_state.detection_results = results
                        
                        # Add to history
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.history.append({
                            "timestamp": timestamp,
                            "image": processed_image,
                            "results": results
                        })
                        
                        # Set next checkup date based on results
                        next_date, urgency = calculate_next_checkup(results)
                        reminder_system.schedule_next_checkup(next_date)
                        
                    st.success(t("analysis_complete"))
                else:
                    st.error(t("model_error"))
                
                # Option to turn off camera after capturing
                if st.button(t("turn_off_camera")):
                    st.session_state.camera_on = False
                    st.rerun()
        else:
            st.session_state.camera_on = False
            # Display the last captured image if available
            if st.session_state.captured_image is not None:
                st.image(st.session_state.captured_image, caption=t("last_captured"), use_container_width=True)
                
                # Only offer analysis if we have a captured image
                if st.button(t("analyze_image")):
                    # Preprocess the image
                    processed_image = preprocess_image(st.session_state.captured_image)
                    
                    # Run dental issue detection
                    if st.session_state.model_loaded:
                        with st.spinner(t("analyzing")):
                            results = st.session_state.decay_detector.detect(processed_image)
                            st.session_state.detection_results = results
                            
                            # Add to history
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.history.append({
                                "timestamp": timestamp,
                                "image": processed_image,
                                "results": results
                            })
                            
                            # Set next checkup date based on results
                            next_date, urgency = calculate_next_checkup(results)
                            reminder_system.schedule_next_checkup(next_date)
                            
                        st.success(t("analysis_complete"))
                    else:
                        st.error(t("model_error"))
            else:
                st.info(t("no_image"))
    
    with col2:
        st.markdown("### Optimal Positioning")
        st.image("assets/sample_teeth.svg", caption="Example of good teeth positioning")
        
        st.markdown("### Dental Regions")
        st.image("assets/dental_regions.svg", caption="Dental regions we analyze")

def results_tab():
    st.header(t("results_header"))
    
    if st.session_state.detection_results is None:
        st.info(t("no_results"))
        return
        
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(t("detected_issues"))
        results = st.session_state.detection_results
        
        # Display results as a table
        df = pd.DataFrame({
            t("issue_column"): list(results.keys()),
            t("confidence_column"): [f"{results[k]:.1f}%" for k in results.keys()],
            t("status_column"): [t("attention_needed") if results[k] > 50 else t("likely_healthy") for k in results.keys()]
        })
        st.dataframe(df, use_container_width=True)
        
        # Overall health assessment
        avg_confidence = np.mean(list(results.values()))
        score, status, color = generate_health_score(results)
        
        st.subheader(t("health_assessment"))
        
        # Display health score as a gauge
        if score is not None:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Health Score"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(231, 76, 60, 0.3)"},
                        {'range': [50, 70], 'color': "rgba(243, 156, 18, 0.3)"},
                        {'range': [70, 85], 'color': "rgba(52, 152, 219, 0.3)"},
                        {'range': [85, 100], 'color': "rgba(46, 204, 113, 0.3)"}
                    ]
                }
            ))
            
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Text assessment based on score
            if score >= 85:
                st.success(t("health_good"))
            elif score >= 70:
                st.info(f"Your dental health is {status}. Some improvements recommended.")
            elif score >= 50:
                st.warning(t("health_minor"))
            else:
                st.error(t("health_significant"))
    
    with col2:
        # 3D Visualization
        st.subheader("3D Tooth Visualization")
        
        # Generate 3D model with decay areas based on detection results
        decay_areas = generate_decay_visualization(st.session_state.detection_results)
        fig = generate_3d_tooth_model(decay_areas)
        
        # Display the 3D model
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("Interactive 3D model: drag to rotate, zoom with scroll wheel")
        
        # Display annotated image
        st.subheader(t("annotated_image"))
        if st.session_state.captured_image is not None:
            # Display the annotated image
            annotated_image = annotate_image(
                st.session_state.captured_image, 
                st.session_state.detection_results
            )
            st.image(annotated_image, caption="Analyzed dental image with annotations", use_container_width=True)
    
    # Recommendations section
    st.subheader(t("recommendations"))
    
    html_recommendations = generate_recommendations(st.session_state.detection_results)
    if html_recommendations:
        st.markdown(html_recommendations, unsafe_allow_html=True)
    else:
        recommendations = []
        
        results = st.session_state.detection_results
        has_decay = results.get("Decay", 0) > 50
        has_plaque = results.get("Plaque", 0) > 50
        has_cavity = results.get("Cavity", 0) > 50
        
        if has_decay:
            recommendations.append(f"""
            - **{t("decay_detected")}**: {t("visit_dentist")}
            - {t("improve_brushing")}
            - {t("use_fluoride")}
            """)
        
        if has_plaque:
            recommendations.append(f"""
            - **{t("plaque_detected")}**: {t("brush_frequently")}
            - {t("floss_daily")}
            - {t("use_mouthwash")}
            """)
        
        if has_cavity:
            recommendations.append(f"""
            - **{t("cavity_detected")}**: {t("schedule_appointment")}
            - {t("avoid_sugar")}
            - {t("maintain_hygiene")}
            """)
        
        if not recommendations:
            recommendations.append(f"""
            - {t("regular_brushing")}
            - {t("continue_flossing")}
            - {t("regular_checkups")}
            """)
        
        for rec in recommendations:
            st.markdown(rec)
    
    st.info(t("disclaimer"))

def report_tab():
    st.header("Your Dental Health Report")
    
    # Check if we have analysis results
    if st.session_state.detection_results is None:
        st.info("No analysis results yet. Please take a photo in the Scan tab first.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Generate health score
        score, status, color = generate_health_score(st.session_state.detection_results)
        
        if score is not None:
            # Create a colored box with the score
            st.markdown(f"""
            <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <h2 style="color: white; margin: 0;">Dental Health Score</h2>
                <h1 style="color: white; font-size: 4em; margin: 10px 0;">{score}</h1>
                <h3 style="color: white; margin: 0;">{status}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Show next checkup recommendation
        next_date, urgency = calculate_next_checkup(st.session_state.detection_results)
        if next_date:
            date_str = next_date.strftime("%B %d, %Y")
            days_until = (next_date - datetime.now()).days
            
            # Set color based on urgency
            if urgency == "Urgent":
                color = "#e74c3c"  # Red
                urgency_text = "Urgent (within 2 weeks)"
            elif urgency == "Soon":
                color = "#f39c12"  # Orange
                urgency_text = "Soon (within 3 months)"
            else:
                color = "#2ecc71"  # Green
                urgency_text = "Regular (within 6 months)"
            
            st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid {color};">
                <h3>Recommended Next Checkup</h3>
                <p style="font-size: 1.2em;"><strong>{date_str}</strong> ({days_until} days from now)</p>
                <p>Priority: <span style="color: {color}; font-weight: bold;">{urgency_text}</span></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show personalized recommendations
        st.subheader("Personalized Recommendations")
        html_recommendations = generate_recommendations(st.session_state.detection_results)
        if html_recommendations:
            st.markdown(html_recommendations, unsafe_allow_html=True)
        
    with col2:
        # Trend chart
        st.subheader("Your Dental Health Trend")
        
        if len(st.session_state.history) >= 2:
            trend_chart = create_trend_chart(st.session_state.history)
            if trend_chart:
                st.markdown(trend_chart, unsafe_allow_html=True)
        else:
            st.info("Not enough data to generate trend chart. Complete at least two scans.")
        
        # Show 3D visualization
        st.subheader("3D Tooth Model")
        
        # Generate 3D model with decay areas based on detection results
        decay_areas = generate_decay_visualization(st.session_state.detection_results)
        fig = generate_3d_tooth_model(decay_areas)
        
        # Display the 3D model
        st.plotly_chart(fig, use_container_width=True)
    
    # Show report download option
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download PDF Report"):
            st.info("In a production app, this would generate and download a complete PDF report with all your dental health information.")
    
    with col2:
        if st.button("📧 Email Report to Me"):
            email = st.session_state.get("reminder_email", "")
            if email:
                st.success(f"In a production app, this would email your dental report to {email}.")
            else:
                st.warning("Please add your email in the Checkup Reminders section first.")
    
    with col3:
        if st.button("👨‍⚕️ Share with Doctor"):
            st.info("In a production app, this would provide options to securely share your dental health data with your dentist.")

def history_tab():
    st.header(t("history_header"))
    
    if not st.session_state.history:
        st.info(t("no_history"))
        return
    
    # Display history in reverse chronological order (newest first)
    for i, entry in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{t('scan_from')} {entry['timestamp']}"):
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.image(entry['image'], caption=t("captured_image"), use_container_width=True)
            
            with col2:
                results = entry['results']
                # Display results as a simple table
                for issue, confidence in results.items():
                    status = t("attention_needed") if confidence > 50 else t("likely_healthy")
                    st.markdown(f"**{issue}**: {confidence:.1f}% - {status}")
                
                # Generate health score for this scan
                score, status, color = generate_health_score(results)
                if score is not None:
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center; margin-top: 10px;">
                        <h4 style="color: white; margin: 0;">Health Score: {score}</h4>
                        <p style="color: white; margin: 0;">{status}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                # Show 3D model for this scan
                decay_areas = generate_decay_visualization(entry['results'])
                fig = generate_3d_tooth_model(decay_areas)
                st.plotly_chart(fig, use_container_width=True)
    
    # Clear history button
    if st.button(t("clear_history")):
        st.session_state.history = []
        st.success(t("history_cleared"))
        st.rerun()

if __name__ == "__main__":
    main()
