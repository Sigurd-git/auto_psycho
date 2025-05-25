"""
Main views for the Auto Psycho TAT Platform.
This module contains the main application routes and views.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.auto_psycho.models import db, Participant, ExperimentSession
from src.auto_psycho.utils.session_manager import SessionManager
import uuid

# Create blueprint
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """
    Home page of the TAT platform.

    Returns:
        Rendered home page template
    """
    return render_template("index.html")


@main_bp.route("/about")
def about():
    """
    About page with information about TAT and the platform.

    Returns:
        Rendered about page template
    """
    return render_template("about.html")


@main_bp.route("/consent")
def consent():
    """
    Informed consent page for participants.

    Returns:
        Rendered consent page template
    """
    return render_template("consent.html")


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Participant registration page.

    Returns:
        GET: Rendered registration form
        POST: Redirect to experiment or registration form with errors
    """
    if request.method == "POST":
        try:
            # Get form data
            age = request.form.get("age", type=int)
            gender = request.form.get("gender")
            education_level = request.form.get("education_level")
            occupation = request.form.get("occupation")
            contact_info = request.form.get("contact_info")
            consent_given = request.form.get("consent_given") == "on"

            # Validate required fields
            if not consent_given:
                flash("您必须同意参与实验才能继续。", "error")
                return render_template("register.html")

            # Generate unique participant code
            participant_code = f"TAT_{uuid.uuid4().hex[:8].upper()}"

            # Create participant
            participant = Participant.create_participant(
                participant_code=participant_code,
                age=age,
                gender=gender,
                education_level=education_level,
                occupation=occupation,
                contact_info=contact_info,
                consent_given=consent_given,
            )

            # Commit participant first to get the ID
            db.session.commit()

            # Create experiment session using the participant ID
            session_code = f"SESSION_{uuid.uuid4().hex[:12].upper()}"
            experiment_session = ExperimentSession.create_session(
                participant_id=participant.id, session_code=session_code
            )

            # Commit session to database
            db.session.commit()

            # Store session information
            session["participant_id"] = participant.id
            session["session_id"] = experiment_session.id
            session["participant_code"] = participant_code
            session["session_code"] = session_code

            flash(f"注册成功！您的参与者编号是：{participant_code}", "success")

            # Directly render instructions template instead of redirecting
            session_info = {
                "participant_code": participant_code,
                "session_code": session_code,
            }
            return render_template(
                "experiment/instructions.html", session_info=session_info
            )

        except Exception as e:
            # Rollback the transaction in case of any error
            db.session.rollback()
            flash("注册过程中出现错误，请重试。", "error")
            return render_template("register.html")

    return render_template("register.html")


@main_bp.route("/continue", methods=["GET", "POST"])
def continue_session():
    """
    Continue an existing experiment session.

    Returns:
        GET: Rendered continue session form
        POST: Redirect to experiment or form with errors
    """
    if request.method == "POST":
        participant_code = request.form.get("participant_code", "").strip()

        if not participant_code:
            flash("请输入您的参与者编号。", "error")
            return render_template("continue.html")

        # Find participant
        participant = Participant.query.filter_by(
            participant_code=participant_code
        ).first()
        if not participant:
            flash("未找到该参与者编号，请检查后重试。", "error")
            return render_template("continue.html")

        # Find active session
        active_session = (
            ExperimentSession.query.filter_by(participant_id=participant.id)
            .filter(ExperimentSession.status.in_(["started", "in_progress"]))
            .first()
        )

        if not active_session:
            flash("未找到活跃的实验会话，请重新注册。", "error")
            return redirect(url_for("main.register"))

        # Store session information
        session["participant_id"] = participant.id
        session["session_id"] = active_session.id
        session["participant_code"] = participant_code
        session["session_code"] = active_session.session_code

        flash(f"欢迎回来，{participant_code}！", "success")

        # Redirect based on session status
        if active_session.status == "started":
            return redirect(url_for("experiment.instructions"))
        else:
            return redirect(url_for("experiment.experiment"))

    return render_template("continue.html")


@main_bp.route("/statistics")
def statistics():
    """
    Public statistics page showing experiment participation data.

    Returns:
        Rendered statistics page template
    """
    # Get basic statistics
    total_participants = Participant.query.count()
    completed_sessions = ExperimentSession.query.filter_by(status="completed").count()
    active_sessions = ExperimentSession.query.filter(
        ExperimentSession.status.in_(["started", "in_progress"])
    ).count()

    stats = {
        "total_participants": total_participants,
        "completed_sessions": completed_sessions,
        "active_sessions": active_sessions,
        "completion_rate": (completed_sessions / total_participants * 100)
        if total_participants > 0
        else 0,
    }

    return render_template("statistics.html", stats=stats)


@main_bp.route("/help")
def help():
    """
    Help page with instructions and FAQ.

    Returns:
        Rendered help page template
    """
    return render_template("help.html")


@main_bp.route("/test_instructions")
def test_instructions():
    """Temporary test route for instructions template."""
    session_info = {
        "participant_code": "TEST_12345678",
        "session_code": "SESSION_TEST123456",
    }
    return render_template("experiment/instructions.html", session_info=session_info)


@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template("errors/404.html"), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template("errors/500.html"), 500
