from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
DB_PATH=Path(__file__).resolve().parents[1]/'storage'/'projectiq.db'
engine=create_engine(f'sqlite:///{DB_PATH}',connect_args={'check_same_thread':False})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base=declarative_base()
def init_db():
    from database.models import Project, AnalysisSnapshot, ChatMessage
    Base.metadata.create_all(bind=engine)
