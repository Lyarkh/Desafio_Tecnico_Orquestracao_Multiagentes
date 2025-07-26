from pydantic import BaseModel, Field


class CodeInput(BaseModel):
    """Modelo para o payload de entrada com o código a ser analisado."""
    code: str = Field(..., description="Trecho de código Python a ser analisado.")

class EnrichedSuggestion(BaseModel):
    """Modelo para uma única sugestão enriquecida pela IA."""
    title: str = Field(..., description="Um título curto e descritivo para a vulnerabilidade encontrada.")
    explanation: str = Field(..., description="Uma explicação detalhada sobre o risco de segurança e o que o código vulnerável faz.")
    code_example: str = Field(..., description="Um exemplo de código corrigido e seguro.")

class AnalysisResponse(BaseModel):
    """Modelo para a resposta final da análise, contendo uma lista de sugestões."""
    suggestions: list[EnrichedSuggestion, None]
