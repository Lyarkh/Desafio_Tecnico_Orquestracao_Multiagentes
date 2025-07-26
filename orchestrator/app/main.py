import logging
import json

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from database import engine, get_db
from crew import create_orchestration_crew


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

schemas.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Code Analysis Orchestrator",
    description="Orquestra a análise de código Python chamando agentes especializados (Segurança, Performance, Estilo de Código), consolida os resultados e os armazena.",
    version="2.0.0"
)

@app.post("/orchestrate-analysis", response_model=models.ConsolidatedResponse)
async def orchestrate_analysis(payload: models.CodeInput, db: Session = Depends(get_db)):
    """
    Orquestra a análise de código:
    1. Recebe um trecho de código.
    2. Envia o código para todos os agentes especializados em paralelo.
    3. Coleta, consolida e retorna as sugestões.
    4. Salva o resultado no banco de dados.
    """
    logging.info("Iniciando orquestração da análise de código.")
    try:
        logging.info("Iniciando a orquestração da análise de código...")

        orchestration_crew = create_orchestration_crew(payload.code)
        result_string = orchestration_crew.kickoff()

        logging.info("Orquestração concluída. Processando o resultado...")

        try:
            result_data = json.loads(result_string.tasks_output[0].raw)
            final_response = models.AnalysisResponse(**result_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Erro ao processar a resposta da IA: {e}\nResposta recebida: {result_string}")
            raise HTTPException(
                status_code=500,
                detail="A resposta final da equipe de IA não é um JSON válido."
            )

        logging.debug("Salvando o resultado no banco de dados...")
        crud.create_analysis_record(
            db=db,
            code_snippet=payload.code,
            suggestions=final_response.dict()
        )
        logging.info("Análise salva com sucesso.")
        return final_response

    except Exception as e:
        logging.error(f"Ocorreu um erro crítico durante a orquestração: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno inesperado no orquestrador: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Endpoint de verificação de saúde para o orquestrador."""
    return {"status": "ok"}
