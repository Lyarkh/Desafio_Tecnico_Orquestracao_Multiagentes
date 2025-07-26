import logging
import json
from http import HTTPStatus

from fastapi import FastAPI, HTTPException

import models
from crew import security_crew


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Security Agent",
    description="Um microsserviço que usa (CrewAI) para analisar vulnerabilidades em código Python.",
    version="2.0.0"
)

@app.post("/analyze", response_model=models.AnalysisResponse)
async def analyze_code(payload: models.CodeInput):
    """
    Endpoint que recebe um código, analisa com bandit e enriquece com Gemini.
    """
    logging.info("Recebida nova requisição para /analyze.")
    try:
        inputs = {'code': payload.code}
        result = security_crew.kickoff(inputs=inputs)

        try:
            result_raw = json.loads(result.tasks_output[0].raw)
            response = models.AnalysisResponse(**result_raw)
            return response

        except (json.JSONDecodeError, TypeError) as e:
            logging.error(f"Erro ao fazer parse da resposta da IA: {e}")
            logging.error(f"Resposta recebida: {result}")
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="A resposta do serviço de IA não pôde ser processada como um JSON válido."
            )

    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado durante a execução do crew: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno no servidor: {str(e)}"
        )

@app.get("/health")
def health_check():
    return {"status": "ok"}
