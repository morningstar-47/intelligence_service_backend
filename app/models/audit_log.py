# app/models/audit_log.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AuditLog(Base):
    """
    Modèle pour les logs d'audit du système
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    
    # Utilisateur ayant effectué l'action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Peut être null pour les actions système
    user = relationship("User")
    
    # Adresse IP
    ip_address = Column(String(45), nullable=True)  # IPv6 peut aller jusqu'à 45 caractères
    
    # Détails de l'action
    action = Column(String(100), nullable=False, index=True)  # Type d'action (login, update, delete, etc.)
    resource_type = Column(String(100), nullable=True, index=True)  # Type de ressource (user, report, etc.)
    resource_id = Column(Integer, nullable=True)  # ID de la ressource
    
    # Description détaillée
    details = Column(Text, nullable=True)
    
    # Données supplémentaires
    metadata = Column(JSON, nullable=True)  # Données additionnelles en JSON
    
    # Horodatage
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Session
    session_id = Column(String(100), nullable=True)  # Identifiant de session
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} on {self.resource_type} by User {self.user_id}>"