import os
import urllib.parse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Localização explícita do arquivo .env na mesma pasta do script
pasta_script = Path(__file__).resolve().parent
caminho_env = pasta_script / ".env"
load_dotenv(dotenv_path=caminho_env)

# ==========================================
# CONFIGURAÇÕES DO BANCO DE DADOS (VIA ENV)
# ==========================================
DB_USER = os.getenv("DB_USER", "avnadmin")
DB_PASS_RAW = os.getenv("DB_PASSWORD") or os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "16814")
DB_NAME = os.getenv("DB_NAME", "defaultdb")

# Tratamento de caracteres especiais na senha
DB_PASS = urllib.parse.quote_plus(DB_PASS_RAW)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# O Aiven exige conexão criptografada via SSL
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {}}
)


# ==========================================
# GESTÃO DE DDL (ARQUIVO .SQL SEPARADO)
# ==========================================
def criar_tabelas_do_ddl():
    """Lê o arquivo ddl_operacoes_analytics.sql e executa a criação de todas as tabelas no MySQL."""
    caminho_ddl = pasta_script / "ddl_operacoes_analytics.sql"
    
    if not caminho_ddl.exists():
        print(f"⚠️  Aviso: Arquivo DDL não encontrado em {caminho_ddl}")
        return

    print("0. Executando DDL para criar/garantir todas as tabelas no banco...")
    conteudo_sql = caminho_ddl.read_text(encoding="utf-8")
    
    # Separa as instruções por ';' para rodar comando por comando com segurança
    comandos = [cmd.strip() for cmd in conteudo_sql.split(";") if cmd.strip()]
    
    with engine.begin() as conn:
        for comando in comandos:
            conn.execute(text(comando))
    print("✓ Estrutura de tabelas verificada e criada na nuvem!\n")


# ==========================================
# PIPELINE ETL
# ==========================================
def extrair_todas_abas(nome_arquivo="dados_brutos.xlsx"):
    """Lê o arquivo Excel inteiro e retorna um dicionário contendo DataFrames para cada aba."""
    print("1. Extraindo todas as abas do Excel...")
    caminho_excel = pasta_script / nome_arquivo
    dict_dfs = pd.read_excel(caminho_excel, sheet_name=None)
    print(f"   Abas encontradas na planilha: {list(dict_dfs.keys())}\n")
    return dict_dfs


def transformar_dados(df):
    """Aplica limpeza e remoção de registros nulos."""
    return df.dropna().copy()


def carregar_dimensao_generica(df, nome_tabela, chave_negocio):
    """
    Carrega tabelas dimensão de forma incremental usando uma coluna de negócio 
    (ex: 'nome_produto', 'cpf_cliente') em vez do ID gerado via AUTO_INCREMENT.
    """
    print(f"3. Processando carga incremental na dimensão [{nome_tabela}]...")
    with engine.begin() as conn:
        # Consulta as chaves de negócio já salvas no banco
        df_existentes = pd.read_sql(f"SELECT {chave_negocio} FROM {nome_tabela}", con=conn)
        valores_no_banco = df_existentes[chave_negocio].tolist()
        
        # Filtra apenas os registros novos da planilha
        if valores_no_banco:
            df_novos = df[~df[chave_negocio].isin(valores_no_banco)].copy()
        else:
            df_novos = df.copy()
        
        # Insere no MySQL deixando o AUTO_INCREMENT gerar a Primary Key
        if not df_novos.empty:
            df_novos.to_sql(
                name=nome_tabela,
                con=conn,
                if_exists="append",
                index=False
            )
            print(f"✓ Sucesso! {len(df_novos)} registro(s) novo(s) inserido(s) em [{nome_tabela}].\n")
        else:
            print(f"ℹ️  [{nome_tabela}]: Nenhum dado novo para inserir.\n")


def carregar_fato_vendas(df_fato):
    """
    Realiza o lookup ('De-Para') do nome_produto e cpf_cliente para buscar os IDs 
    gerados no banco e carrega os dados formatados na fato_vendas.
    """
    print("3. Processando de-para de chaves e carga na [fato_vendas]...")
    
    with engine.begin() as conn:
        # 1. Busca os mapeamentos de IDs salvos nas dimensões no banco
        df_produtos = pd.read_sql("SELECT id_produto, nome_produto FROM dim_produto", con=conn)
        df_clientes = pd.read_sql("SELECT id_cliente, cpf_cliente FROM dim_cliente", con=conn)
        
        # Convertendo colunas de junção para string tratada
        df_fato['nome_produto'] = df_fato['nome_produto'].astype(str).str.strip()
        df_produtos['nome_produto'] = df_produtos['nome_produto'].astype(str).str.strip()
        
        df_fato['cpf_cliente'] = df_fato['cpf_cliente'].astype(str).str.strip()
        df_clientes['cpf_cliente'] = df_clientes['cpf_cliente'].astype(str).str.strip()

        # 2. Faz o Merge (Lookup) para recuperar id_produto e id_cliente
        df_fato_processado = df_fato.merge(df_produtos, on="nome_produto", how="inner")
        df_fato_processado = df_fato_processado.merge(df_clientes, on="cpf_cliente", how="inner")
        
        # 3. Garante/Recalcula o valor_total se quantidade e valor_unitario existirem
        if "quantidade" in df_fato_processado.columns and "valor_unitario" in df_fato_processado.columns:
            df_fato_processado["valor_total"] = df_fato_processado["quantidade"] * df_fato_processado["valor_unitario"]

        # 4. Remove colunas de texto da planilha que não existem na tabela fato do SQL
        colunas_fato_sql = ["data_venda", "id_produto", "id_cliente", "quantidade", "valor_unitario", "valor_total"]
        
        # Seleciona apenas as colunas presentes na estrutura do banco
        colunas_finais = [col for col in colunas_fato_sql if col in df_fato_processado.columns]
        df_final = df_fato_processado[colunas_finais].copy()

        if not df_final.empty:
            df_final.to_sql(
                name="fato_vendas",
                con=conn,
                if_exists="append",
                index=False
            )
            print(f"✓ Sucesso! {len(df_final)} venda(s) registrada(s) na [fato_vendas].\n")
        else:
            print("⚠️ Nenhuma venda carregada: Verifique se os produtos e clientes da planilha estão cadastrados no banco.\n")


def executar_pipeline():
    try:
        # 0. Garante a estrutura do banco via DDL
        criar_tabelas_do_ddl()
        
        # 1. Extrai todas as abas
        dict_abas = extrair_todas_abas("dados_brutos.xlsx")
        
        # 2. Mapeamento das tabelas Dimensão e suas Chaves de Negócio
        mapeamento_dimensoes = {
            "dim_produto": "nome_produto",
            "dim_cliente": "cpf_cliente",
            "dim_loja": "nome_loja"
        }
        
        # PASSO A: Carrega todas as Dimensões PRIMEIRO
        for nome_aba, chave in mapeamento_dimensoes.items():
            if nome_aba in dict_abas:
                print(f"--- Processando Dimensão: '{nome_aba}' (Chave de Negócio: {chave}) ---")
                df_tratado = transformar_dados(dict_abas[nome_aba])
                carregar_dimensao_generica(df_tratado, nome_tabela=nome_aba, chave_negocio=chave)

        # PASSO B: Carrega a Tabela Fato
        if "fato_vendas" in dict_abas:
            print("--- Processando Tabela Fato: 'fato_vendas' ---")
            df_fato_tratado = transformar_dados(dict_abas["fato_vendas"])
            carregar_fato_vendas(df_fato_tratado)

        print("🚀 Pipeline executado com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro na execução do pipeline: {e}")


if __name__ == "__main__":
    executar_pipeline()