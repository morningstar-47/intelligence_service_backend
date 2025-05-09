# Points de terminaison d'authentification
# app/api/api_v1/endpoints/auth.py
from typing import Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token
from app.core.logging import log_auth_activity
from app.crud.user import authenticate_user, get_user_by_email, update_user_last_login
from app.models.user import User
from app.schemas.auth import Token, LoginRequest, UserInfo, ResetPasswordRequest, ResetPasswordConfirm

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Authentification avec matricule et mot de passe pour obtenir un token JWT
    """
    # Récupérer l'adresse IP
    client_ip = request.client.host if request.client else None
    
    # Authentifier l'utilisateur
    user = authenticate_user(db, login_data.matricule, login_data.password)
    if not user:
        log_auth_activity(
            matricule=login_data.matricule,
            action="login_failed",
            details="Identifiants invalides",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matricule ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que l'utilisateur est actif
    if not user.is_active:
        log_auth_activity(
            matricule=user.matricule,
            action="login_failed",
            details="Compte inactif",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur inactif",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mettre à jour la date de dernière connexion
    now = datetime.utcnow()
    update_user_last_login(db, user.id, now)
    
    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.matricule,
        expires_delta=access_token_expires,
        additional_data={
            "role": user.role,
            "clearance_level": user.clearance_level,
            "user_id": user.id
        }
    )
    
    # Journaliser la connexion réussie
    log_auth_activity(
        matricule=user.matricule,
        action="login_success",
        details=f"Connexion réussie (rôle: {user.role}, niveau: {user.clearance_level})",
        ip_address=client_ip,
        metadata={"user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "matricule": user.matricule,
        "full_name": user.full_name
    }


@router.post("/login/form", response_model=Token)
def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    Authentification OAuth2 avec formulaire standard
    """
    # Récupérer l'adresse IP
    client_ip = request.client.host if request.client else None
    
    # Authentifier l'utilisateur (le champ username contient le matricule)
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        log_auth_activity(
            matricule=form_data.username,
            action="login_failed",
            details="Identifiants invalides (formulaire OAuth2)",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Matricule ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que l'utilisateur est actif
    if not user.is_active:
        log_auth_activity(
            matricule=user.matricule,
            action="login_failed",
            details="Compte inactif (formulaire OAuth2)",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur inactif",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mettre à jour la date de dernière connexion
    now = datetime.utcnow()
    update_user_last_login(db, user.id, now)
    
    # Créer le token d'accès
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.matricule,
        expires_delta=access_token_expires,
        additional_data={
            "role": user.role,
            "clearance_level": user.clearance_level,
            "user_id": user.id
        }
    )
    
    # Journaliser la connexion réussie
    log_auth_activity(
        matricule=user.matricule,
        action="login_success",
        details=f"Connexion réussie via formulaire OAuth2 (rôle: {user.role})",
        ip_address=client_ip,
        metadata={"user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "matricule": user.matricule,
        "full_name": user.full_name
    }


@router.get("/me", response_model=UserInfo)
def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Récupère les informations de l'utilisateur actuellement connecté
    """
    # Journaliser l'accès
    client_ip = request.client.host if request.client else None
    log_auth_activity(
        matricule=current_user.matricule,
        action="profile_access",
        details="Accès aux informations du profil",
        ip_address=client_ip
    )
    
    return {
        "id": current_user.id,
        "matricule": current_user.matricule,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "clearance_level": current_user.clearance_level,
        "last_login": current_user.last_login
    }


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Déconnecte l'utilisateur actuel
    
    Note: Avec JWT, la déconnexion côté serveur est limitée car les tokens
    restent valides jusqu'à expiration. Cet endpoint est surtout utile pour
    journaliser la déconnexion et pourrait être utilisé avec une liste noire
    de tokens en production.
    """
    # Récupérer l'adresse IP
    client_ip = request.client.host if request.client else None
    
    # Journaliser la déconnexion
    log_auth_activity(
        matricule=current_user.matricule,
        action="logout",
        details="Déconnexion utilisateur",
        ip_address=client_ip,
        metadata={"user_id": current_user.id}
    )
    
    return {"detail": "Déconnexion réussie"}


@router.post("/reset-password/request")
def request_password_reset(
    request: Request,
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Demande de réinitialisation de mot de passe
    
    Note: Dans une implémentation réelle, cela enverrait un email avec un lien
    de réinitialisation. Pour l'exemple, nous simulons le processus.
    """
    # Récupérer l'adresse IP
    client_ip = request.client.host if request.client else None
    
    # Vérifier que l'utilisateur existe
    user = get_user_by_email(db, reset_data.matricule)
    if not user:
        # Pour des raisons de sécurité, ne pas indiquer si l'utilisateur existe
        log_auth_activity(
            matricule=reset_data.matricule,
            action="reset_password_request",
            details="Demande de réinitialisation pour un matricule inexistant",
            ip_address=client_ip
        )
        return {"detail": "Si ce matricule existe, un email a été envoyé avec les instructions de réinitialisation"}
    
    # Vérifier que l'utilisateur est actif
    if not user.is_active:
        log_auth_activity(
            matricule=user.matricule,
            action="reset_password_request",
            details="Demande de réinitialisation pour un compte inactif",
            ip_address=client_ip,
            metadata={"user_id": user.id}
        )
        return {"detail": "Si ce matricule existe, un email a été envoyé avec les instructions de réinitialisation"}
    
    # Créer un token temporaire pour la réinitialisation
    token_expires = timedelta(hours=1)
    reset_token = create_access_token(
        subject=user.matricule,
        expires_delta=token_expires,
        additional_data={"action": "reset_password"}
    )
    
    # En production, envoi d'un email avec le token
    # Pour l'exemple, on renvoie simplement le token
    
    # Journaliser la demande
    log_auth_activity(
        matricule=user.matricule,
        action="reset_password_request",
        details="Demande de réinitialisation de mot de passe",
        ip_address=client_ip,
        metadata={"user_id": user.id}
    )
    
    # En production, ne pas renvoyer le token
    if settings.LOG_LEVEL == "DEBUG":
        return {
            "detail": "Email de réinitialisation envoyé",
            "debug_token": reset_token  # Uniquement pour le développement
        }
    
    return {"detail": "Si ce matricule existe, un email a été envoyé avec les instructions de réinitialisation"}


@router.post("/reset-password/confirm")
def confirm_password_reset(
    request: Request,
    reset_data: ResetPasswordConfirm,
    db: Session = Depends(get_db)
) -> Any:
    """
    Confirme la réinitialisation de mot de passe avec le token fourni
    """
    # Récupérer l'adresse IP
    client_ip = request.client.host if request.client else None
    
    try:
        # Décoder le token de réinitialisation
        payload = jwt.decode(
            reset_data.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Vérifier que c'est bien un token de réinitialisation
        if payload.get("action") != "reset_password":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de réinitialisation invalide",
            )
        
        # Récupérer l'utilisateur à partir du matricule dans le token
        matricule = payload.get("sub")
        if not matricule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalide",
            )
        
        user = get_user_by_matricule(db, matricule)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilisateur invalide ou inactif",
            )
        
        # Mettre à jour le mot de passe
        user.hashed_password = get_password_hash(reset_data.new_password)
        db.commit()
        
        # Journaliser la réinitialisation
        log_auth_activity(
            matricule=user.matricule,
            action="reset_password_success",
            details="Réinitialisation de mot de passe réussie",
            ip_address=client_ip,
            metadata={"user_id": user.id}
        )
        
        return {"detail": "Mot de passe réinitialisé avec succès"}
        
    except JWTError:
        log_auth_activity(
            matricule="unknown",
            action="reset_password_failed",
            details="Tentative de réinitialisation avec un token invalide",
            ip_address=client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de réinitialisation invalide ou expiré",
        )