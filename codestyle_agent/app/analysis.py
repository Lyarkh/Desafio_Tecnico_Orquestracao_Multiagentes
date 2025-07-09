import logging
import asyncio
import os
import subprocess
import tempfile

from models import EnrichedSuggestion
from call_api import call_gemini_api


async def run_hybrid_analysis(code: str) -> list[EnrichedSuggestion]:
    """
    Executa a análise de estilo híbrida: primeiro com o flake8, depois enriquecendo com a IA.
    Se o flake8 não encontrar nada, a IA faz uma análise geral de boas práticas.
    """
    temp_dir = tempfile.mkdtemp()
    temp_filename = f"{temp_dir}/temp_code_for_style_analysis.py"
    with open(temp_filename, "w") as f:
        f.write(code)

    logging.info(f"Executando o flake8 no arquivo: {temp_filename}")
    result = subprocess.run(
        ["flake8", "--format=%(row)d:%(col)d:%(code)s:%(text)s", temp_filename],
        capture_output=True,
        text=True,
        check=False
    )
    os.remove(temp_filename)

    flake8_results = result.stdout.strip().split('\n') if result.stdout.strip() else []

    tasks = []
    enriched_suggestions = []
    if flake8_results:
        logging.info(f"Flake8 encontrou {len(flake8_results)} problemas. Enriquecendo com a IA...")
        for issue_line in flake8_results:
            parts = issue_line.split(':', 3)
            if len(parts) < 4: continue

            line_num, col_num, error_code, error_message = parts

            code_line = code.splitlines()[int(line_num) - 1]

            prompt = f"""
            A ferramenta de análise de estilo de código 'flake8' encontrou o seguinte problema em um código Python:
            - Código do Erro: {error_code.strip()}
            - Mensagem: {error_message.strip()}
            - Linha do problema: {line_num}
            - Código na linha: "{code_line.strip()}"

            Atue como um desenvolvedor Python sênior e especialista em PEP 8. Sua tarefa é analisar este problema e fornecer uma explicação clara e útil.
            Por favor, faça o seguinte:
            1. Crie um título amigável e descritivo para este problema de estilo (ex: "Remover Espaços em Branco no Final da Linha").
            2. Escreva uma explicação clara e concisa (em português do Brasil) sobre por que isso é uma convenção de estilo importante e como melhora a legibilidade ou evita erros.
            3. Forneça um exemplo de código corrigido.

            Retorne a resposta estritamente no seguinte formato JSON, com as chaves "title", "explanation", e "code_example":
            """
            tasks.append(call_gemini_api(prompt, error_code))

        api_responses = await asyncio.gather(*tasks)

        for response_json in api_responses:
            if "title" in response_json and "explanation" in response_json:
                enriched_suggestions.append(EnrichedSuggestion(**response_json))
            else:
                logging.warning(f"Não foi possível obter uma sugestão válida da IA para o problema: {error_message}")
    else:
        logging.info("O flake8 não encontrou problemas. Solicitando uma análise geral de boas práticas da IA.")
        prompt = f"""
        A ferramenta 'flake8' não encontrou problemas de estilo no código abaixo.
        Código para análise:
        ---
        {code}
        ---
        Atue como um desenvolvedor Python sênior e mentor. Faça uma revisão geral deste código. Procure por oportunidades de torná-lo mais "Pythônico", legível e alinhado com as melhores práticas de desenvolvimento que vão além do que o flake8 verifica.

        - Se você encontrar alguma melhoria (ex: usar um list comprehension, melhorar nomes de variáveis, etc.), descreva a mais importante.
        - Se você não encontrar nenhuma melhoria, confirme que o código já segue um alto padrão de qualidade e boas práticas.

        Retorne a resposta estritamente no seguinte formato JSON com as chaves "title", "explanation", e "code_example":
        - "title": Um título para sua análise. Se estiver tudo bem, use "Análise de Estilo de Código Concluída".
        - "explanation": Sua análise. Se estiver tudo bem, escreva algo como "Nenhum ponto de melhoria óbvio foi encontrado. O código está limpo, legível e segue as boas práticas do Python.".
        - "code_example": Se encontrou uma melhoria, mostre a sugestão. Se não, retorne o código original ou um comentário como "# Nenhuma alteração de estilo sugerida.".
        """
        ia_response_json = await call_gemini_api(prompt, 'Sem issues')
        if "title" in ia_response_json and "explanation" in ia_response_json:
            enriched_suggestions.append(EnrichedSuggestion(**ia_response_json))
        else:
            logging.warning("Não foi possível obter uma sugestão válida da IA para a análise geral.")

    return enriched_suggestions
