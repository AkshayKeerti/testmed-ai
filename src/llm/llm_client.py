"""
LLM Client for TrustMed AI
Integrates Ollama with Langchain for conversational AI
"""

from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TrustMedLLMClient:
    """LLM Client for TrustMed AI using Ollama + Langchain"""
    
    def __init__(self, model_name: str = "llama3.1:8b"):
        """Initialize LLM client"""
        self.model_name = model_name
        self.llm = OllamaLLM(model=model_name)
        logger.info(f"Initialized LLM client with model: {model_name}")
    
    def generate_response(self, message: str, context: str = "") -> str:
        """Generate response from LLM"""
        try:
            # Create prompt with context if provided
            if context:
                prompt = f"Context: {context}\n\nUser: {message}\n\nAssistant:"
            else:
                prompt = f"User: {message}\n\nAssistant:"
            
            response = self.llm.invoke(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."
    
    def chat_with_history(self, messages: List[Dict[str, str]]) -> str:
        """Chat with conversation history"""
        try:
            # Convert messages to Langchain format
            langchain_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    langchain_messages.append(AIMessage(content=msg["content"]))
            
            # Generate response
            response = self.llm.invoke(langchain_messages)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Error in chat with history: {e}")
            return "I apologize, but I'm having trouble processing your message right now."
    
    def test_connection(self) -> bool:
        """Test LLM connection"""
        try:
            response = self.generate_response("Hello, are you working?")
            return len(response) > 0
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False

# Test the LLM client
if __name__ == "__main__":
    client = TrustMedLLMClient()
    
    print("Testing LLM Client...")
    print(f"Connection test: {client.test_connection()}")
    
    # Test basic response
    response = client.generate_response("What is diabetes?")
    print(f"Response: {response}")
    
    # Test with context
    context = "Medical information: Diabetes is a metabolic disorder."
    response = client.generate_response("Tell me more about this condition.", context)
    print(f"Contextual response: {response}")
