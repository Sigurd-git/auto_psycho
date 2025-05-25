"""
Configuration settings for the Auto Psycho TAT Platform.
This module contains all configuration classes for different environments.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the base directory (project root)
basedir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(os.path.dirname(basedir))


class Config:
    """Base configuration class with common settings."""

    # Flask Configuration
    SECRET_KEY: str = (
        os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key-change-in-production"
    )

    # Database Configuration
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(project_dir, 'data', 'tat_experiment.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL") or "gpt-4o"

    # Application Configuration
    APP_NAME: str = os.environ.get("APP_NAME") or "Auto Psycho TAT Platform"
    APP_VERSION: str = os.environ.get("APP_VERSION") or "0.1.0"
    MAX_PARTICIPANTS: int = int(os.environ.get("MAX_PARTICIPANTS") or 1000)
    SESSION_TIMEOUT: int = int(os.environ.get("SESSION_TIMEOUT") or 3600)

    # Analysis Configuration
    ANALYSIS_LANGUAGE: str = os.environ.get("ANALYSIS_LANGUAGE") or "chinese"
    REPORT_FORMAT: str = os.environ.get("REPORT_FORMAT") or "detailed"

    # File Upload Configuration
    UPLOAD_FOLDER: str = "static/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size

    # TAT Configuration
    TAT_IMAGES_FOLDER: str = "static/tat_images"
    DEFAULT_TAT_IMAGES: int = 10  # Number of TAT images to show per session
    STORY_TIME_LIMIT: int = 300  # 5 minutes per story in seconds


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG: bool = True
    TESTING: bool = False


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG: bool = False
    TESTING: bool = False

    # Override with more secure settings for production
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(project_dir, 'data', 'tat_experiment.db')}"
    )


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG: bool = True
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = (
        "sqlite:///:memory:"  # In-memory database for testing
    )


# Configuration dictionary for easy access
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
