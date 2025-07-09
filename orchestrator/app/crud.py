from sqlalchemy.orm import Session
import schemas


def create_analysis_record(db: Session, code_snippet: str, suggestions: dict):
    """
    Cria e salva um novo registro de análise no banco de dados.
    """
    db_record = schemas.AnalysisHistory(
        code_snippet=code_snippet,
        suggestions=suggestions
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record
