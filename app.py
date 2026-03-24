from pathlib import Path
import pandas as pd
import streamlit as st
from src.mailer import get_missing_smtp_vars, send_bulk_emails

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
    .block-container {
        padding-top: 0.9rem;
        padding-bottom: 2rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
        max-width: 1680px;
    }
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 0;
    }
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    footer {
        display: none !important;
    }
    h3 {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
        color: #f5f7fa !important;
        margin-top: 1.35rem !important;
        margin-bottom: 0.7rem !important;
        letter-spacing: -0.02em;
    }
    div[data-testid="stWidgetLabel"] p {
        color: #a8bdd2 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
    }
    div[data-baseweb="select"] > div {
        background: linear-gradient(180deg, #0f1f31 0%, #0b1726 100%) !important;
        border: 1px solid rgba(200, 169, 107, 0.18) !important;
        border-radius: 12px !important;
        min-height: 46px !important;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
    }
    div[data-baseweb="select"] span {
        color: #f5f7fa !important;
        font-weight: 600 !important;
    }
    .stTextArea textarea {
        background: linear-gradient(180deg, #0f1f31 0%, #0b1726 100%) !important;
        color: #f5f7fa !important;
        border: 1px solid rgba(200, 169, 107, 0.16) !important;
        border-radius: 14px !important;
        min-height: 130px !important;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.16);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(200, 169, 107, 0.14);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
        background: linear-gradient(180deg, #0b1726 0%, #091321 100%);
    }
    div[data-testid="stDataFrame"] [role="grid"] {
        background: transparent !important;
    }
    div[data-testid="stDataFrame"] [role="columnheader"] {
        background: rgba(255, 255, 255, 0.03) !important;
    }

    .stTextArea textarea {
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
        padding: 1rem 1.1rem !important;
    }

    .aging-card {
        background: linear-gradient(180deg, #101f31 0%, #0b1726 100%);
        border: 1px solid rgba(200, 169, 107, 0.16);
        border-radius: 16px;
        padding: 18px 18px 16px 18px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
        min-height: 118px;
    }
    .aging-title {
        color: #f5f7fa;
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 0.55rem;
    }
    .aging-meta {
        color: #9fb3c8;
        font-size: 0.88rem;
        margin-bottom: 0.22rem;
    }
    .aging-value {
        color: #f5f7fa;
        font-size: 1.35rem;
        font-weight: 800;
        margin-top: 0.5rem;
    }

    .pipeline-card {
        position: relative;
        background: linear-gradient(180deg, #101f31 0%, #0b1726 100%);
        border: 1px solid rgba(200, 169, 107, 0.16);
        border-radius: 16px;
        padding: 18px 16px 16px 16px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
        min-height: 118px;
        overflow: hidden;
    }
    .pipeline-chip {
        width: 44px;
        height: 4px;
        border-radius: 999px;
        margin-bottom: 0.8rem;
    }
    .pipeline-title {
        color: #f5f7fa;
        font-weight: 800;
        font-size: 0.96rem;
        line-height: 1.2;
        margin-bottom: 0.45rem;
    }
    .pipeline-meta {
        color: #9fb3c8;
        font-size: 0.86rem;
        margin-bottom: 0.2rem;
    }
    .pipeline-value {
        color: #f5f7fa;
        font-size: 1.2rem;
        font-weight: 800;
        margin-top: 0.55rem;
    }
    .pipeline-note {
        color: #b8c7d8;
        font-size: 0.92rem;
        margin-top: 0.45rem;
        margin-bottom: 0.2rem;
    }

    .product-note {
        color: #b8c7d8;
        font-size: 0.92rem;
        margin-top: 0.45rem;
        margin-bottom: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def carregar_dados(csv_path: str, csv_mtime_ns: int):
    return pd.read_csv(csv_path)

AUDITORIA_COLUNAS = [
    "data_hora",
    "cliente",
    "destinatario",
    "canal",
    "assunto",
    "status",
    "detalhe",
    "valor",
    "lote",
    "operador",
    "origem",
    "template_usado",
    "clientes_lote",
    "aptos_canal",
]

def carregar_auditoria(csv_path: str):
    caminho = Path(csv_path)
    if not caminho.exists() or caminho.stat().st_size == 0:
        return pd.DataFrame(columns=AUDITORIA_COLUNAS)

    historico = pd.read_csv(caminho)
    for coluna in AUDITORIA_COLUNAS:
        if coluna not in historico.columns:
            historico[coluna] = ""
    return historico[AUDITORIA_COLUNAS].copy()

def salvar_auditoria_csv(registros, csv_path: str):
    if not registros:
        return []

    caminho = Path(csv_path)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    novos = pd.DataFrame(registros)
    for coluna in AUDITORIA_COLUNAS:
        if coluna not in novos.columns:
            novos[coluna] = ""
    novos = novos[AUDITORIA_COLUNAS].copy()

    if caminho.exists() and caminho.stat().st_size > 0:
        historico = pd.read_csv(caminho)
        for coluna in AUDITORIA_COLUNAS:
            if coluna not in historico.columns:
                historico[coluna] = ""
        historico = historico[AUDITORIA_COLUNAS].copy()
        combinado = pd.concat([novos, historico], ignore_index=True)
    else:
        combinado = novos.copy()

    combinado = combinado[AUDITORIA_COLUNAS].head(5000)
    combinado.to_csv(caminho, index=False)
    return combinado.head(200).to_dict("records")

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

csv_path = "data/clientes_exemplo.csv"
csv_mtime_ns = Path(csv_path).stat().st_mtime_ns
df = carregar_dados(csv_path, csv_mtime_ns)

for coluna, valor_padrao in {
    "email": "",
    "telefone": "",
    "consentimento_contato": "Nao",
}.items():
    if coluna not in df.columns:
        df[coluna] = valor_padrao
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


aging_resumo = (
    df.groupby("faixa_atraso", as_index=False)
      .agg(clientes=("nome", "count"), valor=("valor_atraso", "sum"))
)
aging_ordem = ["Atraso crítico", "Atraso moderado", "Atraso leve"]
aging_resumo["faixa_atraso"] = pd.Categorical(
    aging_resumo["faixa_atraso"],
    categories=aging_ordem,
    ordered=True,
)
aging_resumo = aging_resumo.sort_values("faixa_atraso")


status_resumo = (
    df.groupby("status_cobranca", as_index=False)
      .agg(clientes=("nome", "count"), valor=("valor_atraso", "sum"))
)

status_map = {
    row["status_cobranca"]: {
        "clientes": int(row["clientes"]),
        "valor": float(row["valor"]),
    }
    for _, row in status_resumo.iterrows()
}

status_cards = [
    "Sem contato",
    "Sem resposta",
    "Negociando",
    "Prometeu pagar",
    "Encaminhar para análise",
]

status_palette = {
    "Sem contato": "#6b7280",
    "Sem resposta": "#c68a12",
    "Negociando": "#1d9b6c",
    "Prometeu pagar": "#2fbf71",
    "Encaminhar para análise": "#d14b4b",
}


produto_resumo = (
    df.groupby("produto", as_index=False)
      .agg(clientes=("nome", "count"), valor=("valor_atraso", "sum"))
      .sort_values("valor", ascending=False)
      .head(4)
)

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




st.subheader("Exposição por produto")
pr1, pr2, pr3, pr4 = st.columns(4)

for col, (_, row) in zip([pr1, pr2, pr3, pr4], produto_resumo.iterrows()):
    with col:
        st.markdown(
            f"""
            <div class="aging-card">
                <div class="aging-title">{row['produto']}</div>
                <div class="aging-meta">Clientes: <strong>{int(row['clientes'])}</strong></div>
                <div class="aging-meta">Participação: <strong>{(float(row['valor']) / float(df["valor_atraso"].sum()) * 100 if float(df["valor_atraso"].sum()) else 0):.1f}%</strong></div>
                <div class="aging-value">{moeda(float(row['valor']))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

produto_top = produto_resumo.iloc[0] if not produto_resumo.empty else None
if produto_top is not None:
    st.markdown(
        f"""
        <div class="product-note">
            Maior exposição atual em <strong>{produto_top['produto']}</strong>,
            concentrando <strong>{moeda(float(produto_top['valor']))}</strong> da carteira em atraso.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Pipeline operacional")
p1, p2, p3, p4, p5 = st.columns(5)

for col, status_nome in zip([p1, p2, p3, p4, p5], status_cards):
    item = status_map.get(status_nome, {"clientes": 0, "valor": 0.0})
    color = status_palette.get(status_nome, "#c8a96b")
    with col:
        st.markdown(
            f"""
            <div class="pipeline-card">
                <div class="pipeline-chip" style="background:{color};"></div>
                <div class="pipeline-title">{status_nome}</div>
                <div class="pipeline-meta">Clientes: <strong>{item['clientes']}</strong></div>
                <div class="pipeline-value">{moeda(float(item['valor']))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

maior_status = max(
    status_cards,
    key=lambda nome: status_map.get(nome, {"valor": 0.0})["valor"]
)
maior_item = status_map.get(maior_status, {"clientes": 0, "valor": 0.0})

st.markdown(
    f"""
    <div class="pipeline-note">
        Maior concentração operacional no momento: <strong>{maior_status}</strong> —
        <strong>{maior_item['clientes']}</strong> cliente(s), totalizando
        <strong>{moeda(float(maior_item['valor']))}</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Aging da carteira")
a1, a2, a3 = st.columns(3)

for col, (_, row) in zip([a1, a2, a3], aging_resumo.iterrows()):
    with col:
        st.markdown(
            f"""
            <div class="aging-card">
                <div class="aging-title">{row['faixa_atraso']}</div>
                <div class="aging-meta">Clientes: <strong>{int(row['clientes'])}</strong></div>
                <div class="aging-meta">Participação: <strong>{(int(row['clientes']) / total_clientes * 100 if total_clientes else 0):.1f}%</strong></div>
                <div class="aging-value">{moeda(float(row['valor']))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

auditoria_path = "data/auditoria_contatos.csv"

if "historico_contatos" not in st.session_state:
    st.session_state["historico_contatos"] = carregar_auditoria(auditoria_path).head(200).to_dict("records")

st.subheader("Ação operacional")
op1, op2 = st.columns([1.2, 0.8])

with op1:
    selecionados = st.multiselect(
        "Selecionar clientes para contato",
        df_view["nome"].tolist(),
    )
    canal_contato = st.selectbox(
        "Canal de contato",
        ["E-mail", "WhatsApp", "E-mail + WhatsApp"],
    )

    lote = df_view[df_view["nome"].isin(selecionados)].copy()
    qtd_lote = len(lote)
    valor_lote = float(lote["valor_atraso"].sum()) if not lote.empty else 0.0

    if not lote.empty:
        email_ok = lote["email"].fillna("").astype(str).str.strip().ne("")
        whatsapp_ok = lote["telefone"].fillna("").astype(str).str.strip().ne("")
        consent_ok = lote["consentimento_contato"].fillna("").astype(str).str.strip().str.lower().eq("sim")
    else:
        email_ok = pd.Series(dtype=bool)
        whatsapp_ok = pd.Series(dtype=bool)
        consent_ok = pd.Series(dtype=bool)

    qtd_email_ok = int(email_ok.sum()) if not lote.empty else 0
    qtd_whatsapp_ok = int(whatsapp_ok.sum()) if not lote.empty else 0
    qtd_consent_ok = int(consent_ok.sum()) if not lote.empty else 0
    qtd_aptos_email = int((email_ok & consent_ok).sum()) if not lote.empty else 0
    qtd_aptos_whatsapp = int((whatsapp_ok & consent_ok).sum()) if not lote.empty else 0

    if canal_contato == "E-mail":
        qtd_aptos_canal = qtd_aptos_email
    elif canal_contato == "WhatsApp":
        qtd_aptos_canal = qtd_aptos_whatsapp
    else:
        qtd_aptos_canal = qtd_aptos_email

    qtd_aptos_email_real = qtd_aptos_email

    if selecionados:
        registro = df[df["nome"] == selecionados[0]].iloc[0]
        mensagem_padrao = registro["script_sugerido"]
        st.caption(
            f"Lote atual: {qtd_lote} cliente(s) • {moeda(valor_lote)} em atraso • aptos ao canal: {qtd_aptos_canal}"
        )

        if qtd_aptos_canal < qtd_lote:
            st.warning("Nem todos os clientes selecionados estão aptos para o canal escolhido. Revise contato e consentimento antes do disparo real.")
        else:
            st.success("Lote apto para evolução do disparo real no canal selecionado.")

        mensagem_revisao = st.text_area(
            "Mensagem para revisão",
            mensagem_padrao,
            height=150,
            key="mensagem_operacional",
        )

        if "E-mail" in canal_contato:
            assunto_email = st.text_input(
                "Assunto do e-mail",
                value="Regularização de pendência financeira",
                key="assunto_email_operacional",
            )

            if qtd_lote > 1:
                st.caption("No envio real em lote, cada cliente recebe o script individual salvo na base. A mensagem revisada acima vale como referência operacional.")

            missing_smtp = get_missing_smtp_vars()
            if missing_smtp:
                st.warning("SMTP ainda não configurado para envio real: " + ", ".join(missing_smtp))
            else:
                st.success("SMTP pronto para envio real de e-mail.")

                if canal_contato == "E-mail + WhatsApp":
                    st.caption("Neste momento, o disparo real cobre apenas o canal de e-mail. O fluxo real de WhatsApp entra na próxima fase.")

                if st.button("Enviar e-mail real para lote apto", use_container_width=True, key="btn_email_real"):
                    lote_email = lote[(email_ok & consent_ok)].copy()

                    if lote_email.empty:
                        st.warning("Nenhum cliente apto para envio real de e-mail neste lote.")
                    else:
                        recipients = []
                        auditoria_base = []
                        timestamp_envio = pd.Timestamp.now()
                        lote_id = f"email-lote-{timestamp_envio.strftime('%Y%m%d%H%M%S')}"

                        for _, row in lote_email.iterrows():
                            body = mensagem_revisao if len(lote_email) == 1 else str(row.get("script_sugerido", "")).strip() or mensagem_revisao
                            recipients.append(
                                {
                                    "nome": str(row.get("nome", "")).strip(),
                                    "email": str(row.get("email", "")).strip(),
                                    "mensagem": body,
                                }
                            )
                            auditoria_base.append(
                                {
                                    "data_hora": timestamp_envio.strftime("%d/%m/%Y %H:%M:%S"),
                                    "cliente": str(row.get("nome", "")).strip(),
                                    "destinatario": str(row.get("email", "")).strip(),
                                    "canal": "E-mail real",
                                    "assunto": assunto_email,
                                    "status": "Pendente",
                                    "detalhe": "",
                                    "valor": float(row.get("valor_atraso", 0) or 0),
                                    "lote": lote_id,
                                    "operador": "Operador sessão",
                                    "origem": "Acao operacional",
                                    "template_usado": body,
                                    "clientes_lote": qtd_lote,
                                    "aptos_canal": qtd_aptos_email_real,
                                }
                            )

                        resultados = send_bulk_emails(
                            recipients=recipients,
                            subject=assunto_email,
                        )

                        auditoria_lote = []
                        for base, resultado in zip(auditoria_base, resultados):
                            registro = base.copy()
                            registro["status"] = "Enviado" if resultado.get("ok") else "Falhou"
                            registro["detalhe"] = (
                                "E-mail enviado com sucesso."
                                if resultado.get("ok")
                                else str(resultado.get("erro", "Erro desconhecido."))
                            )
                            auditoria_lote.append(registro)

                        enviados_ok = sum(1 for item in resultados if item.get("ok"))
                        falhas = len(resultados) - enviados_ok

                        st.session_state["historico_contatos"] = salvar_auditoria_csv(
                            auditoria_lote,
                            auditoria_path,
                        )

                        if enviados_ok:
                            st.success(f"Envio real concluído: {enviados_ok} e-mail(s) enviados com sucesso.")
                        if falhas:
                            erros = [str(item.get("erro", "Erro desconhecido.")) for item in resultados if not item.get("ok")]
                            st.error(f"{falhas} envio(s) falharam. Revise SMTP ou dados de contato do lote.")
                            if erros:
                                st.code("\n".join(erros[:3]))

        if st.button("Registrar disparo simulado", use_container_width=True):
            novo_registro = {
                "data_hora": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"),
                "cliente": f"Lote com {qtd_lote} cliente(s)",
                "destinatario": "-",
                "canal": canal_contato,
                "assunto": assunto_email if "E-mail" in canal_contato else "-",
                "status": "Simulado",
                "detalhe": "Disparo apenas registrado para auditoria operacional.",
                "valor": valor_lote,
                "lote": f"simulado-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}",
                "operador": "Operador sessão",
                "origem": "Acao operacional",
                "template_usado": mensagem_revisao,
                "clientes_lote": qtd_lote,
                "aptos_canal": qtd_aptos_canal,
            }
            st.session_state["historico_contatos"] = salvar_auditoria_csv(
                [novo_registro],
                auditoria_path,
            )
            st.success(f"Disparo simulado registrado para {qtd_lote} cliente(s) via {canal_contato}.")
    else:
        st.info("Selecione um ou mais clientes da carteira para iniciar a ação operacional.")

with op2:
    st.markdown("#### Resumo do lote")
    r1, r2 = st.columns(2)
    with r1:
        st.metric("Clientes selecionados", qtd_lote)
        st.metric("WhatsApp pronto", qtd_whatsapp_ok)
    with r2:
        st.metric("Valor do lote", moeda(valor_lote))
        st.metric("E-mail pronto", qtd_email_ok)

    st.caption(f"Consentimento OK: {qtd_consent_ok} • Aptos ao canal: {qtd_aptos_canal}")

    st.markdown("#### Auditoria de contatos")
    historico = pd.DataFrame(st.session_state["historico_contatos"])
    if historico.empty:
        st.caption("Nenhum disparo registrado nesta sessão.")
    else:
        colunas_auditoria = AUDITORIA_COLUNAS.copy()
        for coluna in colunas_auditoria:
            if coluna not in historico.columns:
                historico[coluna] = ""

        historico = historico[colunas_auditoria].copy()
        historico["valor"] = pd.to_numeric(historico["valor"], errors="coerce").fillna(0.0)
        historico["status"] = historico["status"].astype(str).fillna("")
        historico["canal"] = historico["canal"].astype(str).fillna("")

        total_registros = len(historico)
        total_enviados = int((historico["status"] == "Enviado").sum())
        total_falhas = int((historico["status"] == "Falhou").sum())
        total_simulados = int((historico["status"] == "Simulado").sum())
        taxa_sucesso = (total_enviados / (total_enviados + total_falhas) * 100) if (total_enviados + total_falhas) else 0.0
        valor_auditado = float(historico["valor"].sum())

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Registros auditados", total_registros)
            st.metric("Enviados", total_enviados)
        with c2:
            st.metric("Falhas", total_falhas)
            st.metric("Simulados", total_simulados)
        with c3:
            st.metric("Taxa de sucesso", f"{taxa_sucesso:.1f}%")
            st.metric("Valor auditado", moeda(valor_auditado))

        canais = historico["canal"].value_counts()
        if not canais.empty:
            resumo_canais = " • ".join(f"{canal}: {quantidade}" for canal, quantidade in canais.items())
            st.caption(f"Distribuição por canal: {resumo_canais}")

        status_opcoes = ["Todos"] + sorted([s for s in historico["status"].dropna().astype(str).unique().tolist() if s])
        canal_opcoes = ["Todos"] + sorted([c for c in historico["canal"].dropna().astype(str).unique().tolist() if c])
        lote_opcoes = ["Todos"] + sorted([l for l in historico["lote"].dropna().astype(str).unique().tolist() if l])

        f1, f2, f3 = st.columns(3)
        with f1:
            filtro_status = st.selectbox("Filtrar por status", status_opcoes, key="audit_filter_status")
        with f2:
            filtro_canal = st.selectbox("Filtrar por canal", canal_opcoes, key="audit_filter_canal")
        with f3:
            filtro_lote = st.selectbox("Filtrar por lote", lote_opcoes, key="audit_filter_lote")

        historico_filtrado = historico.copy()
        if filtro_status != "Todos":
            historico_filtrado = historico_filtrado[historico_filtrado["status"] == filtro_status]
        if filtro_canal != "Todos":
            historico_filtrado = historico_filtrado[historico_filtrado["canal"] == filtro_canal]
        if filtro_lote != "Todos":
            historico_filtrado = historico_filtrado[historico_filtrado["lote"] == filtro_lote]

        st.caption(f"Registros no recorte atual: {len(historico_filtrado)}")

        historico_export = historico_filtrado.copy()
        historico_export["valor"] = historico_export["valor"].fillna(0.0)

        historico_view = historico_filtrado.copy()
        historico_view["valor"] = historico_view["valor"].apply(moeda)

        st.download_button(
            "Exportar auditoria filtrada (CSV)",
            data=historico_export.to_csv(index=False).encode("utf-8"),
            file_name="auditoria_contatos_filtrada.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_exportar_auditoria_csv",
        )

        st.dataframe(historico_view, use_container_width=True, hide_index=True)

with st.expander("Ver top 5 clientes críticos"):
    top5 = df[df["prioridade"] == "Alta"].copy()
    top5 = top5.sort_values(by=["ordem_prioridade", "dias_atraso", "valor_atraso"], ascending=[True, False, False]).head(5)

    if top5.empty:
        st.info("Nenhum cliente em prioridade alta no momento.")
    else:
        st.dataframe(
            top5[["nome", "produto", "valor_atraso", "dias_atraso", "status_cobranca", "proxima_acao"]].style.format({"valor_atraso": moeda}),
            use_container_width=True,
        )
