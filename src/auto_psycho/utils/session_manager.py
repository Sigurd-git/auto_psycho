"""
Session management utilities for the TAT experiment platform.
This module provides helper functions for managing experiment sessions.
"""

from typing import Optional, Dict, Any
from flask import session
from src.auto_psycho.models import Participant, ExperimentSession


class SessionManager:
    """
    Utility class for managing experiment sessions and participant data.
    """

    @staticmethod
    def get_current_participant() -> Optional[Participant]:
        """
        Get the current participant from the session.

        Returns:
            Participant instance if found, None otherwise
        """
        participant_id = session.get("participant_id")
        if participant_id:
            return Participant.query.get(participant_id)
        return None

    @staticmethod
    def get_current_session() -> Optional[ExperimentSession]:
        """
        Get the current experiment session from the session.

        Returns:
            ExperimentSession instance if found, None otherwise
        """
        session_id = session.get("session_id")
        if session_id:
            return ExperimentSession.query.get(session_id)
        return None

    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if the current user is authenticated (has valid session).

        Returns:
            True if authenticated, False otherwise
        """
        return all(
            [
                session.get("participant_id"),
                session.get("session_id"),
                session.get("participant_code"),
                session.get("session_code"),
            ]
        )

    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """
        Get current session information.

        Returns:
            Dictionary containing session information
        """
        return {
            "participant_id": session.get("participant_id"),
            "session_id": session.get("session_id"),
            "participant_code": session.get("participant_code"),
            "session_code": session.get("session_code"),
            "is_authenticated": SessionManager.is_authenticated(),
        }

    @staticmethod
    def clear_session() -> None:
        """Clear all session data."""
        keys_to_remove = [
            "participant_id",
            "session_id",
            "participant_code",
            "session_code",
        ]
        for key in keys_to_remove:
            session.pop(key, None)

    @staticmethod
    def validate_session() -> bool:
        """
        Validate that the current session is still valid.

        Returns:
            True if session is valid, False otherwise
        """
        if not SessionManager.is_authenticated():
            return False

        # Check if participant and session still exist in database
        participant = SessionManager.get_current_participant()
        experiment_session = SessionManager.get_current_session()

        if not participant or not experiment_session:
            SessionManager.clear_session()
            return False

        # Check if session belongs to participant
        if experiment_session.participant_id != participant.id:
            SessionManager.clear_session()
            return False

        return True

    @staticmethod
    def require_authentication(func):
        """
        Decorator to require authentication for view functions.

        Args:
            func: View function to decorate

        Returns:
            Decorated function
        """
        from functools import wraps
        from flask import redirect, url_for, flash

        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not SessionManager.validate_session():
                flash("请先注册或继续现有会话。", "error")
                return redirect(url_for("main.index"))
            return func(*args, **kwargs)

        return decorated_function
