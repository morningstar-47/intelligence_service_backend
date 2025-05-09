# app/db/init_db.py
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole, ClearanceLevel
from app.models.report import Report
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


# Données initiales pour les utilisateurs de démonstration
INITIAL_USERS = [
    {
        "matricule": "AD-1234A",
        "full_name": "Admin User",
        "email": "admin@intelligence-service.com",
        "password": "password123",
        "role": UserRole.ADMIN,
        "clearance_level": ClearanceLevel.TOP_SECRET,
        "is_active": True
    },
    {
        "matricule": "CM-5678B",
        "full_name": "Commander User",
        "email": "commander@intelligence-service.com",
        "password": "password123",
        "role": UserRole.COMMANDER,
        "clearance_level": ClearanceLevel.SECRET,
        "is_active": True
    },
    {
        "matricule": "FD-9012C",
        "full_name": "Field Agent",
        "email": "field@intelligence-service.com",
        "password": "password123",
        "role": UserRole.FIELD,
        "clearance_level": ClearanceLevel.CONFIDENTIAL,
        "is_active": True
    }
]


def init_db(db: Session) -> None:
    """
    Initialise la base de données avec des données de démonstration
    
    Args:
        db: Session de base de données
    """
    # Créer les utilisateurs initiaux
    create_initial_users(db)
    
    # Créer des données de démonstration
    if settings.BACKEND_CORS_ORIGINS:
        create_demo_data(db)


def create_initial_users(db: Session) -> None:
    """
    Crée les utilisateurs initiaux s'ils n'existent pas déjà
    
    Args:
        db: Session de base de données
    """
    for user_data in INITIAL_USERS:
        # Vérifier si l'utilisateur existe déjà
        user = db.query(User).filter(User.matricule == user_data["matricule"]).first()
        
        if not user:
            # Créer l'utilisateur avec le mot de passe hashé
            db_user = User(
                matricule=user_data["matricule"],
                full_name=user_data["full_name"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                clearance_level=user_data["clearance_level"],
                is_active=user_data["is_active"]
            )
            
            db.add(db_user)
            db.commit()
            logger.info(f"Created initial user: {user_data['matricule']} ({user_data['role']})")


def create_demo_data(db: Session) -> None:
    """
    Crée des données de démonstration pour une installation initiale
    
    Args:
        db: Session de base de données
    """
    # Créer des rapports de démonstration
    create_demo_reports(db)
    
    # Créer des alertes de démonstration
    create_demo_alerts(db)
    
    # Créer des entrées d'audit de démonstration
    create_demo_audit_logs(db)


def create_demo_reports(db: Session) -> None:
    """
    Crée des rapports de démonstration
    
    Args:
        db: Session de base de données
    """
    # Vérifier si des rapports existent déjà
    reports_count = db.query(Report).count()
    
    if reports_count == 0:
        # Créer des rapports de démonstration
        demo_reports = [
            Report(
                title="Activité suspecte à la frontière Est",
                content="Plusieurs véhicules non identifiés ont été observés traversant la frontière Est à 0300 heures. "
                        "Les véhicules semblaient transporter du matériel lourd sous bâches. "
                        "Aucun marquage visible. Estimation de 5-7 personnes par véhicule.",
                source="Poste d'observation Alpha-3",
                classification="secret",
                location="48.3794° N, 25.5583° E",
                submitted_by_id=3,  # Field Agent
                status="pending"
            ),
            Report(
                title="Interception de communications cryptées",
                content="Interception d'un flux inhabituel de communications cryptées dans le secteur Delta. "
                        "Le chiffrement utilisé correspond à celui documenté dans le dossier T-7392. "
                        "Fréquence et volume suggérant une opération planifiée.",
                source="Station d'écoute Bravo-6",
                classification="top_secret",
                location="49.8397° N, 24.0297° E",
                submitted_by_id=3,  # Field Agent
                status="approved",
                approved_by_id=2  # Commander
            ),
            Report(
                title="Analyse de propagande sur réseaux sociaux",
                content="Augmentation significative de 72% de contenus de propagande ciblant les institutions gouvernementales. "
                        "La majorité des comptes impliqués ont été créés dans les 30 derniers jours. "
                        "Analyse linguistique suggère une origine étrangère malgré des tentatives de masquage.",
                source="Unité de surveillance numérique",
                classification="confidential",
                location="Cyberespace",
                submitted_by_id=3,  # Field Agent
                status="approved",
                approved_by_id=2  # Commander
            )
        ]
        
        db.add_all(demo_reports)
        db.commit()
        logger.info(f"Created {len(demo_reports)} demo reports")


def create_demo_alerts(db: Session) -> None:
    """
    Crée des alertes de démonstration
    
    Args:
        db: Session de base de données
    """
    # Vérifier si des alertes existent déjà
    alerts_count = db.query(Alert).count()
    
    if alerts_count == 0:
        # Créer des alertes de démonstration
        demo_alerts = [
            Alert(
                title="Mouvement de troupes détecté",
                description="Mouvement inhabituel de troupes à 15km de la frontière Nord. "
                            "Estimation de 200-300 personnels et 25-30 véhicules blindés. "
                            "Formation suggérant une préparation offensive.",
                alert_type=AlertType.TACTICAL,
                severity=AlertSeverity.HIGH,
                location="50.4501° N, 30.5234° E",
                created_by_id=2  # Commander
            ),
            Alert(
                title="Tentative d'intrusion système détectée",
                description="Multiples tentatives d'intrusion détectées sur le réseau sécurisé Alpha. "
                            "Signatures correspondant à l'acteur de menace SERPENT. "
                            "Aucune compromission confirmée à ce stade.",
                alert_type=AlertType.CYBER,
                severity=AlertSeverity.MEDIUM,
                location="Système réseau Alpha",
                created_by_id=1  # Admin
            ),
            Alert(
                title="Contact perdu avec l'agent de terrain",
                description="Contact perdu avec l'agent NIGHTHAWK en mission dans le secteur Charlie. "
                            "Dernier check-in il y a 12 heures. Procédure d'urgence ECHO initié.",
                alert_type=AlertType.FIELD,
                severity=AlertSeverity.CRITICAL,
                location="45.9432° N, 24.9668° E",
                created_by_id=2  # Commander
            )
        ]
        
        db.add_all(demo_alerts)
        db.commit()
        logger.info(f"Created {len(demo_alerts)} demo alerts")


def create_demo_audit_logs(db: Session) -> None:
    """
    Crée des entrées d'audit de démonstration
    
    Args:
        db: Session de base de données
    """
    # Vérifier si des logs d'audit existent déjà
    audit_count = db.query(AuditLog).count()
    
    if audit_count == 0:
        # Créer des logs d'audit de démonstration
        demo_logs = [
            AuditLog(
                user_id=1,  # Admin
                action="user_create",
                resource_type="user",
                resource_id=3,  # Field Agent ID
                details="Created new field agent account"
            ),
            AuditLog(
                user_id=2,  # Commander
                action="report_approve",
                resource_type="report",
                resource_id=2,  # Report ID
                details="Approved intelligence report: Interception de communications cryptées"
            ),
            AuditLog(
                user_id=1,  # Admin
                action="settings_change",
                resource_type="system",
                resource_id=None,
                details="Updated system security settings: Enhanced authentication requirements"
            ),
            AuditLog(
                user_id=3,  # Field Agent
                action="report_submit",
                resource_type="report",
                resource_id=1,  # Report ID
                details="Submitted new intelligence report: Activité suspecte à la frontière Est"
            )
        ]
        
        db.add_all(demo_logs)
        db.commit()
        logger.info(f"Created {len(demo_logs)} demo audit logs")