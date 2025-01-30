"""
Agent modules for the AI Customer Service System
"""

from typing import Dict, Type
from langchain.agents import BaseSingleActionAgent

# This will be populated with agent implementations
AVAILABLE_AGENTS: Dict[str, Type[BaseSingleActionAgent]] = {} 