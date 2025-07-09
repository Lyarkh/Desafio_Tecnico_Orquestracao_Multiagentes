import json
import logging
import os

import google.generativeai as genai


async def call_gemini_api(prompt: str, task_name: str) -> dict:
    """
    Chama a API do Gemini para obter uma sugestão enriquecida em formato JSON.

    Args:
        prompt: O prompt detalhado a ser enviado para o modelo.

    Returns:
        Um dicionário contendo a sugestão enriquecida ou um dicionário de erro.
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    model_name = os.environ.get('MODEL_NAME')

    if not api_key or not model_name:
        logging.error("A chamada à API do Gemini foi pulada porque a chave de API não está configurada.")
        return {
            "title": "Erro de Configuração",
            "explanation": "A API do Gemini não foi chamada porque a GOOGLE_API_KEY ou MODEL_NAME não está configurada no ambiente.",
            "code_example": "# Configure a chave de API para habilitar a análise."
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
        # Retornamos um dicionário com o erro para que o fluxo não quebre.
        return {
            "title": "Erro na Análise da IA",
            "explanation": f"Não foi possível gerar a sugestão. Detalhes do erro: {e}",
            "code_example": "# Nenhum exemplo de código pôde ser gerado."
        }
