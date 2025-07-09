from pydantic import BaseModel, Field


class CodeInput(BaseModel):
    """Modelo para o payload de entrada com o código a ser analisado."""
    code: str = Field(..., description="Trecho de código Python a ser analisado.")

class EnrichedSuggestion(BaseModel):
    """Modelo para uma única sugestão enriquecida pela IA."""
    title: str
    explanation: str
    code_example: str

class AnalysisResponse(BaseModel):
    """Modelo para a resposta final da análise, contendo uma lista de sugestões."""
    suggestions: list[EnrichedSuggestion]
