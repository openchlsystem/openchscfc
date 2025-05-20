from datetime import datetime
import json
import requests
import logging
from django.conf import settings
from typing import Dict, Any, List, Optional

from webhook_handler.models import Conversation

logger = logging.getLogger(__name__)

class MaternalHealthChatbot:
    """
    A WhatsApp chatbot that handles maternal health inquiries by forwarding messages
    to a Mistral AI model and responding to the user with the generated content.
    
    This class:
    1. Processes incoming WhatsApp messages
    2. Forwards messages to the Mistral API
    3. Sends responses back to users
    4. Handles special keywords for conversation flows
    """
    
    def __init__(self):
        """Initialize the chatbot with configuration."""
        self.model_endpoint = getattr(settings, 'MISTRAL_API_ENDPOINT', 'http://192.168.8.18:11434/api/generate')
        self.user_data = {}  # Store user context (language, pregnancy week, etc.)
        self.active_sessions = set()  # Track active chatbot sessions
    
    def _generate_system_prompt(self, user_wa_id: str) -> str:
        """
        Generate the system prompt to be sent to the model.
        
        Args:
            user_wa_id: WhatsApp ID of the user
            
        Returns:
            System prompt with user context
        """
        # Get user data or use defaults
        user_language = self.user_data.get(user_wa_id, {}).get('user_language', 'en')
        gestational_week = self.user_data.get(user_wa_id, {}).get('gestational_week', None)
        is_postnatal = self.user_data.get(user_wa_id, {}).get('is_postnatal', False)
        
        # Construct context
        context = {
            "user_language": user_language,
            "gestational_week": gestational_week,
            "is_postnatal": is_postnatal
        }
        
        # Create system prompt with context - enhanced for strict maternal health focus
        system_prompt = (
            "You are \"MamaCare\", a specialized maternal health assistant for Kenyan women. "
            "Your sole purpose is to provide factual, evidence-based information about pregnancy, "
            "childbirth, postnatal care, and infant health. "
            f"Context: {json.dumps(context)}\n\n"
            
            "IMPORTANT CONSTRAINTS:\n"
            "- ONLY respond to questions related to maternal health, pregnancy, childbirth, postnatal care, and infant health.\n"
            "- If asked about ANY other topic, politely redirect to maternal health and suggest relevant topics.\n"
            "- Do NOT engage with political, religious, entertainment, or other non-medical topics.\n"
            "- Do NOT provide financial advice, relationship counseling, or career guidance.\n"
            "- FOCUS exclusively on maternal health education and support.\n\n"
            
            "COMMUNICATION STYLE:\n"
            "- Use simple, actionable language (Grade 4 reading level)\n"
            "- Differentiate between \"normal\" vs \"warning\" symptoms in medical information\n"
            "- Include emojis sparingly for warmth (e.g., 👶, 🏥)\n"
            "- Cite sources when possible (e.g., \"WHO recommends...\")\n"
            "- For emergencies, say: \"URGENT: Contact clinic NOW at [local emergency number]\"\n\n"
            
            f"FORMAT RESPONSES AS:\n[{user_language}] Response: [Your reply]\n\n"
            
            "CRITICAL HEALTH GUIDANCE:\n"
            "- For specific medical questions: \"Please consult your healthcare provider about [topic].\"\n"
            "- For emergency symptoms: \"This requires immediate medical attention. Go to the nearest hospital.\"\n"
            "- Always emphasize the importance of regular antenatal care visits.\n"
            "- Provide evidence-based information from WHO, CDC, or other reputable health organizations.\n"
            "- Maintain cultural sensitivity to Kenyan maternal health traditions while promoting safe practices."
        )
        
        return system_prompt
    
    def is_active_session(self, user_id: str) -> bool:
        """
        Check if the user has an active chatbot session.
        First checks in-memory set, then falls back to database if needed.
        """
        # First check in-memory set
        if user_id in self.active_sessions:
            return True
            
        # If not found in memory, check database
        try:
            # Check if a conversation exists with chatbot metadata
            conversation = Conversation.objects.filter(
                sender_id=user_id,
                platform='whatsapp',
                is_active=True
            ).first()
            
            if conversation and conversation.metadata:
                # Check if there's chatbot_active flag in metadata
                metadata = conversation.metadata
                if isinstance(metadata, dict) and metadata.get('chatbot_active') is True:
                    # Sync with in-memory set
                    self.active_sessions.add(user_id)
                    return True
        except Exception as e:
            logger.error(f"Error checking chatbot session in database: {str(e)}")
        
        return False

    def activate_session(self, user_id: str) -> None:
        """
        Activate a chatbot session for the user.
        """
        self.active_sessions.add(user_id)
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'user_language': 'en',
                'gestational_week': None,
                'is_postnatal': False
            }
        
        # Also store in database for persistence
        try:
            conversation, created = Conversation.objects.get_or_create(
                sender_id=user_id,
                platform='whatsapp',
                defaults={
                    'conversation_id': f"whatsapp-{user_id}",
                    'is_active': True,
                    'metadata': {'chatbot_active': True, 'activated_at': str(datetime.now())}
                }
            )
            
            if not created:
                # Update existing conversation
                if not conversation.metadata:
                    conversation.metadata = {}
                
                conversation.is_active = True
                conversation.metadata['chatbot_active'] = True
                conversation.metadata['activated_at'] = str(datetime.now())
                conversation.save()
        except Exception as e:
            logger.error(f"Error storing chatbot session in database: {str(e)}")
    def deactivate_session(self, user_id: str) -> None:
        """
        Deactivate a chatbot session for the user.
        
        Args:
            user_id: WhatsApp ID of the user
        """
        if user_id in self.active_sessions:
            self.active_sessions.remove(user_id)
        
        # Also update database
        try:
            conversation = Conversation.objects.filter(
                sender_id=user_id,
                platform='whatsapp'
            ).first()
            
            if conversation:
                conversation.metadata = {
                    **conversation.metadata,
                    'chatbot_active': False,
                    'deactivated_at': str(datetime.now())
                }
                conversation.save(update_fields=['metadata'])
        except Exception as e:
            logger.error(f"Error updating chatbot session in database: {str(e)}")
        
    def handle_health_keyword(self, user_wa_id: str) -> str:
        """
        Handle the special 'HEALTH' keyword that initiates the maternal health conversation flow.
        
        Args:
            user_wa_id: WhatsApp ID of the user
            
        Returns:
            Response message to send to the user
        """
        # Set default user data for new users
        if user_wa_id not in self.user_data:
            self.user_data[user_wa_id] = {
                'user_language': 'en',
                'gestational_week': None,
                'is_postnatal': False
            }
        
        # Welcome message for the maternal health flow
        welcome_message = (
            "[English] Response: Welcome to MamaCare, your maternal health assistant! 👶\n\n"
            "I'm here to support your pregnancy journey with:\n"
            "- Weekly pregnancy updates\n"
            "- Appointment reminders\n"
            "- Symptom guidance\n"
            "- Health tips\n\n"
            "What would you like to know about maternal health today?\n\n"
            "You can also reply with:\n"
            "- \"LANGUAGE\" to change language (English, Swahili, Sheng)\n"
            "- \"WEEK\" followed by your pregnancy week (e.g., \"WEEK 24\")\n"
            "- \"EMERGENCY\" for urgent maternal health guidance\n"
            "- \"EXIT\" to end our conversation"
        )
        
        return welcome_message
    
    def process_command(self, user_wa_id: str, message: str) -> Optional[str]:
        """
        Process special command keywords in the message.
        
        Args:
            user_wa_id: WhatsApp ID of the user
            message: The user's message
            
        Returns:
            Response message if a command was processed, None otherwise
        """
        message_upper = message.strip().upper()
        
        # Initialize user data if not exists
        if user_wa_id not in self.user_data:
            self.user_data[user_wa_id] = {
                'user_language': 'en',
                'gestational_week': None,
                'is_postnatal': False
            }
        
        # Handle the HEALTH keyword
        if message_upper == "HEALTH":
            return self.handle_health_keyword(user_wa_id)
        
        # Handle EXIT keyword to end the session
        if message_upper == "EXIT":
            self.deactivate_session(user_wa_id)
            return f"[{self.user_data[user_wa_id]['user_language']}] Response: You've exited the maternal health assistant. If you need help with maternal health in the future, just send 'HEALTH' to start again."
        
        # Handle language change
        if message_upper == "LANGUAGE":
            return (
                "[English] Response: Please select your preferred language:\n"
                "- Reply with \"EN\" for English\n"
                "- Reply with \"SW\" for Swahili\n"
                "- Reply with \"SH\" for Sheng"
            )
        
        # Set language preference
        if message_upper in ["EN", "SW", "SH"]:
            language_map = {"EN": "en", "SW": "sw", "SH": "sh"}
            self.user_data[user_wa_id]['user_language'] = language_map.get(message_upper, "en")
            
            response_messages = {
                "en": "[English] Response: Language set to English! How can I help you today?",
                "sw": "[Swahili] Response: Lugha imewekwa kwa Kiswahili! Naweza kukusaidia aje leo?",
                "sh": "[Sheng] Response: Sasa tunaongea kwa Sheng! Nikupee usaidizi aje leo?"
            }
            
            return response_messages[self.user_data[user_wa_id]['user_language']]
        
        # Set pregnancy week
        if message_upper.startswith("WEEK "):
            try:
                week = int(message_upper.replace("WEEK ", ""))
                if 1 <= week <= 42:
                    self.user_data[user_wa_id]['gestational_week'] = week
                    return f"[{self.user_data[user_wa_id]['user_language']}] Response: Thanks! I've updated your pregnancy to week {week}. 👶"
                else:
                    return f"[{self.user_data[user_wa_id]['user_language']}] Response: Please enter a valid pregnancy week between 1 and 42."
            except ValueError:
                return f"[{self.user_data[user_wa_id]['user_language']}] Response: Please provide a valid number, e.g., \"WEEK 24\"."
        
        # Handle emergency keyword
        if message_upper == "EMERGENCY":
            return (
                f"[{self.user_data[user_wa_id]['user_language']}] Response: ⚠️ URGENT: For maternal emergencies, contact your clinic immediately! ⚠️\n\n"
                "Warning signs that require immediate attention:\n"
                "- Severe bleeding\n"
                "- Severe headache with vision changes\n"
                "- Difficulty breathing\n"
                "- Seizures\n"
                "- Severe abdominal pain\n\n"
                "Call emergency services now at: 999 or 112"
            )
        
        # No command was processed
        return None
    
    # Update the get_model_response method in your MaternalHealthChatbot class

    def get_model_response(self, user_wa_id: str, user_message: str) -> str:
        """
        Get response from the Mistral API with improved error handling.
        
        Args:
            user_wa_id: WhatsApp ID of the user
            user_message: Message from the user
            
        Returns:
            Generated response from the model
        """
        try:
            # Generate system prompt with user context
            system_prompt = self._generate_system_prompt(user_wa_id)
            
            # Prepare request payload
            payload = {
                "model": "mistral",
                "prompt": f"{system_prompt}\n\nUser: {user_message}",
                "stream": False
            }
            
            # Add timeout and debug logging
            logger.info(f"Sending request to Mistral API: {self.model_endpoint}")
            logger.debug(f"Payload: {json.dumps(payload)}")
            
            # Make request to model API with increased timeout
            response = requests.post(
                self.model_endpoint,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=60  # Increased timeout to 60 seconds
            )
            
            # Log the response status
            logger.info(f"Mistral API response status: {response.status_code}")
            
            # Check if request was successful
            if response.status_code == 200:
                response_data = response.json()
                logger.debug(f"Mistral API raw response: {json.dumps(response_data)}")
                
                if 'response' in response_data:
                    # Request successful, return the response
                    return response_data['response']
                else:
                    # Unexpected response format, log and return error
                    logger.error(f"Unexpected Mistral API response format: {response_data}")
                    
                    # Check if there's an 'error' field in the response
                    if 'error' in response_data:
                        logger.error(f"Mistral API error: {response_data['error']}")
                    
                    # Return a fallback maternal health message instead of generic error
                    return self._get_fallback_response(user_wa_id, user_message)
            else:
                # API request failed with non-200 status
                logger.error(f"Mistral API request failed with status {response.status_code}: {response.text}")
                
                # Return a fallback response instead of generic error
                return self._get_fallback_response(user_wa_id, user_message)
                    
        except requests.exceptions.Timeout:
            # Handle timeout specifically
            logger.error("Mistral API request timed out after 60 seconds")
            return "[English] Response: I'm sorry, but the response is taking longer than expected. Let me know if you'd like general information about maternal health while we work on fixing this issue."
        
        except requests.exceptions.ConnectionError:
            # Handle connection errors specifically
            logger.error(f"Connection error to Mistral API at {self.model_endpoint}")
            return "[English] Response: I'm having trouble connecting to my knowledge base right now. Please try again in a few moments, or ask me about common pregnancy symptoms or nutrition tips."
            
        except Exception as e:
            # Log detailed exception info for debugging
            logger.exception(f"Error getting Mistral API response: {str(e)}")
            return self._get_fallback_response(user_wa_id, user_message)

    def _get_fallback_response(self, user_wa_id: str, user_message: str) -> str:
        """
        Provide a relevant fallback response when the API fails.
        Attempts to match the query to pre-defined maternal health information.
        
        Args:
            user_wa_id: WhatsApp ID of the user
            user_message: Message from the user
            
        Returns:
            Fallback response
        """
        # Get user language from data or default to English
        user_language = self.user_data.get(user_wa_id, {}).get('user_language', 'en')
        language_prefix = "[English]" if user_language == "en" else "[Swahili]" if user_language == "sw" else "[Sheng]"
        
        # Check if message contains keywords to provide relevant fallback
        message_lower = user_message.lower()
        
        # Check if this is related to pregnancy weeks
        if 'week' in message_lower or 'weeks' in message_lower or 'pregnancy' in message_lower:
            return f"{language_prefix} Response: During pregnancy, regular prenatal care is essential. The first trimester (weeks 1-12) focuses on organ development, the second trimester (weeks 13-26) is when you might feel movement, and the third trimester (weeks 27-40) prepares for birth. Each week brings new developments for your baby. Would you like info about a specific pregnancy week?"
        
        # Check if related to symptoms
        elif 'symptom' in message_lower or 'pain' in message_lower or 'feeling' in message_lower:
            return f"{language_prefix} Response: Common pregnancy symptoms include morning sickness, fatigue, and back pain. Warning signs that need immediate attention include severe abdominal pain, bleeding, reduced fetal movement, severe headaches with vision changes, or difficulty breathing. Always consult your healthcare provider about concerning symptoms."
        
        # Check if related to nutrition
        elif 'eat' in message_lower or 'food' in message_lower or 'nutrition' in message_lower or 'diet' in message_lower:
            return f"{language_prefix} Response: Good nutrition during pregnancy includes plenty of fruits, vegetables, whole grains, lean protein, and healthy fats. Folate-rich foods help prevent birth defects, iron supports blood production, and calcium helps build baby's bones. Stay hydrated and take prenatal vitamins as recommended by your doctor."
        
        # Generic fallback for other topics
        else:
            return f"{language_prefix} Response: I'm currently experiencing some technical difficulties connecting to my knowledge base. While we work to resolve this, please feel free to ask about common maternal health topics like prenatal care, nutrition during pregnancy, symptom management, or preparing for childbirth. For urgent concerns, please contact your healthcare provider."
        
    def process_message(self, sender_id: str, message_text: str) -> str:
        """
        Process an incoming WhatsApp message and generate a response.
        
        Args:
            sender_id: WhatsApp ID of the sender
            message_text: Text content of the message
            
        Returns:
            Response to send back to the user
        """
        try:
            # Check for special commands first
            command_response = self.process_command(sender_id, message_text)
            if command_response:
                return command_response
            
            # If no special command, get response from AI model
            return self.get_model_response(sender_id, message_text)
            
        except Exception as e:
            logger.exception(f"Error processing message: {str(e)}")
            return "[English] Response: I apologize, but I encountered an error processing your request. Please try again or type 'EXIT' and then 'HEALTH' to restart the conversation."