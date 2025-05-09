# app/schemas/auth.py
import re
from typing import Optional
from pydantic import BaseModel, validator


class Token(BaseModel):
    """Schéma de réponse pour un token d'authentification"""
    access_token: str
    token_type: str
    role: str
    matricule: str
    full_name: str


class TokenPayload(BaseModel):
    """Schéma pour le contenu d'un token JWT"""
    sub: Optional[str] = None  # matricule
    exp: Optional[int] = None  # timestamp d'expiration
    role: Optional[str] = None
    clearance_level: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Schéma pour la requête de connexion"""
    matricule: str
    password: str
    
    @validator("matricule")
    def validate_matricule(cls, v):
        """Valide le format du matricule (format: AF-1234P)"""
        pattern = r'^[A-Z]{2}-\d{4}[A-Z]$'
        if not re.match(pattern, v):
            raise ValueError("Le matricule doit avoir le format XX-9999X (ex: AF-1234P)")
        return v


class UserInfo(BaseModel):
    """Schéma pour les informations de l'utilisateur connecté"""
    id: int
    matricule: str
    full_name: str
    email: str
    role: str
    clearance_level: str
    last_login: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    """Schéma pour la demande de réinitialisation de mot de passe"""
    matricule: str
    
    @validator("matricule")
    def validate_matricule(cls, v):
        """Valide le format du matricule (format: AF-1234P)"""
        pattern = r'^[A-Z]{2}-\d{4}[A-Z]$'
        if not re.match(pattern, v):
            raise ValueError("Le matricule doit avoir le format XX-9999X (ex: AF-1234P)")
        return v


class ResetPasswordConfirm(BaseModel):
    """Schéma pour la confirmation de réinitialisation de mot de passe"""
    token: str
    new_password: str
    
    @validator("new_password")
    def password_strength(cls, v):
        """Vérifie la force du mot de passe"""
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v