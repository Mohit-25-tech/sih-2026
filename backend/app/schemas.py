from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ExtractedFieldSchema(BaseModel):
    id: Optional[int] = None
    field_name: str
    visual_value: Optional[str] = None
    mrz_value: Optional[str] = None
    is_match: bool = True
    confidence: float = 1.0

    class Config:
        from_attributes = True


class TamperResultSchema(BaseModel):
    id: Optional[int] = None
    ela_heatmap_path: str
    ela_score: float
    is_tampered: bool
    anomaly_regions: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class RiskScoreSchema(BaseModel):
    id: Optional[int] = None
    score: float
    risk_level: str  # LOW, MEDIUM, HIGH
    factors: Dict[str, Any]
    summary_reasoning: str

    class Config:
        from_attributes = True


class AuditLogSchema(BaseModel):
    id: Optional[int] = None
    document_id: Optional[int] = None
    officer_id: str
    action: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentDetailResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    document_type: str
    upload_time: datetime
    status: str
    extracted_fields: List[ExtractedFieldSchema] = []
    tamper_result: Optional[TamperResultSchema] = None
    risk_score: Optional[RiskScoreSchema] = None
    face_match: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    id: int
    filename: str
    document_type: str
    upload_time: datetime
    status: str
    risk_level: Optional[str] = "LOW"
    risk_score: Optional[float] = 0.0

    class Config:
        from_attributes = True


class FaceVerifyRequest(BaseModel):
    document_id: int
    live_image_base64: Optional[str] = None


class FaceVerifyResponse(BaseModel):
    document_id: int
    match_score: float  # 0 to 100
    is_match: bool
    threshold: float = 70.0
    details: str
