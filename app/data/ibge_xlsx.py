import pandas as pd
from pathlib import Path

UF2CODE = {
    "Rondônia":"11","Acre":"12","Amazonas":"13","Roraima":"14","Pará":"15","Amapá":"16","Tocantins":"17",
    "Maranhão":"21","Piauí":"22","Ceará":"23","Rio Grande do Norte":"24","Paraíba":"25","Pernambuco":"26",
    "Alagoas":"27","Sergipe":"28","Bahia":"29","Minas Gerais":"31","Espírito Santo":"32","Rio de Janeiro":"33",
    "São Paulo":"35","Paraná":"41","Santa Catarina":"42","Rio Grande do Sul":"43","Mato Grosso do Sul":"50",
    "Mato Grosso":"51","Goiás":"52","Distrito Federal":"53",
    "Brasil":"0","Norte":"1","Nordeste":"2","Sudeste":"3","Sul":"4","Centro-Oeste":"5"
}

def _find_header_and_firstrow(df_nohdr: pd.DataFrame):
    col0 = df_nohdr[0].astype(str).str.strip()
    first_data_idx = col0[col0.isin(UF2CODE.keys())].index.min()
    header_idx = col0.loc[:first_data_idx-1].replace("nan", pd.NA).last_valid_index()
    return int(header_idx), int(first_data_idx)

def read_ibge_uf_total_from_xlsx(
    xlsx_path: str | Path,
    sheet_name: str = "Tabela 1",
    col_label: str = "Total",
    year: int = 2022,
) -> pd.DataFrame:
    """
    Lê XLSX do IBGE (Censo 2022) e retorna: uf, geo_id, geo_level, year, value
    Acha automaticamente a linha de header correta e a coluna solicitada.
    """
    xlsx_path = Path(xlsx_path)

    # 1) descobrir linha candidata de header
    df0 = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None, dtype=str)
    header_idx, _ = _find_header_and_firstrow(df0)

    # 2) tentar header_idx, header_idx+1, +2, +3
    chosen_df = None
    chosen_col = None
    first_col_name = None
    last_cols_snapshot = None

    def norm_cols(cols):
        # normaliza: strip + colapsa espaços + lowercase
        return [" ".join(str(c).split()).strip() for c in cols]

    for h in [header_idx, header_idx + 1, header_idx + 2, header_idx + 3]:
        try:
            df_try = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=h, dtype=str)
        except Exception:
            continue

        cols_norm = norm_cols(df_try.columns)
        last_cols_snapshot = cols_norm[:]  # para mensagem de erro caso não encontre

        # procura a coluna pedida (case-insensitive / startswith)
        wanted = col_label.strip().lower()
        cand = None
        for c in cols_norm:
            if c.lower().startswith(wanted):
                cand = c
                break

        if cand:
            chosen_df = df_try
            chosen_df.columns = cols_norm
            chosen_col = cand
            first_col_name = chosen_df.columns[0]
            break

    if chosen_df is None or chosen_col is None:
        raise ValueError(
            f"Coluna '{col_label}' não encontrada no sheet '{sheet_name}'. "
            f"Tente ajustar o parâmetro 'column'. Exemplo de colunas lidas: {last_cols_snapshot}"
        )

    # 3) filtrar somente UFs (remove Brasil e Regiões)
    chosen_df[first_col_name] = chosen_df[first_col_name].astype(str).str.strip()
    chosen_df = chosen_df[chosen_df[first_col_name].isin(UF2CODE.keys())].copy()
    chosen_df = chosen_df[~chosen_df[first_col_name].isin(
        ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
    )]

    # 4) conversão numérica robusta (., , e %)
    def to_float(x: str | float | int | None):
        if pd.isna(x):
            return None
        s = str(x).strip().replace("%", "")
        # remove separador de milhar e troca vírgula por ponto
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None

    chosen_df["value"] = chosen_df[chosen_col].map(to_float)
    chosen_df["uf"] = chosen_df[first_col_name]
    chosen_df["geo_id"] = chosen_df["uf"].map(UF2CODE)
    chosen_df["geo_level"] = "uf"
    chosen_df["year"] = year

    out = chosen_df[["uf", "geo_id", "geo_level", "year", "value"]].dropna(subset=["value", "geo_id"])
    return out.reset_index(drop=True)
