# Dépendances d'injection
# app/api/deps.py
import logging
from typing import Generator, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.logging import log_auth_activity
from app.models.user import User, UserRole, ClearanceLevel
from app.schemas.auth import TokenPayload
from app.crud.user import get_user_by_matricule

logger = logging.getLogger(__name__)

# Point de terminaison pour l'authentification OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuellement authentifié
    à partir du token JWT.
    
    Args:
        db: Session de base de données
        token: Token JWT d'authentification
    
    Returns:
        User: Utilisateur actuel
    
    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
    """
    try:
        # Décoder le token JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Valider le contenu du token
        token_data = TokenPayload(**payload)
        
        # Vérifier que le token n'est pas expiré
        if token_data.exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token sans expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except (JWTError, ValidationError) as e:
        logger.warning(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les identifiants",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Récupérer l'utilisateur à partir du matricule dans le token
    user = get_user_by_matricule(db, matricule=token_data.sub)
    
    if user is None:
        log_auth_activity(
            matricule=token_data.sub,
            action="token_invalid_user",
            details="Tentative d'accès avec un token contenant un matricule invalide",
            ip_address=None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel et vérifier qu'il est actif
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        User: Utilisateur actuel et actif
    
    Raises:
        HTTPException: Si l'utilisateur n'est pas actif
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte utilisateur inactif",
        )
    return current_user


def get_current_user_with_permissions(
    required_roles: List[UserRole],
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel et vérifier ses permissions
    
    Args:
        required_roles: Liste des rôles autorisés
        current_user: Utilisateur actuel
    
    Returns:
        User: Utilisateur actuel avec les permissions requises
    
    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions requises
    """
    if current_user.role not in required_roles:
        log_auth_activity(
            matricule=current_user.matricule,
            action="permission_denied",
            details=f"Tentative d'accès à une ressource réservée aux rôles: {required_roles}",
            ip_address=None
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissions insuffisantes. Rôles requis: {required_roles}",
        )
    return current_user


def get_current_user_with_clearance(
    min_clearance: ClearanceLevel,
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel et vérifier son niveau d'habilitation
    
    Args:
        min_clearance: Niveau d'habilitation minimum requis
        current_user: Utilisateur actuel
    
    Returns:
        User: Utilisateur actuel avec le niveau d'habilitation requis
    
    Raises:
        HTTPException: Si l'utilisateur n'a pas le niveau d'habilitation requis
    """
    # Mapping des niveaux d'habilitation
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: 1,
        ClearanceLevel.SECRET: 2,
        ClearanceLevel.TOP_SECRET: 3
    }
    
    # Vérifier que l'utilisateur a un niveau d'habilitation suffisant
    user_clearance_level = clearance_levels[current_user.clearance_level]
    required_clearance_level = clearance_levels[min_clearance]
    
    if user_clearance_level < required_clearance_level:
        log_auth_activity(
            matricule=current_user.matricule,
            action="clearance_denied",
            details=f"Tentative d'accès à une ressource nécessitant l'habilitation: {min_clearance}",
            ip_address=None
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant. Niveau requis: {min_clearance}",
        )
    return current_user