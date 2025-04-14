from sqlalchemy import Column, String, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    last_build_time = Column(DateTime, nullable=False)
    duration = Column(String, nullable=True)
    commit_hash = Column(String, nullable=True)
    build_logs = relationship("BuildLog", back_populates="pipeline")


class BuildLog(Base):
    __tablename__ = "build_logs"

    id = Column(String, primary_key=True)
    pipeline_id = Column(String, ForeignKey("pipelines.id"))
    log_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False)
    pipeline = relationship("Pipeline", back_populates="build_logs")


# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cicd_dashboard")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
