# Sécurité et gestion des JWT
# app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Génère un token JWT avec les informations d'authentification
    
    Args:
        subject: Sujet du token (généralement le matricule de l'utilisateur)
        expires_delta: Délai d'expiration du token
        additional_data: Données supplémentaires à inclure dans le token
    
    Returns:
        Token JWT encodé
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Données de base du token
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Ajouter les données supplémentaires si fournies
    if additional_data:
        to_encode.update(additional_data)
    
    # Encoder le token avec la clé secrète
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe en clair correspond au hash stocké
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe stocké
    
    Returns:
        True si le mot de passe correspond, False sinon
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Génère le hash d'un mot de passe
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Hash du mot de passe
    """
    return pwd_context.hash(password)