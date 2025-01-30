from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
from .greeter import GreeterAgent
from .email_manager import EmailManagementAgent
from .content_manager import ContentManagementAgent
from .product_info import ProductInformationAgent
from ..core.exceptions import (
    BaseCustomException,
    ContentBlockedError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    handle_agent_error
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/agents",
    tags=["agents"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"error": "An unexpected error occurred"}
                }
            }
        }
    }
)

# Initialize agents
try:
    greeter_agent = GreeterAgent()
    email_agent = EmailManagementAgent()
    content_agent = ContentManagementAgent()
    product_agent = ProductInformationAgent()
except Exception as e:
    logger.error(f"Failed to initialize agents: {str(e)}")
    raise

class Message(BaseModel):
    """Message model for requests."""
    content: str = Field(
        ...,
        description="The message content to be processed by the agent",
        min_length=1,
        max_length=1000,
        example="Hi, I need help with ChromaPages"
    )
    agent_type: Optional[str] = Field(
        default="greeter",
        description="The type of agent to handle the message",
        example="greeter"
    )

    class Config:
        schema_extra = {
            "example": {
                "content": "Hi, I need help with ChromaPages",
                "agent_type": "greeter"
            }
        }

class ErrorResponse(BaseModel):
    """Model for error responses."""
    error_type: str = Field(..., description="The type of error that occurred")
    message: str = Field(..., description="A human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    status_code: int = Field(..., description="The HTTP status code")

class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    response: str = Field(..., description="The agent's response to the message")
    agent_type: str = Field(..., description="The type of agent that handled the message")
    should_route: bool = Field(
        default=False,
        description="Whether the conversation should be routed to a specialist"
    )
    suggested_agent: Optional[str] = Field(
        None,
        description="The suggested specialist agent type if routing is recommended"
    )
    error: Optional[Dict[str, Any]] = Field(
        None,
        description="Error details if an error occurred"
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "Hello! Welcome to ChromaPages. How can I help you today?",
                "agent_type": "greeter",
                "should_route": False,
                "suggested_agent": None,
                "error": None
            }
        }

@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully processed the message",
            "model": ChatResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid request",
            "model": ErrorResponse
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        }
    },
    summary="Process a chat message",
    description="""
    Process a chat message and get a response from the appropriate agent.
    
    The message will be handled by the specified agent type, or the greeter agent by default.
    If the message requires specialist knowledge, the response will indicate that the conversation
    should be routed to a specialist agent.
    
    Rate limits apply to prevent abuse.
    """
)
async def chat(message: Message):
    """Handle chat messages and route to appropriate agents."""
    try:
        if not message.content.strip():
            raise ValidationError("Message content cannot be empty")
            
        if message.agent_type == "greeter":
            response = await greeter_agent.process_message(message.content)
            should_route = greeter_agent.should_route_to_specialist(message.content)
            suggested_agent = get_suggested_agent(message.content) if should_route else None
            
            return ChatResponse(
                response=response,
                agent_type="greeter",
                should_route=should_route,
                suggested_agent=suggested_agent
            )
            
        elif message.agent_type == "email":
            response = await email_agent.process_message(message.content)
            return ChatResponse(
                response=response,
                agent_type="email",
                should_route=email_agent.needs_escalation(message.content)
            )
            
        elif message.agent_type == "content":
            response = await content_agent.process_message(message.content)
            return ChatResponse(
                response=response,
                agent_type="content"
            )
            
        elif message.agent_type == "product":
            response = await product_agent.process_message(message.content)
            return ChatResponse(
                response=response,
                agent_type="product"
            )
            
        else:
            raise ValidationError("Invalid agent type", {"valid_types": ["greeter", "email", "content", "product"]})
            
    except BaseCustomException as e:
        error_details = handle_agent_error(e)
        logger.error(f"Agent error: {error_details}")
        return ChatResponse(
            response=error_details["message"],
            agent_type=message.agent_type,
            error=error_details
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        error_details = handle_agent_error(e)
        return ChatResponse(
            response="An unexpected error occurred. Please try again later.",
            agent_type=message.agent_type,
            error=error_details
        )

def get_suggested_agent(message: str) -> Optional[str]:
    """Determine which specialist agent to route to based on message content."""
    try:
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['content', 'page', 'seo', 'blog', 'website']):
            return "content"
        elif any(word in message_lower for word in ['email', 'spam', 'newsletter']):
            return "email"
        elif any(word in message_lower for word in ['product', 'item', 'price', 'stock']):
            return "product"
        
        return None
        
    except Exception as e:
        logger.error(f"Error in agent suggestion: {str(e)}")
        return None

class AgentType(BaseModel):
    """Model for agent type information."""
    type: str = Field(..., description="The agent type identifier")
    name: str = Field(..., description="The display name of the agent")
    description: str = Field(..., description="A description of the agent's role")

class AgentTypesResponse(BaseModel):
    """Response model for agent types endpoint."""
    available_agents: List[AgentType] = Field(
        ...,
        description="List of available agent types"
    )

@router.get(
    "/types",
    response_model=AgentTypesResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved agent types",
            "model": AgentTypesResponse
        }
    },
    summary="Get available agent types",
    description="Retrieve a list of all available agent types and their descriptions."
)
async def get_agent_types():
    """Get available agent types."""
    try:
        return AgentTypesResponse(
            available_agents=[
                AgentType(
                    type="greeter",
                    name="Customer Service Greeter",
                    description="Initial contact and routing agent"
                ),
                AgentType(
                    type="email",
                    name="Email Management Specialist",
                    description="Handles email-related inquiries"
                ),
                AgentType(
                    type="content",
                    name="Content Management Specialist",
                    description="Handles content creation and optimization"
                ),
                AgentType(
                    type="product",
                    name="Product Information Specialist",
                    description="Provides product information and recommendations"
                )
            ]
        )
    except Exception as e:
        logger.error(f"Error retrieving agent types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent types"
        )

class ConversationMessage(BaseModel):
    """Model for a conversation message."""
    role: str = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")
    timestamp: float = Field(..., description="The Unix timestamp of the message")

class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history endpoint."""
    history: List[ConversationMessage] = Field(
        ...,
        description="List of conversation messages"
    )

@router.get(
    "/conversation/{agent_type}",
    response_model=ConversationHistoryResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Successfully retrieved conversation history",
            "model": ConversationHistoryResponse
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid agent type",
            "model": ErrorResponse
        }
    },
    summary="Get conversation history",
    description="""
    Retrieve the conversation history for a specific agent type.
    
    The history includes all messages exchanged with the agent, including
    user messages, agent responses, and system messages.
    """
)
async def get_conversation_history(
    agent_type: str = Field(
        ...,
        description="The type of agent to get history for",
        example="greeter"
    )
):
    """Get conversation history for a specific agent."""
    try:
        if agent_type == "greeter":
            return ConversationHistoryResponse(history=greeter_agent.get_conversation_history())
        elif agent_type == "email":
            return ConversationHistoryResponse(history=email_agent.get_conversation_history())
        elif agent_type == "content":
            return ConversationHistoryResponse(history=content_agent.get_conversation_history())
        elif agent_type == "product":
            return ConversationHistoryResponse(history=product_agent.get_conversation_history())
        else:
            raise ValidationError(
                "Invalid agent type",
                {"valid_types": ["greeter", "email", "content", "product"]}
            )
            
    except ValidationError as e:
        error_details = handle_agent_error(e)
        raise HTTPException(
            status_code=error_details["status_code"],
            detail=error_details
        )
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history"
        ) 
