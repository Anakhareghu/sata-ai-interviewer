import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Resume(Base):
    """Resume model storing uploaded resumes and extracted data."""
    __tablename__ = "resumes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), nullable=False, index=True)  # Links to SATA user
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # pdf, docx
    
    # Extracted data (JSON)
    raw_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=dict)  # {technical: [], soft: []}
    projects = Column(JSON, default=list)          # [{name, description, technologies}]
    work_experience = Column(JSON, default=list)   # [{company, role, duration, description}]
    internships = Column(JSON, default=list)       # [{company, role, duration}]
    certifications = Column(JSON, default=list)    # [{name, issuer, year}]
    education = Column(JSON, default=list)         # [{degree, institution, gpa, year}]
    contact_info = Column(JSON, default=dict)      # {email, phone, linkedin}
    
    # Analysis results
    skill_gaps = Column(JSON, default=list)
    domain_specialization = Column(String(100), nullable=True)  # AI/ML, Web, Data, etc.
    experience_level = Column(String(50), nullable=True)  # Entry, Mid, Senior
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Resume {self.id} - {self.filename}>"
