from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from database import Base


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    code_snippet = Column(String, nullable=False)
    suggestions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
