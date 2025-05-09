# Intelligence-Service Backend

Backend pour le tableau de bord de service de renseignement militaire avec authentification basée sur les rôles, intégration IA et redirection automatique.

## 🌟 Fonctionnalités

- **Authentification sécurisée** : Système basé sur matricule (format: AF-1234P) et JWT
- **Contrôle d'accès basé sur les rôles** : Admin, Commander, Field Agent
- **Niveaux d'habilitation** : Top Secret, Secret, Confidential
- **Module d'IA intégré** : Analyse de menaces, traitement du langage naturel, détection d'anomalies
- **Gestion des rapports** : Création, édition, approbation, commentaires
- **Système d'alertes** : Notifications en temps réel, recommandations automatiques
- **Journalisation d'audit** : Suivi détaillé de toutes les activités
- **API RESTful** : Endpoints structurés et documentés avec OpenAPI

## 🛠️ Technologies

- **Framework** : FastAPI
- **Base de données** : PostgreSQL
- **ORM** : SQLAlchemy
- **Migrations** : Alembic
- **Authentification** : JWT avec Python-JOSE
- **Validation de données** : Pydantic v2
- **IA/ML** : NumPy, scikit-learn, NLTK, spaCy
- **Géospatial** : GeoPandas
- **Conteneurisation** : Docker & Docker Compose

## 🚀 Installation

### Prérequis

- Python 3.11+
- Docker et Docker Compose
- Poetry

### Installation avec Docker (recommandée)

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/your-org/intelligence-service-backend.git
   cd intelligence-service-backend
   ```

2. Créer un fichier `.env` à partir du modèle :
   ```bash
   cp .env.example .env
   ```

3. Configurer les variables d'environnement dans le fichier `.env`

4. Démarrer les conteneurs Docker :
   ```bash
   docker-compose up -d
   ```

5. L'API sera disponible à l'adresse : http://localhost:8000
   La documentation OpenAPI sera disponible à : http://localhost:8000/api/v1/docs

### Installation locale (développement)

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/your-org/intelligence-service-backend.git
   cd intelligence-service-backend
   ```

2. Installer les dépendances avec Poetry :
   ```bash
   poetry install
   ```

3. Créer un fichier `.env` à partir du modèle :
   ```bash
   cp .env.example .env
   ```

4. Configurer les variables d'environnement dans le fichier `.env`

5. Activer l'environnement virtuel :
   ```bash
   poetry shell
   ```

6. Appliquer les migrations de base de données :
   ```bash
   alembic upgrade head
   ```

7. Exécuter le serveur :
   ```bash
   uvicorn app.main:app --reload
   ```

## 📁 Structure du projet

```
intelligence-service-backend/
├── app/                              # Application principale
│   ├── __init__.py
│   ├── main.py                       # Point d'entrée FastAPI
│   ├── api/                          # Routes API
│   │   ├── __init__.py
│   │   ├── api_v1/                   # API v1
│   │       ├── __init__.py
│   │       ├── api.py                # Routeur principal
│   │       ├── endpoints/            # Points d'entrée API
│   │           ├── auth.py           # Authentification
│   │           ├── users.py          # Gestion utilisateurs
│   │           ├── reports.py        # Gestion rapports
│   │           ├── alerts.py         # Gestion alertes
│   │           ├── map_data.py       # Données cartographiques
│   │           ├── ai.py             # Endpoints d'IA
│   │           └── settings.py       # Paramètres système
│   ├── core/                         # Fonctionnalités centrales
│   │   ├── __init__.py
│   │   ├── config.py                 # Configuration
│   │   ├── security.py               # Sécurité et JWT
│   │   ├── permissions.py            # Système de permissions
│   │   └── logging.py                # Configuration logs
│   ├── crud/                         # Opérations CRUD
│   │   ├── __init__.py
│   │   ├── user.py                   # CRUD utilisateurs
│   │   ├── report.py                 # CRUD rapports
│   │   └── ...
│   ├── db/                           # Base de données
│   │   ├── __init__.py
│   │   ├── base.py                   # Classe base
│   │   ├── session.py                # Session SQLAlchemy
│   │   └── init_db.py                # Initialisation DB
│   ├── models/                       # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py                   # Modèle utilisateur
│   │   ├── report.py                 # Modèle rapport
│   │   └── ...
│   ├── schemas/                      # Schémas Pydantic
│   │   ├── __init__.py
│   │   ├── user.py                   # Schémas utilisateur
│   │   ├── report.py                 # Schémas rapport
│   │   └── ...
│   └── ai/                           # Module d'IA
│       ├── __init__.py
│       ├── integration/
│       │   └── ai_service.py         # Service d'IA principal
│       ├── models/
│       │   ├── saved_models/         # Modèles entraînés
│       │   ├── threat_analyzer.py    # Analyseur de menaces
│       │   └── ...
│       └── data_processing/
│           ├── text_processor.py     # Traitement du texte
│           └── ...
├── alembic/                          # Migrations de base de données
├── tests/                            # Tests
├── uploads/                          # Fichiers téléchargés
├── docker-compose.yml                # Configuration Docker Compose
├── Dockerfile                        # Configuration Docker
├── pyproject.toml                    # Configuration du projet
└── README.md                         # Documentation
```

## 🔒 Authentification et contrôle d'accès

### Format de matricule

Les utilisateurs sont identifiés par un matricule au format `XX-9999X`, par exemple `AF-1234P`.

### Rôles et permissions

- **Admin** : Accès complet à toutes les fonctionnalités
- **Commander** : Gestion des opérations, approbation des rapports, analyse stratégique
- **Field Agent** : Soumission de rapports, consultation de ressources spécifiques

### Niveaux d'habilitation

- **Top Secret** : Accès à toutes les informations
- **Secret** : Accès aux informations Secret, Confidential et Unclassified
- **Confidential** : Accès aux informations Confidential et Unclassified

## 🧠 Module d'IA

Le backend intègre plusieurs capacités d'intelligence artificielle :

- **Analyse de menaces** : Évaluation des risques et attribution de scores de menace
- **Analyse de rapports** : Extraction d'informations clés, génération de tags, calcul de crédibilité
- **Résumé de renseignement** : Synthèse des informations issues de multiples rapports
- **Détection d'anomalies** : Identification de patterns anormaux dans les données
- **Traitement du langage naturel** : Requêtes en langage naturel pour l'exploration de données
- **Analyse géospatiale** : Étude des clusters de points géographiques

## 📚 Documentation API

La documentation OpenAPI est disponible à l'adresse suivante : http://localhost:8000/api/v1/docs

Documentation ReDoc : http://localhost:8000/api/v1/redoc

## 🧪 Tests

Exécuter les tests avec pytest :

```bash
pytest
```

Avec couverture de code :

```bash
pytest --cov=app
```

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).