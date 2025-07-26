import subprocess
import tempfile
import os

from crewai.tools import BaseTool


class Flake8AnalysisTool(BaseTool):
    name: str = "Analisador de Estilo de Código Python com Flake8"
    description: str = (
        "Esta ferramenta executa o linter 'flake8' em um trecho de código Python para encontrar "
        "violações do guia de estilo PEP 8 e outros problemas de qualidade de código. "
        "Ela retorna a saída bruta do flake8 como uma string de texto."
    )

    def _run(self, code: str) -> str:
        """
        Executa o flake8 em um arquivo temporário contendo o código fornecido.
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.py', encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_filename = temp_file.name

            result = subprocess.run(
                ["flake8", "--format=%(row)d:%(col)d:%(code)s:%(text)s", temp_filename],
                capture_output=True,
                text=True,
                check=False
            )
        finally:
            if 'temp_filename' in locals() and os.path.exists(temp_filename):
                os.remove(temp_filename)

        if not result.stdout:
            return "Nenhum problema de estilo de código encontrado pelo Flake8."

        return result.stdout
