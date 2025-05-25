"""
OpenAI-powered psychological analysis for TAT responses.
This module provides AI analysis capabilities using OpenAI's GPT models.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from src.auto_psycho.config import Config
from src.auto_psycho.models import TATResponse, AnalysisResult, ExperimentSession

# Set up logging
logger = logging.getLogger(__name__)


class OpenAIAnalyzer:
    """
    AI-powered analyzer for TAT responses using OpenAI's GPT models.
    
    This class provides methods to analyze individual TAT responses and
    generate comprehensive psychological profiles based on multiple responses.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """
        Initialize the OpenAI analyzer.
        
        Args:
            api_key: OpenAI API key (uses config if not provided)
            model: OpenAI model to use (uses config if not provided)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Analysis prompts
        self.prompts = {
            'individual_response': self._get_individual_response_prompt(),
            'session_summary': self._get_session_summary_prompt(),
            'personality_profile': self._get_personality_profile_prompt()
        }
    
    def analyze_individual_response(
        self, 
        response: TATResponse, 
        image_description: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze an individual TAT response.
        
        Args:
            response: TAT response to analyze
            image_description: Description of the TAT image shown
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Prepare the prompt
            prompt = self.prompts['individual_response'].format(
                image_description=image_description,
                story_text=response.story_text,
                word_count=response.word_count,
                response_time=response.response_time or "未记录"
            )
            
            # Call OpenAI API
            response_obj = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的心理学家，专门分析主题统觉测验(TAT)的回答。请用中文回答。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis_text = response_obj.choices[0].message.content
            
            # Parse structured results
            structured_results = self._parse_individual_analysis(analysis_text)
            
            return {
                'raw_analysis': analysis_text,
                'structured_results': structured_results,
                'confidence_score': self._calculate_confidence_score(analysis_text),
                'emotional_tone': structured_results.get('emotional_tone'),
                'psychological_themes': structured_results.get('psychological_themes'),
                'personality_indicators': structured_results.get('personality_indicators')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing individual response: {str(e)}")
            return {
                'raw_analysis': f"分析过程中出现错误: {str(e)}",
                'structured_results': {},
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def analyze_session_summary(self, session: ExperimentSession) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis summary for an entire session.
        
        Args:
            session: Experiment session to analyze
            
        Returns:
            Dictionary containing session analysis results
        """
        try:
            # Collect all responses
            responses = session.tat_responses
            if not responses:
                return {
                    'raw_analysis': "没有找到TAT回答数据",
                    'structured_results': {},
                    'confidence_score': 0.0,
                    'error': "No responses found"
                }
            
            # Prepare response summaries
            response_summaries = []
            for resp in responses:
                summary = f"图片 {resp.image_index + 1}: {resp.story_text[:200]}..."
                response_summaries.append(summary)
            
            # Prepare the prompt
            prompt = self.prompts['session_summary'].format(
                participant_info=self._get_participant_info(session.participant),
                total_responses=len(responses),
                response_summaries="\n".join(response_summaries)
            )
            
            # Call OpenAI API
            response_obj = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的心理学家，专门分析主题统觉测验(TAT)的整体结果。请用中文提供详细的心理分析报告。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            analysis_text = response_obj.choices[0].message.content
            
            # Parse structured results
            structured_results = self._parse_session_analysis(analysis_text)
            
            return {
                'raw_analysis': analysis_text,
                'structured_results': structured_results,
                'confidence_score': self._calculate_confidence_score(analysis_text),
                'psychological_themes': structured_results.get('psychological_themes'),
                'personality_traits': structured_results.get('personality_traits'),
                'emotional_patterns': structured_results.get('emotional_patterns'),
                'recommendations': structured_results.get('recommendations')
            }
            
        except Exception as e:
            logger.error(f"Error analyzing session summary: {str(e)}")
            return {
                'raw_analysis': f"分析过程中出现错误: {str(e)}",
                'structured_results': {},
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def generate_personality_profile(self, session: ExperimentSession) -> Dict[str, Any]:
        """
        Generate a detailed personality profile based on all TAT responses.
        
        Args:
            session: Experiment session to analyze
            
        Returns:
            Dictionary containing personality profile results
        """
        try:
            # Get session summary first
            session_analysis = self.analyze_session_summary(session)
            
            # Prepare the prompt for personality profiling
            prompt = self.prompts['personality_profile'].format(
                session_analysis=session_analysis['raw_analysis'],
                participant_info=self._get_participant_info(session.participant)
            )
            
            # Call OpenAI API
            response_obj = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的心理学家，专门根据TAT测验结果生成详细的人格画像。请用中文提供科学、专业的人格分析报告。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            analysis_text = response_obj.choices[0].message.content
            
            # Parse structured results
            structured_results = self._parse_personality_profile(analysis_text)
            
            return {
                'raw_analysis': analysis_text,
                'structured_results': structured_results,
                'confidence_score': self._calculate_confidence_score(analysis_text),
                'personality_traits': structured_results.get('personality_traits'),
                'psychological_needs': structured_results.get('psychological_needs'),
                'behavioral_patterns': structured_results.get('behavioral_patterns'),
                'recommendations': structured_results.get('recommendations')
            }
            
        except Exception as e:
            logger.error(f"Error generating personality profile: {str(e)}")
            return {
                'raw_analysis': f"分析过程中出现错误: {str(e)}",
                'structured_results': {},
                'confidence_score': 0.0,
                'error': str(e)
            }
    
    def _get_individual_response_prompt(self) -> str:
        """Get the prompt template for individual response analysis."""
        return """
请分析以下TAT(主题统觉测验)回答：

图片描述: {image_description}
参与者的故事: {story_text}
字数: {word_count}
回答时间: {response_time}秒

请从以下几个方面进行分析：
1. 情感基调 (积极、消极、中性、复杂)
2. 主要心理主题 (如成就、亲密关系、权力、恐惧等)
3. 人格特征指标 (如外向性、神经质、开放性等)
4. 防御机制的使用
5. 故事结构和逻辑性
6. 对人际关系的态度
7. 应对压力的方式

请提供详细的分析，并给出置信度评估。
"""
    
    def _get_session_summary_prompt(self) -> str:
        """Get the prompt template for session summary analysis."""
        return """
请对以下TAT测验会话进行综合分析：

参与者信息: {participant_info}
总回答数: {total_responses}

所有回答摘要:
{response_summaries}

请提供综合分析报告，包括：
1. 整体心理状态评估
2. 主要人格特征
3. 情感模式和情绪调节能力
4. 人际关系模式
5. 应对机制和防御策略
6. 心理需求分析
7. 潜在的心理健康指标
8. 建议和关注点

请提供专业、详细的心理学分析报告。
"""
    
    def _get_personality_profile_prompt(self) -> str:
        """Get the prompt template for personality profile generation."""
        return """
基于以下TAT测验分析结果，请生成详细的人格画像：

会话分析结果: {session_analysis}
参与者信息: {participant_info}

请生成包含以下内容的详细人格画像：
1. 核心人格特征 (五大人格维度分析)
2. 心理需求层次 (根据默里的需求理论)
3. 情感特征和情绪模式
4. 认知风格和思维模式
5. 人际关系模式和社交倾向
6. 应对压力和挫折的方式
7. 潜在的成长点和发展建议
8. 心理健康状况评估

请提供科学、客观、有建设性的人格分析报告。
"""
    
    def _get_participant_info(self, participant) -> str:
        """Format participant information for analysis."""
        info_parts = []
        if participant.age:
            info_parts.append(f"年龄: {participant.age}")
        if participant.gender:
            info_parts.append(f"性别: {participant.gender}")
        if participant.education_level:
            info_parts.append(f"教育水平: {participant.education_level}")
        if participant.occupation:
            info_parts.append(f"职业: {participant.occupation}")
        
        return ", ".join(info_parts) if info_parts else "信息未提供"
    
    def _parse_individual_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse individual response analysis into structured format."""
        # This is a simplified parser - in production, you might want more sophisticated parsing
        return {
            'emotional_tone': self._extract_emotional_tone(analysis_text),
            'psychological_themes': self._extract_themes(analysis_text),
            'personality_indicators': self._extract_personality_indicators(analysis_text)
        }
    
    def _parse_session_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse session analysis into structured format."""
        return {
            'psychological_themes': self._extract_themes(analysis_text),
            'personality_traits': self._extract_personality_traits(analysis_text),
            'emotional_patterns': self._extract_emotional_patterns(analysis_text),
            'recommendations': self._extract_recommendations(analysis_text)
        }
    
    def _parse_personality_profile(self, analysis_text: str) -> Dict[str, Any]:
        """Parse personality profile into structured format."""
        return {
            'personality_traits': self._extract_personality_traits(analysis_text),
            'psychological_needs': self._extract_psychological_needs(analysis_text),
            'behavioral_patterns': self._extract_behavioral_patterns(analysis_text),
            'recommendations': self._extract_recommendations(analysis_text)
        }
    
    def _extract_emotional_tone(self, text: str) -> str:
        """Extract emotional tone from analysis text."""
        # Simple keyword-based extraction
        if any(word in text for word in ['积极', '正面', '乐观', '愉快']):
            return '积极'
        elif any(word in text for word in ['消极', '负面', '悲观', '沮丧']):
            return '消极'
        elif any(word in text for word in ['复杂', '矛盾', '混合']):
            return '复杂'
        else:
            return '中性'
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract psychological themes from analysis text."""
        themes = []
        theme_keywords = {
            '成就': ['成就', '成功', '目标', '完成'],
            '亲密关系': ['关系', '亲密', '爱情', '友谊'],
            '权力': ['权力', '控制', '支配', '领导'],
            '恐惧': ['恐惧', '害怕', '焦虑', '担心'],
            '自主': ['独立', '自主', '自由', '自立']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_personality_indicators(self, text: str) -> List[str]:
        """Extract personality indicators from analysis text."""
        indicators = []
        personality_keywords = {
            '外向': ['外向', '社交', '活跃', '开朗'],
            '内向': ['内向', '内敛', '安静', '独处'],
            '神经质': ['焦虑', '不稳定', '情绪化', '敏感'],
            '开放性': ['开放', '创新', '想象', '好奇']
        }
        
        for trait, keywords in personality_keywords.items():
            if any(keyword in text for keyword in keywords):
                indicators.append(trait)
        
        return indicators
    
    def _extract_personality_traits(self, text: str) -> List[str]:
        """Extract personality traits from analysis text."""
        return self._extract_personality_indicators(text)
    
    def _extract_emotional_patterns(self, text: str) -> List[str]:
        """Extract emotional patterns from analysis text."""
        patterns = []
        pattern_keywords = {
            '情绪稳定': ['稳定', '平衡', '调节'],
            '情绪波动': ['波动', '不稳定', '变化'],
            '情绪压抑': ['压抑', '抑制', '隐藏'],
            '情绪表达': ['表达', '开放', '直接']
        }
        
        for pattern, keywords in pattern_keywords.items():
            if any(keyword in text for keyword in keywords):
                patterns.append(pattern)
        
        return patterns
    
    def _extract_psychological_needs(self, text: str) -> List[str]:
        """Extract psychological needs from analysis text."""
        needs = []
        need_keywords = {
            '安全需求': ['安全', '稳定', '保护'],
            '归属需求': ['归属', '接纳', '群体'],
            '尊重需求': ['尊重', '认可', '地位'],
            '自我实现': ['实现', '发展', '成长']
        }
        
        for need, keywords in need_keywords.items():
            if any(keyword in text for keyword in keywords):
                needs.append(need)
        
        return needs
    
    def _extract_behavioral_patterns(self, text: str) -> List[str]:
        """Extract behavioral patterns from analysis text."""
        patterns = []
        behavior_keywords = {
            '主动性': ['主动', '积极', '进取'],
            '被动性': ['被动', '消极', '等待'],
            '合作性': ['合作', '协作', '团队'],
            '竞争性': ['竞争', '对抗', '争胜']
        }
        
        for pattern, keywords in behavior_keywords.items():
            if any(keyword in text for keyword in keywords):
                patterns.append(pattern)
        
        return patterns
    
    def _extract_recommendations(self, text: str) -> str:
        """Extract recommendations from analysis text."""
        # Look for recommendation sections
        lines = text.split('\n')
        recommendations = []
        
        for line in lines:
            if any(keyword in line for keyword in ['建议', '推荐', '应该', '可以']):
                recommendations.append(line.strip())
        
        return '\n'.join(recommendations) if recommendations else "暂无具体建议"
    
    def _calculate_confidence_score(self, analysis_text: str) -> float:
        """Calculate confidence score based on analysis text characteristics."""
        # Simple heuristic based on text length and content
        text_length = len(analysis_text)
        
        # Base score on text length
        if text_length < 100:
            base_score = 0.3
        elif text_length < 500:
            base_score = 0.6
        elif text_length < 1000:
            base_score = 0.8
        else:
            base_score = 0.9
        
        # Adjust based on content quality indicators
        quality_indicators = ['分析', '表明', '显示', '反映', '建议']
        quality_score = sum(1 for indicator in quality_indicators if indicator in analysis_text) / len(quality_indicators)
        
        # Combine scores
        final_score = (base_score + quality_score) / 2
        return min(final_score, 1.0) 