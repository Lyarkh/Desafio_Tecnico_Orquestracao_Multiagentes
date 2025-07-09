import logging

from fastapi import FastAPI

from analysis import run_hybrid_analysis
import models


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Code Style Agent",
    description="Analisa trechos de código Python em busca de melhorias de estilo e boas práticas, utilizando Flake8 e a API Gemini.",
    version="1.0.0"
)

@app.post("/analyze", response_model=models.AnalysisResponse)
async def analyze_code(payload: models.CodeInput):
    """
    Endpoint que recebe um código, analisa com flake8 e enriquece com Gemini.
    """
    logging.info("Recebida nova requisição para /analyze (Code Style).")
    suggestions = await run_hybrid_analysis(payload.code)
    return models.AnalysisResponse(suggestions=suggestions)

@app.get("/health")
def health_check():
    """Endpoint de health check para o orquestrador."""
    return {"status": "ok"}
