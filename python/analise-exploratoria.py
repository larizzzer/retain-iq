import pandas as pd

dados = pd.read_csv('Churn Modeling.csv')

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