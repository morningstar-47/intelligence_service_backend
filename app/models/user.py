# app/models/user.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, enum.Enum):
    """Rôles possibles pour un utilisateur"""
    ADMIN = "admin"
    COMMANDER = "commander"
    FIELD = "field"


class ClearanceLevel(str, enum.Enum):
    """Niveaux d'habilitation de sécurité"""
    TOP_SECRET = "top_secret"
    SECRET = "secret"
    CONFIDENTIAL = "confidential"


class User(Base):
    """
    Modèle pour les utilisateurs du système
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    clearance_level = Column(Enum(ClearanceLevel), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    submitted_reports = relationship("Report", foreign_keys="Report.submitted_by_id", back_populates="submitted_by")
    approved_reports = relationship("Report", foreign_keys="Report.approved_by_id", back_populates="approved_by")
    map_settings = relationship("MapSettings", uselist=False, back_populates="user")
    
    def __repr__(self):
        return f"<User {self.id}: {self.matricule} ({self.role})>"