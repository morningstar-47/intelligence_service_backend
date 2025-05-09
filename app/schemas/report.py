# app/schemas/report.py
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, validator, Field


# Schéma de base pour un rapport
class ReportBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=10)
    source: Optional[str] = None
    classification: str
    location: Optional[str] = None
    coordinates: Optional[str] = None
    
    @validator("classification")
    def validate_classification(cls, v):
        """Vérifie que la classification est valide"""
        valid_classifications = ["top_secret", "secret", "confidential", "unclassified"]
        if v not in valid_classifications:
            raise ValueError(f"La classification doit être l'une des suivantes: {', '.join(valid_classifications)}")
        return v


# Schéma pour la création d'un rapport
class ReportCreate(ReportBase):
    pass


# Schéma pour la mise à jour d'un rapport
class ReportUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    source: Optional[str] = None
    classification: Optional[str] = None
    location: Optional[str] = None
    coordinates: Optional[str] = None
    status: Optional[str] = None
    
    @validator("classification")
    def validate_classification(cls, v):
        """Vérifie que la classification est valide si fournie"""
        if v:
            valid_classifications = ["top_secret", "secret", "confidential", "unclassified"]
            if v not in valid_classifications:
                raise ValueError(f"La classification doit être l'une des suivantes: {', '.join(valid_classifications)}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        """Vérifie que le statut est valide si fourni"""
        if v:
            valid_statuses = ["draft", "pending", "approved", "rejected", "archived"]
            if v not in valid_statuses:
                raise ValueError(f"Le statut doit être l'un des suivants: {', '.join(valid_statuses)}")
        return v


# Schéma pour un tag
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    
    class Config:
        orm_mode = True


# Schéma pour un commentaire
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    report_id: int


class Comment(CommentBase):
    id: int
    report_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user_name: Optional[str] = None
    
    class Config:
        orm_mode = True


# Schéma pour une pièce jointe
class AttachmentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int


class AttachmentCreate(AttachmentBase):
    report_id: int
    file_path: str


class Attachment(AttachmentBase):
    id: int
    report_id: int
    uploaded_by_id: int
    uploaded_at: datetime
    
    class Config:
        orm_mode = True


# Schéma pour le rapport complet (sortie)
class Report(ReportBase):
    id: int
    status: str
    submitted_by_id: int
    submitted_by_name: Optional[str] = None
    approved_by_id: Optional[int] = None
    approved_by_name: Optional[str] = None
    report_date: datetime
    created_at: datetime
    updated_at: datetime
    ai_analysis: Optional[str] = None
    threat_level: Optional[str] = None
    credibility_score: Optional[int] = None
    tags: List[Tag] = []
    comments: List[Comment] = []
    attachments: List[Attachment] = []
    
    class Config:
        orm_mode = True


# Schéma pour la liste des rapports (sortie)
class ReportList(BaseModel):
    items: List[Report]
    total: int
    page: int
    page_size: int
    pages: int
    
    class Config:
        orm_mode = True


# Schéma pour l'approbation d'un rapport
class ReportApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None
    
    @validator("rejection_reason")
    def validate_rejection_reason(cls, v, values):
        """Vérifie qu'une raison de rejet est fournie si le rapport est rejeté"""
        if "approved" in values and not values["approved"] and not v:
            raise ValueError("Une raison de rejet doit être fournie lorsqu'un rapport est rejeté")
        return v


# Schéma pour l'analyse IA d'un rapport
class ReportAIAnalysis(BaseModel):
    ai_analysis: str
    threat_level: Optional[str] = None
    credibility_score: Optional[int] = None
    entities: Optional[Dict[str, List[str]]] = None
    suggested_tags: Optional[List[str]] = None
    related_reports: Optional[List[int]] = None