# Pipeline ETL & Modelagem Dimensional (Star Schema) — Operações & Vendas

Este projeto consiste em um **pipeline de dados (ETL)** desenvolvido em **Python** para automatizar a extração, transformação e carga de dados de uma planilha Excel (`dados_brutos.xlsx`) para um banco de dados relacional **MySQL** (hospedado na nuvem via **Aiven**). 

A modelagem segue os princípios de **Data Warehousing (Modelagem Dimensional / Star Schema)**, garantindo o desacoplamento entre a entrada de dados (focada no usuário de negócio) e a integridade do banco de dados analítico.

---

## 📌 Arquitetura do Banco de Dados (Star Schema)

O modelo dimensional é composto por três **Tabelas Dimensão** (`dim_`) e uma **Tabela Fato** (`fato_`):

```text
                     +-------------------+
                     |    dim_loja       |
                     +-------------------+
                     | id_loja (PK)      |
                     | nome_loja (UQ)    |
                     | tipo_loja         |
                     | gerente_loja      |
                     +-------------------+
                               |
+-------------------+          |          +-------------------+
|   dim_produto     |          |          |    dim_cliente    |
+-------------------+          |          +-------------------+
| id_produto (PK)   |----------+----------| id_cliente (PK)   |
| nome_produto (UQ) |          |          | cpf_cliente (UQ)  |
| categoria         |          |          | nome_cliente      |
| preco_producao    |          v          | cidade / estado   |
| preco_venda       |   +--------------+  | data_cadastro     |
+-------------------+   |  fato_vendas |  +-------------------+
                        +--------------+
                        | id_venda(PK) |
                        | data_venda   |
                        | id_produto(FK|
                        | id_cliente(FK|
                        | quantidade   |
                        | valor_unitar |
                        | valor_total  |
                        +--------------+
```

### Estrutura das Tabelas:
* **`dim_produto`**: Armazena o cadastro de produtos (`id_produto`, `nome_produto`, `categoria`, `preco_producao`, `preco_venda`).
* **`dim_cliente`**: Armazena o cadastro de clientes (`id_cliente`, `cpf_cliente`, `nome_cliente`, `cidade`, `estado`, `data_cadastro`).
* **`dim_loja`**: Armazena os canais ou filiais de vendas (`id_loja`, `nome_loja`, `tipo_loja`, `gerente_loja`).
* **`fato_vendas`**: Registra as transações financeiras (`id_venda`, `data_venda`, `id_produto`, `id_cliente`, `quantidade`, `valor_unitario`, `valor_total`).

---

## 🧰 Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Manipulação e Transformação de Dados:** `pandas`, `openpyxl`
* **Conectividade & ORM:** `SQLAlchemy`, `PyMySQL`
* **Banco de Dados Relacional:** MySQL 8.0 (Instância na nuvem via **Aiven**)
* **Gerenciamento de Variáveis de Ambiente:** `python-dotenv`
* **IDE / Ferramentas de Consulta:** VS Code, MySQL Workbench

---

## 🚀 Destaques e Regras de Negócio do ETL

1. **Gestão Automática de DDL:**
   * Executa o arquivo `ddl_operacoes_analytics.sql` na inicialização do pipeline para garantir que os bancos, tabelas e restrições (`UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`) estejam prontos na nuvem.

2. **Carga Incremental Sem Duplicidades (Chaves de Negócio):**
   * Em vez de exigir que o usuário digite IDs no Excel, as dimensões utilizam **Chaves de Negócio** (`nome_produto`, `cpf_cliente`, `nome_loja`) para checar se o registro já existe no MySQL antes de inserir.
   * Os IDs numéricos (`AUTO_INCREMENT`) são gerados exclusivamente pelo MySQL.

3. **Mapeamento "De-Para" / Lookup Automático (`fato_vendas`):**
   * O usuário preenche a aba `fato_vendas` no Excel utilizando dados inteligíveis (`nome_produto` e `cpf_cliente`).
   * Antes da gravação, o Python faz uma junção (`merge`) com o banco de dados, recupera os Surrogate Keys (`id_produto` e `id_cliente`) e os insere na tabela Fato mantendo a **integridade referencial**.

4. **Higienização de Dados e Padronização de Tipos:**
   * Remove automaticamente espaços extras no início/fim de cabeçalhos (`.str.strip()`).
   * Padroniza tipos numéricos e textuais (ex: conversão explícita de CPF para `string`) para evitar falsos registros duplicados durante a comparação do Pandas com o MySQL.

---

## 📂 Estrutura do Repositório

```text
├── .env                       # Variáveis de ambiente (credenciais do MySQL Aiven)
├── dados_brutos.xlsx          # Planilha Excel com as abas de origem
├── ddl_operacoes_analytics.sql # Script SQL DDL de criação do schema e restrições
├── etl_pipeline.py            # Script principal contendo o fluxo de ETL
└── README.md                  # Documentação do projeto
```

---

## ⚙️ Configuração e Execução

### 1. Instalar dependências
```bash
pip install pandas sqlalchemy pymysql openpyxl python-dotenv
```

### 2. Configurar o arquivo `.env`
Crie um arquivo `.env` na raiz do projeto com os dados de conexão do Aiven:

```env
DB_USER=avnadmin
DB_PASSWORD=sua_senha_aiven
DB_HOST=seu-host.aivencloud.com
DB_PORT=16814
DB_NAME=defaultdb
```

### 3. Preencher o arquivo `dados_brutos.xlsx`
Certifique-se de que a planilha possui as abas correspondentes:
* **`dim_produto`**: Colunas (`nome_produto`, `categoria`, `preco_producao`, `preco_venda`).
* **`dim_cliente`**: Colunas (`cpf_cliente`, `nome_cliente`, `cidade`, `estado`, `data_cadastro`).
* **`dim_loja`**: Colunas (`nome_loja`, `tipo_loja`, `gerente_loja`).
* **`fato_vendas`**: Colunas (`data_venda`, `nome_produto`, `cpf_cliente`, `quantidade`, `valor_unitario`).

### 4. Executar o Pipeline
```bash
python etl_pipeline.py
```

---

## 📊 Exemplos de Consultas SQL (Analytics)

Após a execução do pipeline, utilize estas consultas no **MySQL Workbench** para extrair métricas de negócio:

### Relatório Consolidado (JOIN)
```sql
SELECT 
    f.id_venda,
    f.data_venda,
    c.nome_cliente,
    c.cpf_cliente,
    p.nome_produto,
    p.categoria,
    f.quantidade,
    f.valor_unitario,
    f.valor_total
FROM fato_vendas f
INNER JOIN dim_produto p ON f.id_produto = p.id_produto
INNER JOIN dim_cliente c ON f.id_cliente = c.id_
