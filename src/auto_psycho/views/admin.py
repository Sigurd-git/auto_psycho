"""
Admin views for the Auto Psycho TAT Platform.
This module contains administrative routes and views.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from src.auto_psycho.models import db, Participant, ExperimentSession, TATResponse, AnalysisResult
from sqlalchemy import func
import csv
import io
from flask import make_response

# Create blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
def dashboard():
    """
    Admin dashboard with statistics and overview.
    
    Returns:
        Rendered admin dashboard template
    """
    # Get basic statistics
    stats = get_dashboard_stats()
    
    # Get recent sessions
    recent_sessions = ExperimentSession.query.order_by(
        ExperimentSession.created_at.desc()
    ).limit(10).all()
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_sessions=recent_sessions
    )


@admin_bp.route('/participants')
def participants():
    """
    List all participants with pagination.
    
    Returns:
        Rendered participants list template
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    participants = Participant.query.order_by(
        Participant.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'admin/participants.html',
        participants=participants
    )


@admin_bp.route('/sessions')
def sessions():
    """
    List all experiment sessions with filtering.
    
    Returns:
        Rendered sessions list template
    """
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    per_page = 20
    
    query = ExperimentSession.query
    
    if status_filter:
        query = query.filter(ExperimentSession.status == status_filter)
    
    sessions = query.order_by(
        ExperimentSession.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'admin/sessions.html',
        sessions=sessions,
        status_filter=status_filter
    )


@admin_bp.route('/session/<int:session_id>')
def session_detail(session_id):
    """
    Show detailed information about a specific session.
    
    Args:
        session_id: ID of the session to view
        
    Returns:
        Rendered session detail template
    """
    session = ExperimentSession.query.get_or_404(session_id)
    
    return render_template(
        'admin/session_detail.html',
        session=session
    )


@admin_bp.route('/responses')
def responses():
    """
    List all TAT responses with filtering.
    
    Returns:
        Rendered responses list template
    """
    page = request.args.get('page', 1, type=int)
    session_id = request.args.get('session_id', type=int)
    per_page = 20
    
    query = TATResponse.query
    
    if session_id:
        query = query.filter(TATResponse.session_id == session_id)
    
    responses = query.order_by(
        TATResponse.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'admin/responses.html',
        responses=responses,
        session_id=session_id
    )


@admin_bp.route('/analysis_results')
def analysis_results():
    """
    List all analysis results.
    
    Returns:
        Rendered analysis results template
    """
    page = request.args.get('page', 1, type=int)
    analysis_type = request.args.get('type', '')
    per_page = 20
    
    query = AnalysisResult.query
    
    if analysis_type:
        query = query.filter(AnalysisResult.analysis_type == analysis_type)
    
    results = query.order_by(
        AnalysisResult.created_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'admin/analysis_results.html',
        results=results,
        analysis_type=analysis_type
    )


@admin_bp.route('/export/participants')
def export_participants():
    """
    Export participants data as CSV.
    
    Returns:
        CSV file download response
    """
    participants = Participant.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Participant Code', 'Age', 'Gender', 'Education Level',
        'Occupation', 'Consent Given', 'Created At', 'Updated At'
    ])
    
    # Write data
    for participant in participants:
        writer.writerow([
            participant.id,
            participant.participant_code,
            participant.age,
            participant.gender,
            participant.education_level,
            participant.occupation,
            participant.consent_given,
            participant.created_at.isoformat() if participant.created_at else '',
            participant.updated_at.isoformat() if participant.updated_at else ''
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=participants.csv'
    
    return response


@admin_bp.route('/export/sessions')
def export_sessions():
    """
    Export sessions data as CSV.
    
    Returns:
        CSV file download response
    """
    sessions = ExperimentSession.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Session Code', 'Participant Code', 'Status', 'Start Time',
        'End Time', 'Total Duration', 'Current Image Index', 'Instructions Shown',
        'Created At'
    ])
    
    # Write data
    for session in sessions:
        writer.writerow([
            session.id,
            session.session_code,
            session.participant.participant_code,
            session.status,
            session.start_time.isoformat() if session.start_time else '',
            session.end_time.isoformat() if session.end_time else '',
            session.total_duration,
            session.current_image_index,
            session.instructions_shown,
            session.created_at.isoformat() if session.created_at else ''
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=sessions.csv'
    
    return response


@admin_bp.route('/export/responses')
def export_responses():
    """
    Export TAT responses data as CSV.
    
    Returns:
        CSV file download response
    """
    responses = TATResponse.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Session Code', 'Participant Code', 'Image Index', 'Image Filename',
        'Story Text', 'Response Time', 'Word Count', 'Emotional Tone',
        'Themes Identified', 'Response Timestamp'
    ])
    
    # Write data
    for response in responses:
        writer.writerow([
            response.id,
            response.session.session_code,
            response.session.participant.participant_code,
            response.image_index,
            response.image_filename,
            response.story_text,
            response.response_time,
            response.word_count,
            response.emotional_tone,
            response.themes_identified,
            response.response_timestamp.isoformat() if response.response_timestamp else ''
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=responses.csv'
    
    return response


@admin_bp.route('/api/stats')
def api_stats():
    """
    API endpoint for dashboard statistics.
    
    Returns:
        JSON response with statistics data
    """
    stats = get_dashboard_stats()
    return jsonify(stats)


@admin_bp.route('/api/delete_session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a session and all related data.
    
    Args:
        session_id: ID of the session to delete
        
    Returns:
        JSON response with success status
    """
    try:
        session = ExperimentSession.query.get_or_404(session_id)
        
        # Delete session (cascades to responses and analysis results)
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '会话已删除'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@admin_bp.route('/api/delete_participant/<int:participant_id>', methods=['DELETE'])
def delete_participant(participant_id):
    """
    Delete a participant and all related data.
    
    Args:
        participant_id: ID of the participant to delete
        
    Returns:
        JSON response with success status
    """
    try:
        participant = Participant.query.get_or_404(participant_id)
        
        # Delete participant (cascades to sessions, responses, and analysis results)
        db.session.delete(participant)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '参与者已删除'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


def get_dashboard_stats():
    """
    Get dashboard statistics.
    
    Returns:
        Dictionary containing various statistics
    """
    # Basic counts
    total_participants = Participant.query.count()
    total_sessions = ExperimentSession.query.count()
    completed_sessions = ExperimentSession.query.filter_by(status='completed').count()
    active_sessions = ExperimentSession.query.filter(
        ExperimentSession.status.in_(['started', 'in_progress'])
    ).count()
    total_responses = TATResponse.query.count()
    total_analyses = AnalysisResult.query.count()
    
    # Completion rate
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Average session duration for completed sessions
    avg_duration_result = db.session.query(
        func.avg(ExperimentSession.total_duration)
    ).filter(
        ExperimentSession.status == 'completed',
        ExperimentSession.total_duration.isnot(None)
    ).scalar()
    
    avg_duration = int(avg_duration_result) if avg_duration_result else 0
    
    # Sessions by status
    status_counts = db.session.query(
        ExperimentSession.status,
        func.count(ExperimentSession.id)
    ).group_by(ExperimentSession.status).all()
    
    status_distribution = {status: count for status, count in status_counts}
    
    # Recent activity (sessions created in last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_sessions = ExperimentSession.query.filter(
        ExperimentSession.created_at >= week_ago
    ).count()
    
    return {
        'total_participants': total_participants,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'active_sessions': active_sessions,
        'total_responses': total_responses,
        'total_analyses': total_analyses,
        'completion_rate': round(completion_rate, 1),
        'avg_duration_minutes': avg_duration // 60 if avg_duration else 0,
        'status_distribution': status_distribution,
        'recent_sessions': recent_sessions
    } 