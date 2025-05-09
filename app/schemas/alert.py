# app/schemas/alert.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator, Field


# Schéma de base pour une alerte
class AlertBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    alert_type: str
    severity: str
    location: Optional[str] = None
    coordinates: Optional[str] = None
    
    @validator("alert_type")
    def validate_alert_type(cls, v):
        """Vérifie que le type d'alerte est valide"""
        valid_types = ["tactical", "strategic", "cyber", "intel", "field", "system"]
        if v not in valid_types:
            raise ValueError(f"Le type d'alerte doit être l'un des suivants: {', '.join(valid_types)}")
        return v
    
    @validator("severity")
    def validate_severity(cls, v):
        """Vérifie que la sévérité est valide"""
        valid_severities = ["low", "medium", "high", "critical"]
        if v not in valid_severities:
            raise ValueError(f"La sévérité doit être l'une des suivantes: {', '.join(valid_severities)}")
        return v


# Schéma pour la création d'une alerte
class AlertCreate(AlertBase):
    related_report_id: Optional[int] = None


# Schéma pour la mise à jour d'une alerte
class AlertUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    coordinates: Optional[str] = None
    assigned_to_id: Optional[int] = None
    
    @validator("alert_type")
    def validate_alert_type(cls, v):
        """Vérifie que le type d'alerte est valide si fourni"""
        if v:
            valid_types = ["tactical", "strategic", "cyber", "intel", "field", "system"]
            if v not in valid_types:
                raise ValueError(f"Le type d'alerte doit être l'un des suivants: {', '.join(valid_types)}")
        return v
    
    @validator("severity")
    def validate_severity(cls, v):
        """Vérifie que la sévérité est valide si fournie"""
        if v:
            valid_severities = ["low", "medium", "high", "critical"]
            if v not in valid_severities:
                raise ValueError(f"La sévérité doit être l'une des suivantes: {', '.join(valid_severities)}")
        return v
    
    @validator("status")
    def validate_status(cls, v):
        """Vérifie que le statut est valide si fourni"""
        if v:
            valid_statuses = ["new", "acknowledged", "in_progress", "resolved", "closed"]
            if v not in valid_statuses:
                raise ValueError(f"Le statut doit être l'un des suivants: {', '.join(valid_statuses)}")
        return v


# Schéma pour une action sur une alerte
class AlertActionBase(BaseModel):
    action: str
    description: str


class AlertActionCreate(AlertActionBase):
    alert_id: int
    data: Optional[Dict[str, Any]] = None


class AlertAction(AlertActionBase):
    id: int
    alert_id: int
    user_id: int
    created_at: datetime
    data: Optional[Dict[str, Any]] = None
    user_name: Optional[str] = None
    
    class Config:
        orm_mode = True


# Schéma pour une alerte complète (sortie)
class Alert(AlertBase):
    id: int
    status: str
    created_by_id: int
    created_by_name: Optional[str] = None
    assigned_to_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    related_report_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    ai_generated: bool
    ai_recommendations: Optional[str] = None
    actions: List[AlertAction] = []
    
    class Config:
        orm_mode = True


# Schéma pour la liste des alertes (sortie)
class AlertList(BaseModel):
    items: List[Alert]
    total: int
    page: int
    page_size: int
    pages: int
    
    class Config:
        orm_mode = True


# Schéma pour l'assignation d'une alerte
class AlertAssign(BaseModel):
    assigned_to_id: int
    note: Optional[str] = None


# Schéma pour la résolution d'une alerte
class AlertResolve(BaseModel):
    resolution_note: str = Field(..., min_length=10)
    status: str = "resolved"
    
    @validator("status")
    def validate_status(cls, v):
        """Vérifie que le statut est valide"""
        valid_statuses = ["resolved", "closed"]
        if v not in valid_statuses:
            raise ValueError(f"Le statut doit être l'un des suivants: {', '.join(valid_statuses)}")
        return v


# Schéma pour la notification d'alerte
class AlertNotification(BaseModel):
    alert_id: int
    user_id: int
    notified_at: datetime
    read: bool = False


# Schéma pour les utilisateurs à notifier
class AlertNotifyUsers(BaseModel):
    user_ids: List[int]
    message: Optional[str] = None