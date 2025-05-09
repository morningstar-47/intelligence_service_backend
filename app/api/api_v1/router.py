# Routeur principal APIv1

# app/api/api_v1/api.py
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, reports, alerts, map_data, settings, ai

# Créer le routeur principal de l'API v1
api_router = APIRouter()

# Enregistrer les routeurs des différents modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(users.router, prefix="/users", tags=["Utilisateurs"])
api_router.include_router(reports.router, prefix="/reports", tags=["Rapports"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alertes"])
api_router.include_router(map_data.router, prefix="/map", tags=["Cartographie"])
api_router.include_router(settings.router, prefix="/settings", tags=["Paramètres"])
api_router.include_router(ai.router, prefix="/ai", tags=["Intelligence Artificielle"])