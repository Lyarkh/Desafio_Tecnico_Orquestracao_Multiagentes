import cProfile
import pstats
import io
import json

from crewai.tools import BaseTool


class CProfileAnalysisTool(BaseTool):
    name: str = "Analisador de Performance de Código Python com cProfile"
    description: str = (
        "Esta ferramenta executa um trecho de código Python dentro do profiler 'cProfile' para "
        "coletar estatísticas de performance, como número de chamadas de função e tempo de execução. "
        "Retorna um relatório de performance em texto."
    )

    def _run(self, code: str) -> str:
        """
        Executa o código dentro do cProfile e captura as estatísticas.
        """

        profiler = cProfile.Profile()
        stream = io.StringIO()

        try:
            profiler.run(code, filename='<string>')
            stats = pstats.Stats(profiler, stream=stream)

            stats.strip_dirs()
            stats.sort_stats('cumulative')
            stats.print_stats()

            return stream.getvalue()

        except Exception as e:
            error_report = {
                "error": "Falha ao executar o código dentro do profiler.",
                "details": str(e)
            }
            return json.dumps(error_report)
        finally:
            stream.close()
