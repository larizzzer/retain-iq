import boto3
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from tqdm import tqdm
import io
import os

# Carregamento das credenciais escritas no arquivo .env
load_dotenv()

# Configurações do S3
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
FILE_NAME = 'Churn Modeling.csv'

# Configurações do RDS
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')

# Extração — lendo CSV do S3
print('\n' + '=' * 40)
print('RETAINIQ — PIPELINE ETL')
print('=' * 40)

try:
    print('\nExtraindo arquivo do S3...')
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
    dados = pd.read_csv(io.BytesIO(response['Body'].read()))
    print(f'✔ {len(dados)} registros extraídos com sucesso!')

except Exception as e:
    print(f'✘ Erro ao extrair do S3: {e}')
    exit(1)

# Transformações
print('\nAplicando transformações...')

dados.columns = [col.lower() for col in dados.columns]
dados = dados.rename(columns={
    'rownumber': 'row_number',
    'customerid': 'customer_id',
    'creditscore': 'credit_score',
    'numofproducts': 'num_of_products',
    'hascrcard': 'has_cr_card',
    'isactivemember': 'is_active_member',
    'estimatedsalary': 'estimated_salary'
})

# Tranformação de dados boolean que estão como 0 e 1 para false e true
dados['has_cr_card'] = dados['has_cr_card'].astype(bool)
dados['is_active_member'] = dados['is_active_member'].astype(bool)
dados['exited'] = dados['exited'].astype(bool)

# Transformação de sobrenomes com caracter corrompido para null
dados['surname'] = dados['surname'].apply(lambda x: None if '?' in str(x) else x)

print('✔ Transformações aplicadas!')

# Carga — carregando no RDS
try:
    print('\nConectando ao RDS...')
    engine = create_engine(
        f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        connect_args={'sslmode': 'require'}
    )

    # Evitar duplicatas — trunca a tabela antes de inserir
    with engine.connect() as conn:
        conn.execute(text('TRUNCATE TABLE customers'))
        conn.commit()
    print('✔ Tabela limpa, sem duplicatas!')

    print('\nCarregando dados no RDS...')
    with tqdm(total=len(dados), desc='Progresso', unit=' registros') as barra:
        dados.to_sql('customers', engine, if_exists='append', index=False, chunksize=500)
        barra.update(len(dados))

    print(f'\n{"=" * 40}')
    print(f'✔ Concluído! {len(dados)} registros carregados.')
    print(f'{"=" * 40}\n')

except Exception as e:
    print(f'✘ Erro ao carregar no RDS: {e}')
    exit(1)