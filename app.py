import pandas as pd
import streamlit as st

st.set_page_config(page_title="Painel Inteligente de Cobrança", layout="wide")

@st.cache_data
def carregar_dados():
    return pd.read_csv("data/clientes_exemplo.csv")

def classificar_faixa(dias):
    if dias <= 15:
        return "Atraso leve"
    if dias <= 60:
        return "Atraso moderado"
    return "Atraso crítico"

def calcular_prioridade(row):
    score = 0

    if 5 <= row["dias_atraso"] <= 30:
        score += 3
    elif 31 <= row["dias_atraso"] <= 60:
        score += 2
    else:
        score += 1

    if row["valor_atraso"] >= 5000:
        score += 3
    elif row["valor_atraso"] >= 1500:
        score += 2
    else:
        score += 1

    if str(row["promessa_pagamento"]).strip().lower() == "sim":
        score += 2

    if row["status_cobranca"] in ["Sem resposta", "Escalar analise"]:
        score += 1

    if row["status_cobranca"] == "Negociando":
        score += 2

    if score >= 8:
        return "Alta"
    if score >= 5:
        return "Média"
    return "Baixa"

def sugerir_acao(row):
    prioridade = row["prioridade"]
    faixa = row["faixa_atraso"]
    status = row["status_cobranca"]

    if status == "Prometeu pagar":
        return "Acompanhar promessa e cobrar no vencimento"
    if status == "Negociando":
        return "Oferecer proposta de renegociação"
    if status == "Sem resposta":
        return "Trocar canal e tentar novo contato"
    if prioridade == "Alta" and faixa == "Atraso crítico":
        return "Escalar e abordar com urgência"
    if prioridade == "Alta":
        return "Ligar hoje"
    if prioridade == "Média":
        return "Enviar mensagem hoje"
    return "Acompanhar carteira"

def gerar_script(row):
    nome = row["nome"]
    produto = row["produto"]
    valor = f'R$ {row["valor_atraso"]:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    dias = int(row["dias_atraso"])
    acao = row["proxima_acao"]

    return (
        f"Olá, {nome}. Identificamos uma pendência relacionada ao produto {produto}, "
        f"com atraso de {dias} dias no valor de {valor}. "
        f"Estamos entrando em contato para buscar a melhor forma de regularização. "
        f"Sugestão de próxima ação: {acao}."
    )

df = carregar_dados()
df["faixa_atraso"] = df["dias_atraso"].apply(classificar_faixa)
df["prioridade"] = df.apply(calcular_prioridade, axis=1)
df["proxima_acao"] = df.apply(sugerir_acao, axis=1)
df["script_sugerido"] = df.apply(gerar_script, axis=1)

st.title("Painel Inteligente de Cobrança")
st.caption("MVP para priorização operacional de carteira inadimplente")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Clientes na carteira", len(df))
col2.metric("Valor total em atraso", f'R$ {df["valor_atraso"].sum():,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Prioridade alta", int((df["prioridade"] == "Alta").sum()))
col4.metric("Promessas ativas", int((df["promessa_pagamento"].astype(str).str.lower() == "sim").sum()))

st.subheader("Carteira priorizada")
filtro = st.selectbox("Filtrar prioridade", ["Todas", "Alta", "Média", "Baixa"])

df_view = df.copy()
if filtro != "Todas":
    df_view = df_view[df_view["prioridade"] == filtro]

df_view = df_view.sort_values(by=["prioridade", "dias_atraso"], ascending=[True, False])

st.dataframe(
    df_view[
        [
            "nome",
            "produto",
            "valor_atraso",
            "dias_atraso",
            "faixa_atraso",
            "status_cobranca",
            "prioridade",
            "proxima_acao",
        ]
    ],
    use_container_width=True,
)

st.subheader("Script sugerido por cliente")
cliente = st.selectbox("Selecione um cliente", df["nome"].tolist())
registro = df[df["nome"] == cliente].iloc[0]

st.text_area("Mensagem sugerida", registro["script_sugerido"], height=180)
