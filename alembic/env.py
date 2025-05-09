# alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import de l'application pour accéder à sa configuration
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au chemin de recherche Python
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.base import Base
from app.models.user import User
from app.models.report import Report, Tag, Attachment, Comment
from app.models.alert import Alert, AlertAction
from app.models.map_data import MapMarker, GeoLayer, MapSettings
from app.models.audit_log import AuditLog

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpréter le fichier .ini par rapport à sa position
fileConfig(config.config_file_name)

# Ajouter l'URL de la base de données de l'application
config.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)

# Ajouter les métadonnées des modèles pour la génération automatique
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Exécute les migrations en mode "offline".

    Cela crée simplement un script de migration SQL à partir des configurations
    et génère le fichier de migration.
    
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Exécute les migrations en mode "online".

    Dans ce mode, les migrations sont exécutées directement sur la base de données.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Comparaison sensible à la casse pour les noms de tables et de colonnes
            # Si vous utilisez une base de données non sensible à la casse, mettez ceci à False
            compare_type=True,
            # Ajouter des options supplémentaires si nécessaire
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()