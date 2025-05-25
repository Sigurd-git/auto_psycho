"""
API views for the Auto Psycho TAT Platform.
This module contains RESTful API endpoints.
"""

from flask import Blueprint, jsonify, request
from src.auto_psycho.models import db, Participant, ExperimentSession, TATResponse, AnalysisResult
from src.auto_psycho.utils.session_manager import SessionManager
from src.auto_psycho.analysis.openai_analyzer import OpenAIAnalyzer

# Create blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with system status
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Auto Psycho TAT Platform is running'
    })


@api_bp.route('/stats')
def get_stats():
    """
    Get basic platform statistics.
    
    Returns:
        JSON response with statistics
    """
    stats = {
        'total_participants': Participant.query.count(),
        'total_sessions': ExperimentSession.query.count(),
        'completed_sessions': ExperimentSession.query.filter_by(status='completed').count(),
        'total_responses': TATResponse.query.count(),
        'total_analyses': AnalysisResult.query.count()
    }
    
    return jsonify(stats)


@api_bp.route('/session/<session_code>')
def get_session_info(session_code):
    """
    Get information about a specific session.
    
    Args:
        session_code: Session code to look up
        
    Returns:
        JSON response with session information
    """
    session = ExperimentSession.query.filter_by(session_code=session_code).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session': session.to_dict(),
        'participant': session.participant.to_dict(),
        'responses_count': len(session.tat_responses),
        'analysis_count': len(session.analysis_results)
    })


@api_bp.route('/session/<session_code>/responses')
def get_session_responses(session_code):
    """
    Get all responses for a specific session.
    
    Args:
        session_code: Session code to look up
        
    Returns:
        JSON response with session responses
    """
    session = ExperimentSession.query.filter_by(session_code=session_code).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    responses = [response.to_dict() for response in session.tat_responses]
    
    return jsonify({
        'session_code': session_code,
        'responses': responses,
        'total_count': len(responses)
    })


@api_bp.route('/session/<session_code>/analysis')
def get_session_analysis(session_code):
    """
    Get analysis results for a specific session.
    
    Args:
        session_code: Session code to look up
        
    Returns:
        JSON response with analysis results
    """
    session = ExperimentSession.query.filter_by(session_code=session_code).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    analyses = [analysis.to_dict() for analysis in session.analysis_results]
    
    return jsonify({
        'session_code': session_code,
        'analyses': analyses,
        'total_count': len(analyses)
    })


@api_bp.route('/analyze_session', methods=['POST'])
def analyze_session_api():
    """
    Trigger AI analysis for a session via API.
    
    Returns:
        JSON response with analysis results
    """
    data = request.get_json()
    
    if not data or 'session_code' not in data:
        return jsonify({'error': 'Session code is required'}), 400
    
    session_code = data['session_code']
    session = ExperimentSession.query.filter_by(session_code=session_code).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if not session.is_completed():
        return jsonify({'error': 'Session is not completed'}), 400
    
    try:
        # Initialize OpenAI analyzer
        analyzer = OpenAIAnalyzer()
        
        # Generate analysis
        analysis_type = data.get('analysis_type', 'session_summary')
        
        if analysis_type == 'session_summary':
            analysis_result = analyzer.analyze_session_summary(session)
        elif analysis_type == 'personality_profile':
            analysis_result = analyzer.generate_personality_profile(session)
        else:
            return jsonify({'error': 'Invalid analysis type'}), 400
        
        # Save analysis result
        analysis_record = AnalysisResult.create_analysis(
            session_id=session.id,
            analysis_type=analysis_type,
            ai_model_used=analyzer.model,
            raw_analysis=analysis_result['raw_analysis'],
            confidence_score=analysis_result.get('confidence_score'),
            psychological_themes=str(analysis_result.get('psychological_themes', [])),
            personality_traits=str(analysis_result.get('personality_traits', [])),
            emotional_patterns=str(analysis_result.get('emotional_patterns', [])),
            recommendations=analysis_result.get('recommendations', '')
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_record.id,
            'analysis_type': analysis_type,
            'confidence_score': analysis_result.get('confidence_score'),
            'message': 'Analysis completed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@api_bp.route('/participant/<participant_code>')
def get_participant_info(participant_code):
    """
    Get information about a specific participant.
    
    Args:
        participant_code: Participant code to look up
        
    Returns:
        JSON response with participant information
    """
    participant = Participant.query.filter_by(participant_code=participant_code).first()
    
    if not participant:
        return jsonify({'error': 'Participant not found'}), 404
    
    sessions = [session.to_dict() for session in participant.experiment_sessions]
    
    return jsonify({
        'participant': participant.to_dict(),
        'sessions': sessions,
        'total_sessions': len(sessions)
    })


@api_bp.route('/validate_session', methods=['POST'])
def validate_session_api():
    """
    Validate a session code via API.
    
    Returns:
        JSON response with validation result
    """
    data = request.get_json()
    
    if not data or 'session_code' not in data:
        return jsonify({'error': 'Session code is required'}), 400
    
    session_code = data['session_code']
    session = ExperimentSession.query.filter_by(session_code=session_code).first()
    
    if not session:
        return jsonify({
            'valid': False,
            'error': 'Session not found'
        })
    
    return jsonify({
        'valid': True,
        'session': session.to_dict(),
        'participant': session.participant.to_dict(),
        'is_active': session.is_active(),
        'is_completed': session.is_completed()
    })


@api_bp.route('/create_participant', methods=['POST'])
def create_participant_api():
    """
    Create a new participant via API.
    
    Returns:
        JSON response with participant information
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request data is required'}), 400
    
    # Validate required fields
    if not data.get('consent_given'):
        return jsonify({'error': 'Consent is required'}), 400
    
    try:
        import uuid
        
        # Generate unique participant code
        participant_code = f"TAT_{uuid.uuid4().hex[:8].upper()}"
        
        # Create participant
        participant = Participant.create_participant(
            participant_code=participant_code,
            age=data.get('age'),
            gender=data.get('gender'),
            education_level=data.get('education_level'),
            occupation=data.get('occupation'),
            contact_info=data.get('contact_info'),
            consent_given=data.get('consent_given', False)
        )
        
        # Create experiment session
        session_code = f"SESSION_{uuid.uuid4().hex[:12].upper()}"
        experiment_session = ExperimentSession.create_session(
            participant_id=participant.id,
            session_code=session_code
        )
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'participant': participant.to_dict(),
            'session': experiment_session.to_dict(),
            'participant_code': participant_code,
            'session_code': session_code
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to create participant: {str(e)}'
        }), 500


@api_bp.route('/submit_response', methods=['POST'])
def submit_response_api():
    """
    Submit a TAT response via API.
    
    Returns:
        JSON response with submission result
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request data is required'}), 400
    
    # Validate required fields
    required_fields = ['session_code', 'image_index', 'story_text']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    session_code = data['session_code']
    session = ExperimentSession.query.filter_by(session_code=session_code).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.is_completed():
        return jsonify({'error': 'Session is already completed'}), 400
    
    try:
        # Create TAT response
        response = TATResponse.create_response(
            session_id=session.id,
            image_index=data['image_index'],
            image_filename=data.get('image_filename', f"tat_{data['image_index']:02d}.jpg"),
            story_text=data['story_text'],
            response_time=data.get('response_time')
        )
        
        # Update session progress
        if data['image_index'] >= session.current_image_index:
            session.current_image_index = data['image_index'] + 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'response_id': response.id,
            'session_progress': session.current_image_index,
            'message': 'Response submitted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to submit response: {str(e)}'
        }), 500


@api_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API endpoints."""
    return jsonify({'error': 'API endpoint not found'}), 404


@api_bp.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors for API endpoints."""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500 