"""
Utility functions for LangChain operations
"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from ..config import get_llm, get_base_chat_prompt, MEMORY_KEY, HUMAN_PREFIX, AI_PREFIX

def create_chat_memory() -> ConversationBufferMemory:
    """
    Create a conversation memory instance
    """
    return ConversationBufferMemory(
        memory_key=MEMORY_KEY,
        return_messages=True,
        human_prefix=HUMAN_PREFIX,
        ai_prefix=AI_PREFIX,
    )

def create_conversation_chain(memory: ConversationBufferMemory = None) -> ConversationChain:
    """
    Create a conversation chain with memory
    """
    if memory is None:
        memory = create_chat_memory()
    
    return ConversationChain(
        llm=get_llm(),
        memory=memory,
        verbose=True
    )

def create_chat_pipeline(memory: ConversationBufferMemory = None):
    """
    Create a chat pipeline with memory and prompt template
    """
    if memory is None:
        memory = create_chat_memory()
    
    prompt = get_base_chat_prompt()
    model = get_llm()
    
    return (
        RunnablePassthrough.assign(
            chat_history=lambda x: memory.load_memory_variables({})[MEMORY_KEY]
        )
        | prompt
        | model
        | StrOutputParser()
    )

def format_chat_history(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """
    Format chat history messages into a structured format
    """
    formatted_messages = []
    for message in messages:
        if isinstance(message, HumanMessage):
            formatted_messages.append({
                "role": "user",
                "content": message.content
            })
        elif isinstance(message, AIMessage):
            formatted_messages.append({
                "role": "assistant",
                "content": message.content
            })
    return formatted_messages

def create_structured_output(message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a structured output format for responses
    """
    output = {
        "message": message,
        "status": "success",
    }
    
    if metadata:
        output["metadata"] = metadata
    
    return output 