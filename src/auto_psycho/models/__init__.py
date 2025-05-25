"""
Database models for the Auto Psycho TAT Platform.
This package contains all SQLAlchemy models for the application.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models to make them available when importing this package
from .participant import Participant
from .experiment_session import ExperimentSession
from .tat_response import TATResponse
from .analysis_result import AnalysisResult

__all__ = [
    'db',
    'Participant',
    'ExperimentSession', 
    'TATResponse',
    'AnalysisResult'
] 