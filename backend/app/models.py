import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(50), default="PASSPORT")  # PASSPORT, VISA, NATIONAL_ID
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="SCREENED")  # PENDING, SCREENED, ERROR
    
    # Relationships
    extracted_fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    tamper_result = relationship("TamperResult", back_populates="document", uselist=False, cascade="all, delete-orphan")
    risk_score = relationship("RiskScore", back_populates="document", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", cascade="all, delete-orphan")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)  # SURNAME, GIVEN_NAME, DOCUMENT_NUMBER, DOB, EXPIRY, NATIONALITY, SEX
    visual_value = Column(String(255), nullable=True)
    mrz_value = Column(String(255), nullable=True)
    is_match = Column(Boolean, default=True)
    confidence = Column(Float, default=1.0)

    document = relationship("Document", back_populates="extracted_fields")


class TamperResult(Base):
    __tablename__ = "tamper_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    ela_heatmap_path = Column(String(500), nullable=False)
    ela_score = Column(Float, default=0.0)  # 0 to 100
    is_tampered = Column(Boolean, default=False)
    anomaly_regions = Column(JSON, nullable=True)  # List of {x, y, width, height, intensity, label}

    document = relationship("Document", back_populates="tamper_result")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)  # 0 to 100
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    factors = Column(JSON, nullable=False)  # Detailed breakdown: {mrz_score, mismatch_score, ela_score, face_score}
    summary_reasoning = Column(Text, nullable=False)

    document = relationship("Document", back_populates="risk_score")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    officer_id = Column(String(100), default="OFFICER_ZENITH_01")
    action = Column(String(100), nullable=False)  # DOCUMENT_SCREENED, FACE_VERIFIED, MANUAL_OVERRIDE
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    details = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="audit_logs")
