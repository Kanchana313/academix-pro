import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Academix Pro - Student Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./students.db"
    
    # Ollama AI Configuration (Optional bonus extension)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Base URL of local Ollama instance")
    OLLAMA_MODEL: str = Field(default="llama3.2:1b", description="Default model for natural language questions")
    OLLAMA_TIMEOUT_SECONDS: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
