import sqlite3
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from sklearn.model_selection import train_test_split

# Conexão com o banco SQLite local
conn = sqlite3.connect('api_amostragem.db')

# ==========================================
# PARTE A - API REST e JSONPlaceholder
# ==========================================
url = "https://jsonplaceholder.typicode.com/posts"

print("--- PARTE A: Consumindo API REST ---")
try:
    response = requests.get(url, timeout=5)
    # Verifica se o código de resposta HTTP é bem-sucedido (200)
    if response.status_code == 200:
        dados_api = response.json()
        df_posts = pd.DataFrame(dados_api)
        print("Dados obtidos com sucesso da API REST pública!")
    else:
        raise Exception(f"Erro HTTP: {response.status_code}")
except Exception as e:
    print(f"API indisponível ({e}). Carregando arquivo de contingência (backup)...")
    backup_path = Path(__file__).resolve().parent / "posts_api_backup.json"
    df_posts = pd.read_json(backup_path)

# Armazena os registros obtidos na tabela posts_api
df_posts.to_sql('posts_api', conn, if_exists='replace', index=False)


# ==========================================
# PARTE B - População para Amostragem
# ==========================================
print("\n--- PARTE B: Análise da População ---")
pop_path = Path(__file__).resolve().parent / "base_transacoes_amostragem.csv"
df_pop = pd.read_csv(pop_path, sep=";", encoding="utf-8")

print(f"Quantidade total de registros na população: {len(df_pop)}")
print("\nDistribuição percentual por Canal:")
print((df_pop['canal'].value_counts(normalize=True) * 100).round(2))

print("\nDistribuição percentual por Classe de Risco:")
print((df_pop['classe_risco'].value_counts(normalize=True) * 100).round(2))


# ==========================================
# PARTE C - Amostra Aleatória Simples (10%)
# ==========================================
# Seleciona 10% da população sem reposição com random_state fixo
amostra_aleatoria = df_pop.sample(frac=0.10, random_state=42)
amostra_aleatoria.to_sql('amostra_aleatoria', conn, if_exists='replace', index=False)


# ==========================================
# PARTE D - Amostra Sistemática
# ==========================================
tamanho_amostra_alvo = len(amostra_aleatoria)
passo = len(df_pop) // tamanho_amostra_alvo
# Sorteia um ponto de partida inicial aleatório dentro do intervalo do passo
inicio = np.random.randint(0, passo)
indices_sistematica = range(inicio, len(df_pop), passo)

amostra_sistematica = df_pop.iloc[list(indices_sistematica)]
amostra_sistematica.to_sql('amostra_sistematica', conn, if_exists='replace', index=False)


# ==========================================
# PARTE E - Amostra Estratificada
# ==========================================
# Utiliza 'classe_risco' como atributo de estratificação mantendo a mesma proporção
_, amostra_estratificada = train_test_split(
    df_pop,
    test_size=0.10,
    random_state=42,
    stratify=df_pop['classe_risco']
)
amostra_estratificada.to_sql('amostra_estratificada', conn, if_exists='replace', index=False)


# ==========================================
# PARTE F - Comparação e Conclusões
# ==========================================
print("\n--- PARTE F: Comparação das Amostras ---")
print(f"Tamanho - População: {len(df_pop)}")
print(f"Tamanho - Amostra Aleatória Simples: {len(amostra_aleatoria)}")
print(f"Tamanho - Amostra Sistemática: {len(amostra_sistematica)}")
print(f"Tamanho - Amostra Estratificada: {len(amostra_estratificada)}")

print("\nDistribuição da Classe de Risco (População vs Estratificada):")
print("População:\n", (df_pop['classe_risco'].value_counts(normalize=True) * 100).round(2))
print("Estratificada:\n", (amostra_estratificada['classe_risco'].value_counts(normalize=True) * 100).round(2))

# Fechamento do banco de dados
conn.close()
print("\nSucesso! Todas as tabelas do Exercício 4 foram salvas no SQLite.")

"""
COMPREENSÃO / COMENTÁRIO PARA A ATIVIDADE:
Qual técnica preservou melhor a composição da população?
R: A Amostra Estratificada preservou perfeitamente a proporção original da 'classe_risco' 
em relação à população, visto que foi parametrizada explicitamente para isso (stratify). 
A Amostra Aleatória Simples também costuma aproximar-se bem devido à lei dos grandes números, 
enquanto a Sistemática pode sofrer variações dependendo da ordenação original da base de dados.
"""