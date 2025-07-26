from crewai import Agent, Task, Crew, Process

import config
from tools import SecurityAgentTool, CodeStyleAgentTool, PerformanceAgentTool
from models import ConsolidatedResponse


security_tool = SecurityAgentTool()
style_tool = CodeStyleAgentTool()
performance_tool = PerformanceAgentTool()


code_review_coordinator = Agent(
    role="Coordenador de Revisão de Código",
    goal="Orquestrar eficientemente a análise de um trecho de código delegando as tarefas para os agentes especialistas apropriados usando as ferramentas disponíveis.",
    backstory=(
        "Você é um gerente de projetos técnico. Sua função não é analisar o código, mas garantir que cada especialista "
        "(Segurança, Estilo, Performance) receba a tarefa e que o trabalho seja feito. Você apenas invoca as ferramentas e passa os resultados adiante."
    ),
    tools=[security_tool, style_tool, performance_tool],
    llm=config.llm_for_review,
    verbose=True,
    allow_delegation=False
)

report_consolidator = Agent(
    role="Consolidador de Relatórios Técnicos",
    goal=f"""
        Coletar os relatórios JSON individuais de cada análise (segurança, estilo, performance)
        e compilá-los em um único relatório JSON final. O relatório final deve ser coeso, bem estruturado
        e seguir estritamente o schema Pydantic(ConsolidatedResponse) a seguir apontando as sugestões de cada um dos agents com as chaves 'security', 'performance' e 'codestyle':
        {ConsolidatedResponse.model_json_schema()}
    """,
    backstory=(
        "Você é um especialista em formatação de dados. Sua função é pegar múltiplos fragmentos de dados estruturados "
        "e montá-los em um documento final unificado, garantindo consistência e aderência ao formato exigido."
    ),
    tools=[],
    llm=config.llm_for_report,
    verbose=True
)

def create_orchestration_crew(code_snippet: str) -> Crew:
    """
    Cria e configura a equipe de orquestração dinamicamente com o código fornecido.
    """

    delegate_security_task = Task(
        description=f"Use a ferramenta 'Analisador de Segurança de Código' para analisar o seguinte trecho de código: ```{code_snippet}```. Retorne o resultado JSON bruto da ferramenta.",
        expected_output="A saída JSON completa, como uma string, retornada pelo agente de segurança.",
        agent=code_review_coordinator
    )

    delegate_style_task = Task(
        description=f"Use a ferramenta 'Analisador de Estilo de Código' para analisar o seguinte trecho de código: ```{code_snippet}```. Retorne o resultado JSON bruto da ferramenta.",
        expected_output="A saída JSON completa, como uma string, retornada pelo agente de estilo.",
        agent=code_review_coordinator
    )

    delegate_performance_task = Task(
        description=f"Use a ferramenta 'Analisador de Performance de Código' para analisar o seguinte trecho de código: ```{code_snippet}```. Retorne o resultado JSON bruto da ferramenta.",
        expected_output="A saída JSON completa, como uma string, retornada pelo agente de performance.",
        agent=code_review_coordinator
    )

    consolidate_report_task = Task(
        description=(
            "Analise os relatórios JSON das tarefas de segurança, estilo e performance. "
            "Extraia a lista de 'suggestions' de cada um deles. "
            "Combine todas as sugestões em uma única lista. "
            "Finalmente, construa o objeto JSON final com a chave 'suggestions' contendo a lista consolidada. "
            "Garanta que a saída seja apenas o JSON, sem nenhum texto ou comentário adicional. "
            "Garanta que sugestões duplicadas que vem de diferentes agentes sejam removidas, mantendo apenas uma instância de cada sugestão única."
        ),
        expected_output="Uma única string JSON que valida com o schema 'ConsolidatedResponse'.",
        agent=report_consolidator,
        context=[delegate_security_task, delegate_style_task, delegate_performance_task]
    )

    return Crew(
        agents=[code_review_coordinator, report_consolidator],
        tasks=[
            delegate_security_task,
            delegate_style_task,
            delegate_performance_task,
            consolidate_report_task,
        ],
        process=Process.sequential,
        verbose=True
    )
