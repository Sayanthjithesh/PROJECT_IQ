import json
from database.connection import SessionLocal
from database.models import Project, AnalysisSnapshot, ChatMessage


def create_project(name, description, source_type, path):
    s = SessionLocal()
    try:
        p = Project(name=name, description=description, source_type=source_type, path=str(path))
        s.add(p); s.commit(); s.refresh(p); return p.id
    finally:
        s.close()


def save_snapshot(project_id, result):
    s = SessionLocal()
    try:
        x = AnalysisSnapshot(project_id=project_id, score=result['score']['total'], maturity=result['score']['maturity'], data=json.dumps(result))
        s.add(x); s.commit(); return x.id
    finally:
        s.close()


def list_projects():
    s = SessionLocal()
    try:
        out = s.query(Project).order_by(Project.created_at.desc()).all(); s.expunge_all(); return out
    finally:
        s.close()


def get_project(pid):
    if not pid: return None
    s = SessionLocal()
    try:
        p = s.query(Project).filter_by(id=pid).first()
        if p: s.expunge(p)
        return p
    finally:
        s.close()


def latest_snapshot(pid):
    s = SessionLocal()
    try:
        x = s.query(AnalysisSnapshot).filter_by(project_id=pid).order_by(AnalysisSnapshot.created_at.desc()).first()
        return json.loads(x.data) if x else None
    finally:
        s.close()


def snapshots(pid):
    s = SessionLocal()
    try:
        xs = s.query(AnalysisSnapshot).filter_by(project_id=pid).order_by(AnalysisSnapshot.created_at).all()
        return [{'date': a.created_at, 'score': a.score, 'maturity': a.maturity, 'data': json.loads(a.data)} for a in xs]
    finally:
        s.close()


def save_chat_message(project_id, role, content):
    if not project_id or not content: return None
    s = SessionLocal()
    try:
        msg = ChatMessage(project_id=project_id, role=role, content=content)
        s.add(msg); s.commit(); s.refresh(msg); return msg.id
    finally:
        s.close()


def get_chat_history(project_id, limit=30):
    if not project_id: return []
    s = SessionLocal()
    try:
        rows = s.query(ChatMessage).filter_by(project_id=project_id).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        rows.reverse()
        return [{'role': r.role, 'content': r.content, 'created_at': r.created_at} for r in rows]
    finally:
        s.close()
