# Gestion des rapports
# app/api/api_v1/endpoints/reports.py
from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db, get_current_active_user, get_current_admin, 
    get_current_commander, get_current_field_agent,
    get_db_ai_service
)
from app.core.logging import log_system_event
from app.models.user import User, UserRole, ClearanceLevel
from app.schemas.report import (
    Report as ReportSchema, ReportCreate, ReportUpdate, ReportList,
    ReportApproval, ReportAIAnalysis, Comment, CommentCreate
)
from app.ai.integration.ai_service import AIService

# Supposons que ces fonctions existent dans le module crud
from app.crud.report import (
    get_report, get_reports, count_reports, create_report, update_report,
    delete_report, approve_report, reject_report, add_comment_to_report,
    get_report_comments, add_tag_to_report, remove_tag_from_report,
    get_tags, create_tag
)

router = APIRouter()


@router.get("/", response_model=ReportList)
def read_reports(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = Query(None),
    classification: str = Query(None),
    submitted_by: int = Query(None),
    approved_by: int = Query(None),
    from_date: datetime = Query(None),
    to_date: datetime = Query(None),
    search: str = Query(None),
    tags: List[str] = Query(None)
) -> Any:
    """
    Récupère la liste des rapports avec filtrage
    """
    # Vérifier les permissions d'accès en fonction du niveau d'habilitation
    # Les utilisateurs ne peuvent voir que les rapports de classification inférieure ou égale à leur niveau
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    
    # Filtrer par rôle (les agents de terrain ne voient que leurs propres rapports)
    if current_user.role == UserRole.FIELD:
        submitted_by = current_user.id
    
    # Récupérer les rapports
    reports = get_reports(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        classification=classification,
        submitted_by=submitted_by,
        approved_by=approved_by,
        from_date=from_date,
        to_date=to_date,
        search=search,
        tags=tags,
        allowed_classifications=allowed_classifications
    )
    
    # Compter le nombre total de rapports pour la pagination
    total = count_reports(
        db=db,
        status=status,
        classification=classification,
        submitted_by=submitted_by,
        approved_by=approved_by,
        from_date=from_date,
        to_date=to_date,
        search=search,
        tags=tags,
        allowed_classifications=allowed_classifications
    )
    
    return {
        "items": reports,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{report_id}", response_model=ReportSchema)
def read_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    report_id: int = Path(..., gt=0)
) -> Any:
    """
    Récupère un rapport spécifique
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )
    
    # Vérifier l'accès en fonction du niveau d'habilitation
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    
    if report.classification not in allowed_classifications:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant pour accéder à ce rapport ({report.classification})"
        )
    
    # Vérifier l'accès pour les agents de terrain (uniquement leurs propres rapports)
    if current_user.role == UserRole.FIELD and report.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que vos propres rapports"
        )
    
    return report


@router.post("/", response_model=ReportSchema, status_code=status.HTTP_201_CREATED)
def create_new_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    report_in: ReportCreate,
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Crée un nouveau rapport
    """
    # Vérifier que l'utilisateur a le niveau d'habilitation nécessaire pour la classification du rapport
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    
    if report_in.classification not in allowed_classifications:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant pour créer un rapport avec cette classification ({report_in.classification})"
        )
    
    # Créer le rapport
    report = create_report(db, report_in, current_user.id)
    
    # Analyser le rapport avec l'IA
    if report and report.id:
        try:
            # Lancer l'analyse en arrière-plan
            # Dans une application réelle, cela serait fait de manière asynchrone avec une tâche de fond
            analysis_result = await ai_service.analyze_report(report)
            
            # Mettre à jour le rapport avec les résultats de l'analyse
            if analysis_result:
                update_data = {
                    "ai_analysis": analysis_result.get("summary", ""),
                    "threat_level": analysis_result.get("threat_level", ""),
                    "credibility_score": analysis_result.get("credibility_score", 0)
                }
                
                update_report(db, report.id, update_data)
                
                # Ajouter les tags suggérés
                suggested_tags = analysis_result.get("suggested_tags", [])
                for tag_name in suggested_tags:
                    # Créer le tag s'il n'existe pas
                    tag = get_tags(db, name=tag_name)
                    if not tag:
                        tag = create_tag(db, tag_name)
                    
                    # Ajouter le tag au rapport
                    add_tag_to_report(db, report.id, tag.id)
        
        except Exception as e:
            # Ne pas bloquer la création du rapport en cas d'erreur d'analyse
            log_system_event(
                "report_analysis_error",
                f"Erreur lors de l'analyse du rapport {report.id}: {str(e)}",
                "error"
            )
    
    log_system_event(
        "report_created",
        f"Rapport créé par {current_user.matricule} (ID: {current_user.id}): {report.title}",
        "info",
        {"report_id": report.id, "classification": report.classification}
    )
    
    return report


@router.put("/{report_id}", response_model=ReportSchema)
def update_report_info(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    report_id: int = Path(..., gt=0),
    report_in: ReportUpdate
) -> Any:
    """
    Met à jour un rapport existant
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )
    
    # Vérifier les permissions (seul l'auteur peut modifier son rapport, ou un admin/commander)
    if (current_user.role == UserRole.FIELD and report.submitted_by_id != current_user.id) or \
       (current_user.role not in [UserRole.ADMIN, UserRole.COMMANDER] and report.submitted_by_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier ce rapport"
        )
    
    # Vérifier que le rapport n'est pas déjà approuvé/rejeté/archivé (sauf pour les admins)
    if current_user.role != UserRole.ADMIN and report.status in ["approved", "rejected", "archived"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de modifier un rapport avec le statut {report.status}"
        )
    
    # Vérifier la classification si elle est modifiée
    if report_in.classification and report_in.classification != report.classification:
        clearance_levels = {
            ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
            ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
            ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
        }
        
        allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
        
        if report_in.classification not in allowed_classifications:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Niveau d'habilitation insuffisant pour attribuer cette classification ({report_in.classification})"
            )
    
    # Mettre à jour le rapport
    updated_report = update_report(db, report_id, report_in)
    
    log_system_event(
        "report_updated",
        f"Rapport mis à jour par {current_user.matricule} (ID: {current_user.id}): {report.title} (ID: {report_id})",
        "info",
        {"report_id": report_id}
    )
    
    return updated_report


@router.delete("/{report_id}", response_model=ReportSchema)
def delete_report_endpoint(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),  # Seul un admin peut supprimer un rapport
    report_id: int = Path(..., gt=0)
) -> Any:
    """
    Supprime un rapport (admin seulement)
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )
    
    # Supprimer le rapport
    deleted_report = delete_report(db, report_id)
    
    log_system_event(
        "report_deleted",
        f"Rapport supprimé par {current_user.matricule} (ID: {current_user.id}): {report.title} (ID: {report_id})",
        "warning",
        {"report_id": report_id}
    )
    
    return deleted_report


@router.post("/{report_id}/approve", response_model=ReportSchema)
def approve_report_endpoint(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_commander),  # Seul un commander ou admin peut approuver
    report_id: int = Path(..., gt=0),
    approval: ReportApproval
) -> Any:
    """
    Approuve ou rejette un rapport
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )
    
    # Vérifier que le rapport est en attente d'approbation
    if report.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le rapport n'est pas en attente d'approbation (statut actuel: {report.status})"
        )
    
    # Vérifier le niveau d'habilitation
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    
    if report.classification not in allowed_classifications:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant pour approuver ce rapport ({report.classification})"
        )
    
    # Approuver ou rejeter le rapport
    if approval.approved:
        updated_report = approve_report(db, report_id, current_user.id)
        action = "approved"
    else:
        updated_report = reject_report(db, report_id, current_user.id, approval.rejection_reason)
        action = "rejected"
    
    log_system_event(
        f"report_{action}",
        f"Rapport {action} par {current_user.matricule} (ID: {current_user.id}): {report.title} (ID: {report_id})",
        "info",
        {"report_id": report_id, "reason": approval.rejection_reason if not approval.approved else None}
    )
    
    return updated_report


@router.post("/{report_id}/comments", response_model=Comment)
def add_comment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    report_id: int = Path(..., gt=0),
    comment_in: CommentCreate
) -> Any:
    """
    Ajoute un commentaire à un rapport
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )
    
    # Vérifier l'accès au rapport
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    
    if report.classification not in allowed_classifications:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant pour commenter ce rapport ({report.classification})"
        )
    
    # Vérifier l'accès pour les agents de terrain (uniquement leurs propres rapports)
    if current_user.role == UserRole.FIELD and report.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez commenter que vos propres rapports"
        )
    
    # Ajouter le commentaire
    comment = add_comment_to_report(db, report_id, current_user.id, comment_in.content)
    
    return comment


@router.get("/{report_id}/comments", response_model=List[Comment])
def get_comments(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    report_id: int = Path(..., gt=0)
) -> Any:
    """
    Récupère les commentaires d'un rapport
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )
    
    # Vérifier l'accès au rapport
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    
    if report.classification not in allowed_classifications:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant pour accéder aux commentaires de ce rapport ({report.classification})"
        )
    
    # Vérifier l'accès pour les agents de terrain (uniquement leurs propres rapports)
    if current_user.role == UserRole.FIELD and report.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez accéder qu'aux commentaires de vos propres rapports"
        )
    
    # Récupérer les commentaires
    comments = get_report_comments(db, report_id)
    
    return comments


@router.post("/{report_id}/analyze", response_model=ReportAIAnalysis)
async def analyze_report_with_ai(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    report_id: int = Path(..., gt=0),
    ai_service: AIService = Depends(get_db_ai_service)
) -> Any:
    """
    Analyse un rapport avec l'IA
    """
    # Récupérer le rapport
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rapport non trouvé"
        )

    # Vérifier l'accès au rapport
    clearance_levels = {
        ClearanceLevel.CONFIDENTIAL: ["confidential", "unclassified"],
        ClearanceLevel.SECRET: ["confidential", "secret", "unclassified"],
        ClearanceLevel.TOP_SECRET: ["confidential", "secret", "top_secret", "unclassified"]
    }
    allowed_classifications = clearance_levels.get(current_user.clearance_level, [])
    if report.classification not in allowed_classifications:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Niveau d'habilitation insuffisant pour accéder à l'analyse de ce rapport ({report.classification})"
        )
    # Vérifier l'accès pour les agents de terrain (uniquement leurs propres rapports)
    if current_user.role == UserRole.FIELD and report.submitted_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez accéder qu'à l'analyse de vos propres rapports"      
        )