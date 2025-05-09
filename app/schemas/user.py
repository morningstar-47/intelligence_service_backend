# app/schemas/user.py
import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator, Field


# Schéma de base pour l'utilisateur
class UserBase(BaseModel):
    matricule: str
    full_name: str
    email: EmailStr
    role: str
    clearance_level: str
    is_active: Optional[bool] = True
    
    @validator("matricule")
    def validate_matricule(cls, v):
        """Valide le format du matricule (format: AF-1234P)"""
        pattern = r'^[A-Z]{2}-\d{4}[A-Z]$'
        if not re.match(pattern, v):
            raise ValueError("Le matricule doit avoir le format XX-9999X (ex: AF-1234P)")
        return v


# Schéma pour la création d'un utilisateur (entrée)
class UserCreate(UserBase):
    password: str
    
    @validator("password")
    def password_strength(cls, v):
        """Vérifie la force du mot de passe"""
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v


# Schéma pour la mise à jour d'un utilisateur (entrée)
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    clearance_level: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator("password")
    def password_strength(cls, v):
        """Vérifie la force du mot de passe si fourni"""
        if v and len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        return v


# Schéma pour les informations d'utilisateur (sortie)
class User(UserBase):
    id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Schéma pour les informations d'utilisateur avec détails (sortie)
class UserDetail(User):
    submitted_reports_count: Optional[int] = 0
    approved_reports_count: Optional[int] = 0
    alerts_created_count: Optional[int] = 0
    
    class Config:
        orm_mode = True


# Schéma pour la liste des utilisateurs (sortie)
class UserList(BaseModel):
    items: List[User]
    total: int
    page: int
    page_size: int
    pages: int

    class Config:
        orm_mode = True


# Schéma pour les informations d'utilisateur connecté (sortie)
class UserProfile(BaseModel):
    id: int
    matricule: str
    full_name: str
    email: EmailStr
    role: str
    clearance_level: str
    last_login: Optional[datetime] = None
    permissions: dict
    
    class Config:
        orm_mode = True


# Schéma pour le changement de mot de passe (entrée)
class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    
    @validator("new_password")
    def password_strength(cls, v, values):
        """Vérifie la force du mot de passe et qu'il est différent de l'ancien"""
        if len(v) < 8:
            raise ValueError("Le nouveau mot de passe doit contenir au moins 8 caractères")
        if "current_password" in values and v == values["current_password"]:
            raise ValueError("Le nouveau mot de passe doit être différent de l'ancien")
        return v