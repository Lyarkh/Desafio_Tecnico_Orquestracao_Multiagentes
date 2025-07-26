import requests
import json
import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel

from models import CodeInput


class AgentAPITool(BaseTool):
    """
    Classe base abstrata para ferramentas que chamam as APIs dos agentes.
    Lida com a lógica comum de chamada HTTP e tratamento de erros.
    """
    agent_name: str
    agent_url: str
    args_schema: Type[BaseModel] = CodeInput

    def _run(self, code: str) -> str:
        """
        Executa a chamada HTTP para o endpoint /analyze do agente especificado.
        """
        try:
            response = requests.post(
                self.agent_url,
                json={"code": code},
                timeout=90
            )

            response.raise_for_status()

            return response.text
        except requests.exceptions.HTTPError as http_err:
            error_details = f"Erro HTTP: {http_err.response.status_code} - {http_err.response.text}"
            return json.dumps({"error": f"Falha ao comunicar com o {self.agent_name}", "details": error_details})
        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Erro de conexão com o {self.agent_name}", "details": str(e)})

class SecurityAgentTool(AgentAPITool):
    name: str = "Analisador de Segurança de Código"
    description: str = "Delega a análise de segurança de um trecho de código Python para o agente especialista em segurança."
    agent_name: str = "Security Agent"
    agent_url: str = os.environ.get('SECURITY_AGENT_URL')

class CodeStyleAgentTool(AgentAPITool):
    name: str = "Analisador de Estilo de Código"
    description: str = "Delega a análise de estilo e boas práticas de um trecho de código Python para o agente especialista em Code Style."
    agent_name: str = "Code Style Agent"
    agent_url: str = os.environ.get('CODESTYLE_AGENT_URL')

class PerformanceAgentTool(AgentAPITool):
    name: str = "Analisador de Performance de Código"
    description: str = "Delega a análise de performance de um trecho de código Python para o agente especialista em Performance."
    agent_name: str = "Performance Agent"
    agent_url: str = os.environ.get('PERFORMANCE_AGENT_URL')
