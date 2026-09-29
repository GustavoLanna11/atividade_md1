# Mineração de Dados - Lista de Exercícios (ISW-039)

Repositório estruturado para a entrega das atividades práticas da disciplina de Mineração de Dados. O objetivo desta lista é aplicar técnicas de análise exploratória, pré-processamento, redução de dimensionalidade (PCA), web scraping, consumo de API REST, armazenamento em SQLite e amostragem utilizando Python.

## 📁 Estrutura do Repositório

- **`exercicio_01/`**: Análise exploratória de uma base de vendas de e-commerce, tratamento de nulos/tipos, criação de atributos derivados, identificação de outliers e carga em SQLite (`vendas_analisadas`).
- **`exercicio_02/`**: Pipeline de ETL, limpeza, tratamento de duplicidades, padronização, normalização e aplicação de PCA (Análise de Componentes Principais) com Scikit-Learn, com salvamento em SQLite (`clientes_preprocessados`).
- **`exercicio_03/`**: Coleta e tratamento de dados de um catálogo de produtos HTML utilizando BeautifulSoup (Web Scraping), limpeza pós-coleta e persistência em SQLite (`produtos_raspados`).
- **`exercicio_04/`**: Consumo de API REST (ou arquivo JSON de contingência) e aplicação de técnicas de amostragem estatística (Aleatória Simples, Sistemática e Estratificada) sobre uma base de transações.

## 🛠️ Tecnologias Utilizadas

- **Python** (Versão 3.x)
- **Pandas** e **NumPy** para manipulação e análise de dados
- **Scikit-Learn** para pré-processamento e PCA
- **BeautifulSoup** para Web Scraping
- **Requests** para consumo de APIs
- **SQLite3** para banco de dados local e geração dos arquivos SQL de entrega
