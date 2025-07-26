from pydantic import BaseModel, Field


class CodeInput(BaseModel):
    """Modelo de entrada para a requisição de análise."""
    code: str

class EnrichedSuggestion(BaseModel):
    """Modelo para uma única sugestão enriquecida pela IA."""
    title: str = Field(..., description="Um título curto e descritivo para a vulnerabilidade encontrada.")
    explanation: str = Field(..., description="Uma explicação detalhada sobre o risco de segurança e o que o código vulnerável faz.")
    code_example: str = Field(..., description="Um exemplo de código corrigido e seguro.")

class AnalysisResponse(BaseModel):
    """Modelo para a resposta final da análise, contendo uma lista de sugestões."""
    suggestions: list[EnrichedSuggestion]

class ConsolidatedResponse(BaseModel):
    """
    Modelo da resposta final consolidada, contendo os resultados de cada agente.
    A estrutura é flexível para acomodar respostas de sucesso ou de erro.
    """
    security: AnalysisResponse
    performance: AnalysisResponse
    codestyle: AnalysisResponse
