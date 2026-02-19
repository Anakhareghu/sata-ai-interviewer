import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class PerformanceScore(Base):
    """Performance evaluation scores for an interview session."""
    __tablename__ = "performance_scores"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False, unique=True)
    student_id = Column(String(36), nullable=False, index=True)
    
    # Core scores (0-100)
    technical_accuracy = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    confidence_level = Column(Float, default=0.0)
    problem_solving = Column(Float, default=0.0)
    domain_knowledge = Column(Float, default=0.0)
    
    # Overall
    overall_score = Column(Float, default=0.0)
    grade = Column(String(2), nullable=True)  # A+, A, B+, B, C+, C, D, F
    
    # Detailed analysis
    strengths = Column(JSON, default=list)     # ["Good technical knowledge", "Clear communication"]
    weaknesses = Column(JSON, default=list)    # ["Hesitant responses", "Lacks depth in ML"]
    improvement_suggestions = Column(JSON, default=list)
    
    # Placement readiness
    placement_ready = Column(String(20), nullable=True)  # Ready, Needs Work, Not Ready
    placement_prediction = Column(Float, nullable=True)  # Probability 0-1
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<PerformanceScore {self.id} - {self.overall_score}%>"


class VoiceAnalytics(Base):
    """Voice and communication analytics for an interview."""
    __tablename__ = "voice_analytics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False, unique=True)
    
    # Speech patterns
    average_speech_rate = Column(Float, nullable=True)  # Words per minute
    filler_word_count = Column(Float, nullable=True)    # Count of "um", "uh", "like"
    filler_word_ratio = Column(Float, nullable=True)    # Percentage
    
    # Timing
    average_response_time = Column(Float, nullable=True)  # Seconds
    longest_pause = Column(Float, nullable=True)
    total_speaking_time = Column(Float, nullable=True)
    
    # Tone analysis
    average_confidence = Column(Float, nullable=True)    # 0-100
    average_clarity = Column(Float, nullable=True)       # 0-100
    tone_consistency = Column(Float, nullable=True)      # 0-100
    
    # Sentiment
    positive_sentiment_ratio = Column(Float, nullable=True)
    neutral_sentiment_ratio = Column(Float, nullable=True)
    negative_sentiment_ratio = Column(Float, nullable=True)
    
    # Detailed metrics per question
    per_question_metrics = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<VoiceAnalytics {self.id}>"


class CareerRecommendation(Base):
    """Career recommendations based on interview and academic performance."""
    __tablename__ = "career_recommendations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=True)
    
    # Recommendations
    recommended_roles = Column(JSON, default=list)  # [{role, match_score, requirements}]
    skill_gaps = Column(JSON, default=list)         # [{skill, importance, resources}]
    suggested_courses = Column(JSON, default=list)  # [{course, platform, url}]
    internship_suggestions = Column(JSON, default=list)  # [{company, role, url}]
    
    # Career path
    career_trajectory = Column(JSON, default=dict)  # {short_term, mid_term, long_term}
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CareerRecommendation {self.id}>"
