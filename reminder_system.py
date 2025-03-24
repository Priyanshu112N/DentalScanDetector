import streamlit as st
from datetime import datetime, timedelta
import json
import os

class DentalReminderSystem:
    """
    A system to manage dental checkup reminders.
    """
    
    def __init__(self):
        """
        Initialize the reminder system.
        """
        # We'll initialize the session state variables in the display_reminder_ui method
        # to ensure they're created within the Streamlit context
    
    def enable_reminders(self, enabled=True):
        """
        Enable or disable reminders.
        
        Args:
            enabled: Boolean indicating if reminders should be enabled
        """
        st.session_state.reminders_enabled = enabled
    
    def set_reminder_frequency(self, frequency):
        """
        Set how often reminders should be sent.
        
        Args:
            frequency: String indicating frequency (daily, weekly, monthly)
        """
        st.session_state.reminder_frequency = frequency
    
    def set_reminder_email(self, email):
        """
        Set the email address for receiving reminders.
        
        Args:
            email: Email address
        """
        st.session_state.reminder_email = email
    
    def schedule_next_checkup(self, date):
        """
        Schedule the next checkup date.
        
        Args:
            date: Datetime object for the next checkup
        """
        st.session_state.next_checkup_date = date
    
    def get_next_checkup_date(self):
        """
        Get the next scheduled checkup date.
        
        Returns:
            Next checkup date or None if not set
        """
        return st.session_state.next_checkup_date
    
    def get_days_until_checkup(self):
        """
        Calculate days until the next checkup.
        
        Returns:
            Number of days until next checkup or None if not scheduled
        """
        if "next_checkup_date" not in st.session_state or st.session_state.next_checkup_date is None:
            return None
        
        days = (st.session_state.next_checkup_date - datetime.now()).days
        return max(0, days)
    
    def generate_ical_file(self):
        """
        Generate an iCalendar file for the next dental checkup.
        
        Returns:
            String with iCalendar content or None if no checkup scheduled
        """
        if "next_checkup_date" not in st.session_state or st.session_state.next_checkup_date is None:
            return None
        
        checkup_date = st.session_state.next_checkup_date
        end_date = checkup_date + timedelta(hours=1)  # Assume 1-hour appointment
        
        # Format dates for iCalendar
        start_str = checkup_date.strftime("%Y%m%dT%H%M%S")
        end_str = end_date.strftime("%Y%m%dT%H%M%S")
        now_str = datetime.now().strftime("%Y%m%dT%H%M%S")
        
        # Create iCalendar content
        ical_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Dental Decay Detector//Dental Checkup//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
DTSTART:{start_str}
DTEND:{end_str}
DTSTAMP:{now_str}
UID:dentalcheckup{start_str}@dentalapp.example.com
CREATED:{now_str}
DESCRIPTION:Scheduled dental checkup based on your Dental Decay Detector app recommendation.
LAST-MODIFIED:{now_str}
LOCATION:Your Dentist's Office
SEQUENCE:0
STATUS:CONFIRMED
SUMMARY:Dental Checkup Appointment
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR
"""
        return ical_content
    
    def display_reminder_ui(self):
        """
        Display UI for managing reminders.
        """
        # Initialize session state variables if they don't exist
        if "reminders_enabled" not in st.session_state:
            st.session_state.reminders_enabled = False
        if "reminder_frequency" not in st.session_state:
            st.session_state.reminder_frequency = "monthly"
        if "next_checkup_date" not in st.session_state:
            st.session_state.next_checkup_date = None
        if "reminder_email" not in st.session_state:
            st.session_state.reminder_email = ""
            
        st.subheader("Checkup Reminders")
        
        # Enable/disable reminders with default value
        reminders_enabled = st.toggle(
            "Enable Checkup Reminders", 
            value=False
        )
        self.enable_reminders(reminders_enabled)
        
        if reminders_enabled:
            # Email for reminders
            email = st.text_input(
                "Email for Reminders",
                value=st.session_state.reminder_email,
                placeholder="Enter your email address"
            )
            self.set_reminder_email(email)
            
            # Reminder frequency
            frequency = st.select_slider(
                "Reminder Frequency",
                options=["Daily", "Weekly", "Monthly"],
                value="Monthly"  # Default to monthly
            )
            self.set_reminder_frequency(frequency.lower())
            
            # Show next checkup info if available
            days_until = self.get_days_until_checkup()
            if days_until is not None and st.session_state.next_checkup_date is not None:
                next_date = st.session_state.next_checkup_date.strftime("%B %d, %Y")
                
                if days_until == 0:
                    st.info(f"⚠️ Your dental checkup is scheduled for today ({next_date})!")
                else:
                    st.info(f"🦷 Your next dental checkup is in {days_until} days ({next_date}).")
                
                # Add calendar button
                if st.button("Add to Calendar"):
                    ical_content = self.generate_ical_file()
                    if ical_content:
                        # In a real app, we would serve this file for download
                        # Since we can't do actual downloads in this demo, just show confirmation
                        st.success("Calendar event generated! In a production app, this would download an .ics file you can import to your calendar.")
            else:
                st.warning("No checkup scheduled yet. Complete a dental scan for a recommended date.")
        
        st.markdown("---")
        
        # Reminder settings explanation
        with st.expander("About Reminders"):
            st.markdown("""
            Reminders help you maintain good dental health by notifying you of upcoming checkups. 
            
            **How it works:**
            1. After scanning your teeth, the app suggests a next checkup date based on your dental health.
            2. Enable reminders and provide your email to receive notifications.
            3. Set your preferred reminder frequency.
            4. Add the appointment to your calendar with one click.
            
            📱 In the full version, you would also receive SMS reminders if you provide your phone number.
            """)


# Create a global instance for use throughout the app
reminder_system = DentalReminderSystem()