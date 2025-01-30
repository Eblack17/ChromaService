"""
Configuration module for the AI Customer Service System
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

# Initialize the Gemini model
def get_llm(model_name: str = "gemini-pro", temperature: float = 0.7):
    """
    Get a configured instance of the Gemini model
    """
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        convert_system_message_to_human=True,
        google_api_key=GOOGLE_API_KEY,
    )

# Base system message for customer service
BASE_SYSTEM_MESSAGE = """You are a helpful and professional customer service AI assistant. 
Your responses should be:
1. Professional and courteous
2. Clear and concise
3. Accurate and helpful
4. Empathetic when appropriate

Always maintain a helpful and positive tone while staying focused on resolving the customer's needs."""

# Create a base chat prompt template
def get_base_chat_prompt():
    """
    Get the base chat prompt template with system message and chat history
    """
    return ChatPromptTemplate.from_messages([
        SystemMessage(content=BASE_SYSTEM_MESSAGE),
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="input"),
    ])

# Memory configuration
MEMORY_KEY = "chat_history"
HUMAN_PREFIX = "Customer"
AI_PREFIX = "Assistant"

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "customer_service_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
} 