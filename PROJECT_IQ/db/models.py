"""
PROJECTIQ - Database Models
SQLite is used locally. Models are written in plain SQLAlchemy so the
same schema can be pointed at PostgreSQL later by changing DATABASE_URL.
"""

import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def _now() -> dt.datetime:
    return dt.datetime.utcnow()


class Project(Base):
    """A user-uploaded project and its most recent known state."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    source_type = Column(String(50), default="zip")  # zip | files | github
    source_reference = Column(String(500), default="")  # github url, etc.
    storage_path = Column(String(500), nullable=False)

    upload_date = Column(DateTime, default=_now)
    last_analyzed_date = Column(DateTime, default=_now)

    current_score = Column(Float, default=0.0)
    current_maturity = Column(String(50), default="Beginner")
    current_goal = Column(String(50), default="Portfolio Ready")

    versions = relationship("AnalysisVersion", back_populates="project",
                             cascade="all, delete-orphan", order_by="AnalysisVersion.version_number")
    chat_messages = relationship("ChatMessage", back_populates="project",
                                  cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class AnalysisVersion(Base):
    """A snapshot of a project's full analysis, created on every (re)analysis."""

    __tablename__ = "analysis_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    analyzed_at = Column(DateTime, default=_now)

    score_total = Column(Float, default=0.0)
    score_breakdown = Column(JSON, default=dict)  # per-category scores + reasons
    maturity_level = Column(String(50), default="Beginner")

    project_dna = Column(JSON, default=dict)
    technologies = Column(JSON, default=dict)
    features = Column(JSON, default=list)
    architecture = Column(JSON, default=dict)
    outlook = Column(JSON, default=dict)
    gaps = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    risk_radar = Column(JSON, default=dict)
    differentiation = Column(JSON, default=dict)
    file_stats = Column(JSON, default=dict)

    project = relationship("Project", back_populates="versions")


class ChatMessage(Base):
    """A single message in a project's AI chatbot history."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    mode = Column(String(50), default="project_assistant")  # project_assistant | mentor
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)

    project = relationship("Project", back_populates="chat_messages")
