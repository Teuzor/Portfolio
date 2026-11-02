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
