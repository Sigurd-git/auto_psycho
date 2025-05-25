"""
Experiment session model for tracking TAT experiment sessions.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db


class ExperimentSession(db.Model):
    """
    Model representing a TAT experiment session.
    
    Attributes:
        id: Primary key for the session
        session_code: Unique identifier for the session
        participant_id: Foreign key to the participant
        status: Current status of the session (started, in_progress, completed, abandoned)
        start_time: When the session was started
        end_time: When the session was completed
        total_duration: Total time spent in seconds
        current_image_index: Index of current TAT image being shown
        instructions_shown: Whether instructions have been shown to participant
        notes: Optional notes about the session
        participant: Relationship to participant
        tat_responses: List of TAT responses in this session
        analysis_results: List of analysis results for this session
    """
    
    __tablename__ = 'experiment_sessions'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Session identification
    session_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Foreign key to participant
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey('participants.id'), nullable=False)
    
    # Session status and timing
    status: Mapped[str] = mapped_column(String(20), default='started')  # started, in_progress, completed, abandoned
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    total_duration: Mapped[Optional[int]] = mapped_column(Integer)  # Duration in seconds
    
    # Session progress
    current_image_index: Mapped[int] = mapped_column(Integer, default=0)
    instructions_shown: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Additional information
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant: Mapped["Participant"] = relationship("Participant", back_populates="experiment_sessions")
    tat_responses: Mapped[List["TATResponse"]] = relationship(
        "TATResponse", 
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="TATResponse.image_index"
    )
    analysis_results: Mapped[List["AnalysisResult"]] = relationship(
        "AnalysisResult", 
        back_populates="session",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the session."""
        return f'<ExperimentSession {self.session_code}>'
    
    def to_dict(self) -> dict:
        """Convert session to dictionary representation."""
        return {
            'id': self.id,
            'session_code': self.session_code,
            'participant_id': self.participant_id,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_duration': self.total_duration,
            'current_image_index': self.current_image_index,
            'instructions_shown': self.instructions_shown,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_session(cls, participant_id: int, session_code: str) -> "ExperimentSession":
        """
        Create a new experiment session.
        
        Args:
            participant_id: ID of the participant
            session_code: Unique session identifier
            
        Returns:
            New ExperimentSession instance
        """
        session = cls(
            participant_id=participant_id,
            session_code=session_code,
            status='started'
        )
        db.session.add(session)
        return session
    
    def start_experiment(self) -> None:
        """Mark the experiment as started and in progress."""
        self.status = 'in_progress'
        self.instructions_shown = True
        self.updated_at = datetime.utcnow()
    
    def complete_session(self) -> None:
        """Mark the session as completed and calculate duration."""
        self.status = 'completed'
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.total_duration = int((self.end_time - self.start_time).total_seconds())
        self.updated_at = datetime.utcnow()
    
    def abandon_session(self) -> None:
        """Mark the session as abandoned."""
        self.status = 'abandoned'
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.total_duration = int((self.end_time - self.start_time).total_seconds())
        self.updated_at = datetime.utcnow()
    
    def advance_to_next_image(self) -> None:
        """Advance to the next TAT image."""
        self.current_image_index += 1
        self.updated_at = datetime.utcnow()
    
    def get_completion_percentage(self, total_images: int = 10) -> float:
        """
        Calculate the completion percentage of the session.
        
        Args:
            total_images: Total number of TAT images in the experiment
            
        Returns:
            Completion percentage (0.0 to 100.0)
        """
        if total_images == 0:
            return 100.0
        return min((self.current_image_index / total_images) * 100, 100.0)
    
    def is_completed(self) -> bool:
        """Check if the session is completed."""
        return self.status == 'completed'
    
    def is_active(self) -> bool:
        """Check if the session is currently active."""
        return self.status in ['started', 'in_progress'] 