# tests/api/test_auth.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.user import get_user_by_matricule
from app.main import app
from app.tests.utils.utils import random_matricule
from app.tests.utils.user import create_random_user


client = TestClient(app)


def test_login_access_token(db: Session) -> None:
    """
    Test d'authentification avec matricule et mot de passe corrects.
    """
    password = "password123"
    user = create_random_user(db, password=password)
    
    login_data = {
        "matricule": user.matricule,
        "password": password,
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    tokens = response.json()
    
    assert response.status_code == 200
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"
    assert tokens["role"] == user.role
    assert tokens["matricule"] == user.matricule


def test_login_wrong_password(db: Session) -> None:
    """
    Test d'authentification avec un mot de passe incorrect.
    """
    password = "password123"
    user = create_random_user(db, password=password)
    
    login_data = {
        "matricule": user.matricule,
        "password": "wrong_password",
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_nonexistent_user() -> None:
    """
    Test d'authentification avec un matricule inexistant.
    """
    login_data = {
        "matricule": random_matricule(),
        "password": "password123",
    }
    
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_inactive_user(db: Session) -> None:
    """
    Test d'authentification avec un utilisateur inactif.
    """
    password = "password123"
    user = create_random_user(db, password=password, is_active=False)

    login_data = {
        "matricule": user.matricule,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    assert response.status_code == 401
    assert "detail" in response.json()  