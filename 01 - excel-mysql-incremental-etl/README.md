# Pipeline ETL Incremental: Excel para MySQL

Este repositório contém um pipeline de dados em Python desenvolvido para automatizar a leitura de arquivos Excel, aplicar limpeza e transformação nos dados e realizar a carga incremental em um banco de dados MySQL, evitando registros duplicados.

---

## 🏗️ Como Funciona o Pipeline

O script segue a arquitetura **ETL (Extract, Transform, Load)**:

1. **Extração (Extract):** Lê a planilha `dados_brutos.xlsx`.
2. **Transformação (Transform):** Remove linhas com valores nulos (`dropna`) e higieniza a estrutura.
3. **Carga Incremental (Load):**
   - Conecta ao MySQL via `SQLAlchemy`.
   - Consulta os `id_produto` já gravados na tabela `dim_produto`.
   - Compara a base nova com a existente e insere apenas os registros inéditos (`append`).

---

## 📁 Estrutura do Projeto

```text
01-excel-mysql-incremental-etl/
├── .env.example                # Modelo de configuração de variáveis de ambiente
├── .gitignore                  # Arquivos e pastas ignorados pelo Git (venv, .env)
├── requirements.txt            # Lista de dependências Python
├── ddl_operacoes_analytics.sql # Script DDL para criação do banco e tabelas
├── etl_pipeline.py             # Script principal do pipeline
├── dados_brutos.xlsx           # Massa de dados para teste
└── README.md                   # Documentação do projeto
```

---

## 🛠️ Pré-requisitos

- **Python 3.10+** instalado.
- **MySQL Server** em execução localmente ou em servidor remoto.
- Cliente SQL (MySQL Workbench, DBeaver ou CLI) para rodar o DDL.

---

## 🚀 Passo a Passo de Execução

### 1. Criar o Banco de Dados e a Tabela

Abra o seu cliente MySQL (ex: MySQL Workbench) e execute o conteúdo do arquivo `ddl_operacoes_analytics.sql`:

```sql
CREATE DATABASE IF NOT EXISTS db_operacoes_analytics;
USE db_operacoes_analytics;

CREATE TABLE IF NOT EXISTS dim_produto (
    id_produto INT PRIMARY KEY,
    nome_produto VARCHAR(255) NOT NULL,
    categoria VARCHAR(100)
);
```

### 2. Abrir o Terminal na Pasta Correta

No VS Code ou terminal de sua preferência, garanta que você está dentro do diretório do projeto:

```powershell
cd "01 - excel-mysql-incremental-etl"
```

### 3. Configurar o Ambiente Virtual (`venv`)

Crie e ative um ambiente isolado para não poluir a instalação global do Python.

**No Windows (PowerShell):**

```powershell
# Libera a execução de scripts no PowerShell (caso ocorra erro de segurança)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente
.\venv\Scripts\activate
```

**No Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as Dependências

Com o ambiente (`venv`) ativo no terminal, execute:

```bash
pip install -r requirements.txt
```

As principais bibliotecas instaladas são:
- `pandas` e `openpyxl`: Manipulação e leitura de planilhas.
- `SQLAlchemy` e `PyMySQL`: Conectividade e ORM com o MySQL.
- `python-dotenv`: Leitura de credenciais a partir do arquivo `.env`.

### 5. Configurar as Credenciais do Banco (`.env`)

Crie uma cópia do arquivo `.env.example` e renomeie para `.env`:

**No Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**No Linux / macOS / Git Bash:**
```bash
cp .env.example .env
```

Abra o arquivo `.env` recém-criado e insira a sua senha do MySQL local na variável `DB_PASS`:

```ini
DB_USER=root
DB_PASS=sua_senha_aqui
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=db_operacoes_analytics
```

> **Nota:** O arquivo `.env` contendo a sua senha real e a pasta `venv/` estão configurados no `.gitignore` e não serão rastreados ou enviados ao GitHub.

### 6. Executar o Pipeline

Execute o script principal:

```bash
python etl_pipeline.py
```

Se tudo estiver correto, a saída no terminal indicará o progresso de cada etapa e a quantidade de novos registros inseridos.

---

## ❓ Resolução de Problemas Comuns

| Erro / Problema | Causa Provável | Solução |
| :--- | :--- | :--- |
| `[Errno 2] No such file or directory: 'etl_pipeline.py'` | O terminal está aberto na pasta errada. | Execute `cd` para navegar até a pasta exata do projeto antes de rodar o comando. |
| `UnauthorizedAccess` / `Activate.ps1 não pode ser carregado` | Políticas de execução do PowerShell bloqueiam scripts locais. | Execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes de ativar a `venv`. |
| `Access denied for user 'root'@'localhost'` | Senha incorreta ou ausência do arquivo `.env`. | Verifique se criou o arquivo `.env` a partir do `.env.example` e se a senha em `DB_PASS` está correta. |
| `Table 'db_operacoes_analytics.dim_produto' doesn't exist` | O script SQL de criação de tabela não foi executado. | Execute o arquivo `ddl_operacoes_analytics.sql` no MySQL Workbench antes de rodar o Python. |
