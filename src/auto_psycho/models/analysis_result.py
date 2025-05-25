"""
Analysis result model for storing AI-generated psychological analysis.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db


class AnalysisResult(db.Model):
    """
    Model representing AI-generated psychological analysis results.
    
    Attributes:
        id: Primary key for the analysis result
        session_id: Foreign key to the experiment session
        analysis_type: Type of analysis performed (individual_response, session_summary, personality_profile)
        ai_model_used: The AI model used for analysis
        analysis_prompt: The prompt used for AI analysis
        raw_analysis: Raw analysis output from AI
        structured_results: Structured analysis results (JSON)
        confidence_score: Confidence score of the analysis (0.0-1.0)
        psychological_themes: Identified psychological themes
        personality_traits: Identified personality traits
        emotional_patterns: Identified emotional patterns
        recommendations: AI-generated recommendations
        analysis_timestamp: When the analysis was performed
        session: Relationship to experiment session
    """
    
    __tablename__ = 'analysis_results'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign key to session
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey('experiment_sessions.id'), nullable=False)
    
    # Analysis metadata
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)  # individual_response, session_summary, personality_profile
    ai_model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    analysis_prompt: Mapped[Optional[str]] = mapped_column(Text)
    
    # Analysis results
    raw_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    structured_results: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    confidence_score: Mapped[Optional[float]] = mapped_column(Float)
    
    # Psychological insights
    psychological_themes: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    personality_traits: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    emotional_patterns: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    recommendations: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    analysis_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session: Mapped["ExperimentSession"] = relationship("ExperimentSession", back_populates="analysis_results")
    
    def __repr__(self) -> str:
        """String representation of the analysis result."""
        return f'<AnalysisResult {self.session_id}-{self.analysis_type}>'
    
    def to_dict(self) -> dict:
        """Convert analysis result to dictionary representation."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'analysis_type': self.analysis_type,
            'ai_model_used': self.ai_model_used,
            'raw_analysis': self.raw_analysis,
            'structured_results': self.structured_results,
            'confidence_score': self.confidence_score,
            'psychological_themes': self.psychological_themes,
            'personality_traits': self.personality_traits,
            'emotional_patterns': self.emotional_patterns,
            'recommendations': self.recommendations,
            'analysis_timestamp': self.analysis_timestamp.isoformat() if self.analysis_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_analysis(
        cls,
        session_id: int,
        analysis_type: str,
        ai_model_used: str,
        raw_analysis: str,
        analysis_prompt: Optional[str] = None,
        **kwargs
    ) -> "AnalysisResult":
        """
        Create a new analysis result.
        
        Args:
            session_id: ID of the experiment session
            analysis_type: Type of analysis performed
            ai_model_used: The AI model used for analysis
            raw_analysis: Raw analysis output from AI
            analysis_prompt: The prompt used for AI analysis
            **kwargs: Additional analysis attributes
            
        Returns:
            New AnalysisResult instance
        """
        analysis = cls(
            session_id=session_id,
            analysis_type=analysis_type,
            ai_model_used=ai_model_used,
            raw_analysis=raw_analysis,
            analysis_prompt=analysis_prompt,
            **kwargs
        )
        db.session.add(analysis)
        return analysis
    
    def update_structured_results(
        self,
        structured_results: Optional[str] = None,
        psychological_themes: Optional[str] = None,
        personality_traits: Optional[str] = None,
        emotional_patterns: Optional[str] = None,
        recommendations: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> None:
        """
        Update the analysis with structured results.
        
        Args:
            structured_results: Structured analysis results (JSON string)
            psychological_themes: Identified psychological themes (JSON string)
            personality_traits: Identified personality traits (JSON string)
            emotional_patterns: Identified emotional patterns (JSON string)
            recommendations: AI-generated recommendations
            confidence_score: Confidence score of the analysis
        """
        if structured_results is not None:
            self.structured_results = structured_results
        if psychological_themes is not None:
            self.psychological_themes = psychological_themes
        if personality_traits is not None:
            self.personality_traits = personality_traits
        if emotional_patterns is not None:
            self.emotional_patterns = emotional_patterns
        if recommendations is not None:
            self.recommendations = recommendations
        if confidence_score is not None:
            self.confidence_score = confidence_score
        self.updated_at = datetime.utcnow()
    
    def get_confidence_level(self) -> str:
        """
        Get the confidence level as a string.
        
        Returns:
            Confidence level: 'low', 'medium', 'high', or 'very_high'
        """
        if not self.confidence_score:
            return 'medium'
        
        if self.confidence_score < 0.3:
            return 'low'
        elif self.confidence_score < 0.6:
            return 'medium'
        elif self.confidence_score < 0.8:
            return 'high'
        else:
            return 'very_high'
    
    def is_session_analysis(self) -> bool:
        """Check if this is a session-level analysis."""
        return self.analysis_type in ['session_summary', 'personality_profile']
    
    def is_response_analysis(self) -> bool:
        """Check if this is a response-level analysis."""
        return self.analysis_type == 'individual_response' 