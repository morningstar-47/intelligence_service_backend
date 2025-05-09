# app/api/api_v1/endpoints/ai.py
from typing import Any, Dict, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db, get_current_active_user, 
    get_current_admin, get_current_commander,
    get_db_ai_service
)
from app.core.logging import log_system_event
from app.models.user import User, UserRole, ClearanceLevel
from app.ai.integration.ai_service import AIService

router = APIRouter()


@router.post("/analyze-threat", response_model=Dict[str, Any])
async def analyze_threat(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data: Dict[str, Any] = Body(...),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Analyse des données pour détecter des menaces potentielles
    """
    try:
        # Vérifier les permissions (niveau d'habilitation minimal)
        if current_user.clearance_level == ClearanceLevel.CONFIDENTIAL:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Niveau d'habilitation insuffisant pour cette analyse"
            )
        
        # Appeler le service d'IA
        analysis_result = await ai_service.analyze_threat(data)
        
        # Journaliser l'analyse
        threat_level = analysis_result.get("threat_level", "unknown")
        log_system_event(
            "threat_analysis",
            f"Analyse de menace effectuée par {current_user.matricule} (niveau: {threat_level})",
            "info" if threat_level in ["negligible", "low"] else "warning",
            {"user_id": current_user.id, "threat_level": threat_level}
        )
        
        return analysis_result
        
    except Exception as e:
        log_system_event(
            "threat_analysis_error",
            f"Erreur lors de l'analyse de menace: {str(e)}",
            "error",
            {"user_id": current_user.id, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse de menace: {str(e)}"
        )


@router.post("/generate-summary", response_model=Dict[str, Any])
async def generate_intelligence_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    timeframe: str = Query("24h", regex=r"^\d+[hdwmy]$"),  # Format: 24h, 7d, 2w, 1m, 1y
    tags: List[str] = Query(None),
    classification: str = Query(None),
    location: str = Query(None),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Génère un résumé des renseignements récents
    """
    try:
        # Vérifier les permissions (commander ou admin)
        if current_user.role not in [UserRole.COMMANDER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les commandants et administrateurs peuvent générer des résumés"
            )
        
        # Calculer la date de début basée sur le timeframe
        time_value = int(''.join(filter(str.isdigit, timeframe)))
        time_unit = timeframe[-1]
        
        now = datetime.utcnow()
        
        if time_unit == 'h':
            start_date = now - timedelta(hours=time_value)
        elif time_unit == 'd':
            start_date = now - timedelta(days=time_value)
        elif time_unit == 'w':
            start_date = now - timedelta(weeks=time_value)
        elif time_unit == 'm':
            start_date = now - timedelta(days=time_value * 30)
        elif time_unit == 'y':
            start_date = now - timedelta(days=time_value * 365)
        else:
            start_date = now - timedelta(hours=24)  # Par défaut: 24h
        
        # Récupérer les rapports selon les critères
        # Notez: Cette fonction get_reports_for_summary devrait être définie dans le module crud
        reports = get_reports_for_summary(
            db,
            start_date=start_date,
            tags=tags,
            classification=classification,
            location=location,
            clearance_level=current_user.clearance_level
        )
        
        if not reports:
            return {"summary": "Aucun rapport disponible pour la période spécifiée avec les critères donnés."}
        
        # Générer le résumé
        summary = await ai_service.generate_intelligence_summary(reports, timeframe)
        
        log_system_event(
            "summary_generated",
            f"Résumé de renseignement généré par {current_user.matricule} (période: {timeframe})",
            "info",
            {"user_id": current_user.id, "timeframe": timeframe, "reports_count": len(reports)}
        )
        
        return {"summary": summary, "reports_count": len(reports), "timeframe": timeframe}
        
    except Exception as e:
        log_system_event(
            "summary_generation_error",
            f"Erreur lors de la génération du résumé: {str(e)}",
            "error",
            {"user_id": current_user.id, "timeframe": timeframe, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération du résumé: {str(e)}"
        )


@router.post("/detect-anomalies", response_model=List[Dict[str, Any]])
async def detect_anomalies(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    data_type: str = Query(..., regex=r"^(reports|alerts|activities|map_data)$"),
    timeframe: str = Query("7d", regex=r"^\d+[hdwmy]$"),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Détecte des anomalies dans les données
    """
    try:
        # Vérifier les permissions (commander ou admin)
        if current_user.role not in [UserRole.COMMANDER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les commandants et administrateurs peuvent détecter des anomalies"
            )
        
        # Calculer la date de début basée sur le timeframe
        time_value = int(''.join(filter(str.isdigit, timeframe)))
        time_unit = timeframe[-1]
        
        now = datetime.utcnow()
        
        if time_unit == 'h':
            start_date = now - timedelta(hours=time_value)
        elif time_unit == 'd':
            start_date = now - timedelta(days=time_value)
        elif time_unit == 'w':
            start_date = now - timedelta(weeks=time_value)
        elif time_unit == 'm':
            start_date = now - timedelta(days=time_value * 30)
        elif time_unit == 'y':
            start_date = now - timedelta(days=time_value * 365)
        else:
            start_date = now - timedelta(days=7)  # Par défaut: 7d
        
        # Récupérer les données selon le type
        if data_type == "reports":
            data_points = get_reports_data_points(db, start_date, current_user.clearance_level)
        elif data_type == "alerts":
            data_points = get_alerts_data_points(db, start_date, current_user.clearance_level)
        elif data_type == "activities":
            data_points = get_activities_data_points(db, start_date, current_user.clearance_level)
        elif data_type == "map_data":
            data_points = get_map_data_points(db, start_date, current_user.clearance_level)
        else:
            data_points = []
        
        if not data_points:
            return []
        
        # Détecter les anomalies
        anomalies = await ai_service.detect_anomalies(data_points)
        
        log_system_event(
            "anomalies_detected",
            f"Détection d'anomalies effectuée par {current_user.matricule} (type: {data_type}, période: {timeframe})",
            "info",
            {"user_id": current_user.id, "data_type": data_type, "timeframe": timeframe, "anomalies_count": len(anomalies)}
        )
        
        return anomalies
        
    except Exception as e:
        log_system_event(
            "anomaly_detection_error",
            f"Erreur lors de la détection d'anomalies: {str(e)}",
            "error",
            {"user_id": current_user.id, "data_type": data_type, "timeframe": timeframe, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la détection d'anomalies: {str(e)}"
        )


@router.post("/query", response_model=Dict[str, Any])
async def process_natural_language_query(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    query: str = Body(..., embed=True),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Traite une requête en langage naturel et renvoie des résultats pertinents
    """
    try:
        # Appeler le service d'IA
        results = await ai_service.process_natural_language_query(query, current_user)
        
        log_system_event(
            "nlp_query",
            f"Requête NLP traitée pour {current_user.matricule}: '{query}'",
            "info",
            {"user_id": current_user.id, "query": query}
        )
        
        return results
        
    except Exception as e:
        log_system_event(
            "nlp_query_error",
            f"Erreur lors du traitement de la requête NLP: {str(e)}",
            "error",
            {"user_id": current_user.id, "query": query, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de la requête: {str(e)}"
        )


@router.post("/analyze-geo-cluster", response_model=Dict[str, Any])
async def analyze_geo_cluster(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    coordinates: List[Dict[str, float]] = Body(...),
    radius: float = Query(10.0, gt=0, le=1000),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Analyse un cluster de points géographiques
    """
    try:
        # Vérifier les permissions (niveau d'habilitation)
        if current_user.clearance_level == ClearanceLevel.CONFIDENTIAL:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Niveau d'habilitation insuffisant pour cette analyse"
            )
        
        # Vérifier que les coordonnées sont valides
        for coord in coordinates:
            if "latitude" not in coord or "longitude" not in coord:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chaque point doit avoir une latitude et une longitude"
                )
            
            lat = coord.get("latitude")
            lng = coord.get("longitude")
            
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Coordonnées invalides: latitude={lat}, longitude={lng}"
                )
        
        # Analyser le cluster
        analysis = await ai_service.analyze_geo_cluster(coordinates, radius)
        
        log_system_event(
            "geo_cluster_analysis",
            f"Analyse de cluster géographique effectuée par {current_user.matricule} ({len(coordinates)} points)",
            "info",
            {"user_id": current_user.id, "points_count": len(coordinates), "radius": radius}
        )
        
        return analysis
        
    except Exception as e:
        log_system_event(
            "geo_cluster_analysis_error",
            f"Erreur lors de l'analyse de cluster géographique: {str(e)}",
            "error",
            {"user_id": current_user.id, "points_count": len(coordinates), "radius": radius, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse de cluster géographique: {str(e)}"
        )


@router.post("/alert-recommendations/{alert_id}", response_model=Dict[str, Any])
async def generate_alert_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    alert_id: int = Path(..., gt=0),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Génère des recommandations d'action pour une alerte
    """
    try:
        # Récupérer l'alerte
        alert = get_alert(db, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerte non trouvée"
            )
        
        # Vérifier l'accès à l'alerte en fonction du niveau d'habilitation
        # (Supposons que les alertes ont aussi un niveau de classification)
        if hasattr(alert, "classification"):
            clearance_levels = {
                ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
                ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
                ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
            }
            
            allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
            
            if alert.classification not in allowed_classifications:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Niveau d'habilitation insuffisant pour cette alerte ({alert.classification})"
                )
        
        # Générer les recommandations
        recommendations = await ai_service.generate_alert_recommendations(alert)
        
        log_system_event(
            "alert_recommendations",
            f"Recommandations générées pour l'alerte {alert_id} par {current_user.matricule}",
            "info",
            {"user_id": current_user.id, "alert_id": alert_id}
        )
        
        return recommendations
        
    except Exception as e:
        log_system_event(
            "alert_recommendations_error",
            f"Erreur lors de la génération de recommandations pour l'alerte {alert_id}: {str(e)}",
            "error",
            {"user_id": current_user.id, "alert_id": alert_id, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération de recommandations: {str(e)}"
        )