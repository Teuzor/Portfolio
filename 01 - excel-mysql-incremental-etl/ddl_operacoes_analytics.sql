-- Criação da base de dados se não existir
CREATE DATABASE IF NOT EXISTS defaultdb;
USE defaultdb;

-- Recriação da tabela dim_produto
CREATE TABLE IF NOT EXISTS dim_produto (
    id_produto INT PRIMARY KEY AUTO_INCREMENT,
    nome_produto VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    preco_producao DECIMAL(10,2),
    preco_venda DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS dim_loja (
	id_loja INT PRIMARY KEY AUTO_INCREMENT,
    nome_loja VARCHAR(100),
    tipo_loja VARCHAR(100),
    gerente_loja VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_cliente (
	id_cliente INT PRIMARY KEY AUTO_INCREMENT,
    cpf_cliente VARCHAR(14) NOT NULL UNIQUE,
    nome_cliente VARCHAR(100),
    cidade VARCHAR(100),
    estado VARCHAR(100),
    data_cadastro DATE
);

CREATE TABLE IF NOT EXISTS fato_vendas (
	id_venda INT PRIMARY KEY AUTO_INCREMENT,
    data_venda DATETIME,
    
    id_produto INT,
    id_cliente INT,
    
    quantidade INT,
    valor_unico DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    
    CONSTRAINT fk_vendas_produto FOREIGN KEY (id_produto) REFERENCES dim_produto(id_produto),
    CONSTRAINT fk_vendas_cliente FOREIGN KEY (id_cliente) REFERENCES dim_cliente(id_cliente)
);