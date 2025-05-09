# app/models/report.py
import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ReportStatus(str, enum.Enum):
    """Statuts possibles pour un rapport de renseignement"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


# Table d'association pour les tags de rapport
report_tag = Table(
    "report_tag",
    Base.metadata,
    Column("report_id", Integer, ForeignKey("report.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
)


class Report(Base):
    """
    Modèle pour les rapports de renseignement
    """
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    classification = Column(String(50), nullable=False, index=True)
    location = Column(String(255), nullable=True)
    coordinates = Column(String(100), nullable=True)
    report_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Relations avec les utilisateurs
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_by = relationship("User", foreign_keys=[submitted_by_id], back_populates="submitted_reports")
    
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = relationship("User", foreign_keys=[approved_by_id], back_populates="approved_reports")
    
    # Statut du rapport
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT, nullable=False, index=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Données d'IA
    ai_analysis = Column(Text, nullable=True)
    threat_level = Column(String(50), nullable=True)
    credibility_score = Column(Integer, nullable=True)
    
    # Relations
    attachments = relationship("Attachment", back_populates="report", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="report", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=report_tag, back_populates="reports")
    
    def __repr__(self):
        return f"<Report {self.id}: {self.title}>"


class Tag(Base):
    """
    Modèle pour les tags associés aux rapports
    """
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Relations
    reports = relationship("Report", secondary=report_tag, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag {self.id}: {self.name}>"


class Attachment(Base):
    """
    Modèle pour les pièces jointes aux rapports
    """
    __tablename__ = "attachment"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Taille en octets
    file_path = Column(String(512), nullable=False)  # Chemin de stockage interne
    
    # Relation avec le rapport
    report_id = Column(Integer, ForeignKey("report.id"), nullable=False)
    report = relationship("Report", back_populates="attachments")
    
    # Métadonnées
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_by = relationship("User")
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Attachment {self.id}: {self.filename}>"


class Comment(Base):
    """
    Modèle pour les commentaires sur les rapports
    """
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    
    # Relations
    report_id = Column(Integer, ForeignKey("report.id"), nullable=False)
    report = relationship("Report", back_populates="comments")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    # Métadonnées
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Report {self.report_id}>"