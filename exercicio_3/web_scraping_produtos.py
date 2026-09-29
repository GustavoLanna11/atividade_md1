import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

# 1. Abrir o ficheiro HTML local fornecido
arquivo_html = Path(__file__).resolve().parent / "catalogo_produtos.html"

if not arquivo_html.exists():
    print(f"Erro: O ficheiro {arquivo_html.name} não foi encontrado na pasta do exercício 3.")
else:
    with open(arquivo_html, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 2. Identificar cartões de produto de forma flexível (procurando classes comuns)
    cartoes = soup.find_all(['div', 'article', 'section', 'li'], class_=lambda x: x and any(c in str(x).lower() for c in ['produto', 'card', 'item', 'product', 'catalogo']))
    
    # Se não encontrar por classe específica, pega todas as divs ou blocos estruturais
    if not cartoes:
        cartoes = soup.find_all(['div', 'article'])

    dados_produtos = []

    # 3. Extração genérica e segura dos atributos
    for cartao in cartoes:
        # Tenta extrair elementos procurando por texto ou atributos parciais nas classes
        id_prod = cartao.find(class_=lambda x: x and ('id' in str(x).lower() or 'codigo' in str(x).lower()))
        nome = cartao.find(['h1', 'h2', 'h3', 'h4', 'strong', 'a'], class_=lambda x: x and ('nome' in str(x).lower() or 'title' in str(x).lower() or 'produto' in str(x).lower()))
        
        # Se não achou nome por classe, pega o primeiro cabeçalho disponível no cartão
        if not nome:
            nome = cartao.find(['h1', 'h2', 'h3', 'h4'])

        categoria = cartao.find(class_=lambda x: x and 'cat' in str(x).lower())
        preco = cartao.find(class_=lambda x: x and ('preco' in str(x).lower() or 'price' in str(x).lower() or 'valor' in str(x).lower()))
        estoque = cartao.find(class_=lambda x: x and 'estoque' in str(x).lower())
        avaliacao = cartao.find(class_=lambda x: x and ('avaliacao' in str(x).lower() or 'rating' in str(x).lower() or 'estrela' in str(x).lower()))

        # Só adiciona se encontrar algum indício de texto relevante
        if nome or preco:
            dados_produtos.append({
                'id_produto': id_prod.get_text(strip=True) if id_prod else None,
                'nome': nome.get_text(strip=True) if nome else None,
                'categoria': categoria.get_text(strip=True) if categoria else None,
                'preco_str': preco.get_text(strip=True) if preco else None,
                'estoque_str': estoque.get_text(strip=True) if estoque else None,
                'avaliacao_str': avaliacao.get_text(strip=True) if avaliacao else None
            })

    df = pd.DataFrame(dados_produtos)

    # Garantir que as colunas essenciais existam mesmo que vazias, evitando KeyErrors
    for col in ['id_produto', 'nome', 'categoria', 'preco_str', 'estoque_str', 'avaliacao_str']:
        if col not in df.columns:
            df[col] = None

    # 4 e 5. Limpeza e Conversão de Tipos
    if 'preco_str' in df.columns:
        df['preco'] = (
            df['preco_str']
            .astype(str)
            .str.replace('R$', '', regex=False)
            .str.replace('$', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .str.replace(r'[^0-9.]', '', regex=True)
            .str.strip()
        )
        df['preco'] = pd.to_numeric(df['preco'], errors='coerce')

    # Conversão de estoque
    if 'estoque_str' in df.columns:
        df['estoque'] = pd.to_numeric(
            df['estoque_str'].astype(str).str.replace(r'\D', '', regex=True), 
            errors='coerce'
        ).fillna(0).astype(int)

    # Conversão de avaliação
    if 'avaliacao_str' in df.columns:
        df['avaliacao'] = pd.to_numeric(
            df['avaliacao_str'].astype(str).str.replace(',', '.', regex=False).str.replace(r'[^0-9.]', '', regex=True), 
            errors='coerce'
        )

    # Limpar colunas temporárias de string
    df = df.drop(columns=['preco_str', 'estoque_str', 'avaliacao_str'], errors='ignore')

    # 7. Tratar campos ausentes
    df['nome'] = df['nome'].fillna('Produto Desconhecido')
    df['categoria'] = df['categoria'].fillna('Geral')
    if 'preco' in df.columns and not df['preco'].dropna().empty:
        df['preco'] = df['preco'].fillna(df['preco'].median())
    else:
        df['preco'] = 0.0

    # 8. Eliminar produtos duplicados
    df = df.drop_duplicates(subset=['nome'], keep='first').copy()

    # 9. Acrescentar coluna data_coleta
    df['data_coleta'] = datetime.now().strftime('%Y-%m-%d')

    print(f"Total de produtos raspados e limpos: {len(df)}")
    print(df.head(3))

    # 10. Armazenar em SQLite na tabela produtos_raspados
    conn = sqlite3.connect('catalogo_ecommerce.db')
    df.to_sql('produtos_raspados', conn, if_exists='replace', index=False)
    conn.close()

    print("\nSucesso! Dados salvos na tabela 'produtos_raspados' no SQLite.")