"""
Report generator for TAT analysis results.
This module provides functionality to generate formatted reports from analysis data.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.auto_psycho.models import ExperimentSession, AnalysisResult, TATResponse


class ReportGenerator:
    """
    Generator for formatted TAT analysis reports.
    
    This class provides methods to generate various types of reports
    from TAT analysis results, including text, HTML, and structured formats.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.report_templates = {
            'detailed': self._get_detailed_template(),
            'summary': self._get_summary_template(),
            'clinical': self._get_clinical_template()
        }
    
    def generate_comprehensive_report(
        self, 
        session: ExperimentSession, 
        analysis_results: List[AnalysisResult],
        format_type: str = 'detailed'
    ) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            session: Experiment session
            analysis_results: List of analysis results
            format_type: Type of report format ('detailed', 'summary', 'clinical')
            
        Returns:
            Formatted report as string
        """
        if format_type not in self.report_templates:
            format_type = 'detailed'
        
        template = self.report_templates[format_type]
        
        # Prepare report data
        report_data = self._prepare_report_data(session, analysis_results)
        
        # Generate report using template
        report = template.format(**report_data)
        
        return report
    
    def generate_html_report(
        self, 
        session: ExperimentSession, 
        analysis_results: List[AnalysisResult]
    ) -> str:
        """
        Generate an HTML formatted report.
        
        Args:
            session: Experiment session
            analysis_results: List of analysis results
            
        Returns:
            HTML formatted report
        """
        report_data = self._prepare_report_data(session, analysis_results)
        
        html_template = self._get_html_template()
        
        return html_template.format(**report_data)
    
    def generate_json_report(
        self, 
        session: ExperimentSession, 
        analysis_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON report.
        
        Args:
            session: Experiment session
            analysis_results: List of analysis results
            
        Returns:
            Structured report data as dictionary
        """
        return self._prepare_structured_data(session, analysis_results)
    
    def _prepare_report_data(
        self, 
        session: ExperimentSession, 
        analysis_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """
        Prepare data for report generation.
        
        Args:
            session: Experiment session
            analysis_results: List of analysis results
            
        Returns:
            Dictionary containing formatted report data
        """
        participant = session.participant
        responses = session.tat_responses
        
        # Basic information
        data = {
            'report_title': 'TAT心理分析报告',
            'generation_date': datetime.now().strftime('%Y年%m月%d日 %H:%M'),
            'participant_code': participant.participant_code,
            'participant_age': participant.age or '未提供',
            'participant_gender': participant.gender or '未提供',
            'participant_education': participant.education_level or '未提供',
            'participant_occupation': participant.occupation or '未提供',
            'session_code': session.session_code,
            'session_start': session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else '未记录',
            'session_end': session.end_time.strftime('%Y-%m-%d %H:%M:%S') if session.end_time else '未记录',
            'session_duration': self._format_duration(session.total_duration),
            'total_responses': len(responses),
            'total_analyses': len(analysis_results)
        }
        
        # Response statistics
        data.update(self._get_response_statistics(responses))
        
        # Analysis summaries
        data.update(self._get_analysis_summaries(analysis_results))
        
        # Individual response details
        data['response_details'] = self._format_response_details(responses)
        
        # Recommendations and insights
        data.update(self._extract_insights(analysis_results))
        
        return data
    
    def _prepare_structured_data(
        self, 
        session: ExperimentSession, 
        analysis_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """
        Prepare structured data for JSON export.
        
        Args:
            session: Experiment session
            analysis_results: List of analysis results
            
        Returns:
            Structured data dictionary
        """
        return {
            'metadata': {
                'report_type': 'tat_analysis',
                'generation_timestamp': datetime.now().isoformat(),
                'platform': 'Auto Psycho TAT Platform',
                'version': '1.0'
            },
            'participant': session.participant.to_dict(),
            'session': session.to_dict(),
            'responses': [response.to_dict() for response in session.tat_responses],
            'analyses': [analysis.to_dict() for analysis in analysis_results],
            'summary': self._generate_summary_insights(session, analysis_results)
        }
    
    def _get_response_statistics(self, responses: List[TATResponse]) -> Dict[str, Any]:
        """
        Calculate response statistics.
        
        Args:
            responses: List of TAT responses
            
        Returns:
            Dictionary containing response statistics
        """
        if not responses:
            return {
                'avg_word_count': 0,
                'avg_response_time': 0,
                'total_words': 0,
                'response_time_range': '无数据'
            }
        
        word_counts = [r.word_count for r in responses if r.word_count]
        response_times = [r.response_time for r in responses if r.response_time]
        
        return {
            'avg_word_count': round(sum(word_counts) / len(word_counts)) if word_counts else 0,
            'avg_response_time': round(sum(response_times) / len(response_times)) if response_times else 0,
            'total_words': sum(word_counts),
            'response_time_range': f"{min(response_times):.1f} - {max(response_times):.1f}秒" if response_times else '无数据',
            'shortest_response': min(word_counts) if word_counts else 0,
            'longest_response': max(word_counts) if word_counts else 0
        }
    
    def _get_analysis_summaries(self, analysis_results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Extract analysis summaries.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Dictionary containing analysis summaries
        """
        summaries = {}
        
        for analysis in analysis_results:
            key = f"{analysis.analysis_type}_summary"
            summaries[key] = analysis.raw_analysis[:500] + "..." if len(analysis.raw_analysis) > 500 else analysis.raw_analysis
            
            # Extract confidence score
            confidence_key = f"{analysis.analysis_type}_confidence"
            summaries[confidence_key] = analysis.get_confidence_level()
        
        return summaries
    
    def _format_response_details(self, responses: List[TATResponse]) -> str:
        """
        Format individual response details.
        
        Args:
            responses: List of TAT responses
            
        Returns:
            Formatted response details string
        """
        details = []
        
        for i, response in enumerate(responses, 1):
            detail = f"""
图片 {i} ({response.image_filename}):
- 字数: {response.word_count or 0}
- 回答时间: {response.response_time:.1f}秒 ({response.get_response_speed_category()})
- 故事长度: {response.get_story_length_category()}
- 情感基调: {response.emotional_tone or '未分析'}

故事内容:
{response.story_text[:200]}{'...' if len(response.story_text) > 200 else ''}
"""
            details.append(detail)
        
        return '\n'.join(details)
    
    def _extract_insights(self, analysis_results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Extract key insights from analysis results.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Dictionary containing extracted insights
        """
        insights = {
            'key_themes': [],
            'personality_traits': [],
            'emotional_patterns': [],
            'recommendations': [],
            'overall_assessment': ''
        }
        
        for analysis in analysis_results:
            # Extract themes
            if analysis.psychological_themes:
                try:
                    themes = eval(analysis.psychological_themes) if isinstance(analysis.psychological_themes, str) else analysis.psychological_themes
                    if isinstance(themes, list):
                        insights['key_themes'].extend(themes)
                except:
                    pass
            
            # Extract personality traits
            if analysis.personality_traits:
                try:
                    traits = eval(analysis.personality_traits) if isinstance(analysis.personality_traits, str) else analysis.personality_traits
                    if isinstance(traits, list):
                        insights['personality_traits'].extend(traits)
                except:
                    pass
            
            # Extract emotional patterns
            if analysis.emotional_patterns:
                try:
                    patterns = eval(analysis.emotional_patterns) if isinstance(analysis.emotional_patterns, str) else analysis.emotional_patterns
                    if isinstance(patterns, list):
                        insights['emotional_patterns'].extend(patterns)
                except:
                    pass
            
            # Extract recommendations
            if analysis.recommendations:
                insights['recommendations'].append(analysis.recommendations)
        
        # Remove duplicates and format
        insights['key_themes'] = list(set(insights['key_themes']))
        insights['personality_traits'] = list(set(insights['personality_traits']))
        insights['emotional_patterns'] = list(set(insights['emotional_patterns']))
        
        # Create overall assessment
        insights['overall_assessment'] = self._create_overall_assessment(insights)
        
        return insights
    
    def _create_overall_assessment(self, insights: Dict[str, Any]) -> str:
        """
        Create an overall assessment summary.
        
        Args:
            insights: Extracted insights dictionary
            
        Returns:
            Overall assessment string
        """
        assessment_parts = []
        
        if insights['key_themes']:
            themes_str = '、'.join(insights['key_themes'][:3])
            assessment_parts.append(f"主要心理主题包括{themes_str}")
        
        if insights['personality_traits']:
            traits_str = '、'.join(insights['personality_traits'][:3])
            assessment_parts.append(f"显示出{traits_str}等人格特征")
        
        if insights['emotional_patterns']:
            patterns_str = '、'.join(insights['emotional_patterns'][:2])
            assessment_parts.append(f"情感模式表现为{patterns_str}")
        
        return '，'.join(assessment_parts) + '。' if assessment_parts else '需要更多数据进行综合评估。'
    
    def _generate_summary_insights(
        self, 
        session: ExperimentSession, 
        analysis_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """
        Generate summary insights for structured export.
        
        Args:
            session: Experiment session
            analysis_results: List of analysis results
            
        Returns:
            Summary insights dictionary
        """
        insights = self._extract_insights(analysis_results)
        response_stats = self._get_response_statistics(session.tat_responses)
        
        return {
            'completion_status': 'completed' if session.is_completed() else 'incomplete',
            'response_quality': self._assess_response_quality(response_stats),
            'key_findings': insights,
            'confidence_assessment': self._calculate_overall_confidence(analysis_results),
            'recommendations_summary': self._summarize_recommendations(insights['recommendations'])
        }
    
    def _assess_response_quality(self, stats: Dict[str, Any]) -> str:
        """
        Assess the quality of responses based on statistics.
        
        Args:
            stats: Response statistics
            
        Returns:
            Quality assessment string
        """
        avg_words = stats.get('avg_word_count', 0)
        
        if avg_words >= 150:
            return '高质量'
        elif avg_words >= 80:
            return '中等质量'
        elif avg_words >= 30:
            return '基本质量'
        else:
            return '质量较低'
    
    def _calculate_overall_confidence(self, analysis_results: List[AnalysisResult]) -> str:
        """
        Calculate overall confidence level.
        
        Args:
            analysis_results: List of analysis results
            
        Returns:
            Overall confidence level string
        """
        if not analysis_results:
            return '无法评估'
        
        confidence_scores = [a.confidence_score for a in analysis_results if a.confidence_score]
        
        if not confidence_scores:
            return '中等'
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        if avg_confidence >= 0.8:
            return '高'
        elif avg_confidence >= 0.6:
            return '中等'
        elif avg_confidence >= 0.4:
            return '较低'
        else:
            return '低'
    
    def _summarize_recommendations(self, recommendations: List[str]) -> str:
        """
        Summarize recommendations into a concise format.
        
        Args:
            recommendations: List of recommendation strings
            
        Returns:
            Summarized recommendations string
        """
        if not recommendations:
            return '暂无具体建议'
        
        # Combine and truncate recommendations
        combined = ' '.join(recommendations)
        
        if len(combined) > 300:
            return combined[:300] + '...'
        
        return combined
    
    def _format_duration(self, duration_seconds: Optional[int]) -> str:
        """
        Format duration in a human-readable format.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if not duration_seconds:
            return '未记录'
        
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        elif minutes > 0:
            return f"{minutes}分钟{seconds}秒"
        else:
            return f"{seconds}秒"
    
    def _get_detailed_template(self) -> str:
        """Get detailed report template."""
        return """
{report_title}
{'=' * 50}

生成时间: {generation_date}

参与者信息
----------
参与者编号: {participant_code}
年龄: {participant_age}
性别: {participant_gender}
教育水平: {participant_education}
职业: {participant_occupation}

实验信息
--------
会话编号: {session_code}
开始时间: {session_start}
结束时间: {session_end}
总用时: {session_duration}
回答数量: {total_responses}
分析数量: {total_analyses}

回答统计
--------
平均字数: {avg_word_count}
总字数: {total_words}
平均回答时间: {avg_response_time}秒
回答时间范围: {response_time_range}
最短回答: {shortest_response}字
最长回答: {longest_response}字

详细分析结果
------------
{session_summary_summary}

置信度评估: {session_summary_confidence}

个体回答详情
------------
{response_details}

心理学洞察
----------
主要心理主题: {key_themes}
人格特征: {personality_traits}
情感模式: {emotional_patterns}

综合评估
--------
{overall_assessment}

建议和关注点
------------
{recommendations}

{'=' * 50}
报告生成时间: {generation_date}
平台: Auto Psycho TAT Platform
注意: 本报告仅供参考，不能替代专业心理咨询。
"""
    
    def _get_summary_template(self) -> str:
        """Get summary report template."""
        return """
{report_title} - 摘要版
{'=' * 30}

参与者: {participant_code} | 生成时间: {generation_date}

基本信息: {participant_age}岁 {participant_gender} | {participant_education} | {participant_occupation}
实验时长: {session_duration} | 回答数量: {total_responses} | 平均字数: {avg_word_count}

综合评估: {overall_assessment}

主要发现:
- 心理主题: {key_themes}
- 人格特征: {personality_traits}
- 情感模式: {emotional_patterns}

建议: {recommendations}

置信度: {session_summary_confidence}
"""
    
    def _get_clinical_template(self) -> str:
        """Get clinical report template."""
        return """
临床心理评估报告 - TAT分析
{'=' * 40}

评估日期: {generation_date}
被评估者: {participant_code}

一、基本信息
年龄: {participant_age} | 性别: {participant_gender}
教育背景: {participant_education}
职业: {participant_occupation}

二、测验过程
测验时间: {session_duration}
完成度: {total_responses}/10个图片
回答质量: 平均{avg_word_count}字/图片

三、心理动力学分析
{session_summary_summary}

四、人格特征评估
主要特征: {personality_traits}
情感模式: {emotional_patterns}
心理主题: {key_themes}

五、临床印象
{overall_assessment}

六、建议
{recommendations}

七、评估可靠性
分析置信度: {session_summary_confidence}

评估者: AI分析系统
日期: {generation_date}
"""
    
    def _get_html_template(self) -> str:
        """Get HTML report template."""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #2c3e50; border-left: 4px solid #3498db; padding-left: 10px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .info-item {{ background: #f8f9fa; padding: 10px; border-radius: 5px; }}
        .analysis-box {{ background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_title}</h1>
        <p>生成时间: {generation_date}</p>
    </div>

    <div class="section">
        <h2>参与者信息</h2>
        <div class="info-grid">
            <div class="info-item"><strong>参与者编号:</strong> {participant_code}</div>
            <div class="info-item"><strong>年龄:</strong> {participant_age}</div>
            <div class="info-item"><strong>性别:</strong> {participant_gender}</div>
            <div class="info-item"><strong>教育水平:</strong> {participant_education}</div>
        </div>
    </div>

    <div class="section">
        <h2>实验信息</h2>
        <div class="info-grid">
            <div class="info-item"><strong>会话编号:</strong> {session_code}</div>
            <div class="info-item"><strong>总用时:</strong> {session_duration}</div>
            <div class="info-item"><strong>回答数量:</strong> {total_responses}</div>
            <div class="info-item"><strong>平均字数:</strong> {avg_word_count}</div>
        </div>
    </div>

    <div class="section">
        <h2>分析结果</h2>
        <div class="analysis-box">
            <h3>综合评估</h3>
            <p>{overall_assessment}</p>
        </div>
    </div>

    <div class="section">
        <h2>建议和关注点</h2>
        <div class="recommendations">
            {recommendations}
        </div>
    </div>

    <div class="footer">
        <p>本报告由 Auto Psycho TAT Platform 生成</p>
        <p><strong>注意:</strong> 本报告仅供参考，不能替代专业心理咨询。</p>
    </div>
</body>
</html>
""" 