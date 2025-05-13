"""Configuration models for the Smart Steps AI module."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration."""

    name: str = "smart_steps_ai"
    version: str = "0.1.0"
    environment: str = Field(default="development", pattern="^(development|testing|production)$")
    log_level: str = Field(default="info", pattern="^(debug|info|warning|error|critical)$")


class PathsConfig(BaseModel):
    """Path configuration."""

    personas_dir: str = "../ss_unity/resources/ai_module/config/personas"
    sessions_dir: str = "data/sessions"
    logs_dir: str = "logs"
    exports_dir: str = "data/exports"


class AIConfig(BaseModel):
    """AI provider configuration."""

    provider: str = Field(default="anthropic", pattern="^(anthropic|mock)$")
    default_model: str = "claude-3-5-sonnet"
    max_tokens: int = Field(default=4000, ge=1, le=100000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    default_persona: str = "professional_therapist"


class MemoryConfig(BaseModel):
    """Memory system configuration."""

    enabled: bool = True
    system: str = Field(default="claude-memory", pattern="^(claude-memory|none)$")
    memory_dir: str = "../claude-memory"


class SessionConfig(BaseModel):
    """Session management configuration."""

    default_session_type: str = "standard"
    max_history_length: int = Field(default=50, ge=1)
    auto_save: bool = True
    auto_save_interval: int = Field(default=60, ge=5, description="Interval in seconds")


class AnalysisConfig(BaseModel):
    """Analysis configuration."""

    default_insight_count: int = Field(default=3, ge=1, le=10)
    sentiment_analysis: bool = True
    progress_tracking: bool = True


class APIConfig(BaseModel):
    """API configuration."""

    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = Field(default=5000, ge=1024, le=65535)
    debug: bool = True
    allow_cors: bool = True


class Config(BaseModel):
    """Complete application configuration."""

    app: AppConfig = Field(default_factory=AppConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    api: APIConfig = Field(default_factory=APIConfig)

    class Config:
        """Pydantic config."""

        extra = "ignore"
