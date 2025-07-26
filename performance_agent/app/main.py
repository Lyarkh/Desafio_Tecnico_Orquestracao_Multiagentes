import logging
import json
from http import HTTPStatus

from fastapi import FastAPI, HTTPException

import models
from crew import performance_crew


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
    logging.info("Recebida nova requisição para /analyze.")
    try:
        inputs = {'code': payload.code}
        result = performance_crew.kickoff(inputs=inputs)

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
    """
    Endpoint de verificação de saúde para monitoramento do serviço.
    Retorna um status "ok" se o agente estiver em execução.
    """
    return {"status": "ok"}
