# Sistema Multiagente de Análise de Código Python

## Visão Geral

Este projeto implementa um sistema avançado para análise e otimização de código Python, utilizando uma arquitetura de microsserviços e o poder da Inteligência Artificial Generativa. Um serviço Orquestrador central gerencia as requisições e coordena o trabalho de múltiplos Agentes especializados.

Cada agente utiliza uma ferramenta de análise específica (segurança, performance, estilo) e, em seguida, enriquece os resultados brutos utilizando a API do Google Gemini. Isso transforma os relatórios técnicos em sugestões práticas, explicativas e acionáveis para o desenvolvedor, com exemplos de código corrigido. O histórico das análises é persistido em um banco de dados PostgreSQL.



## Arquitetura do **Sistema**
A arquitetura foi projetada para ser modular e escalável, utilizando contêineres Docker para isolar cada serviço e a API do Gemini para a camada de inteligência.
```
      +------------------+
      |      Usuário     |
      +--------+---------+
               | (HTTP POST /orchestrate-analysis)
               v
+--------------+-----------------+      +------------------------+
|    Orquestrador (FastAPI)      +----->|   Banco de Dados       |
|      (localhost:8080)          |      |     (PostgreSQL)       |
+--------------+-----------------+      +------------------------+
               |
               | (Chama os agentes em sequência)
               |
+--------------v--------------------------------v--------------------------------v-----------------+
|              |(POST /analyze)                 |(POST /analyze)                 | (POST /analyze) |
|  +-----------+-----------+      +-------------+-------------+      +-----------+-----------+     |
|  |   Agente de Segurança |      | Agente de Estilo de Cód.  |      | Agente de Performance |     |
|  |  (bandit) + Gemini    |      | (pylint) + Gemini         |      | (cProfile) + Gemini   |     |
|  |      port 8001        |      |      port 8002            |      |      port 8003        |     |
|  +-----------------------+      +---------------------------+      +-----------------------+     |
|                                                                                                  |
|                                   Rede Docker Interna                                            |
+--------------------------------------------------------------------------------------------------+
```

## Descrição dos Componentes

### 1. Orquestrador (orchestrator)
Tecnologia: Python 3.11, FastAPI, SQLAlchemy.

#### Responsabilidades:

Expor o endpoint principal `POST /orchestrate-analysis` para receber o código.

Orquestrar o fluxo, chamando sequencialmente os agentes especializados.

Agregar as sugestões de cada agente em um relatório final consolidado.

Persistir o código e o relatório no banco de dados PostgreSQL.

## 2. Agentes Especializados (security_agent, performance_agent, codestyle_agent)
O fluxo de trabalho para cada agente é o mesmo:

Recebe o código do Orquestrador no endpont `POST /analyse`.

Executa sua ferramenta de análise local especializada.

Envia o relatório da ferramenta para a API do Google Gemini através de um prompt específico.

Recebe da IA uma análise enriquecida, com explicações detalhadas e exemplos práticos.

Retorna uma lista de sugestões estruturadas para o Orquestrador.

### Agente de Segurança (security_agent)

**Ferramenta:** bandit.

**Foco:** Identificar vulnerabilidades de segurança e fornecer explicações sobre os riscos e como corrigi-los.

### Agente de Estilo de Código (codestyle_agent)

**Ferramenta:** flake8.

**Foco:** Verificar a conformidade com a PEP 8 e outras boas práticas, explicando a importância de cada regra de estilo.

### Agente de Performance (performance_agent)

**Ferramenta:** cProfile.

**Foco:** Analisar o perfil de execução do código para encontrar gargalos e sugerir otimizações de performance.

## 3. Banco de Dados (db)

**Tecnologia:** PostgreSQL 15.

**Responsabilidade:** Armazenar o histórico de todas as análises na tabela analysis_history.

## Como Executar o Projeto
### Pré-requisitos
- Docker
- Docker Compose
- Uma API Key do Google Gemini.

### 1. Configuração do Ambiente
Antes de iniciar, é crucial configurar as variáveis de ambiente.

Crie um arquivo chamado .env na raiz do projeto a partir do exemplo.

Preencha o arquivo .env com suas credenciais seguindo o .env.example:

#### Variáveis da API do Google Gemini
```
GOOGLE_API_KEY=SUA_API_KEY_AQUI
MODEL_NAME=gemini-1.5-flash
```

### 2. Inicialização dos Serviços
Com o Docker em execução, abra um terminal na raiz do projeto e execute:
```
docker-compose up --build
```
Este comando irá construir e iniciar todos os contêineres. Aguarde até que os logs indiquem que os serviços estão prontos.

A tabela no banco de dados será criada na inicialização do serviço, mas caso queira rodar posteriormente. A query se encontra em [init.sql](database/init.sql)

### Como Usar a API
Para submeter um código para análise, envie uma requisição POST para o endpoint /orchestrate-analysis do Orquestrador.

Para auxiliar. Existe uma collections para utilização na pasta collections. [collection_multiagentes](collections/Sistema%20Multi%20Agentes.postman_collection.json)

**URL:** http://localhost:8080/orchestrate-analysis
**Método:** POST

**Body (JSON):**
```json
{
  "code": "SEU_CODIGO_PYTHON_AQUI"
}
```

**Exemplo de Requisição (cURL)**
```bash
curl -X POST "http://localhost:8080/orchestrate-analysis" \
-H "Content-Type: application/json" \
-d '{
  "code": "def soma(a, b): return a + b"
}'
```

### Exemplo de Resposta (JSON)
A API retornará um objeto JSON com as sugestões estruturadas de cada agente:
```json
{
    "security": {
        "suggestions": [
            {
                "title": "Análise de Segurança Concluída",
                "explanation": "Nenhuma vulnerabilidade de segurança óbvia foi encontrada...",
                "code_example": "def codigo_teste(a, b):\n   return a + b"
            }
        ]
    },
    "performance": {
        "suggestions": [
            {
                "title": "Sem gargalos de performance identificados",
                "explanation": "O relatório do cProfile indica que a função `codigo_teste` não apresenta nenhum gargalo de performance significativo...",
                "code_example": "def codigo_teste(a, b):\n   return a + b"
            }
        ]
    },
    "codestyle": {
        "suggestions": [
            {
                "title": "Nova linha no final do arquivo",
                "explanation": "O erro W292 do flake8, \"no newline at end of file\", indica que o arquivo Python está faltando uma nova linha em branco ao final...",
                "code_example": "def soma(a, b):\n   return a + b\n"
            }
        ]
    }
}
```

### Acessando banco

Caso seja necessário visualizar o banco. Você pode acessar o bash do container com o comando:
```bash
    >> docker compose exec postgres bash
    7d20360295e2:/#
```

Depois se conecta ao banco pelo usuário apresentado no `docker-compose.yaml`

```bash
    >> psql -U root postgres_db
    psql (15.13)
    Type "help" for help.

    postgres_db=#
```

E por fim, é possivel fazer o select ou queries no banco:
```bash
    >> select count(*) from analysis_history;
    count
    -------
        1
    (1 row)
```
### Decisões Técnicas

**Docker e Docker Compose:** Simplificam a configuração do ambiente e garantem a portabilidade da aplicação.

### Escalabilidade e Melhorias Futuras
Para garantir que o sistema possa crescer, as seguintes estratégias podem ser implementadas:

**Balanceamento de Carga (Load Balancing):** Introduzir um reverse proxy (como Nginx) na frente dos agentes. Se um agente se tornar um gargalo, podemos escalá-lo horizontalmente, e o balanceador distribuirá as requisições.

**Comunicação Assíncrona com Filas de Mensagens:** Para desacoplar o Orquestrador dos Agentes, poderíamos usar uma fila (como RabbitMQ ou Kafka). O Orquestrador publicaria uma tarefa, e os agentes a consumiriam. Isso aumenta a resiliência e melhora o tempo de resposta da API principal.



### Estratégias de Escalabilidade e Boas Práticas
A arquitetura de microsserviços é o primeiro passo para a escalabilidade. Abaixo, detalhamos as estratégias para garantir que o sistema cresça de forma sustentável e resiliente.

#### a. Balanceamento de Carga (Load Balancing)
À medida que o volume de requisições aumenta, um único contêiner por serviço se torna um gargalo.

**Estratégia:** Introduzir um Reverse Proxy / Load Balancer (como Nginx ou Traefik) na frente dos nossos serviços.

#### Implementação:

O docker-compose.yaml seria atualizado para incluir um serviço Nginx.

Em vez de expor as portas dos agentes (8001, 8002, 8003), apenas o Nginx exporia uma porta (ex: 80).

A configuração do Nginx definiria upstreams para cada grupo de agentes e distribuiria o tráfego entre eles.

Para escalar um serviço, bastaria aumentar o número de réplicas no docker-compose:
```bash
    docker-compose up --build --scale security_agent=3.
```
Arquitetura com Load Balancer:
```

      +---------+      +----------------+      +---------------------+
      | Usuário |----->|     Nginx      |----->| security_agent (x3) |
      +---------+      | (Load Balancer)|--+   +---------------------+
                       +----------------+  |
                                           |   +---------------------+
                                           +-->| performance_agent(x1)|
                                           |   +---------------------+
                                           |
                                           |   +---------------------+
                                           +-->| codestyle_agent (x1)|
                                               +---------------------+
```

#### b. Comunicação Assíncrona com Filas de Mensagens
A orquestração síncrona atual (baseada em REST) tem duas desvantagens: o cliente precisa esperar pela conclusão de todo o processo e o sistema é menos resiliente a falhas.

**Estratégia:** Desacoplar os serviços utilizando um Message Broker como RabbitMQ.

##### Novo Fluxo de Trabalho:

O cliente envia um `POST /orchestrate-analysis` com o código.

O Orquestrador valida a requisição, gera um analysis_id, publica uma mensagem na fila analysis_tasks com o código e o ID, e retorna imediatamente ao cliente uma resposta 202 Accepted com o analysis_id.

Cada agente (agora um worker) consome mensagens da fila analysis_tasks, executa sua análise e publica o resultado em outra fila, analysis_results, incluindo o analysis_id.

Um novo serviço (ou o próprio Orquestrador) consome da fila analysis_results, agrega os dados por analysis_id e salva o relatório final no banco de dados.

O cliente pode consultar o status e o resultado final através de um novo endpoint `GET /analysis/{analysis_id}`.

##### Arquitetura com Fila de Mensagens:

```
+---------+  1. POST   +--------------+  2. Publica Tarefa  +------------+  3. Workers  +-------------------+
| Usuário |----------->| Orquestrador |-------------------->| RabbitMQ   |------------>|  Agentes (Workers) |
+---------+  <-- 202 --+--------------+                     |(Fila Tasks)|             +-------------------+
  (com ID)                                                 +-------------+                      | 4. Publica Resultado
                                                                 ^                              |
                                                                 |                              v
                                                          +----------------+             +-----------+
                                                          |  Agregador de  |<------------| RabbitMQ  |
                                                          |    Resultados  |             |(Fila Res.)|
                                                          +----------------+             +-----------+
                                                                 | 5. Salva no DB
                                                                 v
                                                          +----------------+
                                                          |    Postgres    |
                                                          +----------------+
```
Benefícios: Maior resiliência (se um agente cair, a mensagem não se perde), escalabilidade (basta adicionar mais workers para consumir a fila) e melhor experiência do usuário (resposta inicial instantânea).