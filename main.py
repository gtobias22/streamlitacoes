# importar as bibliotecas

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta

# Criar funções de carregamento de dados

@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(period="1d", start="2010-01-01", end="2024-07-01")
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    tickers = list(base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]
    return tickers

acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)


# Criar a interface do streamlit

st.write("""
# App Preço de Ações
O gráfico abaixo representa a evolução do preço de ações ao longo do anos.
""")  # Markdown

# Preparar as visualizações = FILTROS
st.sidebar.header("Filtros")

# Filtro de Ações
lista_acoes = st.sidebar.multiselect("Escolha as ações para visualizar",dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica:"Close"})

# Filtro de datas
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_data = st.sidebar.slider("Selecione o período", min_value=data_inicial, max_value=data_final, value=(data_inicial, data_final), step=timedelta(days=1))
dados = dados.loc[intervalo_data[0]:intervalo_data[1]]

# Criar o gráfico

st.line_chart(dados)

# Criar nossa performace

texto_performace_ativo = ""


if len(lista_acoes) ==0:
    lista_acoes = list(dados.columns)

elif len(lista_acoes) ==1:
    dados = dados.rename(columns={"Close":acao_unica})

carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)


for i, acao in enumerate(lista_acoes):
    performace_ativo = dados[acao].iloc[-1]/dados[acao].iloc[0] - 1
    performace_ativo = float(performace_ativo)

    carteira[i] = carteira[i] * (1 + performace_ativo)

    if performace_ativo > 0:
        # :cor[texto]
        texto_performace_ativo = texto_performace_ativo + f"  \n{acao}: :green[{performace_ativo:.1%}]"
    elif performace_ativo < 0:
        texto_performace_ativo = texto_performace_ativo + f"  \n{acao}: :red[{performace_ativo:.1%}]"
    else:
        texto_performace_ativo = texto_performace_ativo + f"  \n{acao}: {performace_ativo:.1%}"

total_final_carteira = sum(carteira)
performace_carteira = total_final_carteira / total_inicial_carteira -1

if performace_carteira > 0:
    # :cor[texto]
    texto_performace_carteira = f"Performace da carteira com todos os ativos: :green[{performace_carteira:.1%}]"
elif performace_ativo < 0:
    texto_performace_carteira = f"Performace da carteira com todos os ativos: :red[{performace_carteira:.1%}]"
else:
    texto_performace_carteira = f"Performace da carteira com todos os ativos: {performace_carteira:.1%}"

st.write(f"""
### Seção de performace dos ativos
Essa foi a performace de cada ativo no período selecionado:
         
{texto_performace_ativo}

{texto_performace_carteira}
         
""")  # Markdown


