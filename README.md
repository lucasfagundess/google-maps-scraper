# Google Maps Scraper - RPA Architecture 🤖

Este projeto é uma solução de RPA (Robotic Process Automation) modular desenvolvida em Python para a extração inteligente de leads do Google Maps. A arquitetura segue o padrão **Dispatcher-Performer**, garantindo resiliência e escalabilidade ao separar a busca de links da extração de dados detalhados.

## 🏗️ Estrutura do Projeto

* **main.py**: Orquestrador central e painel de controle da execução.
* **src/**: Motores lógicos do robô (Extração de links e Parsing de dados).
* **inputs/**: Pasta contendo o arquivo `buscas.xlsx` (critérios de busca).
* **outputs/**: Resultados da extração com versionamento por timestamp.
* **logs/**: Histórico detalhado de execução para auditoria e debug.

## 🚀 Como Executar

### 1. Pré-requisitos
* Python 3.8+ instalado.
* Google Chrome instalado.

### 2. Instalação de Dependências
Instale as bibliotecas necessárias utilizando o gerenciador de pacotes:
```
pip install -r requirements.txt
```

3. Configuração de Busca
Preencha o arquivo inputs/buscas.xlsx com as seguintes colunas:
Tipo, Bairro, Cidade, Estado.

4. Execução (Duas opções)
Opção A (Desenvolvedor):
Execute via terminal ou VS Code:

```
python main.py
```

Opção B (Usuário Final):
Basta dar um duplo clique no arquivo RODAR_EXTRATOR.bat na raiz do projeto. Ele abrirá um terminal automático, configurará o ambiente e iniciará a automação.

⚙️ Configurações (Painel de Controle)
No arquivo main.py, você pode ajustar o comportamento do robô:

HEADLESS_EXTRACTOR: True/False (Exibir ou ocultar o navegador na busca de links).

HEADLESS_PARSER: True/False (Exibir ou ocultar o navegador na extração de detalhes).

📊 Saídas e Logs
outputs/dados_extraidos_YYYYMMDD_HHMMSS.xlsx: Arquivo único por rodada.

outputs/dados_mais_recentes.xlsx: Cópia sempre atualizada da última execução.

logs/execucao_YYYYMMDD_HHMMSS.log: Relatório técnico de tudo o que aconteceu durante o processo.


Desenvolvido por Lucas Fagundes da Silva

