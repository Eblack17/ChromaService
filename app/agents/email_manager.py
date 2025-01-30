from typing import List, Any, Dict
from .base import BaseAgent

class EmailManagementAgent(BaseAgent):
    """Agent responsible for handling email-related tasks and communications."""
    
    def __init__(self):
        super().__init__(
            name="Email Management Specialist",
            description="a specialist responsible for handling email-related inquiries, \
            managing communication preferences, and resolving email delivery issues."
        )
        self.email_categories = {
            'spam': 'Issues with spam or unwanted emails',
            'delivery': 'Email delivery problems or delays',
            'settings': 'Email settings and preferences',
            'notifications': 'Notification settings and management',
            'technical': 'Technical email issues'
        }
    
    def _get_context_prompt(self) -> str:
        """Get the specialized context prompt for the email management agent."""
        base_prompt = super()._get_context_prompt()
        return f"""{base_prompt}

        Your primary responsibilities are:
        1. Help users with email-related issues
        2. Troubleshoot email delivery problems
        3. Assist with email settings and preferences
        4. Handle spam and security concerns
        5. Manage notification preferences
        
        When handling email issues:
        - First identify the specific type of email problem
        - Ask for relevant details (e.g., email address, timing of issues)
        - Provide step-by-step solutions
        - Explain any technical terms in simple language
        
        Categories of issues you handle:
        {self._format_categories()}
        
        If an issue requires technical intervention or system access:
        - Clearly explain what needs to be done
        - Indicate when escalation is needed"""
    
    def _format_categories(self) -> str:
        """Format the email categories for the prompt."""
        return "\n".join([f"- {key}: {value}" for key, value in self.email_categories.items()])
    
    async def _generate_response(self, message: str) -> str:
        """Generate a response using the Email Management Agent's specialized logic.
        
        Args:
            message (str): The message to process
            
        Returns:
            str: The generated response
        """
        return await super()._generate_response(message)
    
    def categorize_email_issue(self, message: str) -> str:
        """Categorize the type of email issue based on the user's message.
        
        Args:
            message (str): The user's message
            
        Returns:
            str: The category of the email issue
        """
        message_lower = message.lower()
        
        # Simple keyword-based categorization
        if any(word in message_lower for word in ['spam', 'junk', 'unwanted']):
            return 'spam'
        elif any(word in message_lower for word in ['delivery', 'receive', 'sent']):
            return 'delivery'
        elif any(word in message_lower for word in ['settings', 'preference', 'configure']):
            return 'settings'
        elif any(word in message_lower for word in ['notification', 'alert', 'update']):
            return 'notifications'
        else:
            return 'technical'
    
    def needs_escalation(self, message: str) -> bool:
        """Determine if the email issue needs escalation to technical support.
        
        Args:
            message (str): The user's message
            
        Returns:
            bool: True if escalation is needed, False otherwise
        """
        escalation_keywords = [
            'hack', 'breach', 'security', 'compromised', 'access',
            'error', 'broken', 'technical', 'bug', 'system'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in escalation_keywords) 