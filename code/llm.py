"""
LLM management module.
Provides unified interface for different LLM providers (OpenAI, Anthropic, Groq, Google Gemini).
"""

import os
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

# Load environment variables
load_dotenv()

def get_llm(model_name: str, temperature: float = 0.1) -> BaseChatModel:
    """
    Get an LLM instance based on model name.
    
    Supported providers:
    - OpenAI: gpt-4, gpt-4o, gpt-4o-mini, gpt-3.5-turbo
    - Anthropic: claude-sonnet-4-5, claude-opus-4, claude-3-5-sonnet, etc.
    - Groq: llama3-70b-8192, mixtral-8x7b-32768, etc.
    - Google: gemini-1.5-pro, gemini-2.5-flash, gemini-1.5-flash-8b, etc.
    
    Args:
        model_name: Name of the model to use
        temperature: Sampling temperature (0-1)
    
    Returns:
        BaseChatModel instance
    """
    model_lower = model_name.lower()
    
    # OpenAI models
    if any(x in model_lower for x in ['gpt-4', 'gpt-3.5']):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    # Anthropic Claude models
    elif any(x in model_lower for x in ['claude', 'sonnet', 'opus']):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    # Groq models
    elif any(x in model_lower for x in ['llama', 'mixtral', 'groq']):
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    # Google Gemini models
    elif 'gemini' in model_lower:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    else:
        raise ValueError(f"Unsupported model: {model_name}")
