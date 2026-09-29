import sqlite3
import pandas as pd
from pathlib import Path

# 1. Localizar e carregar a base de dados
arquivo = Path(__file__).resolve().parent / "base_vendas_ecommerce.csv"
df = pd.read_csv(arquivo, sep=";", encoding="utf-8")

print("--- 1. Cinco primeiras linhas ---")
print(df.head())

print("\n--- 2. Quantidade de registros, atributos e tipos de dados ---")
print(f"Total de registros (linhas): {df.shape[0]}")
print(f"Total de atributos (colunas): {df.shape[1]}")
print("\nTipos de dados originais:")
print(df.dtypes)

print("\n--- 3. Quantidade de valores ausentes por coluna ---")
print(df.isnull().sum())

# 4. Conversão correta de atributos numéricos interpretados de forma inadequada
colunas_monetarias = ['preco_unitario', 'desconto']
for col in colunas_monetarias:
    if col in df.columns and df[col].dtype == 'object':
        df[col] = df[col].astype(str).str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

# Garantir que quantidade seja inteira
if 'quantidade' in df.columns:
    df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')

print("\n--- 5. Estatísticas descritivas (Atributos Numéricos) ---")
# Calculando média, mediana, mínimo, máximo e desvio padrão
print(df.describe().T[['mean', '50%', 'min', 'max', 'std']].rename(columns={'50%': 'median'}))

# 6. Criar o atributo valor_bruto (quantidade x preco_unitario)
df['valor_bruto'] = df['quantidade'] * df['preco_unitario']

# 7. Criar o atributo valor_liquido (considerando o desconto)
df['valor_liquido'] = df['valor_bruto'] - df['desconto']

print("\n--- 8. Identificação de Outliers em valor_liquido ---")
# Critério estatístico utilizando a Amplitude Interquartil (IQR)
Q1 = df['valor_liquido'].quantile(0.25)
Q3 = df['valor_liquido'].quantile(0.75)
IQR = Q3 - Q1
limite_superior = Q3 + 1.5 * IQR
limite_inferior = Q1 - 1.5 * IQR

outliers = df[(df['valor_liquido'] > limite_superior) | (df['valor_liquido'] < limite_inferior)]
print(f"Critério adotado: Limite Superior IQR ({limite_superior:.2f}) e Inferior ({limite_inferior:.2f})")
print(f"Quantidade de transações consideradas outliers/muito afastadas: {len(outliers)}")

print("\n--- 9. Faturamento líquido total por região e por categoria ---")
faturamento_regiao = df.groupby('regiao')['valor_liquido'].sum().reset_index()
print("\nFaturamento por Região:")
print(faturamento_regiao)

faturamento_categoria = df.groupby('categoria')['valor_liquido'].sum().reset_index()
print("\nFaturamento por Categoria:")
print(faturamento_categoria)

# 10. Armazenar os dados resultantes em SQLite na tabela vendas_analisadas
# Cria um banco de dados local chamado 'ecommerce.db'
conn = sqlite3.connect('ecommerce.db')

df.to_sql('vendas_analisadas', conn, if_exists='replace', index=False)

conn.close()
print("\n--- 10. Sucesso! Dados armazenados na tabela 'vendas_analisadas' no SQLite. ---")