import boto3
import pandas as pd
import io
from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client('s3')
response = s3.get_object(
    Bucket=os.getenv('AWS_BUCKET_NAME'),
    Key='Churn Modeling.csv'
)
dados = pd.read_csv(io.BytesIO(response['Body'].read()))

# Informações das cinco primeiras linhas
print("====== Informações Iniciais ======")
print(dados.head(10))

# Informações sobre os tipos de cada coluna
print("\n====== Informações Gerais ======")
print(dados.info())

# Informações estatísticas
print("\n====== Estatística ======")
print(dados.describe())

# Informações sobre sobrenomes incorretos
sobrenomes = dados[dados['Surname'].str.contains('\?', regex=True)]
print(f"\n{sobrenomes}")

# Valores nulos
print("\n====== Valores Nulos ======")
print(dados.isnull().sum())

# Valores únicos por coluna categórica
print("\n====== Valores Únicos ======")
print(dados['Geography'].value_counts())
print(dados['Gender'].value_counts())

# Distribuição do churn
print("\n====== Distribuição de Churn ======")
print(dados['Exited'].value_counts())
print(dados['Exited'].value_counts(normalize=True).mul(100).round(2))

# Clientes com saldo zero
print("\n====== Clientes com Saldo Zero ======")
saldo_zero = dados[dados['Balance'] == 0]
print(f"Total: {len(saldo_zero)} clientes")

# Faixa etária
print("\n====== Faixa Etária ======")
print(f"Idade mínima: {dados['Age'].min()}")
print(f"Idade máxima: {dados['Age'].max()}")
print(f"Idade média: {dados['Age'].mean():.1f}")