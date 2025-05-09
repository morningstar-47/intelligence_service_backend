# app/main.py
import time
from typing import Any

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api_v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging, log_request
from app.db.init_db import init_db
from app.db.session import get_db

# Configurer la journalisation
setup_logging()

# Créer l'application FastAPI
app = FastAPI(
    title="Intelligence-Service API",
    description="API pour le tableau de bord de service de renseignement militaire",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configurer les CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Ajouter les routes de l'API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware pour journaliser les requêtes et mesurer le temps de réponse
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Journaliser la requête
    log_request(request, process_time)
    
    # Ajouter le temps de réponse aux en-têtes
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Gestionnaire d'exception global
    """
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue"},
    )


@app.get("/")
def read_root() -> Any:
    """
    Point de terminaison racine
    """
    return {
        "name": "Intelligence-Service API",
        "version": "1.0.0",
        "documentation": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
def health_check() -> Any:
    """
    Vérification de l'état de santé de l'API
    """
    return {"status": "ok", "version": "1.0.0"}


# Initialiser la base de données au démarrage
@app.on_event("startup")
def startup_event():
    """
    Événement de démarrage de l'application
    """
    db = next(get_db())
    init_db(db)