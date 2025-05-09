# app/db/base.py
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Classe de base pour tous les modèles SQLAlchemy
    
    Attributes:
        id: L'identifiant primaire
        __name__: Le nom de la classe, utilisé comme nom de table par défaut
    """
    
    id: Any
    __name__: str
    
    # Générer le nom de la table automatiquement à partir du nom de la classe
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()