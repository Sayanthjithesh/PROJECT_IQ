from sqlalchemy import Column,Integer,String,DateTime,Float,Text,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base
class Project(Base):
    __tablename__='projects'; id=Column(Integer,primary_key=True); name=Column(String(200)); description=Column(Text,default=''); source_type=Column(String(30)); created_at=Column(DateTime,default=datetime.utcnow); path=Column(Text); snapshots=relationship('AnalysisSnapshot',back_populates='project',cascade='all,delete-orphan')
class AnalysisSnapshot(Base):
    __tablename__='analysis_snapshots'; id=Column(Integer,primary_key=True); project_id=Column(Integer,ForeignKey('projects.id')); created_at=Column(DateTime,default=datetime.utcnow); score=Column(Float); maturity=Column(String(50)); data=Column(Text); project=relationship('Project',back_populates='snapshots')
class ChatMessage(Base):
    __tablename__='chat_messages'; id=Column(Integer,primary_key=True); project_id=Column(Integer,index=True); role=Column(String(20)); content=Column(Text); created_at=Column(DateTime,default=datetime.utcnow)
