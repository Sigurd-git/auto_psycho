"""
Experiment views for the Auto Psycho TAT Platform.
This module contains experiment-related routes and views.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from src.auto_psycho.models import db, ExperimentSession, TATResponse
from src.auto_psycho.utils.session_manager import SessionManager
from src.auto_psycho.analysis.openai_analyzer import OpenAIAnalyzer
import time
import os
import glob

# Create blueprint
experiment_bp = Blueprint("experiment", __name__)


@experiment_bp.route("/instructions")
@SessionManager.require_authentication
def instructions():
    """
    Show experiment instructions to the participant.

    Returns:
        Rendered instructions page template
    """
    session_info = SessionManager.get_session_info()
    return render_template("experiment/instructions.html", session_info=session_info)


@experiment_bp.route("/start", methods=["POST"])
@SessionManager.require_authentication
def start_experiment():
    """
    Start the TAT experiment.

    Returns:
        Redirect to first TAT image
    """
    experiment_session = SessionManager.get_current_session()
    if experiment_session:
        experiment_session.start_experiment()
        db.session.commit()
        flash("实验已开始！", "success")

    return redirect(url_for("experiment.experiment"))


@experiment_bp.route("/experiment")
@SessionManager.require_authentication
def experiment():
    """
    Main experiment page showing TAT images and collecting responses.

    Returns:
        Rendered experiment page template
    """
    experiment_session = SessionManager.get_current_session()
    if not experiment_session:
        flash("会话无效，请重新开始。", "error")
        return redirect(url_for("main.index"))

    # Check if experiment is completed
    if experiment_session.is_completed():
        return redirect(url_for("experiment.results"))

    # Get current image index
    current_index = experiment_session.current_image_index

    # Get available TAT images
    tat_images = get_tat_images()

    # Check if all images are completed
    if current_index >= len(tat_images):
        experiment_session.complete_session()
        db.session.commit()
        return redirect(url_for("experiment.results"))

    # Get current image
    current_image = tat_images[current_index]

    # Calculate progress
    progress = ((current_index) / len(tat_images)) * 100

    return render_template(
        "experiment/experiment.html",
        current_image=current_image,
        current_index=current_index,
        total_images=len(tat_images),
        progress=progress,
        session_info=SessionManager.get_session_info(),
    )


@experiment_bp.route("/submit_response", methods=["POST"])
@SessionManager.require_authentication
def submit_response():
    """
    Submit a TAT response and advance to next image.

    Returns:
        JSON response with success status
    """
    experiment_session = SessionManager.get_current_session()
    if not experiment_session:
        return jsonify({"success": False, "error": "会话无效"})

    # Get form data
    story_text = request.form.get("story_text", "").strip()
    image_index = request.form.get("image_index", type=int)
    response_time = request.form.get("response_time", type=float)

    # Validate input
    if not story_text:
        return jsonify({"success": False, "error": "请输入故事内容"})

    if len(story_text) < 20:
        return jsonify({"success": False, "error": "故事内容太短，请至少输入20个字符"})

    # Get image filename
    tat_images = get_tat_images()
    if image_index >= len(tat_images):
        return jsonify({"success": False, "error": "图片索引无效"})

    image_filename = tat_images[image_index]

    # Create TAT response
    tat_response = TATResponse.create_response(
        session_id=experiment_session.id,
        image_index=image_index,
        image_filename=image_filename,
        story_text=story_text,
        response_time=response_time,
    )

    # Advance to next image
    experiment_session.advance_to_next_image()

    # Commit to database
    db.session.commit()

    # Check if experiment is completed
    if experiment_session.current_image_index >= len(tat_images):
        experiment_session.complete_session()
        db.session.commit()
        return jsonify(
            {
                "success": True,
                "completed": True,
                "redirect_url": url_for("experiment.results"),
            }
        )

    return jsonify({"success": True, "completed": False})


@experiment_bp.route("/results")
@SessionManager.require_authentication
def results():
    """
    Show experiment results and AI analysis.

    Returns:
        Rendered results page template
    """
    experiment_session = SessionManager.get_current_session()
    if not experiment_session:
        flash("会话无效，请重新开始。", "error")
        return redirect(url_for("main.index"))

    if not experiment_session.is_completed():
        flash("请先完成实验。", "warning")
        return redirect(url_for("experiment.experiment"))

    # Get all responses
    responses = experiment_session.tat_responses

    # Check if analysis already exists
    existing_analysis = experiment_session.analysis_results

    return render_template(
        "experiment/results.html",
        experiment_session=experiment_session,
        responses=responses,
        analysis_results=existing_analysis,
        session_info=SessionManager.get_session_info(),
    )


@experiment_bp.route("/analyze", methods=["POST"])
@SessionManager.require_authentication
def analyze_responses():
    """
    Trigger AI analysis of TAT responses.

    Returns:
        JSON response with analysis status
    """
    experiment_session = SessionManager.get_current_session()
    if not experiment_session:
        return jsonify({"success": False, "error": "会话无效"})

    if not experiment_session.is_completed():
        return jsonify({"success": False, "error": "请先完成实验"})

    try:
        # Initialize OpenAI analyzer
        analyzer = OpenAIAnalyzer()

        # Generate session summary analysis
        session_analysis = analyzer.analyze_session_summary(experiment_session)

        # Create analysis result record
        from src.auto_psycho.models import AnalysisResult

        analysis_result = AnalysisResult.create_analysis(
            session_id=experiment_session.id,
            analysis_type="session_summary",
            ai_model_used=analyzer.model,
            raw_analysis=session_analysis["raw_analysis"],
            confidence_score=session_analysis.get("confidence_score"),
            psychological_themes=str(session_analysis.get("psychological_themes", [])),
            personality_traits=str(session_analysis.get("personality_traits", [])),
            emotional_patterns=str(session_analysis.get("emotional_patterns", [])),
            recommendations=session_analysis.get("recommendations", ""),
        )

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "analysis_id": analysis_result.id,
                "message": "AI分析完成！",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"分析过程中出现错误: {str(e)}"})


@experiment_bp.route("/download_report/<int:analysis_id>")
@SessionManager.require_authentication
def download_report(analysis_id):
    """
    Download analysis report as PDF or text file.

    Args:
        analysis_id: ID of the analysis result

    Returns:
        File download response
    """
    from src.auto_psycho.models import AnalysisResult
    from flask import make_response

    analysis = AnalysisResult.query.get_or_404(analysis_id)

    # Verify that the analysis belongs to the current session
    current_session = SessionManager.get_current_session()
    if not current_session or analysis.session_id != current_session.id:
        flash("无权访问该分析报告。", "error")
        return redirect(url_for("experiment.results"))

    # Generate report content
    report_content = generate_report_content(analysis)

    # Create response
    response = make_response(report_content)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f"attachment; filename=TAT_Analysis_Report_{analysis_id}.txt"
    )

    return response


def get_tat_images():
    """
    Get list of available TAT images.

    Returns:
        List of TAT image filenames
    """
    # Look for TAT images in the Flask static directory
    image_patterns = [
        "src/auto_psycho/static/images/tat/*.jpg",
        "src/auto_psycho/static/images/tat/*.jpeg",
        "src/auto_psycho/static/images/tat/*.png",
    ]

    images = []
    for pattern in image_patterns:
        images.extend(glob.glob(pattern))

    # If no images found, create placeholder list
    if not images:
        # Create placeholder image list for development
        images = [f"tat_{i:02d}.jpg" for i in range(1, 11)]
    else:
        # Sort images to ensure consistent order
        images.sort()

    return [os.path.basename(img) for img in images]


def generate_report_content(analysis):
    """
    Generate formatted report content from analysis result.

    Args:
        analysis: AnalysisResult instance

    Returns:
        Formatted report content as string
    """
    session = analysis.session
    participant = session.participant

    report = f"""
TAT心理分析报告
================

参与者信息:
- 参与者编号: {participant.participant_code}
- 年龄: {participant.age or "未提供"}
- 性别: {participant.gender or "未提供"}
- 教育水平: {participant.education_level or "未提供"}
- 职业: {participant.occupation or "未提供"}

实验信息:
- 会话编号: {session.session_code}
- 开始时间: {session.start_time.strftime("%Y-%m-%d %H:%M:%S") if session.start_time else "未记录"}
- 完成时间: {session.end_time.strftime("%Y-%m-%d %H:%M:%S") if session.end_time else "未记录"}
- 总用时: {session.total_duration // 60 if session.total_duration else 0}分钟
- 回答数量: {len(session.tat_responses)}

AI分析结果:
- 分析模型: {analysis.ai_model_used}
- 置信度: {(analysis.confidence_score if analysis.confidence_score is not None else 0.0):.2f}
- 分析时间: {analysis.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S") if analysis.analysis_timestamp else "未记录"}

详细分析:
{analysis.raw_analysis}

心理主题: {analysis.psychological_themes or "未识别"}
人格特征: {analysis.personality_traits or "未识别"}
情感模式: {analysis.emotional_patterns or "未识别"}

建议和关注点:
{analysis.recommendations or "暂无具体建议"}

================
报告生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}
平台: Auto Psycho TAT Platform
注意: 本报告仅供参考，不能替代专业心理咨询。
"""

    return report
