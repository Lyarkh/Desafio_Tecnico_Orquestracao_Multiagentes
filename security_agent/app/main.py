import logging

from fastapi import FastAPI

from analysis import run_hybrid_analysis
import models


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Security Agent",
    description="Analisa trechos de código Python em busca de vulnerabilidades de segurança, enriquecendo os resultados com a API Gemini.",
    version="1.1.0"
)

@app.post("/analyze", response_model=models.AnalysisResponse)
async def analyze_code(payload: models.CodeInput):
    """
    Endpoint que recebe um código, analisa com bandit e enriquece com Gemini.
    """
    logging.info("Recebida nova requisição para /analyze.")
    suggestions = await run_hybrid_analysis(payload.code)
    return models.AnalysisResponse(suggestions=suggestions)

@app.get("/health")
def health_check():
    return {"status": "ok"}
