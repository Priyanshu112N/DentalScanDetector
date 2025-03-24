class TranslationService:
    """
    A simple translation service for the Dental Decay Detector.
    Provides multi-language support for key messages and UI elements.
    """
    
    def __init__(self, default_language="english"):
        """
        Initialize the translation service with a default language.
        
        Args:
            default_language: The default language to use
        """
        self.current_language = default_language
        self.supported_languages = ["english", "spanish", "french", "chinese", "arabic"]
        self.translations = self._load_translations()
    
    def _load_translations(self):
        """
        Load translations for all supported languages.
        
        Returns:
            Dictionary of translations for each language
        """
        # Define translations for various elements of the app
        return {
            "english": {
                # App title and welcome messages
                "app_title": "Dental Decay Detector",
                "app_description": "Take a picture of your teeth with your mobile camera to detect potential dental issues.",
                "app_subtitle": "This app uses image analysis to identify common dental problems like decay, cavities, and plaque.",
                
                # Tab names
                "tab_scan": "Scan Teeth",
                "tab_results": "Results",
                "tab_history": "History",
                "tab_report": "My Report",
                
                # Scan tab
                "scan_header": "Take a Photo of Your Teeth",
                "instructions_title": "Instructions:",
                "instruction_1": "Position your camera to get a clear view of your teeth",
                "instruction_2": "Ensure good lighting for best results",
                "instruction_3": "Try to keep your mouth open wide enough to see the teeth clearly",
                "camera_options": "Camera Options:",
                "turn_on_camera": "Turn On Camera",
                "use_last_image": "Use Last Image",
                "take_picture": "Take a picture of your teeth",
                "last_captured": "Last captured image",
                "no_image": "No image captured yet. Turn on the camera to take a picture.",
                "turn_off_camera": "Turn Off Camera",
                "analyze_image": "Analyze Image",
                "analyzing": "Analyzing your dental image...",
                "analysis_complete": "Analysis complete! Go to the Results tab to see details.",
                "model_error": "Model not loaded properly. Please refresh the page and try again.",
                
                # Results tab
                "results_header": "Analysis Results",
                "no_results": "No analysis results yet. Please take a photo in the Scan tab first.",
                "detected_issues": "Detected Issues",
                "issue_column": "Issue",
                "confidence_column": "Confidence",
                "status_column": "Status",
                "attention_needed": "⚠️ Attention needed",
                "likely_healthy": "✅ Likely healthy",
                "health_assessment": "Overall Dental Health Assessment",
                "health_good": "Your dental health appears to be good. Keep up with regular dental hygiene.",
                "health_minor": "Some minor issues detected. Consider scheduling a dental checkup.",
                "health_significant": "Significant dental issues detected. We recommend consulting a dentist soon.",
                "annotated_image": "Annotated Image",
                "recommendations": "Recommendations",
                "decay_detected": "Dental Decay Detected",
                "plaque_detected": "Plaque Buildup Detected",
                "cavity_detected": "Possible Cavity Detected",
                "visit_dentist": "Visit your dentist for a professional assessment",
                "improve_brushing": "Improve brushing technique, focusing on all tooth surfaces",
                "use_fluoride": "Consider using fluoride toothpaste and mouthwash",
                "brush_frequently": "Increase brushing frequency to at least twice daily",
                "floss_daily": "Start using dental floss daily if you don't already",
                "use_mouthwash": "Consider using an antibacterial mouthwash",
                "schedule_appointment": "Schedule a dental appointment soon",
                "avoid_sugar": "Avoid sugary foods and drinks",
                "maintain_hygiene": "Maintain thorough oral hygiene while waiting for your appointment",
                "regular_brushing": "Maintain regular brushing (2 minutes, twice daily)",
                "continue_flossing": "Continue flossing daily",
                "regular_checkups": "Schedule regular dental checkups twice a year",
                "disclaimer": "Note: This app provides preliminary analysis only and is not a substitute for professional dental care.",
                
                # History tab
                "history_header": "Scan History",
                "no_history": "No scan history available yet. Complete a scan to record your history.",
                "scan_from": "Scan from",
                "captured_image": "Captured Image",
                "clear_history": "Clear History",
                "history_cleared": "History cleared successfully!",
                
                # 3D Visualization
                "tooth_model": "3D Tooth Model",
                "visualization": "Interactive 3D Visualization",
                "rotate_model": "Drag to rotate the model",
                "decay_area": "Decay Area",
                
                # Report tab
                "report_header": "Your Dental Health Report",
                "health_score": "Dental Health Score",
                "excellent": "Excellent",
                "good": "Good",
                "fair": "Fair",
                "needs_attention": "Needs Attention",
                "trend_chart": "Health Trend Chart",
                "not_enough_data": "Not enough data to generate trend chart. Complete at least two scans.",
                "personalized_recommendations": "Personalized Recommendations",
                "next_checkup": "Recommended Next Checkup",
                "checkup_urgent": "Urgent (within 2 weeks)",
                "checkup_soon": "Soon (within 3 months)",
                "checkup_regular": "Regular (within 6 months)",
                "download_report": "Download Full Report",
                "email_report": "Email Report",
                "share_doctor": "Share with Doctor",
                
                # Settings
                "settings": "Settings",
                "language": "Language",
                "notifications": "Checkup Reminders",
                "enable_reminders": "Enable Reminders",
                "reminder_frequency": "Reminder Frequency",
                "save_settings": "Save Settings",
            },
            
            "spanish": {
                # App title and welcome messages
                "app_title": "Detector de Caries Dental",
                "app_description": "Toma una foto de tus dientes con la cámara de tu móvil para detectar posibles problemas dentales.",
                "app_subtitle": "Esta aplicación utiliza análisis de imágenes para identificar problemas dentales comunes como caries, cavidades y placa.",
                
                # Tab names
                "tab_scan": "Escanear Dientes",
                "tab_results": "Resultados",
                "tab_history": "Historial",
                "tab_report": "Mi Informe",
                
                # Scan tab
                "scan_header": "Toma una Foto de tus Dientes",
                "instructions_title": "Instrucciones:",
                "instruction_1": "Posiciona tu cámara para obtener una vista clara de tus dientes",
                "instruction_2": "Asegúrate de tener buena iluminación para mejores resultados",
                "instruction_3": "Intenta mantener tu boca lo suficientemente abierta para ver los dientes claramente",
                "camera_options": "Opciones de Cámara:",
                "turn_on_camera": "Encender Cámara",
                "use_last_image": "Usar Última Imagen",
                "take_picture": "Toma una foto de tus dientes",
                "last_captured": "Última imagen capturada",
                "no_image": "Aún no hay imagen capturada. Enciende la cámara para tomar una foto.",
                "turn_off_camera": "Apagar Cámara",
                "analyze_image": "Analizar Imagen",
                "analyzing": "Analizando tu imagen dental...",
                "analysis_complete": "¡Análisis completo! Ve a la pestaña de Resultados para ver los detalles.",
                "model_error": "El modelo no se cargó correctamente. Por favor, actualiza la página e inténtalo de nuevo.",
                
                # Results tab - other translations omitted for brevity
                "results_header": "Resultados del Análisis",
                "no_results": "Aún no hay resultados de análisis. Por favor, toma una foto en la pestaña Escanear primero.",
                
                # more translations would be added here...
            },
            
            "french": {
                # App title and welcome messages
                "app_title": "Détecteur de Caries Dentaires",
                "app_description": "Prenez une photo de vos dents avec votre caméra mobile pour détecter d'éventuels problèmes dentaires.",
                "app_subtitle": "Cette application utilise l'analyse d'image pour identifier les problèmes dentaires courants comme les caries, les cavités et la plaque dentaire.",
                
                # Other French translations would be added here...
            },
            
            # Other languages would be implemented similarly
        }
    
    def set_language(self, language):
        """
        Set the current language for the application.
        
        Args:
            language: The language to use
        """
        if language in self.supported_languages:
            self.current_language = language
        else:
            # Fallback to English if language not supported
            self.current_language = "english"
    
    def get_supported_languages(self):
        """
        Get a list of supported languages.
        
        Returns:
            List of supported language names
        """
        return self.supported_languages
    
    def translate(self, key):
        """
        Translate a specific key to the current language.
        
        Args:
            key: The translation key to look up
            
        Returns:
            Translated text or the key itself if translation not found
        """
        # Get translations for current language
        lang_dict = self.translations.get(self.current_language, {})
        
        # Return translation or fallback to English or the key itself
        if key in lang_dict:
            return lang_dict[key]
        elif key in self.translations.get("english", {}):
            return self.translations["english"][key]
        else:
            return key

# Create a global instance for use throughout the app
translator = TranslationService()