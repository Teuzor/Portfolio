-- Criação da base de dados se não existir
CREATE DATABASE IF NOT EXISTS db_operacoes_analytics;
USE db_operacoes_analytics;

-- Recriação da tabela dim_produto
CREATE TABLE IF NOT EXISTS dim_produto (
    id_produto INT PRIMARY KEY,
    nome_produto VARCHAR(255) NOT NULL,
    categoria VARCHAR(100)
);