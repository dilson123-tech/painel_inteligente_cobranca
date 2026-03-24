import pandas as pd
import streamlit as st

st.set_page_config(page_title="Painel Inteligente de Cobrança", layout="wide")

st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(180deg, #0d1b2a 0%, #0a1624 100%);
        border: 1px solid rgba(200, 169, 107, 0.18);
        border-radius: 16px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
        min-height: 108px;
    }
    .metric-label {
        font-size: 0.88rem;
        color: #9fb3c8;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f5f7fa;
        line-height: 1.1;
        white-space: nowrap;
    }
    .section-card {
        background: linear-gradient(180deg, #0b1726 0%, #091321 100%);
        border: 1px solid rgba(200, 169, 107, 0.14);
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f5f7fa;
        margin-bottom: 12px;
    }
    .insight-card {
        background: linear-gradient(180deg, #101f31 0%, #0b1726 100%);
        border-left: 4px solid #C8A96B;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        color: #f5f7fa;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
    }
    .hero-kicker {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(200, 169, 107, 0.12);
        border: 1px solid rgba(200, 169, 107, 0.28);
        color: #C8A96B;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 0.9rem;
        text-transform: uppercase;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f5f7fa;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #9fb3c8;
        font-size: 1rem;
        margin-bottom: 0.6rem;
    }
    .hero-description {
        color: #c8d4e0;
        font-size: 0.96rem;
        margin-bottom: 1.2rem;
        max-width: 980px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def carregar_dados():
    return pd.read_csv("data/clientes_exemplo.csv")

def moeda(valor):
    return f'R$ {valor:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")

def classificar_faixa(dias):
    if dias <= 15:
        return "Atraso leve"
    if dias <= 60:
        return "Atraso moderado"
    return "Atraso crítico"

def calcular_prioridade(row):
    score = 0
    dias = int(row["dias_atraso"])
    valor = float(row["valor_atraso"])
    status = str(row["status_cobranca"]).strip()
    promessa = str(row["promessa_pagamento"]).strip().lower()

    if dias >= 90:
        score += 4
    elif dias >= 61:
        score += 3
    elif dias >= 31:
        score += 2
    elif dias >= 5:
        score += 1

    if valor >= 10000:
        score += 4
    elif valor >= 5000:
        score += 3
    elif valor >= 1500:
        score += 2
    else:
        score += 1

    if promessa == "sim":
        score += 1

    if status == "Prometeu pagar":
        score += 2
    elif status == "Negociando":
        score += 3
    elif status == "Sem resposta":
        score += 2
    elif status == "Encaminhar para análise":
        score += 3
    elif status == "Sem contato":
        score += 1

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
        return "Encaminhar para análise com urgência"
    if prioridade == "Alta":
        return "Ligar hoje"
    if prioridade == "Média":
        return "Enviar mensagem hoje"
    return "Acompanhar carteira"

def gerar_script(row):
    nome = row["nome"]
    produto = row["produto"]
    valor = moeda(row["valor_atraso"])
    dias = int(row["dias_atraso"])
    acao = row["proxima_acao"]
    return (
        f"Olá, {nome}. Identificamos uma pendência relacionada ao produto {produto}, "
        f"com atraso de {dias} dias no valor de {valor}. "
        f"Estamos entrando em contato para buscar a melhor forma de regularização. "
        f"Sugestão de próxima ação: {acao}."
    )

def render_metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_insight(texto):
    st.markdown(f'<div class="insight-card">{texto}</div>', unsafe_allow_html=True)

df = carregar_dados()
df["faixa_atraso"] = df["dias_atraso"].apply(classificar_faixa)
df["prioridade"] = df.apply(calcular_prioridade, axis=1)
df["proxima_acao"] = df.apply(sugerir_acao, axis=1)
df["script_sugerido"] = df.apply(gerar_script, axis=1)

ordem_prioridade = {"Alta": 0, "Média": 1, "Baixa": 2}
df["ordem_prioridade"] = df["prioridade"].map(ordem_prioridade)

total_clientes = len(df)
total_atraso = df["valor_atraso"].sum()
ticket_medio = df["valor_atraso"].mean()
clientes_alta = int((df["prioridade"] == "Alta").sum())
promessas_ativas = int((df["promessa_pagamento"].astype(str).str.lower() == "sim").sum())
criticos = int((df["faixa_atraso"] == "Atraso crítico").sum())
perc_criticos = (criticos / total_clientes * 100) if total_clientes else 0

clientes_acao_hoje = int(df["proxima_acao"].isin([
    "Encaminhar para análise com urgência",
    "Ligar hoje",
    "Enviar mensagem hoje",
    "Trocar canal e tentar novo contato",
    "Oferecer proposta de renegociação",
]).sum())

casos_analise = int((df["status_cobranca"] == "Encaminhar para análise").sum())
valor_prioridade_alta = df.loc[df["prioridade"] == "Alta", "valor_atraso"].sum()
promessas_acompanhar = int((df["status_cobranca"] == "Prometeu pagar").sum())
perc_alta = (clientes_alta / total_clientes * 100) if total_clientes else 0
perc_acao_hoje = (clientes_acao_hoje / total_clientes * 100) if total_clientes else 0

valor_negociando = df.loc[df["status_cobranca"] == "Negociando", "valor_atraso"].sum()
valor_promessas = df.loc[df["status_cobranca"] == "Prometeu pagar", "valor_atraso"].sum()
valor_sem_resposta = df.loc[df["status_cobranca"] == "Sem resposta", "valor_atraso"].sum()
clientes_negociando = int((df["status_cobranca"] == "Negociando").sum())
clientes_sem_resposta = int((df["status_cobranca"] == "Sem resposta").sum())

st.markdown('<div class="hero-kicker">Recovery Intelligence Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Painel Inteligente de Cobrança</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Visão executiva para priorização operacional, recuperação e acompanhamento da carteira inadimplente</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-description">Solução orientada a dados para apoiar equipes de cobrança, priorizar carteiras críticas, aumentar produtividade operacional e dar visibilidade gerencial sobre promessas, negociação e recuperação.</div>',
    unsafe_allow_html=True,
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1: render_metric_card("Clientes", total_clientes)
with k2: render_metric_card("Carteira em atraso", moeda(total_atraso))
with k3: render_metric_card("Ticket médio", moeda(ticket_medio))
with k4: render_metric_card("Prioridade alta", clientes_alta)
with k5: render_metric_card("Promessas ativas", promessas_ativas)
with k6: render_metric_card("% carteira crítica", f"{perc_criticos:.1f}%")

st.subheader("Resumo executivo")
re1, re2 = st.columns([1.2, 1])

with re1:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">Leitura da carteira</div>
            <ul>
                <li>Total em atraso sob gestão: <strong>{moeda(total_atraso)}</strong></li>
                <li>Clientes em atraso crítico: <strong>{criticos}</strong></li>
                <li>Casos de alta prioridade: <strong>{clientes_alta}</strong></li>
                <li>Promessas ativas para acompanhamento: <strong>{promessas_ativas}</strong></li>
                <li>Ticket médio por cliente: <strong>{moeda(ticket_medio)}</strong></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with re2:
    render_insight(f"<strong>{perc_alta:.1f}% da carteira</strong> está concentrada em casos de prioridade alta.")
    render_insight(f"<strong>{moeda(valor_prioridade_alta)}</strong> está concentrado nos clientes que exigem ação prioritária.")
    render_insight(f"<strong>{perc_acao_hoje:.1f}% da base</strong> demanda atuação operacional imediata.")
    render_insight(f"Existem <strong>{casos_analise}</strong> caso(s) que já exigem encaminhamento para análise.")

st.subheader("Ações prioritárias do dia")
a1, a2, a3, a4 = st.columns(4)
with a1: render_metric_card("Clientes para atuar hoje", clientes_acao_hoje)
with a2: render_metric_card("Promessas para acompanhar", promessas_acompanhar)
with a3: render_metric_card("Casos para análise", casos_analise)
with a4: render_metric_card("Valor em alta prioridade", moeda(valor_prioridade_alta))

st.subheader("Oportunidades de recuperação")
o1, o2, o3 = st.columns(3)
with o1:
    render_insight(f"Há <strong>{clientes_negociando}</strong> cliente(s) em negociação, representando <strong>{moeda(valor_negociando)}</strong> em potencial de regularização.")
with o2:
    render_insight(f"As promessas ativas somam <strong>{moeda(valor_promessas)}</strong>, com alto potencial de conversão em curto prazo.")
with o3:
    render_insight(f"Os casos sem resposta concentram <strong>{moeda(valor_sem_resposta)}</strong> e pedem ajuste de canal ou abordagem.")

st.subheader("Carteira priorizada")
f1, f2, f3 = st.columns(3)
filtro_prioridade = f1.selectbox("Filtrar prioridade", ["Todas", "Alta", "Média", "Baixa"])
filtro_status = f2.selectbox("Filtrar status", ["Todos"] + sorted(df["status_cobranca"].dropna().unique().tolist()))
filtro_faixa = f3.selectbox("Filtrar faixa de atraso", ["Todas", "Atraso leve", "Atraso moderado", "Atraso crítico"])

df_view = df.copy()
if filtro_prioridade != "Todas":
    df_view = df_view[df_view["prioridade"] == filtro_prioridade]
if filtro_status != "Todos":
    df_view = df_view[df_view["status_cobranca"] == filtro_status]
if filtro_faixa != "Todas":
    df_view = df_view[df_view["faixa_atraso"] == filtro_faixa]

df_view = df_view.sort_values(by=["ordem_prioridade", "dias_atraso", "valor_atraso"], ascending=[True, False, False])

tabela = df_view[["nome", "produto", "valor_atraso", "dias_atraso", "faixa_atraso", "status_cobranca", "prioridade", "proxima_acao"]].copy()

st.dataframe(
    tabela.style
    .format({"valor_atraso": moeda})
    .map(lambda v: "background-color: #3b0d0d; color: #ffffff;" if v == "Alta" else ("background-color: #3b2f0d; color: #ffffff;" if v == "Média" else "background-color: #0f2e1c; color: #ffffff;"), subset=["prioridade"])
    .map(lambda v: "background-color: #4a0d0d; color: #ffffff;" if v == "Atraso crítico" else ("background-color: #4a320d; color: #ffffff;" if v == "Atraso moderado" else "background-color: #123524; color: #ffffff;"), subset=["faixa_atraso"]),
    use_container_width=True,
)

st.subheader("Top 5 clientes críticos")
top5 = df[df["prioridade"] == "Alta"].copy()
top5 = top5.sort_values(by=["ordem_prioridade", "dias_atraso", "valor_atraso"], ascending=[True, False, False]).head(5)

if top5.empty:
    st.info("Nenhum cliente em prioridade alta no momento.")
else:
    st.dataframe(
        top5[["nome", "produto", "valor_atraso", "dias_atraso", "status_cobranca", "proxima_acao"]].style.format({"valor_atraso": moeda}),
        use_container_width=True,
    )

st.subheader("Script sugerido por cliente")
cliente = st.selectbox("Selecione um cliente", df["nome"].tolist())
registro = df[df["nome"] == cliente].iloc[0]
st.text_area("Mensagem sugerida", registro["script_sugerido"], height=180)
