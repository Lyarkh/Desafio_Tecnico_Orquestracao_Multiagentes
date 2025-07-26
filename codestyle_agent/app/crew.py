from crewai import Agent, Task, Crew, Process

from config import llm
from tools import Flake8AnalysisTool
from models import AnalysisResponse


flake8_tool = Flake8AnalysisTool()

code_style_analyst_agent = Agent(
    role="Desenvolvedor Python Sênior e Revisor de Código Detalhista",
    goal=f"""
        Analisar o relatório da ferramenta 'flake8' e convertê-lo em sugestões práticas e educativas
        para outros desenvolvedores, com foco em legibilidade e conformidade com a PEP 8.
        Sua saída final DEVE ser um objeto JSON que valide estritamente com o seguinte schema Pydantic:
        {AnalysisResponse.model_json_schema()}
    """,
    backstory=(
        "Você é um defensor fervoroso de código limpo e bem escrito. Com uma década de experiência em Python, "
        "você acredita que a qualidade do código é tão importante quanto sua funcionalidade. Sua missão é guiar "
        "outros desenvolvedores a escreverem um código mais claro, legível e manutenível."
    ),
    tools=[flake8_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

code_style_task = Task(
    description=(
        "1. Receba o seguinte trecho de código Python: {code}\n"
        "2. Utilize sua ferramenta 'Flake8AnalysisTool' para executar a análise de estilo.\n"
        "3. Analise a saída de texto retornada pela ferramenta.\n"
        "4. Para cada problema apontado pelo flake8, crie uma sugestão clara contendo um 'title' (ex: 'E501: Linha muito longa'), "
        "uma 'explanation' detalhada do porquê essa é uma má prática, e um 'code_example' mostrando a linha corrigida.\n"
        "5. Formate TODAS as sugestões em um único objeto JSON que corresponda exatamente ao schema Pydantic fornecido em seu objetivo.\n"
        "6. Caso não haja problemas encontrados, retorne um JSON vazio com uma lista de sugestões informando que nao foram encontradas correções necessárias seguindo o JSON esperado. "
        "Onde o 'title' deve ser 'Nenhuma problema encontrada', a 'explanation' deve ser 'Nenhuma problema foi identificada no código fornecido.' e o 'code_example' deve estar vazio."
        "7. O formato de output do Flake8 vai estar nesse formato: %(row)d:%(col)d:%(code)s:%(text)s, onde row é a linha do erro, col é a coluna do erro, code é o código do erro e text é a mensagem de erro."
    ),
    expected_output=(
        "Uma string contendo um único objeto JSON válido. O JSON deve ter uma chave 'suggestions' contendo uma lista de objetos, "
        "cada um com as chaves 'title', 'explanation' e 'code_example'."
    ),
    agent=code_style_analyst_agent
)

code_style_crew = Crew(
    agents=[code_style_analyst_agent],
    tasks=[code_style_task],
    process=Process.sequential
)
