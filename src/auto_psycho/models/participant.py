"""
Participant model for storing participant information.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import db


class Participant(db.Model):
    """
    Model representing a participant in the TAT experiment.
    
    Attributes:
        id: Primary key for the participant
        participant_code: Unique identifier for the participant
        age: Age of the participant
        gender: Gender of the participant
        education_level: Education level of the participant
        occupation: Occupation of the participant
        contact_info: Optional contact information
        consent_given: Whether participant has given informed consent
        created_at: Timestamp when participant was created
        updated_at: Timestamp when participant was last updated
        experiment_sessions: List of experiment sessions for this participant
    """
    
    __tablename__ = 'participants'
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Participant identification
    participant_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Demographic information
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    education_level: Mapped[Optional[str]] = mapped_column(String(100))
    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Contact and consent
    contact_info: Mapped[Optional[str]] = mapped_column(Text)
    consent_given: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiment_sessions: Mapped[List["ExperimentSession"]] = relationship(
        "ExperimentSession", 
        back_populates="participant",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        """String representation of the participant."""
        return f'<Participant {self.participant_code}>'
    
    def to_dict(self) -> dict:
        """Convert participant to dictionary representation."""
        return {
            'id': self.id,
            'participant_code': self.participant_code,
            'age': self.age,
            'gender': self.gender,
            'education_level': self.education_level,
            'occupation': self.occupation,
            'consent_given': self.consent_given,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def create_participant(cls, participant_code: str, **kwargs) -> "Participant":
        """
        Create a new participant with the given code and optional attributes.
        
        Args:
            participant_code: Unique identifier for the participant
            **kwargs: Additional participant attributes
            
        Returns:
            New Participant instance
        """
        participant = cls(participant_code=participant_code, **kwargs)
        db.session.add(participant)
        return participant
    
    def update_info(self, **kwargs) -> None:
        """
        Update participant information.
        
        Args:
            **kwargs: Attributes to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def give_consent(self) -> None:
        """Mark that the participant has given informed consent."""
        self.consent_given = True
        self.updated_at = datetime.utcnow() 