"""
PROJECTIQ - Project Data Access Helpers

Small helpers pages use to load a project and its analysis versions as
plain dictionaries (detached from the SQLAlchemy session) so they can
be safely used after the session context closes.
"""

from typing import Dict, List, Optional

from db.database import get_session
from db.models import AnalysisVersion, Project


def get_project_dict(project_id: int) -> Optional[Dict]:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            return None
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "current_score": project.current_score,
            "current_maturity": project.current_maturity,
            "current_goal": project.current_goal,
            "storage_path": project.storage_path,
            "upload_date": project.upload_date,
            "last_analyzed_date": project.last_analyzed_date,
            "version_count": len(project.versions),
        }


def get_latest_version_dict(project_id: int) -> Optional[Dict]:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None or not project.versions:
            return None
        v = project.versions[-1]
        return _version_to_dict(v)


def get_all_versions(project_id: int) -> List[Dict]:
    with get_session() as session:
        project = session.get(Project, project_id)
        if project is None:
            return []
        return [_version_to_dict(v) for v in project.versions]


def _version_to_dict(v: AnalysisVersion) -> Dict:
    return {
        "version_number": v.version_number,
        "analyzed_at": v.analyzed_at,
        "score_total": v.score_total,
        "score_breakdown": v.score_breakdown,
        "maturity_level": v.maturity_level,
        "project_dna": v.project_dna,
        "technologies": v.technologies,
        "features": v.features,
        "architecture": v.architecture,
        "outlook": v.outlook,
        "gaps": v.gaps,
        "recommendations": v.recommendations,
        "risk_radar": v.risk_radar,
        "differentiation": v.differentiation,
        "file_stats": v.file_stats,
    }
