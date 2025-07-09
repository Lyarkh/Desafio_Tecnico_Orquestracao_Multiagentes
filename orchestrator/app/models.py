from typing import Dict, Any

from pydantic import BaseModel


class CodeInput(BaseModel):
    """Modelo de entrada para a requisição de análise."""
    code: str

class ConsolidatedResponse(BaseModel):
    """
    Modelo da resposta final consolidada, contendo os resultados de cada agente.
    A estrutura é flexível para acomodar respostas de sucesso ou de erro.
    """
    security: Dict[str, Any]
    performance: Dict[str, Any]
    codestyle: Dict[str, Any]
