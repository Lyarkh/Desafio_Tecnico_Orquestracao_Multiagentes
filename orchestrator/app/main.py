import os
import httpx
import asyncio
import logging

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import models
import schemas
import crud
from database import SessionLocal, engine


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

schemas.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Code Analysis Orchestrator",
    description="Orquestra a análise de código Python chamando agentes especializados (Segurança, Performance, Estilo de Código), consolida os resultados e os armazena.",
    version="1.0.0"
)

AGENT_URLS = {
    "security": os.environ.get('SECURITY_AGENT_URL'),
    "performance": os.environ.get('PERFORMANCE_AGENT_URL'),
    "codestyle": os.environ.get('CODESTYLE_AGENT_URL'),
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def call_analysis_agent(client: httpx.AsyncClient, agent_name: str, code: str):
    """
    Função auxiliar para chamar o endpoint /analyze de um agente específico.
    """
    agent_base_url = AGENT_URLS.get(agent_name)
    if not agent_base_url:
        logging.warning(f"URL para o agente {agent_name} não configurada.")
        return agent_name, {"error": f"URL do agente {agent_name} não configurada."}

    url = f'{agent_base_url}/analyze'
    try:
        logging.info(f"Chamando o agente: {agent_name} em {url}")
        response = await client.post(url, json={"code": code}, timeout=60.0)
        response.raise_for_status()
        return agent_name, response.json()

    except httpx.RequestError as e:
        logging.error(f"Erro ao chamar o agente {agent_name}: {e}")
        return agent_name, {"error": f"Agente {agent_name} indisponível: {e.__class__.__name__}"}

    except Exception as e:
        logging.error(f"Erro inesperado ao processar resposta do agente {agent_name}: {e}")
        return agent_name, {"error": f"Erro inesperado no agente {agent_name}: {str(e)}"}

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
    async with httpx.AsyncClient() as client:
        tasks = [
            call_analysis_agent(client, name, payload.code)
            for name in AGENT_URLS if AGENT_URLS.get(name)
        ]
        results = await asyncio.gather(*tasks)

    consolidated_report = {name: result for name, result in results}

    logging.info("Consolidação dos resultados concluída.")
    try:
        crud.create_analysis_record(
            db=db,
            code_snippet=payload.code,
            suggestions=consolidated_report
        )
        logging.info("Registro da análise salvo no banco de dados com sucesso.")
    except Exception as e:
        logging.error(f"Falha ao salvar o registro no banco de dados: {e}")

    return consolidated_report

@app.get("/health")
def health_check():
    """Endpoint de verificação de saúde para o orquestrador."""
    return {"status": "ok"}
