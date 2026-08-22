from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IncidentRecord(BaseModel):
    incident_id: str
    title: str
    description: str
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    component: Optional[str] = None
    service: Optional[str] = None
    severity: Optional[str] = None
    environment: Optional[str] = None
    incident_type: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None
    source_file: Optional[str] = None
    row_number: Optional[int] = None
    search_text: Optional[str] = None


class IncidentAnalysisRequest(BaseModel):
    description: str
    component: Optional[str] = None
    severity: Optional[str] = None
    environment: Optional[str] = None
    incident_type: Optional[str] = None


class SimilarIncidentQuery(BaseModel):
    description: str
    component: Optional[str] = None
    severity: Optional[str] = None
    environment: Optional[str] = None
    incident_type: Optional[str] = None


class SimilarIncident(BaseModel):
    incident_id: str
    title: str
    description: str
    project: Optional[str] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    similarity_score: float
    keyword_score: Optional[float] = None
    retrieval_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceIncident(BaseModel):
    incident_id: str
    similarity_score: float


class IncidentUploadResponse(BaseModel):
    success: bool = True
    message: str
    source_files: List[str] = Field(default_factory=list)
    total_incidents: int = 0
    indexed_incidents: int = 0
    duplicates_removed: int = 0
    skipped_rows: int = 0


class SimilarIncidentResponse(BaseModel):
    incidents: List[SimilarIncident] = Field(default_factory=list)


class IncidentAnalysisResponse(BaseModel):
    analysis_id: Optional[str] = None
    root_cause: str
    resolution: str
    evidence_incidents: List[EvidenceIncident] = Field(default_factory=list)
    evidence_strength: str
    summary: str
    evidence_explanation: str = ""
    similar_incidents: List[SimilarIncident] = Field(default_factory=list)
    retrieval_diagnostics: Dict[str, Any] = Field(default_factory=dict)


class StoredAnalysisResponse(BaseModel):
    id: str
    created_at: Any
    input: Dict[str, Any]
    result: IncidentAnalysisResponse
