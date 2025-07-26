from crewai import Agent, Task, Crew, Process

from config import llm
from tools import BanditAnalysisTool
from models import AnalysisResponse


bandit_tool = BanditAnalysisTool()

security_analyst_agent = Agent(
    role="Especialista em Segurança de Aplicações (AppSec) e Revisor de Código Sênior",
    goal=f"""
        Analisar relatórios da ferramenta de segurança 'bandit' e traduzi-los em sugestões claras,
        práticas e acionáveis para desenvolvedores.
        Sua saída final DEVE ser um objeto JSON que valide estritamente com o seguinte schema Pydantic:
        {AnalysisResponse.model_json_schema()}
    """,
    backstory=(
        "Você é um engenheiro de segurança com anos de experiência em análise de vulnerabilidades em código Python. "
        "Sua especialidade é transformar relatórios técnicos complexos em conselhos práticos que os desenvolvedores "
        "possam entender e aplicar imediatamente para corrigir falhas de segurança."
    ),
    tools=[bandit_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

analysis_task = Task(
    description=(
        "1. Receba o trecho de código Python a seguir: {code}\n"
        "2. Utilize sua ferramenta 'BanditAnalysisTool' para executar a análise de segurança neste código.\n"
        "3. Analise o relatório JSON bruto retornado pela ferramenta.\n"
        "4. Para cada vulnerabilidade encontrada, crie uma sugestão clara contendo um 'title', uma 'explanation' detalhada do risco e um 'code_example' mostrando a correção.\n"
        "5. Formate TODAS as sugestões em um único objeto JSON que corresponda exatamente ao schema Pydantic fornecido em seu objetivo. Não adicione nenhuma palavra, comentário ou formatação markdown fora do JSON.\n"
        "6. Caso não haja vulnerabilidades, retorne um JSON vazio com uma lista de sugestões informando que nao foram encontradas vulnerabilidades seguindo o  JSON esperado. "
        "Onde o 'title' deve ser 'Nenhuma vulnerabilidade encontrada', a 'explanation' deve ser 'Nenhuma vulnerabilidade foi identificada no código fornecido.' e o 'code_example' deve estar vazio."
    ),
    expected_output=(
        "Uma string contendo um único objeto JSON válido. O JSON deve ter uma chave 'suggestions' que contém uma lista de objetos, "
        "cada um com as chaves 'title', 'explanation' e 'code_example'."
    ),
    agent=security_analyst_agent
)

security_crew = Crew(
    agents=[security_analyst_agent],
    tasks=[analysis_task],
    process=Process.sequential
)
