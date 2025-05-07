# platform_adapters/whatsapp/conversation_flows.py

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MaternalHealthConversationFlow:
    """
    Manages the conversation flow for maternal health discussions.
    
    This class:
    1. Tracks conversation state for maternal health topics
    2. Provides structured flow for common maternal health scenarios
    3. Formats prompts for the Mistral model
    4. Processes model responses
    """
    
    # Conversation states
    STATES = {
        'INITIAL': 'initial',             # Starting point
        'LANGUAGE_SELECT': 'language',    # Language selection
        'WEEK_UPDATE': 'week_update',     # Weekly pregnancy update
        'ANC_REMINDER': 'anc_reminder',   # Antenatal care reminder
        'SYMPTOM_CHECK': 'symptom_check', # Symptom checker
        'MENTAL_HEALTH': 'mental_health', # Mental health check-in
        'GENERAL_CHAT': 'general_chat'    # General maternal health conversation
    }
    
    def __init__(self):
        """Initialize the conversation flow manager."""
        self.user_states = {}  # Maps user IDs to states
    
    def get_user_state(self, user_id: str) -> Dict[str, Any]:
        """
        Get the current conversation state for a user.
        
        Args:
            user_id: WhatsApp ID of the user
            
        Returns:
            User's conversation state data
        """
        if user_id not in self.user_states:
            # Initialize with default state
            self.user_states[user_id] = {
                'state': self.STATES['INITIAL'],
                'language': 'en',
                'gestational_week': None,
                'is_postnatal': False,
                'last_topic': None,
                'clinic_date': None,
                'mood_rating': None
            }
        
        return self.user_states[user_id]
    
    def update_user_state(self, user_id: str, updates: Dict[str, Any]) -> None:
        """
        Update a user's conversation state.
        
        Args:
            user_id: WhatsApp ID of the user
            updates: Dictionary of state updates
        """
        if user_id not in self.user_states:
            self.get_user_state(user_id)
        
        self.user_states[user_id].update(updates)
    
    def process_initial_message(self, user_id: str, message: str) -> str:
        """
        Process the initial 'HEALTH' message to start the maternal health flow.
        
        Args:
            user_id: WhatsApp ID of the user
            message: User's message
            
        Returns:
            Prompt for the model
        """
        # Reset/initialize user state
        self.update_user_state(user_id, {
            'state': self.STATES['GENERAL_CHAT'],
            'last_topic': 'welcome'
        })
        
        # Prepare welcome message prompt
        prompt = (
            "Generate a welcoming introduction for MamaCare, the maternal health assistant. "
            "In {user_language}, include:\n\n"
            "1. A warm greeting\n"
            "2. Brief explanation of how MamaCare can help with pregnancy/maternal health\n"
            "3. Available features (weekly updates, symptom checks, reminders)\n"
            "4. Instructions to use commands like LANGUAGE, WEEK, EMERGENCY\n\n"
            "Keep it simple, friendly, and under 200 words. Add appropriate emojis."
        ).format(user_language=self.user_states[user_id]['language'])
        
        return prompt
    
    def process_message(self, user_id: str, message: str) -> str:
        """
        Process a user message and generate an appropriate prompt for the model.
        
        Args:
            user_id: WhatsApp ID of the user
            message: User's message
            
        Returns:
            Prompt for the model
        """
        # Get current user state
        user_state = self.get_user_state(user_id)
        message_upper = message.strip().upper()
        
        # Check for special commands
        if message_upper == "HEALTH":
            return self.process_initial_message(user_id, message)
        
        if message_upper == "LANGUAGE":
            self.update_user_state(user_id, {'state': self.STATES['LANGUAGE_SELECT']})
            return (
                "Generate a language selection menu for MamaCare in {user_language}. "
                "Offer options for English, Swahili, and Sheng. Explain how to select each."
            ).format(user_language=user_state['language'])
        
        if message_upper in ["EN", "SW", "SH"] and user_state['state'] == self.STATES['LANGUAGE_SELECT']:
            language_map = {"EN": "en", "SW": "sw", "SH": "sh"}
            self.update_user_state(user_id, {
                'language': language_map.get(message_upper, "en"),
                'state': self.STATES['GENERAL_CHAT']
            })
            return (
                "Generate a confirmation that the language has been set to {language}. "
                "Use that language in your response. Be brief and friendly."
            ).format(language=language_map.get(message_upper, "en"))
        
        if message_upper.startswith("WEEK "):
            try:
                week = int(message_upper.replace("WEEK ", ""))
                if 1 <= week <= 42:
                    self.update_user_state(user_id, {
                        'gestational_week': week,
                        'state': self.STATES['WEEK_UPDATE']
                    })
                    return self.generate_week_update_prompt(user_id, week)
                else:
                    return (
                        "Generate a friendly error message in {language} explaining that pregnancy weeks "
                        "must be between 1 and 42. Include guidance on the correct format."
                    ).format(language=user_state['language'])
            except ValueError:
                return (
                    "Generate a friendly error message in {language} explaining that the WEEK command "
                    "needs to be followed by a number (e.g., WEEK 24). Include an example."
                ).format(language=user_state['language'])
        
        if message_upper == "EMERGENCY":
            self.update_user_state(user_id, {'last_topic': 'emergency'})
            return (
                "Generate an URGENT maternal health emergency message in {language}. Include:\n\n"
                "1. Clear emergency header with warning emoji\n"
                "2. List of 5 key danger signs that require immediate medical attention\n"
                "3. Instructions to call emergency services (999 or 112)\n"
                "4. Reminder to go to nearest hospital/clinic immediately\n\n"
                "Use simple, direct language. Format for readability with appropriate emphasis."
            ).format(language=user_state['language'])
        
        if message_upper == "SYMPTOM":
            self.update_user_state(user_id, {'state': self.STATES['SYMPTOM_CHECK']})
            return (
                "Generate a symptom checker introduction in {language}. Explain that the user "
                "can describe their symptoms and you'll help determine if they're normal or concerning. "
                "Give examples of how to describe symptoms clearly."
            ).format(language=user_state['language'])
        
        if message_upper == "MOOD":
            self.update_user_state(user_id, {'state': self.STATES['MENTAL_HEALTH']})
            return (
                "Generate a mental health check-in message in {language}. Ask the user to rate "
                "their mood from 1-5, where 1 is very low and 5 is excellent. Include a simple emoji "
                "scale and mention that maternal mental health is important."
            ).format(language=user_state['language'])
        
        # Handle mood rating responses
        if user_state['state'] == self.STATES['MENTAL_HEALTH'] and message.strip() in ["1", "2", "3", "4", "5"]:
            mood_rating = int(message.strip())
            self.update_user_state(user_id, {'mood_rating': mood_rating, 'state': self.STATES['GENERAL_CHAT']})
            return (
                "Respond to a mood rating of {rating}/5 in {language}. If the rating is 3 or below, "
                "offer 1-2 simple coping strategies and normalize their feelings. For any rating, provide "
                "encouragement and a reminder that mental health is important during pregnancy. "
                "Be warm and supportive."
            ).format(rating=mood_rating, language=user_state['language'])
        
        # Handle symptom check responses
        if user_state['state'] == self.STATES['SYMPTOM_CHECK']:
            self.update_user_state(user_id, {'last_topic': 'symptoms', 'state': self.STATES['GENERAL_CHAT']})
            return (
                "User reports: \"{symptom}\" in {language}. Classify as [normal/warning/emergency] and "
                "respond in {language}. For normal symptoms, provide simple management tips. "
                "For warning symptoms, suggest when to see a healthcare provider. For emergency symptoms, "
                "provide clear instructions to seek immediate care. Include brief reasoning for your classification."
            ).format(symptom=message, language=user_state['language'])
        
        # Default case: general maternal health conversation
        self.update_user_state(user_id, {'state': self.STATES['GENERAL_CHAT']})
        return (
            "The user asks: \"{question}\" related to maternal health. Respond in {language} with "
            "factual, helpful information. Keep your answer concise (under 200 words), use simple language, "
            "and cite authoritative sources where appropriate (WHO, medical guidelines). Include emojis "
            "sparingly for warmth. If this requires specific medical expertise, include a reminder to "
            "consult with a healthcare provider."
        ).format(question=message, language=user_state['language'])
    
    def generate_week_update_prompt(self, user_id: str, week: int) -> str:
        """
        Generate a weekly pregnancy update prompt.
        
        Args:
            user_id: WhatsApp ID of the user
            week: Pregnancy week number
            
        Returns:
            Prompt for the model
        """
        user_state = self.get_user_state(user_id)
        
        return (
            "Generate a week {week} pregnancy update in {language}. Include:\n\n"
            "1. Baby's size (fruit comparison)\n"
            "2. Key development happening this week\n"
            "3. One self-care tip\n"
            "4. One nutrition recommendation\n"
            "5. One important symptom to watch for\n\n"
            "Keep it friendly, simple, and add 1-2 appropriate emojis. Format for easy reading."
        ).format(week=week, language=user_state['language'])
    
    def process_model_response(self, user_id: str, response: str) -> str:
        """
        Process the model's response before sending it to the user.
        
        Args:
            user_id: WhatsApp ID of the user
            response: Raw response from the model
            
        Returns:
            Processed response ready to send to the user
        """
        # Most responses can be sent directly to the user
        # This is a hook for any post-processing needed
        return response