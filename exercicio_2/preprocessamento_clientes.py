import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 1. Extração e Diagnóstico
arquivo = Path(__file__).resolve().parent / "base_clientes_varejo.csv"
df = pd.read_csv(arquivo, sep=";", encoding="utf-8")

print("--- ETAPA 1: Diagnóstico Inicial ---")
print(f"Total de registros recebidos: {len(df)}")
print(f"Total de atributos (colunas): {df.shape[1]}")
print("\nTipos de dados:")
print(df.dtypes)
print("\nValores ausentes por coluna:")
print(df.isnull().sum())

# Duplicidades completas e por ID de cliente
duplicados_completos = df.duplicated().sum()
duplicados_cliente = df.duplicated(subset=['id_cliente']).sum()
print(f"\nDuplicados exatos (linha completa): {duplicados_completos}")
print(f"Registros repetidos por id_cliente: {duplicados_cliente}")

# 2. Limpeza
# Remove duplicidades completas e garante unacidade por id_cliente
limpo = df.drop_duplicates().copy()
if 'id_cliente' in limpo.columns:
    limpo = limpo.drop_duplicates(subset=['id_cliente'], keep='last').copy()

# Padronizar campos textuais (ex: cidade)
if 'cidade' in limpo.columns:
    limpo['cidade'] = limpo['cidade'].str.strip().str.title()

# Tratamento correto de valores ausentes em colunas numéricas (usando a mediana de cada coluna)
colunas_numericas_analise = ['idade', 'renda_mensal', 'ticket_medio']
for col in colunas_numericas_analise:
    if col in limpo.columns:
        limpo[col] = pd.to_numeric(limpo[col], errors='coerce')
        limpo[col] = limpo[col].fillna(limpo[col].median())

# Tratamento de ausentes para categoria_cliente
if 'categoria_cliente' in limpo.columns:
    limpo['categoria_cliente'] = limpo['categoria_cliente'].fillna('DESCONHECIDO')

# 3. Transformação (Padronização e Codificação)
scaler = StandardScaler()
dados_escala = limpo[colunas_numericas_analise].fillna(0)
matriz_padronizada = scaler.fit_transform(dados_escala)

# Codificação de variável categórica (categoria_cliente) utilizando One-Hot Encoding
if 'categoria_cliente' in limpo.columns:
    limpo['categoria_cliente'] = limpo['categoria_cliente'].str.strip().str.upper()
    limpo = pd.get_dummies(limpo, columns=['categoria_cliente'], prefix='cat', drop_first=False)

# 4. PCA (Análise de Componentes Principais)
pca = PCA(n_components=2)
componentes_pca = pca.fit_transform(matriz_padronizada)

# Adiciona os dois componentes principais ao DataFrame
limpo['componente_1'] = componentes_pca[:, 0]
limpo['componente_2'] = componentes_pca[:, 1]

print("\n--- ETAPA 4: PCA ---")
print(f"Variância explicada pelo Componente 1: {pca.explained_variance_ratio_[0]*100:.2f}%")
print(f"Variância explicada pelo Componente 2: {pca.explained_variance_ratio_[1]*100:.2f}%")
print(f"Variância acumulada: {sum(pca.explained_variance_ratio_)*100:.2f}%")

# 5. Carga (Armazenamento em SQLite)
conn = sqlite3.connect('varejo_clientes.db')
limpo.to_sql('clientes_preprocessados', conn, if_exists='replace', index=False)
conn.close()

print("\n--- ETAPA 5: Sucesso! Dados armazenados na tabela 'clientes_preprocessados' no SQLite. ---")