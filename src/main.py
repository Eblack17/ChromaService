from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from .utils import create_chat_pipeline, create_chat_memory, create_structured_output
from .config import get_llm

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Customer Service System",
    description="A Multi-Agent System for customer service using LangChain and Google's Gemini",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a chat memory instance
chat_memory = create_chat_memory()

# Create a chat pipeline
chat_pipeline = create_chat_pipeline(chat_memory)

class ChatInput(BaseModel):
    message: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Customer Service System",
        "version": "1.0.0",
        "status": "operational"
    }

# Chat endpoint
@app.post("/chat")
async def chat(chat_input: ChatInput):
    try:
        # Process the message through the chat pipeline
        response = chat_pipeline.invoke({"input": chat_input.message})
        
        # Create structured response
        return create_structured_output(
            message=response,
            metadata={
                "model": "gemini-pro",
                "type": "chat"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("APP_PORT", 8000))) 
