# app/ai/integration/ai_service.py
import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import settings
from app.core.logging import log_system_event
from app.models.user import User, ClearanceLevel
from app.models.report import Report

logger = logging.getLogger(__name__)


class AIService:
    """
    Service d'intégration pour les fonctionnalités d'IA
    """
    
    def __init__(self, models_path: str = None):
        """
        Initialise le service d'IA
        
        Args:
            models_path: Chemin vers les modèles sauvegardés
        """
        self.models_path = models_path or settings.AI_MODELS_PATH
        self.models = {}
        self.vectorizers = {}
        self.is_initialized = False
        
        # Vérifier si les fonctionnalités d'IA sont activées
        self.enabled = settings.ENABLE_AI_FEATURES
        
        if not self.enabled:
            logger.warning("Les fonctionnalités d'IA sont désactivées")
            return
            
        # Initialisation des modèles et vectoriseurs
        try:
            self._initialize_models()
            self.is_initialized = True
            logger.info("Service d'IA initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service d'IA: {str(e)}")
            log_system_event(
                "ai_initialization_error",
                f"Erreur lors de l'initialisation du service d'IA: {str(e)}",
                "error"
            )
    
    def _initialize_models(self):
        """
        Initialise les modèles d'IA
        """
        # Créer le répertoire des modèles s'il n'existe pas
        os.makedirs(self.models_path, exist_ok=True)
        
        # Initialiser les vectoriseurs pour l'analyse de texte
        self.vectorizers["tfidf"] = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english"
        )
        
        # Initialiser le modèle de détection d'anomalies
        self.models["anomaly_detector"] = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        
        # Autres modèles à initialiser selon les besoins...
    
    async def analyze_threat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les données pour détecter des menaces potentielles
        
        Args:
            data: Données à analyser
        
        Returns:
            Résultats de l'analyse
        """
        if not self.enabled or not self.is_initialized:
            return {"error": "Service d'IA non disponible"}
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(0.5)
            
            # Analyse de base des données d'entrée
            content = data.get("content", "")
            source = data.get("source", "unknown")
            location = data.get("location", "unknown")
            
            # Simulation d'analyse de menace basique
            keywords = {
                "critical": ["explosion", "attaque", "sabotage", "infiltration", "attentat"],
                "high": ["mouvement", "troupes", "suspect", "surveillance", "intrusion"],
                "medium": ["activité", "inhabituel", "déplacement", "communication", "crypté"],
                "low": ["observation", "patrouille", "routine", "reconnaissance"]
            }
            
            # Déterminer le niveau de menace
            threat_level = "negligible"
            threat_factors = []
            
            content_lower = content.lower()
            
            for level, words in keywords.items():
                found_words = [word for word in words if word in content_lower]
                if found_words:
                    threat_level = level
                    threat_factors.extend(found_words)
                    break
            
            # Calculer un score de crédibilité (0-100)
            credibility_score = min(len(content.split()) / 5, 100)
            
            # Résultats
            return {
                "threat_level": threat_level,
                "credibility_score": int(credibility_score),
                "factors": threat_factors,
                "summary": f"Analyse de menace complétée. Niveau: {threat_level}. Facteurs identifiés: {', '.join(threat_factors)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de menace: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_report(self, report: Report) -> Dict[str, Any]:
        """
        Analyse un rapport de renseignement
        
        Args:
            report: Rapport à analyser
        
        Returns:
            Résultats de l'analyse
        """
        if not self.enabled or not self.is_initialized:
            return {"error": "Service d'IA non disponible"}
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(0.5)
            
            content = report.content
            title = report.title
            
            # Analyse des mots-clés pour déterminer les tags
            keywords_to_tags = {
                "communication": "communications",
                "cyber": "cyber",
                "réseau": "réseau",
                "frontière": "frontière",
                "véhicule": "transport",
                "armement": "armement",
                "maritime": "maritime",
                "aérien": "aérien",
                "terrorisme": "terrorisme",
                "civil": "civil",
                "économie": "économique"
            }
            
            combined_text = (title + " " + content).lower()
            suggested_tags = []
            
            for keyword, tag in keywords_to_tags.items():
                if keyword in combined_text:
                    suggested_tags.append(tag)
            
            # Déterminer le niveau de menace
            threat_keywords = {
                "critical": ["imminent", "catastrophique", "attentat", "explosion"],
                "high": ["élevé", "dangereux", "armée", "attaque"],
                "medium": ["suspect", "inhabituel", "préoccupant"],
                "low": ["mineur", "routine", "observation"]
            }
            
            threat_level = "negligible"
            for level, words in threat_keywords.items():
                if any(word in combined_text for word in words):
                    threat_level = level
                    break
            
            # Calculer un score de crédibilité (0-100)
            # Dans une implémentation réelle, utiliserait des facteurs comme:
            # - fiabilité de la source
            # - cohérence interne
            # - recoupement avec d'autres informations
            # - précision des détails
            credibility_factors = {
                "length": min(len(content) / 1000, 1) * 20,  # longueur du rapport (max 20 pts)
                "details": 30 if len(content.split()) > 200 else 15,  # niveau de détail
                "source": 20 if report.source else 0,  # présence d'une source
                "location": 15 if report.location else 0,  # présence d'une localisation
                "base": 15  # score de base
            }
            
            credibility_score = sum(credibility_factors.values())
            
            # Extraction d'entités (simulation)
            entities = {
                "locations": [report.location] if report.location else [],
                "persons": [],
                "organizations": [],
                "dates": []
            }
            
            # Résultats
            return {
                "summary": f"Analyse du rapport '{report.title}' complétée.",
                "threat_level": threat_level,
                "credibility_score": int(credibility_score),
                "suggested_tags": suggested_tags,
                "entities": entities,
                "related_reports": [],  # Dans une implémentation réelle, rechercherait des rapports similaires
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du rapport {report.id}: {str(e)}")
            return {"error": str(e)}
    
    async def generate_intelligence_summary(self, reports: List[Report], timeframe: str) -> str:
        """
        Génère un résumé des renseignements récents
        
        Args:
            reports: Liste des rapports à inclure dans le résumé
            timeframe: Période de temps concernée
        
        Returns:
            Résumé généré
        """
        if not self.enabled or not self.is_initialized:
            return "Service d'IA non disponible. Impossible de générer un résumé."
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(1)
            
            if not reports:
                return "Aucun rapport disponible pour la période spécifiée."
            
            # Regrouper les rapports par classification
            reports_by_classification = {}
            for report in reports:
                if report.classification not in reports_by_classification:
                    reports_by_classification[report.classification] = []
                reports_by_classification[report.classification].append(report)
            
            # Générer le résumé
            summary_parts = [
                f"RÉSUMÉ DE RENSEIGNEMENT - PÉRIODE: {timeframe}",
                f"Nombre total de rapports: {len(reports)}",
                ""
            ]
            
            # Pour chaque classification, ajouter une section
            for classification, class_reports in reports_by_classification.items():
                summary_parts.append(f"== CLASSIFICATION: {classification.upper()} ({len(class_reports)} rapports) ==")
                
                # Simuler l'extraction des thèmes principaux
                themes = {}
                for report in class_reports:
                    words = report.content.lower().split()
                    for keyword in ["mouvement", "communication", "activité", "menace", "intrusion"]:
                        if keyword in words:
                            if keyword not in themes:
                                themes[keyword] = 0
                            themes[keyword] += 1
                
                # Ajouter les thèmes au résumé
                if themes:
                    summary_parts.append("\nThèmes principaux identifiés:")
                    for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True):
                        summary_parts.append(f"- {theme.capitalize()}: mentionné dans {count} rapport(s)")
                
                # Ajouter un résumé des rapports les plus importants
                summary_parts.append("\nRapports significatifs:")
                for i, report in enumerate(sorted(class_reports, key=lambda r: r.created_at, reverse=True)[:3]):
                    summary_parts.append(f"- {report.title} ({report.report_date.strftime('%d/%m/%Y')})")
                
                summary_parts.append("")
            
            # Ajouter une section de recommandations
            summary_parts.append("== RECOMMANDATIONS ==")
            summary_parts.append("1. Continuer la surveillance des activités signalées")
            summary_parts.append("2. Renforcer la présence dans les zones mentionnées")
            summary_parts.append("3. Vérifier les sources des rapports pour confirmer les informations")
            
            # Finaliser le résumé
            summary_parts.append("\nFin du résumé généré automatiquement.")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {str(e)}")
            return f"Erreur lors de la génération du résumé: {str(e)}"
    
    async def detect_anomalies(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Détecte des anomalies dans les données
        
        Args:
            data_points: Points de données à analyser
        
        Returns:
            Liste des anomalies détectées
        """
        if not self.enabled or not self.is_initialized:
            return [{"error": "Service d'IA non disponible"}]
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(1)
            
            if not data_points:
                return []
            
            # Extraction des caractéristiques
            features = []
            for point in data_points:
                # Extraire les caractéristiques numériques
                point_features = []
                for key, value in point.items():
                    if isinstance(value, (int, float)):
                        point_features.append(value)
                    elif key == "timestamp" and isinstance(value, str):
                        try:
                            dt = datetime.fromisoformat(value)
                            point_features.append(dt.hour)
                            point_features.append(dt.weekday())
                        except ValueError:
                            # Ignorer les timestamps invalides
                            pass
                
                if point_features:
                    # Normaliser à une longueur fixe pour l'algorithme
                    while len(point_features) < 5:
                        point_features.append(0)
                    features.append(point_features[:5])  # Limiter à 5 caractéristiques
            
            if not features:
                return []
            
            # Utiliser Isolation Forest pour la détection d'anomalies
            model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
            model.fit(features)
            
            # Prédire les anomalies (-1 pour anomalie, 1 pour normal)
            predictions = model.predict(features)
            
            # Collecter les anomalies
            anomalies = []
            for i, pred in enumerate(predictions):
                if pred == -1:  # C'est une anomalie
                    anomaly = {
                        "data_point": data_points[i],
                        "anomaly_score": abs(model.score_samples([features[i]])[0]),
                        "timestamp": datetime.utcnow().isoformat(),
                        "reason": "Comportement statistiquement aberrant détecté"
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'anomalies: {str(e)}")
            return [{"error": str(e)}]
    
    async def process_natural_language_query(self, query: str, user: User) -> Dict[str, Any]:
        """
        Traite une requête en langage naturel
        
        Args:
            query: Requête en langage naturel
            user: Utilisateur effectuant la requête
        
        Returns:
            Résultats de la requête
        """
        if not self.enabled or not self.is_initialized:
            return {"error": "Service d'IA non disponible"}
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(0.5)
            
            # Vérifier les permissions de l'utilisateur (niveau d'habilitation)
            clearance_levels = {
                ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
                ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
                ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
            }
            
            allowed_classifications = clearance_levels.get(user.clearance_level, [])
            
            # Analyser la requête en langage naturel
            query_lower = query.lower()
            
            # Déterminer le type de requête
            query_type = "unknown"
            if any(kw in query_lower for kw in ["rapport", "document", "information"]):
                query_type = "report_search"
            elif any(kw in query_lower for kw in ["alerte", "menace", "danger"]):
                query_type = "alert_search"
            elif any(kw in query_lower for kw in ["carte", "position", "localisation"]):
                query_type = "map_search"
            elif any(kw in query_lower for kw in ["utilisateur", "agent", "personnel"]):
                query_type = "user_search"
            elif any(kw in query_lower for kw in ["résumé", "synthèse", "analyse"]):
                query_type = "summary_request"
            
            # Simuler des résultats en fonction du type de requête
            if query_type == "report_search":
                return {
                    "query_type": query_type,
                    "interpreted_as": "Recherche de rapports",
                    "results": [
                        {"id": 1, "title": "Exemple de rapport trouvé", "relevance": 0.85},
                        {"id": 2, "title": "Second rapport pertinent", "relevance": 0.67}
                    ],
                    "metadata": {
                        "total_matches": 2,
                        "filtered_by_clearance": True,
                        "allowed_classifications": allowed_classifications
                    }
                }
            elif query_type == "alert_search":
                return {
                    "query_type": query_type,
                    "interpreted_as": "Recherche d'alertes",
                    "results": [
                        {"id": 1, "title": "Alerte de sécurité", "severity": "high", "relevance": 0.92},
                        {"id": 2, "title": "Alerte opérationnelle", "severity": "medium", "relevance": 0.75}
                    ],
                    "metadata": {
                        "total_matches": 2,
                        "filtered_by_clearance": True
                    }
                }
            elif query_type == "map_search":
                return {
                    "query_type": query_type,
                    "interpreted_as": "Recherche cartographique",
                    "results": [
                        {"id": 1, "location": "48.8566° N, 2.3522° E", "description": "Zone d'intérêt", "relevance": 0.88}
                    ],
                    "metadata": {
                        "total_matches": 1
                    }
                }
            elif query_type == "summary_request":
                return {
                    "query_type": query_type,
                    "interpreted_as": "Demande de résumé",
                    "summary": "Résumé automatique basé sur les derniers rapports et alertes. Les activités récentes montrent une augmentation des incidents signalés dans le secteur Est.",
                    "metadata": {
                        "based_on": {"reports": 5, "alerts": 3, "timeframe": "7d"}
                    }
                }
            else:
                return {
                    "query_type": "unknown",
                    "interpreted_as": "Requête non reconnue",
                    "suggestions": [
                        "Essayez de formuler votre question différemment",
                        "Spécifiez le type d'information recherchée (rapport, alerte, etc.)",
                        "Utilisez des mots-clés plus spécifiques"
                    ]
                }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête NLP: {str(e)}")
            return {"error": str(e)}
    
    async def analyze_geo_cluster(self, coordinates: List[Dict[str, float]], radius: float) -> Dict[str, Any]:
        """
        Analyse un cluster de points géographiques
        
        Args:
            coordinates: Liste de coordonnées (latitude, longitude)
            radius: Rayon de recherche en kilomètres
        
        Returns:
            Résultats de l'analyse
        """
        if not self.enabled or not self.is_initialized:
            return {"error": "Service d'IA non disponible"}
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(0.8)
            
            if not coordinates:
                return {"error": "Aucune coordonnée fournie"}
            
            # Convertir les coordonnées en tableau numpy
            points = np.array([[point["latitude"], point["longitude"]] for point in coordinates])
            
            # Utiliser DBSCAN pour la détection de clusters
            # Epsilon ≈ radius in degrees (approximation simple)
            eps_in_degrees = radius / 111.0  # 1 degree ≈ 111km
            dbscan = DBSCAN(eps=eps_in_degrees, min_samples=2, metric='haversine')
            clusters = dbscan.fit_predict(points)
            
            # Compter le nombre de points par cluster
            n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
            noise_points = list(clusters).count(-1)
            
            # Calculer les centres des clusters
            cluster_centers = []
            for i in range(n_clusters):
                cluster_points = points[clusters == i]
                center = cluster_points.mean(axis=0)
                cluster_centers.append({
                    "latitude": float(center[0]),
                    "longitude": float(center[1]),
                    "points_count": len(cluster_points)
                })
            
            # Résultats
            return {
                "clusters_count": n_clusters,
                "noise_points": noise_points,
                "total_points": len(coordinates),
                "cluster_centers": cluster_centers,
                "analysis": {
                    "density": n_clusters / len(coordinates) if coordinates else 0,
                    "dispersion": noise_points / len(coordinates) if coordinates else 0,
                    "radius_km": radius
                },
                "recommendations": [
                    "Surveiller les centres des clusters pour détecter tout changement",
                    f"Augmenter la surveillance dans les zones à forte densité ({n_clusters} clusters détectés)",
                    "Investiguer les points isolés qui pourraient indiquer des activités anormales"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de cluster géographique: {str(e)}")
            return {"error": str(e)}
    
    async def generate_alert_recommendations(self, alert: Any) -> Dict[str, Any]:
        """
        Génère des recommandations d'action pour une alerte
        
        Args:
            alert: Alerte à analyser
        
        Returns:
            Recommandations générées
        """
        if not self.enabled or not self.is_initialized:
            return {"error": "Service d'IA non disponible"}
        
        try:
            # Simulation du temps de traitement
            await asyncio.sleep(0.5)
            
            # Analyse du type d'alerte et de sa sévérité
            alert_type = getattr(alert, "alert_type", "unknown")
            severity = getattr(alert, "severity", "low")
            description = getattr(alert, "description", "")
            
            # Générer des recommandations spécifiques selon le type d'alerte
            recommendations = []
            
            # Recommandations générales basées sur la sévérité
            if severity == "critical":
                recommendations.append("Activation immédiate de la cellule de crise")
                recommendations.append("Notification de tous les personnels clés")
                recommendations.append("Préparation d'un rapport de situation toutes les 30 minutes")
            elif severity == "high":
                recommendations.append("Établir une équipe d'intervention dédiée")
                recommendations.append("Notification des décideurs principaux")
                recommendations.append("Préparation d'un rapport de situation toutes les 2 heures")
            elif severity == "medium":
                recommendations.append("Surveillance renforcée de la situation")
                recommendations.append("Notification des responsables concernés")
                recommendations.append("Préparation d'un rapport quotidien")
            else:  # low
                recommendations.append("Surveillance standard de la situation")
                recommendations.append("Documentation dans le rapport hebdomadaire")
            
            # Recommandations spécifiques selon le type d'alerte
            if alert_type == "tactical":
                recommendations.append("Déployer des équipes de reconnaissance sur le terrain")
                recommendations.append("Préparer des plans d'intervention tactique")
            elif alert_type == "strategic":
                recommendations.append("Analyser l'impact stratégique à moyen et long terme")
                recommendations.append("Évaluer les implications sur les opérations en cours")
            elif alert_type == "cyber":
                recommendations.append("Isoler les systèmes potentiellement compromis")
                recommendations.append("Activer les protocoles de défense cyber")
                recommendations.append("Prévoir une analyse forensique complète")
            elif alert_type == "intel":
                recommendations.append("Recouper l'information avec d'autres sources")
                recommendations.append("Intensifier la collecte de renseignements sur ce sujet")
            elif alert_type == "field":
                recommendations.append("Déployer des équipes supplémentaires sur le terrain")
                recommendations.append("Établir un périmètre de sécurité")
            
            # Analyse basique du contenu pour des recommandations supplémentaires
            keywords = {
                "communication": "Établir des canaux de communication sécurisés",
                "intrusion": "Renforcer les mesures de sécurité physique",
                "mouvement": "Suivre les déplacements via surveillance satellite",
                "civils": "Prévoir des mesures de protection des populations",
                "infrastructure": "Évaluer la vulnérabilité des infrastructures critiques"
            }
            
            for keyword, recommendation in keywords.items():
                if keyword in description.lower():
                    recommendations.append(recommendation)
            
            # Résultats
            return {
                "recommendations": recommendations,
                "priority": severity,
                "response_time": {
                    "critical": "immédiat",
                    "high": "< 1 heure",
                    "medium": "< 4 heures",
                    "low": "< 24 heures"
                }.get(severity, "à déterminer"),
                "ai_confidence": 0.85,  # Simulé
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de recommandations: {str(e)}")
            return {"error": str(e)}