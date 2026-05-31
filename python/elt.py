import boto3
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
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
print('\nExtraindo arquivo do S3...')

s3 = boto3.client('s3')
response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
dados = pd.read_csv(io.BytesIO(response['Body'].read()))

# Load — carregando no RDS
print('\nCarregando no RDS...')

engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    connect_args={'sslmode': 'require'}
)

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

# Transformação de sobrenomes com caracter corrompido e carregamento de dados com sql
dados['surname'] = dados['surname'].apply(lambda x: None if '?' in str(x) else x)
dados.to_sql('customers', engine, if_exists='replace', index=False)

print(f'\nConcluído! {len(dados)} registros carregados.')