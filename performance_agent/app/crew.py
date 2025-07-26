from crewai import Agent, Task, Crew, Process

from config import llm
from tools import CProfileAnalysisTool
from models import AnalysisResponse


cprofile_tool = CProfileAnalysisTool()

performance_engineer_agent = Agent(
    role="Engenheiro de Software Sênior especialista em Otimização de Performance",
    goal=f"""
        Analisar o relatório de performance da ferramenta 'cProfile' para identificar os principais
        gargalos de execução em um código Python e fornecer sugestões de otimização claras e eficazes.
        Sua saída final DEVE ser um objeto JSON que valide estritamente com o seguinte schema Pydantic:
        {AnalysisResponse.model_json_schema()}
    """,
    backstory=(
        "Você é um engenheiro experiente obcecado por velocidade e eficiência. Você tem um talento especial para ler "
        "relatórios de profiling complexos e identificar exatamente qual função ou linha de código está atrasando a aplicação. "
        "Suas sugestões são sempre práticas e focadas em gerar o maior impacto de performance."
    ),
    tools=[cprofile_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

performance_analysis_task = Task(
    description=(
        "1. Receba o seguinte trecho de código Python: {code}\n"
        "2. Utilize sua ferramenta 'CProfileAnalysisTool' para executar o código e obter o relatório de performance.\n"
        "3. Analise a saída de texto do cProfile. Foque nas funções com maior 'tottime' (tempo total) e 'cumtime' (tempo cumulativo).\n"
        "4. Identifique o principal gargalo de performance. Crie uma sugestão detalhada contendo um 'title' (ex: 'Alto tempo de execução na função X'), "
        "uma 'explanation' explicando por que a função é lenta (ex: loop ineficiente, muitas chamadas), e um 'code_example' mostrando uma versão otimizada do código.\n"
        "5. Formate a sugestão em um único objeto JSON que corresponda exatamente ao schema Pydantic fornecido em seu objetivo.\n"
        "6. Caso não haja problemas de performance, retorne um JSON vazio com uma lista de sugestões informando que nao foram encontradas correções necessárias seguindo o JSON esperado. "
        "Onde o 'title' deve ser 'Nenhuma problema de performance encontrada', a 'explanation' deve ser 'Nenhuma problema foi identificada no código fornecido.' e o 'code_example' deve estar vazio."
    ),
    expected_output=(
        "Uma string contendo um único objeto JSON válido. O JSON deve ter uma chave 'suggestions' contendo uma lista de objetos, "
        "cada um com as chaves 'title', 'explanation' e 'code_example'."
    ),
    agent=performance_engineer_agent
)

performance_crew = Crew(
    agents=[performance_engineer_agent],
    tasks=[performance_analysis_task],
    process=Process.sequential
)
