from typing import List, Any
from .base import BaseAgent

class GreeterAgent(BaseAgent):
    """Agent responsible for initial customer interactions and basic FAQ."""
    
    def __init__(self):
        super().__init__(
            name="Customer Service Greeter",
            description="a friendly customer service representative responsible for welcoming customers, \
            understanding their needs, and providing basic assistance or routing them to specialized agents."
        )
        self.greeting_sent = False
    
    def _get_context_prompt(self) -> str:
        """Get the specialized context prompt for the greeter agent."""
        base_prompt = super()._get_context_prompt()
        return f"""{base_prompt}

        Your primary responsibilities are:
        1. Welcome customers warmly and professionally
        2. Understand their initial query or concern
        3. Provide immediate help for basic questions
        4. Identify when to route to specialized agents
        
        When greeting:
        - If this is the first interaction, introduce yourself
        - Be concise but friendly
        - Ask about how you can help
        
        For routing decisions:
        - Content/SEO issues → Content Management Agent
        - Product questions → Product Information Agent
        - Email/communication issues → Email Management Agent
        - Complex issues → Escalation Agent
        
        Always maintain context from the conversation history."""
    
    async def _generate_response(self, message: str) -> str:
        """Generate a response using the Greeter's specialized logic.
        
        Args:
            message (str): The message to process
            
        Returns:
            str: The generated response
        """
        response = await super()._generate_response(message)
        
        # If this is the first interaction and we haven't sent a greeting
        if not self.greeting_sent and len(self.conversation_history) <= 2:
            self.greeting_sent = True
            greeting = "Hello! Welcome to ChromaPages customer service. "
            response = greeting + response
        
        return response
    
    def should_route_to_specialist(self, message: str) -> bool:
        """Determine if the conversation should be routed to a specialist agent.
        
        Args:
            message (str): The user's message
            
        Returns:
            bool: True if the conversation should be routed, False otherwise
        """
        # This is a simple check - in a real system, you'd want more sophisticated logic
        specialist_keywords = {
            'content': 'content_management',
            'seo': 'content_management',
            'website': 'content_management',
            'product': 'product_info',
            'feature': 'product_info',
            'email': 'email_management',
            'notification': 'email_management',
            'technical': 'escalation'
        }
        
        message_lower = message.lower()
        for keyword in specialist_keywords:
            if keyword in message_lower:
                return True
        
        return False 