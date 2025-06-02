"""LLM Manager for handling multiple AI providers"""

import os
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None
    Anthropic = None

try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_community.llms import HuggingFacePipeline
except ImportError:
    ChatOpenAI = None
    ChatAnthropic = None
    HuggingFacePipeline = None

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"


class LLMManager:
    """Manages multiple LLM providers and provides unified interface"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers based on API keys"""
        
        # OpenAI
        if settings.openai_api_key and OpenAI:
            try:
                self.providers[LLMProvider.OPENAI] = {
                    "client": OpenAI(api_key=settings.openai_api_key),
                    "langchain": ChatOpenAI(
                        api_key=settings.openai_api_key,
                        model="gpt-3.5-turbo",
                        temperature=0.7
                    ) if ChatOpenAI else None
                }
                if not self.default_provider:
                    self.default_provider = LLMProvider.OPENAI
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Anthropic
        if settings.anthropic_api_key and Anthropic:
            try:
                self.providers[LLMProvider.ANTHROPIC] = {
                    "client": Anthropic(api_key=settings.anthropic_api_key),
                    "langchain": ChatAnthropic(
                        api_key=settings.anthropic_api_key,
                        model="claude-3-sonnet-20240229",
                        temperature=0.7
                    ) if ChatAnthropic else None
                }
                if not self.default_provider:
                    self.default_provider = LLMProvider.ANTHROPIC
                logger.info("Anthropic provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
        
        # Azure OpenAI
        if settings.azure_openai_api_key and settings.azure_openai_endpoint and OpenAI:
            try:
                self.providers[LLMProvider.AZURE_OPENAI] = {
                    "client": OpenAI(
                        api_key=settings.azure_openai_api_key,
                        azure_endpoint=settings.azure_openai_endpoint,
                        api_version=settings.azure_openai_api_version
                    ),
                    "langchain": ChatOpenAI(
                        api_key=settings.azure_openai_api_key,
                        azure_endpoint=settings.azure_openai_endpoint,
                        api_version=settings.azure_openai_api_version,
                        model="gpt-35-turbo"
                    ) if ChatOpenAI else None
                }
                if not self.default_provider:
                    self.default_provider = LLMProvider.AZURE_OPENAI
                logger.info("Azure OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
        
        # Hugging Face (local/free option)
        if settings.huggingface_api_token:
            try:
                # This would use a local model or HF inference API
                self.providers[LLMProvider.HUGGINGFACE] = {
                    "client": None,  # Would implement HF client
                    "langchain": None  # Would implement HF pipeline
                }
                if not self.default_provider:
                    self.default_provider = LLMProvider.HUGGINGFACE
                logger.info("Hugging Face provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Hugging Face: {e}")
        
        # Fallback to local/mock provider if no API keys
        if not self.providers:
            self.providers[LLMProvider.LOCAL] = {
                "client": None,
                "langchain": None
            }
            self.default_provider = LLMProvider.LOCAL
            logger.warning("No API keys found, using local/mock provider")
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Get provider client"""
        if provider is None:
            provider = self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        return self.providers[provider]
    
    def get_langchain_llm(self, provider: Optional[LLMProvider] = None):
        """Get LangChain LLM instance"""
        provider_info = self.get_provider(provider)
        return provider_info.get("langchain")
    
    async def generate_response(
        self, 
        prompt: str, 
        provider: Optional[LLMProvider] = None,
        **kwargs
    ) -> str:
        """Generate response using specified provider"""
        
        if provider is None:
            provider = self.default_provider
        
        provider_info = self.get_provider(provider)
        client = provider_info["client"]
        
        try:
            if provider == LLMProvider.OPENAI or provider == LLMProvider.AZURE_OPENAI:
                response = client.chat.completions.create(
                    model=kwargs.get("model", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000)
                )
                return response.choices[0].message.content
            
            elif provider == LLMProvider.ANTHROPIC:
                response = client.messages.create(
                    model=kwargs.get("model", "claude-3-sonnet-20240229"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000)
                )
                return response.content[0].text
            
            elif provider == LLMProvider.LOCAL:
                # Mock response for local provider
                return f"Mock response for: {prompt[:100]}..."
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Error generating response with {provider}: {e}")
            # Fallback to mock response
            return f"Error occurred. Mock response for: {prompt[:100]}..."
    
    def get_embedding_model(self, provider: Optional[LLMProvider] = None):
        """Get embedding model for the provider"""
        if provider is None:
            provider = self.default_provider
        
        # For now, we'll use sentence-transformers as default
        # This can be extended to use provider-specific embeddings
        try:
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            logger.warning("sentence-transformers not available, using mock embeddings")
            return None


# Global LLM manager instance
llm_manager = LLMManager()