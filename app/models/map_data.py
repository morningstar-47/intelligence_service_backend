# app/models/map_data.py
import enum
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class MapMarkerType(str, enum.Enum):
    """Types de marqueurs cartographiques"""
    INTEL = "intel"  # Point de renseignement
    THREAT = "threat"  # Menace identifiée
    ASSET = "asset"  # Ressource/actif
    AGENT = "agent"  # Agent de terrain
    INCIDENT = "incident"  # Incident rapporté
    OPERATION = "operation"  # Opération en cours
    BASE = "base"  # Base/installation
    CHECKPOINT = "checkpoint"  # Poste de contrôle
    CUSTOM = "custom"  # Marqueur personnalisé


class MapMarker(Base):
    """
    Modèle pour les marqueurs cartographiques
    """
    __tablename__ = "map_marker"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Coordonnées géographiques
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Type de marqueur
    marker_type = Column(Enum(MapMarkerType), nullable=False, index=True)
    
    # Métadonnées
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relations optionnelles
    report_id = Column(Integer, ForeignKey("report.id"), nullable=True)
    report = relationship("Report")
    
    alert_id = Column(Integer, ForeignKey("alert.id"), nullable=True)
    alert = relationship("Alert")
    
    # Propriétés visuelles
    color = Column(String(50), nullable=True)  # Couleur du marqueur
    icon = Column(String(50), nullable=True)  # Icône du marqueur
    
    # Options supplémentaires
    is_visible = Column(Boolean, default=True, nullable=False)  # Visibilité sur la carte
    min_zoom_level = Column(Integer, nullable=True)  # Niveau de zoom minimal pour voir le marqueur
    
    # Données personnalisées
    custom_data = Column(JSON, nullable=True)  # Données supplémentaires en JSON
    
    def __repr__(self):
        return f"<MapMarker {self.id}: {self.title} ({self.marker_type})>"


class GeoLayer(Base):
    """
    Modèle pour les couches géographiques (zones, lignes, etc.)
    """
    __tablename__ = "geo_layer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type de couche (polygon, line, etc.)
    layer_type = Column(String(50), nullable=False)
    
    # Données géographiques (GeoJSON)
    geo_data = Column(JSON, nullable=False)
    
    # Métadonnées
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Propriétés visuelles
    color = Column(String(50), nullable=True)
    fill_color = Column(String(50), nullable=True)
    stroke_width = Column(Integer, nullable=True)
    opacity = Column(Float, nullable=True)
    
    # Options
    is_visible = Column(Boolean, default=True, nullable=False)
    is_interactive = Column(Boolean, default=True, nullable=False)
    min_zoom_level = Column(Integer, nullable=True)
    z_index = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<GeoLayer {self.id}: {self.name} ({self.layer_type})>"


class MapSettings(Base):
    """
    Modèle pour les paramètres de carte par utilisateur
    """
    __tablename__ = "map_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # Utilisateur
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    user = relationship("User")
    
    # Paramètres de vue
    default_latitude = Column(Float, nullable=True)
    default_longitude = Column(Float, nullable=True)
    default_zoom = Column(Integer, nullable=True)
    
    # Préférences d'affichage
    preferred_map_type = Column(String(50), nullable=True)  # satellite, terrain, streets, etc.
    show_grid = Column(Boolean, default=True, nullable=False)
    show_labels = Column(Boolean, default=True, nullable=False)
    
    # Filtres
    visible_marker_types = Column(JSON, nullable=True)  # Liste des types à afficher
    
    # Métadonnées
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MapSettings for User {self.user_id}>"