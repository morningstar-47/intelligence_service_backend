# app/models/alert.py
import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AlertType(str, enum.Enum):
    """Types d'alertes possibles"""
    TACTICAL = "tactical"  # Alertes tactiques sur le terrain
    STRATEGIC = "strategic"  # Alertes stratégiques (niveau élevé)
    CYBER = "cyber"  # Alertes de cybersécurité
    INTEL = "intel"  # Alertes de renseignement
    FIELD = "field"  # Alertes des agents de terrain
    SYSTEM = "system"  # Alertes système


class AlertSeverity(str, enum.Enum):
    """Niveaux de sévérité des alertes"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    """Statuts possibles pour une alerte"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# Table d'association pour les notifications d'alertes
alert_notification = Table(
    "alert_notification",
    Base.metadata,
    Column("alert_id", Integer, ForeignKey("alert.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("notified_at", DateTime, default=func.now(), nullable=False),
    Column("read", Boolean, default=False, nullable=False)
)


class Alert(Base):
    """
    Modèle pour les alertes du système
    """
    __tablename__ = "alert"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    
    location = Column(String(255), nullable=True)
    coordinates = Column(String(100), nullable=True)
    
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW, nullable=False, index=True)
    
    # Relations avec les utilisateurs
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    # Relation avec un rapport (si applicable)
    related_report_id = Column(Integer, ForeignKey("report.id"), nullable=True)
    related_report = relationship("Report")
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Données d'IA
    ai_generated = Column(Boolean, default=False, nullable=False)
    ai_recommendations = Column(Text, nullable=True)
    
    # Relations
    actions = relationship("AlertAction", back_populates="alert", cascade="all, delete-orphan")
    notified_users = relationship("User", secondary=alert_notification)
    
    def __repr__(self):
        return f"<Alert {self.id}: {self.title} ({self.alert_type}, {self.severity})>"


class AlertAction(Base):
    """
    Modèle pour les actions prises sur une alerte
    """
    __tablename__ = "alert_action"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relation avec l'alerte
    alert_id = Column(Integer, ForeignKey("alert.id"), nullable=False)
    alert = relationship("Alert", back_populates="actions")
    
    # Détails de l'action
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Utilisateur ayant effectué l'action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Données supplémentaires (au format texte)
    data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<AlertAction {self.id}: {self.action} on Alert {self.alert_id}>"