##### projeto 12


##########################################################
# PROJETO 12
# VALUE AT RISK (VaR) NOS COMBUSTIVEIS
#
# Autor: Junior
##########################################################

import streamlit as st
import pandas as pd
import numpy as np
import unicodedata

import plotly.graph_objects as go
import plotly.express as px

from scipy.stats import norm
from scipy.stats import t
from scipy.stats import skew
from scipy.stats import kurtosis


from datetime import datetime

##########################################################
# CONFIGURAÇÃO
##########################################################

st.set_page_config(
    page_title="Projeto 12 - Value at Risk on Fuels",
    page_icon="📉",
    layout="wide"
)

##########################################################
# TÍTULO
##########################################################

st.title("📉 Projeto 12")
st.subheader("Value at Risk (VaR) nos combustiveis")

st.markdown(
"""
Este aplicativo calcula o Value at Risk utilizando:

- VaR Histórico
- VaR Normal
- VaR Student-t
"""
)

st.divider()

##########################################################
# SIDEBAR
##########################################################

st.sidebar.header("Configurações")

produto = st.sidebar.text_input(
    "COMBUSTIVEL",
    "GASOLINA COMUM"
)

ESTADO = st.sidebar.text_input(
    "ESTADO",
    "SAO PAULO"
)


confianca = st.sidebar.selectbox(
    "Nível de confiança",
    [0.95,0.99]
)

capital = st.sidebar.number_input(
    "Capital Investido (R$)",
    value=100000.0,
    step=1000.0
)

#####################
### DOWNLOAD DOS  DADOS
################

@st.cache_data
def carregar_anp():

    url1 = "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/shlp/2001-2012/mensal-estados-2001-a-2012.xlsx"

    url2 = "https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/precos-revenda-e-de-distribuicao-combustiveis/shlp/mensal/mensal-estados-desde-jan2013.xlsx"

    df1 = pd.read_excel(url1, header=12)
    df2 = pd.read_excel(url2, header=16)

    df = pd.concat([df1, df2], ignore_index=True)

    mapeamento = {
    "PRECO MÉDIO REVENDA": "PREÇO MÉDIO REVENDA",
    "PRECO MÍNIMO REVENDA": "PREÇO MÍNIMO REVENDA",
    "PRECO MÁXIMO REVENDA": "PREÇO MÁXIMO REVENDA",
    "PRECO MÉDIO DISTRIBUIÇÃO": "PREÇO MÉDIO DISTRIBUIÇÃO",
    "PRECO MÍNIMO DISTRIBUIÇÃO": "PREÇO MÍNIMO DISTRIBUIÇÃO",
    "PRECO MÁXIMO DISTRIBUIÇÃO": "PREÇO MÁXIMO DISTRIBUIÇÃO",
    }

    for antiga, nova in mapeamento.items():
        if antiga in df.columns:
            df[nova] = df[nova].fillna(df[antiga])
            df.drop(columns=antiga, inplace=True)

    
    # PADRONIZA PRODUTO
    df["PRODUTO"] = (
        df["PRODUTO"]
        .astype(str)
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
        .str.upper()
        .str.strip()
    )
    

    df["MÊS"] = pd.to_datetime(df["MÊS"])

    return df

##########################################################
# CARREGA BASE COMPLETA
##########################################################

df_total = carregar_anp()

if df_total.empty:

    st.error("Não foi possível baixar os dados.")

    st.stop()


##########################################################
# FILTRO
##########################################################

df = (
    df_total[
        (df_total["PRODUTO"] == produto) &
        (df_total["ESTADO"] == ESTADO)
    ]
    .sort_values("MÊS")
    .copy()
)

# Retorno logarítmico
df["RETORNO"] = np.log(
    df["PREÇO MÉDIO REVENDA"] /
    df["PREÇO MÉDIO REVENDA"].shift(1)
)

df["RETORNO"] = df["RETORNO"].replace(
    [np.inf, -np.inf],
    np.nan
)

df.dropna(subset=["RETORNO"], inplace=True)


if df.empty:

    st.error("Nenhum dado encontrado.")

    st.stop()

##########################################################
# ESTATÍSTICAS
##########################################################

preco_atual = df["PREÇO MÉDIO REVENDA"].iloc[-1]

retorno_medio = df["RETORNO"].mean()

volatilidade = df["RETORNO"].std()

assimetria = skew(df["RETORNO"])

curtose = kurtosis(df["RETORNO"])

retorno_max = df["RETORNO"].max()

retorno_min = df["RETORNO"].min()

##########################################################
# ABAS
##########################################################

aba1,aba2,aba3,aba4 = st.tabs(

[
"Dashboard",
"Preço",
"Retornos",
"VaR"
]

)

##########################################################
# DASHBOARD
##########################################################

with aba1:

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Preço Atual",
        f"{preco_atual:,.2f}"
    )

    c2.metric(
        "Retorno Médio",
        f"{retorno_medio:.3%}"
    )

    c3.metric(
        "Volatilidade",
        f"{volatilidade:.3%}"
    )

    st.write("")

    c4,c5,c6 = st.columns(3)

    c4.metric(
        "Assimetria",
        f"{assimetria:.3f}"
    )

    c5.metric(
        "Curtose",
        f"{curtose:.3f}"
    )

    c6.metric(
        "Observações",
        len(df)
    )

##########################################################
# ABA PREÇO
##########################################################

with aba2:

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df["MÊS"],
            y=df["PREÇO MÉDIO REVENDA"],
            mode="lines",
            name="Preço"

        )

    )

    fig.update_layout(

        title="Preço do combustivel",

        xaxis_title="Data",

        yaxis_title="Preço",

        template="plotly_white"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

##########################################################
# ABA RETORNOS
##########################################################

with aba3:

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df["MÊS"],

            y=df["RETORNO"],

            mode="lines",

            name="Retorno"

        )

    )

    fig.update_layout(

        title="Retornos Logarítmicos",

        xaxis_title="Data",

        yaxis_title="Retorno",

        template="plotly_white"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Histograma")

    fig2 = px.histogram(

        df,

        x="RETORNO",

        nbins=60,

        marginal="box"

    )

    fig2.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

##########################################################
# ABA VAR
##########################################################

with aba4:

    st.header("Value at Risk (VaR)")

    retornos = df["RETORNO"]

    ######################################################
    # VaR Histórico
    ######################################################

    var_hist = np.quantile(
        retornos,
        1 - confianca
    )

    ######################################################
    # VaR Normal
    ######################################################

    media = retornos.mean()

    desvio = retornos.std()

    z = norm.ppf(
        1 - confianca
    )

    var_normal = media + z * desvio

    ######################################################
    # VaR Student-t
    ######################################################
    retornos = df["RETORNO"].dropna()

    # Remove infinito e valores inválidos
    retornos = retornos[np.isfinite(retornos)]


    graus_liberdade, loc, escala = t.fit(retornos)

    var_student = t.ppf(
        1 - confianca,
        graus_liberdade,
        loc=loc,
        scale=escala
    )

    ######################################################
    # VaR EM REAIS
    ######################################################

    perda_hist = abs(var_hist) * capital

    perda_normal = abs(var_normal) * capital

    perda_student = abs(var_student) * capital

    ######################################################
    # MÉTRICAS
    ######################################################

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "VaR Histórico",
        f"{var_hist:.2%}"
    )

    c2.metric(
        "VaR Normal",
        f"{var_normal:.2%}"
    )

    c3.metric(
        "VaR Student-t",
        f"{var_student:.2%}"
    )

    st.divider()

    ######################################################
    # TABELA
    ######################################################

    resultado = pd.DataFrame({

        "Método":[
            "Histórico",
            "Normal",
            "Student-t"
        ],

        "VaR":[
            var_hist,
            var_normal,
            var_student
        ],

        "Perda (R$)":[
            perda_hist,
            perda_normal,
            perda_student
        ]

    })

    resultado["VaR"] = resultado["VaR"].map(
        lambda x: f"{x:.2%}"
    )

    resultado["Perda (R$)"] = resultado["Perda (R$)"].map(
        lambda x: f"R$ {x:,.2f}"
    )

    st.subheader("Resultados")

    st.dataframe(
        resultado,
        use_container_width=True,
        hide_index=True
    )

    ######################################################
    # GRÁFICO DOS RETORNOS
    ######################################################

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=df["MÊS"],

            y=retornos,

            mode="lines",

            name="Retornos",

            line=dict(color="black")

        )

    )

    ######################################################

    fig.add_hline(

        y=var_hist,

        line_color="red",

        line_dash="dash",

        annotation_text="Histórico"

    )

    ######################################################

    fig.add_hline(

        y=var_normal,

        line_color="blue",

        line_dash="dash",

        annotation_text="Normal"

    )

    ######################################################

    fig.add_hline(

        y=var_student,

        line_color="green",

        line_dash="dash",

        annotation_text="Student"

    )

    ######################################################

    fig.update_layout(

        title="Comparação entre os modelos de VaR",

        xaxis_title="Data",

        yaxis_title="Retorno",

        template="plotly_white",

        height=600

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    ######################################################
    # HISTOGRAMA COM VAR
    ######################################################

    fig2 = go.Figure()

    fig2.add_trace(

        go.Histogram(

            x=retornos,

            nbinsx=60,

            name="Retornos",

            opacity=0.75

        )

    )

    ######################################################

    fig2.add_vline(

        x=var_hist,

        line_color="red",

        annotation_text="Hist"

    )

    ######################################################

    fig2.add_vline(

        x=var_normal,

        line_color="blue",

        annotation_text="Normal"

    )

    ######################################################

    fig2.add_vline(

        x=var_student,

        line_color="green",

        annotation_text="Student"

    )

    ######################################################

    fig2.update_layout(

        title="Distribuição dos Retornos",

        template="plotly_white",

        bargap=0.05,

        height=550

    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )
