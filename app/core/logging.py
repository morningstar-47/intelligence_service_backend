# Configuration des logs
# app/core/logging.py
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.config import settings

# Configurer le logger
logger = logging.getLogger(__name__)


def setup_logging():
    """
    Configure la journalisation globale de l'application
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configuration de base
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Désactiver les logs trop verbeux
    if log_level > logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def log_auth_activity(
    matricule: str,
    action: str,
    details: str,
    ip_address: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Journalise une activité d'authentification
    
    Args:
        matricule: Matricule de l'utilisateur
        action: Type d'action (login, logout, etc.)
        details: Description détaillée de l'activité
        ip_address: Adresse IP de l'utilisateur
        metadata: Métadonnées additionnelles
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "matricule": matricule,
        "action": action,
        "details": details,
        "ip_address": ip_address
    }
    
    if metadata:
        log_entry["metadata"] = metadata
    
    # Journaliser l'activité
    logger.info(f"Auth activity: {action} by {matricule}: {details}")
    
    # En production, on pourrait stocker ces logs dans la base de données
    # via un modèle AuditLog ou envoyer à un service de monitoring externe
    if settings.ENABLE_AUDIT_LOGGING:
        try:
            # Ici on pourrait ajouter le log à la base de données
            # Cette implémentation est simplifiée pour l'exemple
            pass
        except Exception as e:
            logger.error(f"Failed to store auth log: {str(e)}")


def log_request(request, response_time: float):
    """
    Journalise une requête HTTP
    
    Args:
        request: Objet requête FastAPI
        response_time: Temps de réponse en secondes
    """
    logger.info(f"{request.method} {request.url.path} - {response_time:.4f}s")


class RequestLoggingMiddleware:
    """
    Middleware pour journaliser les requêtes HTTP
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Calculer le temps de réponse
                response_time = time.time() - start_time
                
                # Récupérer les informations de la requête
                method = scope.get("method", "UNKNOWN")
                path = scope.get("path", "UNKNOWN")
                
                # Journaliser la requête
                logger.info(f"{method} {path} - {response_time:.4f}s - {message.get('status', 'UNKNOWN')}")
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def log_system_event(
    event_type: str,
    message: str,
    severity: str = "info",
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Journalise un événement système
    
    Args:
        event_type: Type d'événement
        message: Description de l'événement
        severity: Niveau de sévérité (info, warning, error, critical)
        metadata: Métadonnées additionnelles
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "message": message,
        "severity": severity
    }
    
    if metadata:
        log_entry["metadata"] = metadata
    
    # Journaliser l'événement avec le niveau de sévérité approprié
    log_method = getattr(logger, severity.lower(), logger.info)
    log_method(f"System event: {event_type} - {message}")
    
    # En production, on pourrait stocker ces logs dans la base de données
    # ou envoyer à un service de monitoring externe