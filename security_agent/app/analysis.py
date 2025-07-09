import asyncio
import json
import logging
import os
import subprocess
import tempfile

from models import EnrichedSuggestion
from call_api import call_gemini_api


async def run_hybrid_analysis(code: str) -> list[EnrichedSuggestion]:
    """
    Executa a análise híbrida: primeiro com o bandit, depois enriquecendo com a IA.

    Args:
        code: O trecho de código Python a ser analisado.

    Returns:
        Uma lista de objetos EnrichedSuggestion.
    """
    temp_dir = tempfile.mkdtemp()
    temp_filename = f"{temp_dir}/temp_code_for_analysis.py"
    with open(temp_filename, "w") as f:
        f.write(code)

    logging.info(f"Executando o bandit no arquivo: {temp_filename}")
    result = subprocess.run(
        ["bandit", "-f", "json", temp_filename],
        capture_output=True,
        text=True,
        check=False
    )

    os.remove(temp_filename)

    if result.returncode != 0 and not result.stdout:
        logging.error(f"Erro ao executar o bandit: {result.stderr}")
        return []

    try:
        bandit_report = json.loads(result.stdout)
        bandit_results = bandit_report.get("results", [])
    except json.JSONDecodeError:
        logging.warning("Falha ao decodificar a saída JSON do bandit. Prosseguindo com análise geral da IA.")
        bandit_results = []

    enriched_suggestions = []
    tasks = []
    if bandit_results:
        logging.info(f"Bandit encontrou {len(bandit_results)} problemas. Enriquecendo com a IA...")
        for issue in bandit_results:
            prompt = f"""
            A ferramenta de análise de segurança estática 'bandit' encontrou o seguinte problema em um código Python:
            - Título do Problema: {issue['issue_text']}
            - Gravidade: {issue['issue_severity']}
            - Confiança: {issue['issue_confidence']}
            - Código com problema: {issue['code']}
            - Linha do problema: {issue['line_number']}
            - Mais informações: {issue['more_info']}

            Atue como um especialista em segurança de aplicações (AppSec). Sua tarefa é analisar este problema e fornecer uma explicação clara e útil.
            Por favor, faça o seguinte:
            1. Crie um título amigável e descritivo para este problema.
            2. Escreva uma explicação clara e concisa (em português do Brasil) sobre por que isso representa uma vulnerabilidade.
            3. Forneça um exemplo de código corrigido e seguro.

            Retorne a resposta estritamente no seguinte formato JSON, com as chaves "title", "explanation", e "code_example":
            """
            tasks.append(call_gemini_api(prompt, issue['issue_text']))

        api_responses = await asyncio.gather(*tasks)

        for response_json in api_responses:
            if "title" in response_json and "explanation" in response_json:
                enriched_suggestions.append(EnrichedSuggestion(**response_json))
            else:
                logging.warning(f"Não foi possível obter uma sugestão válida da IA para o problema: {issue['issue_text']}")

    else:
        logging.info("O bandit não encontrou vulnerabilidades. Solicitando uma análise de segurança geral da IA.")
        prompt = f"""
        A ferramenta 'bandit' não encontrou vulnerabilidades de segurança no código abaixo.
        Código para análise:
        ---
        {code}
        ---
        Atue como um especialista em segurança de aplicações (AppSec) e desenvolvedor Python sênior. Faça uma revisão de segurança geral deste código. Procure por possíveis vulnerabilidades, más práticas de segurança ou falhas de lógica que o bandit pode não ter detectado.

        - Se você encontrar alguma vulnerabilidade ou ponto de melhoria, descreva o mais importante.
        - Se você não encontrar nenhuma vulnerabilidade, confirme que o código parece seguro de uma perspectiva geral.

        Retorne a resposta estritamente no seguinte formato JSON com as chaves "title", "explanation", e "code_example":
        - "title": Um título para sua análise. Se estiver tudo bem, use "Análise de Segurança Concluída".
        - "explanation": Sua análise. Se estiver tudo bem, escreva algo como "Nenhuma vulnerabilidade de segurança óbvia foi encontrada após uma análise geral. O código segue boas práticas de segurança.".
        - "code_example": Se encontrou um problema, mostre a correção. Se não, retorne o código original ou um comentário como "# Nenhuma alteração de segurança necessária.".
        """
        ia_response_json = await call_gemini_api(prompt, 'Sem issues')
        if "title" in ia_response_json and "explanation" in ia_response_json:
            enriched_suggestions.append(EnrichedSuggestion(**ia_response_json))
        else:
            logging.warning("Não foi possível obter uma sugestão válida da IA para a análise geral.")

    return enriched_suggestions
