import subprocess
import tempfile
import os
import json

from crewai.tools import BaseTool


class BanditAnalysisTool(BaseTool):
    name: str = "Analisador de Segurança de Código Python com Bandit"
    description: str = (
        "Esta ferramenta executa a análise de segurança 'bandit' em um trecho de código Python. "
        "Ela recebe o código como uma string e retorna o relatório de vulnerabilidades em formato JSON bruto."
    )

    def _run(self, code: str) -> str:
        """
        Executa o bandit em um arquivo temporário contendo o código fornecido.
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py', encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_filename = temp_file.name

            result = subprocess.run(
                ["bandit", "-f", "json", temp_filename],
                capture_output=True,
                text=True,
                check=False
            )
        finally:
            if 'temp_filename' in locals() and os.path.exists(temp_filename):
                os.remove(temp_filename)

        if result.returncode != 0 and not result.stdout:
            error_report = {
                "error": "Falha ao executar a ferramenta Bandit.",
                "details": result.stderr.strip()
            }
            return json.dumps(error_report)

        return result.stdout
