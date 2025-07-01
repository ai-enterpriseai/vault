"""
Configuration management for VAULT_APP backend
"""

import os
from typing import List


class Settings:
    """Application settings."""
    
    def __init__(self):
        # Application
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        
        # API Configuration
        self.ALLOWED_ORIGINS: List[str] = [
            "http://localhost:3000",
            "http://localhost:5173"
        ]
        
        # Database
        self.QDRANT_URL: str = os.getenv("QDRANT_URL", "")
        self.QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
        self.QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "vault_documents")
        
        # API Keys
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "")
        self.COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
        
        # File handling
        self.MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
        self.UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")


# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings