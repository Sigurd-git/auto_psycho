"""
TAT response model for storing participant responses to TAT images.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db


class TATResponse(db.Model):
    """
    Model representing a participant's response to a TAT image.
    
    Attributes:
        id: Primary key for the response
        session_id: Foreign key to the experiment session
        image_index: Index of the TAT image (0-based)
        image_filename: Filename of the TAT image shown
        story_text: The story told by the participant
        response_time: Time taken to respond in seconds
        word_count: Number of words in the story
        emotional_tone: Detected emotional tone of the story
        themes_identified: Identified psychological themes
        response_timestamp: When the response was recorded
        session: Relationship to experiment session
    """
    
    __tablename__ = 'tat_responses'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Foreign key to session
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey('experiment_sessions.id'), nullable=False)
    
    # Image information
    image_index: Mapped[int] = mapped_column(Integer, nullable=False)
    image_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Response content
    story_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_time: Mapped[Optional[float]] = mapped_column(Float)  # Time in seconds
    word_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Analysis fields (populated by AI analysis)
    emotional_tone: Mapped[Optional[str]] = mapped_column(String(100))
    themes_identified: Mapped[Optional[str]] = mapped_column(Text)  # JSON string of themes
    
    # Timestamps
    response_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session: Mapped["ExperimentSession"] = relationship("ExperimentSession", back_populates="tat_responses")
    
    def __repr__(self) -> str:
        """String representation of the response."""
        return f'<TATResponse {self.session_id}-{self.image_index}>'
    
    def to_dict(self) -> dict:
        """Convert response to dictionary representation."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'image_index': self.image_index,
            'image_filename': self.image_filename,
            'story_text': self.story_text,
            'response_time': self.response_time,
            'word_count': self.word_count,
            'emotional_tone': self.emotional_tone,
            'themes_identified': self.themes_identified,
            'response_timestamp': self.response_timestamp.isoformat() if self.response_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_response(
        cls, 
        session_id: int, 
        image_index: int, 
        image_filename: str, 
        story_text: str,
        response_time: Optional[float] = None
    ) -> "TATResponse":
        """
        Create a new TAT response.
        
        Args:
            session_id: ID of the experiment session
            image_index: Index of the TAT image
            image_filename: Filename of the TAT image
            story_text: The story told by the participant
            response_time: Time taken to respond in seconds
            
        Returns:
            New TATResponse instance
        """
        # Calculate word count
        word_count = len(story_text.split()) if story_text else 0
        
        response = cls(
            session_id=session_id,
            image_index=image_index,
            image_filename=image_filename,
            story_text=story_text,
            response_time=response_time,
            word_count=word_count
        )
        db.session.add(response)
        return response
    
    def update_analysis(
        self, 
        emotional_tone: Optional[str] = None, 
        themes_identified: Optional[str] = None
    ) -> None:
        """
        Update the response with analysis results.
        
        Args:
            emotional_tone: Detected emotional tone
            themes_identified: Identified psychological themes (JSON string)
        """
        if emotional_tone is not None:
            self.emotional_tone = emotional_tone
        if themes_identified is not None:
            self.themes_identified = themes_identified
        self.updated_at = datetime.utcnow()
    
    def get_story_length_category(self) -> str:
        """
        Categorize the story length based on word count.
        
        Returns:
            Category string: 'short', 'medium', 'long', or 'very_long'
        """
        if not self.word_count:
            return 'short'
        
        if self.word_count < 50:
            return 'short'
        elif self.word_count < 150:
            return 'medium'
        elif self.word_count < 300:
            return 'long'
        else:
            return 'very_long'
    
    def get_response_speed_category(self) -> str:
        """
        Categorize the response speed based on response time.
        
        Returns:
            Category string: 'fast', 'normal', 'slow', or 'very_slow'
        """
        if not self.response_time:
            return 'normal'
        
        if self.response_time < 60:  # Less than 1 minute
            return 'fast'
        elif self.response_time < 180:  # Less than 3 minutes
            return 'normal'
        elif self.response_time < 300:  # Less than 5 minutes
            return 'slow'
        else:
            return 'very_slow' 