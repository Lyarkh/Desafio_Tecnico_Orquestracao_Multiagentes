import cProfile
import pstats
import io
import logging

from call_api import call_gemini_api
from models import EnrichedSuggestion


async def run_hybrid_analysis(code: str) -> list[EnrichedSuggestion]:
    """
    Executa a análise de performance: primeiro com cProfile, depois enriquecendo com a IA.

    Args:
        code: O trecho de código Python a ser analisado.

    Returns:
        Uma lista contendo um único objeto EnrichedSuggestion com a análise.
    """
    logging.info("Iniciando análise de performance com cProfile.")

    try:
        profiler = cProfile.Profile()
        profiler.run(code)

        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        stats.print_stats()

        performance_report = s.getvalue()

        enriched_suggestions = []
        if len(performance_report.splitlines()) < 5:
            logging.info("O relatório do cProfile é muito curto. Solicitando análise de boas práticas de performance.")
            prompt = f"""
                Atue como um desenvolvedor Python Sênior especialista em otimização de performance.
                O código a seguir foi executado, mas foi muito rápido para gerar um relatório de profiling detalhado.

                **Código Analisado:**
                ```python
                {code}
                ```

                **Sua Análise:**
                Faça uma análise estática do código e forneça a sugestão de otimização de performance mais impactante que você conseguir identificar.
                Se nenhuma otimização óbvia for necessária, sugira uma boa prática geral de performance que se aplique ao contexto do código.

                Retorne a resposta estritamente no seguinte formato JSON, com as chaves "title", "explanation", e "code_example":
                - "title": Um título para sua sugestão (ex: "Uso de List Comprehension para Melhor Legibilidade e Performance").
                - "explanation": Sua explicação sobre a boa prática ou otimização.
                - "code_example": Um exemplo de código aplicando a sugestão. Se nenhuma alteração for necessária, retorne o código original.
                """
        else:
            logging.info("Relatório do cProfile gerado com sucesso. Solicitando interpretação da IA.")
            prompt = f"""
                Atue como um desenvolvedor Python Sênior especialista em otimização de performance.
                Sua tarefa é analisar um trecho de código e o relatório de performance gerado pela ferramenta `cProfile`.

                **Código Analisado:**
                ```python
                {code}
                ```

                **Relatório do cProfile:**
                ```
                {performance_report}
                ```

                **Sua Análise:**
                1.  **Identifique o Principal Gargalo:** Com base no relatório (`tottime`, `cumtime`, `ncalls`), qual função ou trecho de código está consumindo mais tempo?
                2.  **Explique o Problema:** Descreva de forma clara e concisa por que essa parte do código é lenta.
                3.  **Forneça uma Solução:** Apresente uma versão otimizada do código, explicando a lógica por trás da melhoria (ex: uso de algoritmos mais eficientes, estruturas de dados adequadas, memoization, etc.).

                Retorne a resposta estritamente no seguinte formato JSON, com as chaves "title", "explanation", e "code_example":
                - "title": Um título descritivo para a otimização (ex: "Otimização de Loop para Reduzir Chamadas de Função").
                - "explanation": Sua explicação detalhada do gargalo e da solução.
                - "code_example": O trecho de código corrigido e otimizado.
                """

    except Exception as e:
        logging.error(f"Erro ao executar ou perfilar o código: {e}")

    ia_response_json = await call_gemini_api(prompt, 'PerformanceAnalysis')

    if "title" in ia_response_json and "explanation" in ia_response_json:
        enriched_suggestions.append(EnrichedSuggestion(**ia_response_json))
    else:
        logging.warning("Não foi possível obter uma sugestão válida da IA para a análise de performance.")

        enriched_suggestions.append(EnrichedSuggestion(
            title="Falha na Análise",
            explanation="Não foi possível processar a resposta da IA. Verifique os logs do agente.",
            code_example="# Nenhuma sugestão disponível."
        ))

    return enriched_suggestions
