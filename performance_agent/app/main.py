import logging
from fastapi import FastAPI
import models
from analysis import run_hybrid_analysis


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Performance Agent",
    description="Um agente que analisa o desempenho de trechos de código Python usando cProfile e enriquece os resultados com a API Gemini para fornecer sugestões de otimização.",
    version="1.0.0"
)

@app.post("/analyze", response_model=models.AnalysisResponse)
async def analyze_code(payload: models.CodeInput):
    """
    Endpoint que recebe um trecho de código, analisa sua performance
    e retorna sugestões de otimização geradas pela IA.
    """
    logging.info("Recebida nova requisição de análise de performance para /analyze.")
    suggestions = await run_hybrid_analysis(payload.code)
    return models.AnalysisResponse(suggestions=suggestions)

@app.get("/health")
def health_check():
    """
    Endpoint de verificação de saúde para monitoramento do serviço.
    Retorna um status "ok" se o agente estiver em execução.
    """
    return {"status": "ok"}
