from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


RECEBIMENTOS_COLUNAS = [
    "recebimento_id",
    "contrato",
    "valor_pago",
    "data_pagamento",
    "origem_pagamento",
    "identificador_externo",
    "status_conciliacao",
    "observacao",
    "operador",
]


def carregar_recebimentos(csv_path: str) -> pd.DataFrame:
    caminho = Path(csv_path)
    if not caminho.exists() or caminho.stat().st_size == 0:
        return pd.DataFrame(columns=RECEBIMENTOS_COLUNAS)

    df = pd.read_csv(caminho)

    for coluna in RECEBIMENTOS_COLUNAS:
        if coluna not in df.columns:
            df[coluna] = ""

    df = df[RECEBIMENTOS_COLUNAS].copy()

    if "valor_pago" in df.columns:
        df["valor_pago"] = pd.to_numeric(df["valor_pago"], errors="coerce").fillna(0.0)

    for coluna in ["contrato", "data_pagamento", "origem_pagamento", "identificador_externo", "status_conciliacao", "observacao", "operador"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("").astype(str).str.strip()

    return df


def salvar_recebimentos_csv(registros: list[dict], csv_path: str) -> pd.DataFrame:
    if not registros:
        return carregar_recebimentos(csv_path)

    caminho = Path(csv_path)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    novos = pd.DataFrame(registros)

    for coluna in RECEBIMENTOS_COLUNAS:
        if coluna not in novos.columns:
            novos[coluna] = ""

    novos = novos[RECEBIMENTOS_COLUNAS].copy()
    novos["valor_pago"] = pd.to_numeric(novos["valor_pago"], errors="coerce").fillna(0.0)

    atual = carregar_recebimentos(csv_path)
    if atual.empty:
        combinado = novos.copy()
    else:
        combinado = pd.concat([novos, atual], ignore_index=True)
    combinado.to_csv(caminho, index=False)

    return combinado


def novo_recebimento(
    contrato: str,
    valor_pago: float,
    data_pagamento: str,
    origem_pagamento: str = "manual",
    identificador_externo: str = "",
    status_conciliacao: str = "Pendente",
    observacao: str = "",
    operador: str = "Sistema",
) -> dict:
    contrato_limpo = str(contrato).strip()
    data_limpa = str(data_pagamento).strip()
    origem_limpa = str(origem_pagamento).strip() or "manual"
    identificador_limpo = str(identificador_externo).strip()
    status_limpo = str(status_conciliacao).strip() or "Pendente"
    observacao_limpa = str(observacao).strip()
    operador_limpo = str(operador).strip() or "Sistema"
    valor = float(valor_pago or 0)

    recebimento_id = f"rec-{contrato_limpo}-{data_limpa}-{valor:.2f}"

    return {
        "recebimento_id": recebimento_id,
        "contrato": contrato_limpo,
        "valor_pago": valor,
        "data_pagamento": data_limpa,
        "origem_pagamento": origem_limpa,
        "identificador_externo": identificador_limpo,
        "status_conciliacao": status_limpo,
        "observacao": observacao_limpa,
        "operador": operador_limpo,
    }


def aplicar_conciliacao_automatica(
    df_clientes: pd.DataFrame,
    df_recebimentos: pd.DataFrame | None,
) -> pd.DataFrame:
    df = df_clientes.copy()

    if "contrato" not in df.columns:
        return df

    if "status_cobranca" not in df.columns:
        df["status_cobranca"] = ""

    if "observacoes" not in df.columns:
        df["observacoes"] = ""

    if "bloquear_cobranca" not in df.columns:
        df["bloquear_cobranca"] = False

    if "valor_pago_total" not in df.columns:
        df["valor_pago_total"] = 0.0

    if df_recebimentos is None or df_recebimentos.empty:
        df["bloquear_cobranca"] = df["bloquear_cobranca"].fillna(False).astype(bool)
        df["valor_pago_total"] = pd.to_numeric(df["valor_pago_total"], errors="coerce").fillna(0.0)
        return df

    recebimentos = df_recebimentos.copy()

    if "contrato" not in recebimentos.columns or "valor_pago" not in recebimentos.columns:
        df["bloquear_cobranca"] = df["bloquear_cobranca"].fillna(False).astype(bool)
        df["valor_pago_total"] = pd.to_numeric(df["valor_pago_total"], errors="coerce").fillna(0.0)
        return df

    recebimentos["contrato"] = recebimentos["contrato"].fillna("").astype(str).str.strip()
    recebimentos["valor_pago"] = pd.to_numeric(recebimentos["valor_pago"], errors="coerce").fillna(0.0)
    recebimentos_validos = recebimentos[recebimentos["contrato"] != ""].copy()

    if recebimentos_validos.empty:
        df["bloquear_cobranca"] = df["bloquear_cobranca"].fillna(False).astype(bool)
        df["valor_pago_total"] = pd.to_numeric(df["valor_pago_total"], errors="coerce").fillna(0.0)
        return df

    resumo = (
        recebimentos_validos.groupby("contrato", as_index=False)["valor_pago"]
        .sum()
        .rename(columns={"valor_pago": "valor_pago_total"})
    )

    df["contrato"] = df["contrato"].fillna("").astype(str).str.strip()
    df["valor_atraso"] = pd.to_numeric(df.get("valor_atraso", 0), errors="coerce").fillna(0.0)

    df = df.merge(resumo, on="contrato", how="left", suffixes=("", "_novo"))
    if "valor_pago_total_novo" in df.columns:
        df["valor_pago_total"] = pd.to_numeric(df["valor_pago_total_novo"], errors="coerce").fillna(
            pd.to_numeric(df["valor_pago_total"], errors="coerce").fillna(0.0)
        )
        df = df.drop(columns=["valor_pago_total_novo"])
    else:
        df["valor_pago_total"] = pd.to_numeric(df["valor_pago_total"], errors="coerce").fillna(0.0)

    pagamento_confirmado = df["valor_pago_total"] >= df["valor_atraso"]
    pagamento_parcial = (df["valor_pago_total"] > 0) & (df["valor_pago_total"] < df["valor_atraso"])

    df.loc[pagamento_parcial, "status_cobranca"] = "Pagamento parcial"
    df.loc[pagamento_confirmado, "status_cobranca"] = "Pagamento confirmado"
    df.loc[pagamento_confirmado, "bloquear_cobranca"] = True
    df.loc[~pagamento_confirmado, "bloquear_cobranca"] = df.loc[~pagamento_confirmado, "bloquear_cobranca"].fillna(False)

    def anexar_obs(obs_atual: object, texto: str) -> str:
        base = str(obs_atual).strip() if pd.notna(obs_atual) else ""
        if not texto:
            return base
        if texto in base:
            return base
        if base:
            return f"{base} | {texto}"
        return texto

    for idx in df.index[pagamento_parcial]:
        texto = f"Conciliação automática: pagamento parcial identificado (R$ {df.at[idx, 'valor_pago_total']:.2f})."
        df.at[idx, "observacoes"] = anexar_obs(df.at[idx, "observacoes"], texto)

    for idx in df.index[pagamento_confirmado]:
        texto = f"Conciliação automática: pagamento confirmado (R$ {df.at[idx, 'valor_pago_total']:.2f})."
        df.at[idx, "observacoes"] = anexar_obs(df.at[idx, "observacoes"], texto)

    df["bloquear_cobranca"] = df["bloquear_cobranca"].fillna(False).astype(bool)
    df["valor_pago_total"] = pd.to_numeric(df["valor_pago_total"], errors="coerce").fillna(0.0)

    return df
