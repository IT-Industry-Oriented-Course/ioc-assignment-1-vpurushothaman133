"""
Configuration Management for Clinical Workflow Agent
Loads settings from environment variables with validation
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field

class AgentConfig(BaseSettings):
    """Agent configuration with validation"""
    
    # HuggingFace API
    huggingface_api_token: str = Field(
        default="",
        description="HuggingFace API token for LLM access"
    )
    
    # Agent Mode
    agent_mode: Literal["sandbox", "production"] = Field(
        default="sandbox",
        description="Operating mode - sandbox uses mock data"
    )
    
    # Logging
    log_level: str = Field(default="INFO")
    enable_audit_log: bool = Field(default=True)
    
    # API Endpoints
    patient_api_base_url: str = Field(default="http://localhost:8000/api")
    insurance_api_base_url: str = Field(default="http://localhost:8000/api")
    scheduling_api_base_url: str = Field(default="http://localhost:8000/api")
    
    # LLM Configuration
    llm_model: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.2",
        description="HuggingFace model to use"
    )
    llm_temperature: float = Field(default=0.1)
    llm_max_tokens: int = Field(default=1000)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global config instance
config = AgentConfig()

def validate_config():
    """Validate critical configuration"""
    if not config.huggingface_api_token:
        raise ValueError(
            "HUGGINGFACE_API_TOKEN is required. "
            "Please set it in .env file or environment variable."
        )
    return True




