# # Configuration environnement
# # app/core/config.py
# import os
# import secrets
# from typing import Dict, List, Optional, Union, Any
# from pydantic import AnyHttpUrl, BaseSettings, validator

# class Settings(BaseSettings):
#     API_V1_STR: str = "/api/v1"
#     SECRET_KEY: str = secrets.token_urlsafe(32)
#     # 60 minutes * 24 heures * 8 jours = 8 jours
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
#     # CORS Origins autorisées
#     BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

#     @validator("BACKEND_CORS_ORIGINS", pre=True)
#     def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
#         if isinstance(v, str) and not v.startswith("["):
#             return [i.strip() for i in v.split(",")]
#         elif isinstance(v, (list, str)):
#             return v
#         raise ValueError(v)

#     # Configuration de la base de données
#     POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
#     POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
#     POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
#     POSTGRES_DB: str = os.getenv("POSTGRES_DB", "intelligence_service")
#     SQLALCHEMY_DATABASE_URI: Optional[str] = None

#     @validator("SQLALCHEMY_DATABASE_URI", pre=True)
#     def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
#         if isinstance(v, str):
#             return v
#         return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}"

#     # Configuration de l'authentification
#     ALGORITHM: str = "HS256"  # Algorithme pour les tokens JWT

#     # Configuration des emails
#     SMTP_TLS: bool = True
#     SMTP_PORT: Optional[int] = None
#     SMTP_HOST: Optional[str] = None
#     SMTP_USER: Optional[str] = None
#     SMTP_PASSWORD: Optional[str] = None
#     EMAILS_FROM_EMAIL: Optional[str] = None
#     EMAILS_FROM_NAME: Optional[str] = None

#     # Chemins pour les modèles IA
#     AI_MODELS_PATH: str = os.getenv("AI_MODELS_PATH", "app/ai/models/saved_models")
    
#     # Journalisation
#     LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
#     # Configuration des niveaux d'habilitation
#     CLEARANCE_LEVELS: Dict[str, int] = {
#         "confidential": 1,
#         "secret": 2,
#         "top_secret": 3
#     }
    
#     # Configuration des rôles
#     ROLES: List[str] = ["admin", "commander", "field"]
    
#     # Activation des fonctionnalités
#     ENABLE_AI_FEATURES: bool = os.getenv("ENABLE_AI_FEATURES", "True").lower() == "true"
#     ENABLE_WEBSOCKETS: bool = os.getenv("ENABLE_WEBSOCKETS", "True").lower() == "true"
#     ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() == "true"
    
#     class Config:
#         case_sensitive = True
#         env_file = ".env"


# settings = Settings()

# Configuration environnement
# app/core/config.py
# Configuration environnement
# app/core/config.py
import os
import secrets
from typing import Dict, List, Optional, Union, Any
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 heures * 8 jours = 8 jours
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # CORS Origins autorisées
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Configuration de la base de données
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "intelligence_service")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str):
            return v
        
        # Access the values from the model data
        postgres_user = info.data.get("POSTGRES_USER", cls.model_fields["POSTGRES_USER"].default)
        postgres_password = cls.model_fields["POSTGRES_PASSWORD"].default
        postgres_server = cls.model_fields["POSTGRES_SERVER"].default
        postgres_db = cls.model_fields["POSTGRES_DB"].default
        
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}/{postgres_db}"

    # ... reste du code inchangé ...

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()