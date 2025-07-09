import json
import logging
import os
import google.generativeai as genai

async def call_gemini_api(prompt: str, task_name: str) -> dict:
    """
    Chama a API do Google Gemini para obter uma sugestão enriquecida em formato JSON.
    Este é um módulo reutilizável para qualquer agente que precise de análise de IA.

    Args:
        prompt: O prompt detalhado a ser enviado para o modelo.
        task_name: Um nome para a tarefa, usado para logging.

    Returns:
        Um dicionário contendo a sugestão enriquecida ou um dicionário de erro.
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    model_name = os.environ.get('MODEL_NAME')

    if not api_key or not model_name:
        logging.error("A chamada à API do Gemini foi pulada porque a GOOGLE_API_KEY ou MODEL_NAME não está configurada.")
        return {
            "title": "Erro de Configuração do Agente",
            "explanation": "A API do Gemini não foi chamada porque a variável de ambiente GOOGLE_API_KEY ou MODEL_NAME não está configurada.",
            "code_example": "# Configure as variáveis de ambiente para habilitar a análise por IA."
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )

        logging.info(f"Enviando prompt da task [{task_name}] para a API do Gemini...")
        response = await model.generate_content_async(prompt)

        return json.loads(response.text)

    except Exception as e:
        logging.error(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
        return {
            "title": "Erro na Análise da IA",
            "explanation": f"Não foi possível gerar a sugestão devido a um erro na API. Detalhes: {e}",
            "code_example": "# Nenhum exemplo de código pôde ser gerado."
        }
