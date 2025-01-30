from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()

def test_gemini_setup():
    try:
        # Initialize the Gemini chat model
        chat = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )
        
        # Test message
        messages = [
            HumanMessage(content="Hello! Can you tell me what's 2+2?")
        ]
        
        # Get response
        response = chat.invoke(messages)
        print("Response from Gemini:", response.content)
        print("\nSetup successful! Your environment is ready to use LangChain with Gemini.")
        
    except Exception as e:
        print("Error during setup test:", str(e))

if __name__ == "__main__":
    test_gemini_setup() 