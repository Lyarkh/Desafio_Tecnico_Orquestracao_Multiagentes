# Sistema Multiagente de Análise de Código Python

## Visão Geral

Este projeto implementa um sistema avançado para análise e otimização de código Python, utilizando uma arquitetura de microsserviços e o poder da Inteligência Artificial Generativa. Um serviço Orquestrador central gerencia as requisições e coordena o trabalho de múltiplos Agentes especializados com a utilização do CrewAI.

Cada agente utiliza uma ferramenta de análise específica (segurança, performance, estilo). Isso transforma os relatórios técnicos em sugestões práticas, explicativas e acionáveis para o desenvolvedor, com exemplos de código corrigido. O histórico das análises é persistido em um banco de dados PostgreSQL.


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

O núcleo do projeto é a utilização do framework CrewAI para definir, gerenciar e executar as tarefas dos agentes.

## 2. Agentes Especializados (security_agent, performance_agent, codestyle_agent)
O fluxo de trabalho para cada agente é o mesmo:

Recebe o código do Orquestrador no endpont `POST /analyse`.

Executa sua ferramenta de análise local especializada.

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

## Banco de Dados (db)

**Tecnologia:** PostgreSQL 15.

**Responsabilidade:** Armazenar o histórico de todas as análises na tabela analysis_history.



## Como Executar o Projeto

Siga os passos abaixo para configurar e executar o ambiente de desenvolvimento local.

### Pré-requisitos

```
Docker
Docker Compose
```

#### 1. Clonar o Repositório
```bash
git clone [https://github.com/Lyarkh/Desafio_Tecnico_Orquestracao_Multiagentes](https://github.com/Lyarkh/Desafio_Tecnico_Orquestracao_Multiagentes)
cd Desafio_Tecnico_Orquestracao_Multiagentes
```

#### 2. Configurar Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto, copiando o exemplo .env.example.

```bash
cp .env.example .env
```
Abra o arquivo .env e preencha as variáveis necessárias.

```
# .env
GOOGLE_API_KEY="sua-chave-de-api-aqui"
MODEL_NAME="gemini-1.5-flash"
```

#### 3. Subir os Containers
Com o Docker em execução, utilize o Docker Compose para construir as imagens e iniciar todos os serviços.

```bash
docker-compose up --build
```
Os seguintes serviços serão iniciados:

**orchestrator:** A API principal do orquestrador (porta 8080).
**codestyle_agent:** O agente de estilo de código (porta 8001).
**security_agent:** O agente de segurança (porta 8002).
**performance_agent:** O agente de performance (porta 8003).
**db:** O banco de dados PostgreSQL (porta 5432).
**pgadmin:** A interface de gerenciamento para o banco de dados (porta 5050).

#### 4. Acessando os Serviços

API do Orquestrador: http://localhost:8080/docs
API do Agente de Estilo: http://localhost:8001/docs
API do Agente de Segurança: http://localhost:8002/docs
API do Agente de Performance: http://localhost:8003/docs

#### 5. Testando a Aplicação
Você pode usar a collection do Postman [collections](/collections/Sistema%20Multi%20Agentes.postman_collection.json) para testar os endpoints e o fluxo de análise. Importe a collection no seu Postman e envie uma requisição para o endpoint de análise do orquestrador.

### Banco de Dados e PgAdmin
O projeto utiliza um banco de dados PostgreSQL para persistir os resultados das análises. Um serviço do PgAdmin é disponibilizado para facilitar a visualização e o gerenciamento dos dados.

Acesso ao PgAdmin:

- URL: http://localhost:5050
- Email/Usuário: admin@admin.com
- Senha: admin

#### Conectando ao Banco de Dados no PgAdmin
Após fazer login no PgAdmin, clique com o botão direito em Servers e vá em Create -> Server....

Na aba General, dê um nome para o servidor (ex: analise_agentes_db).

Na aba Connection, preencha os seguintes campos:

Host name/address: postgres_db (este é o nome do serviço do container do banco de dados no docker-compose.yaml).

- Port: 5432
- Maintenance database: postgres_db
- Username: admin
- Password: admin

Clique em Save.

Agora você poderá navegar pelas tabelas e visualizar os dados salvos pelo orquestrador. A tabela principal é a analysis_results.

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
A API retornará um objeto JSON com as sugestões estruturadas:
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