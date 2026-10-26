import os
import urllib.parse
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Carrega as variáveis do ficheiro .env local
load_dotenv()

# ==========================================
# CONFIGURAÇÕES DO BANCO DE DADOS (VIA ENV)
# ==========================================
DB_USER = os.getenv("DB_USER", "root")
DB_PASS_RAW = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "db_operacoes_analytics")

# Tratamento de caracteres especiais na senha
DB_PASS = urllib.parse.quote_plus(DB_PASS_RAW)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)


# ==========================================
# PIPELINE ETL
# ==========================================
def extrair_dados():
    print("1. Iniciando extração dos dados...")
    pasta_script = os.path.dirname(os.path.abspath(__file__))
    caminho_excel = os.path.join(pasta_script, "dados_brutos.xlsx")
    
    df = pd.read_excel(caminho_excel)
    return df


def transformar_dados(df):
    print("2. Aplicando regras de negócio e limpeza (Transform)...")
    df_limpo = df.dropna().copy()
    return df_limpo


def carregar_dados(df):
    print("3. Conectando ao Banco de Dados e carregando (Load)...")
    with engine.begin() as conn:
        # 1. Consulta quais IDs já estão salvos no MySQL
        df_existentes = pd.read_sql("SELECT id_produto FROM dim_produto", con=conn)
        ids_no_banco = df_existentes['id_produto'].tolist()
        
        # 2. Mantém no DataFrame apenas os IDs que NÃO estão no banco
        df_novos = df[~df['id_produto'].isin(ids_no_banco)].copy()
        
        # 3. Insere apenas os registros novos
        if not df_novos.empty:
            df_novos.to_sql(
                name="dim_produto",
                con=conn,
                if_exists="append",
                index=False
            )
            print(f"{len(df_novos)} novo(s) registro(s) inserido(s) com sucesso!")
        else:
            print("Nenhum dado novo para inserir.")


def executar_pipeline():
    try:
        df_bruto = extrair_dados()
        df_tratado = transformar_dados(df_bruto)
        carregar_dados(df_tratado)
    except Exception as e:
        print(f"\nErro na execução do pipeline: {e}")


if __name__ == "__main__":
    executar_pipeline()