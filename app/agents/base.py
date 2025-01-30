from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from ..core.config import get_settings
from ..core.exceptions import (
    GeminiError,
    GeminiSafetyError,
    GeminiQuotaError,
    GeminiInvalidRequestError,
    GeminiUnavailableError,
    ConfigurationError,
    handle_agent_error
)
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

# Configure logging
logger = logging.getLogger(__name__)

settings = get_settings()

# Configure the Gemini model
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise ConfigurationError("Failed to initialize Gemini model", {"error": str(e)})

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, description: str):
        """Initialize the base agent.
        
        Args:
            name (str): Name of the agent
            description (str): Description of the agent's role
            
        Raises:
            ConfigurationError: If agent initialization fails
            GeminiError: If Gemini model initialization fails
        """
        try:
            self.name = name
            self.description = description
            
            # Configure model with safety settings
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]
            
            try:
                self.model = genai.GenerativeModel(
                    model_name='gemini-pro',
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {str(e)}")
                raise GeminiError("Failed to initialize Gemini model", {"error": str(e)})
                
            self.conversation_history: List[Dict[str, str]] = []
            
        except GeminiError:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize agent {name}: {str(e)}")
            raise ConfigurationError(f"Failed to initialize agent {name}", {"error": str(e)})
    
    def _add_to_history(self, role: str, content: str):
        """Add a message to the conversation history.
        
        Args:
            role (str): Role of the message sender (user/assistant)
            content (str): Content of the message
        """
        try:
            self.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": time.time()
            })
        except Exception as e:
            logger.warning(f"Failed to add message to history: {str(e)}")
    
    def _get_context_prompt(self) -> str:
        """Get the context prompt for the agent.
        
        Returns:
            str: The context prompt describing the agent's role
        """
        return f"""You are {self.name}, {self.description}. 
        Always maintain a professional and helpful tone.
        If you need to escalate to a human agent, clearly indicate this.
        Base your responses on the conversation history when relevant."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_response(self, message: str) -> str:
        """Generate a response based on the message with retry logic.
        
        Args:
            message (str): The message to process
            
        Returns:
            str: The generated response
            
        Raises:
            GeminiSafetyError: If content is blocked by safety filters
            GeminiQuotaError: If API quota is exceeded
            GeminiInvalidRequestError: If the request is invalid
            GeminiUnavailableError: If the service is unavailable
        """
        try:
            response = await self.model.generate_content_async(
                message,
                stream=False
            )
            
            if response.prompt_feedback.block_reason:
                error_msg = f"Content blocked by Gemini: {response.prompt_feedback.block_reason}"
                logger.warning(error_msg)
                raise GeminiSafetyError(error_msg, {
                    "block_reason": response.prompt_feedback.block_reason
                })
                
            return response.text if hasattr(response, 'text') else str(response)
            
        except genai.types.generation_types.BlockedPromptException as e:
            raise GeminiSafetyError("Content blocked by Gemini safety filters", {"error": str(e)})
        except genai.types.generation_types.GenerationException as e:
            if "quota" in str(e).lower():
                raise GeminiQuotaError("Gemini API quota exceeded", {"error": str(e)})
            elif "invalid" in str(e).lower():
                raise GeminiInvalidRequestError("Invalid request to Gemini API", {"error": str(e)})
            elif "unavailable" in str(e).lower():
                raise GeminiUnavailableError("Gemini API service unavailable", {"error": str(e)})
            raise GeminiError("Failed to generate content", {"error": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error in Gemini content generation: {str(e)}")
            raise GeminiError("Unexpected error during content generation", {"error": str(e)})
    
    async def process_message(self, message: str) -> str:
        """Process an incoming message and return a response.
        
        Args:
            message (str): The incoming message to process
            
        Returns:
            str: The agent's response
        """
        # Add user message to history
        self._add_to_history("user", message)
        
        try:
            # Combine context prompt with user message
            combined_message = f"{self._get_context_prompt()}\n\nUser message: {message}"
            
            # Get response from model
            response = await self._generate_response(combined_message)
            
            # Add response to history
            self._add_to_history("assistant", response)
            
            return response
            
        except GeminiSafetyError as e:
            error_response = "I apologize, but I cannot provide a response to that query as it may contain inappropriate content. Please rephrase your request."
            self._add_to_history("system", error_response)
            return error_response
            
        except GeminiQuotaError as e:
            error_response = "I apologize, but we are experiencing high demand. Please try again in a moment."
            self._add_to_history("system", error_response)
            return error_response
            
        except GeminiUnavailableError as e:
            error_response = "I apologize, but the service is temporarily unavailable. Please try again later."
            self._add_to_history("system", error_response)
            return error_response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_response = "I apologize, but I'm having trouble processing your request. Please try again in a moment."
            self._add_to_history("system", error_response)
            return error_response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history.
        
        Returns:
            List[Dict[str, str]]: List of conversation messages
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        try:
            self.conversation_history = []
        except Exception as e:
            logger.error(f"Failed to clear conversation history: {str(e)}") 