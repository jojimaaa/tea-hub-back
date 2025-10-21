# app/routers/data_routes.py

from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
import numpy as np
import pandas as pd
import tempfile
import io
import matplotlib.pyplot as plt

from app.database import SessionLocal
from app import models
from app.services.data_service import (
    get_or_create_source,
    get_or_create_indicator,
    upsert_observations,
)
from app.data.ibge_xlsx import read_ibge_uf_total_from_xlsx

router = APIRouter()


# ------------------------- DB SESSION -------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------- MOCK + CORRELAÇÃO -------------------------

@router.post("/mock/load", summary="Load Mock Data")
def load_mock_data(db: Session = Depends(get_db)):
    """
    Popula 2 indicadores sintéticos (MOCK_A e MOCK_B) por UF (ano=2022).
    """
    src = get_or_create_source(db, "MOCK", description="Dados sintéticos")
    indA = get_or_create_indicator(db, "MOCK_A", "Renda média (UF)", "R$", src)
    indB = get_or_create_indicator(db, "MOCK_B", "Taxa estimada TEA (UF)", "prop.", src)

    ufs = [f"{code}" for code in [11,12,13,14,15,16,17,21,22,23,24,25,26,27,28,29,31,32,33,35,41,42,43,50,51,52,53]]
    x = np.linspace(1500, 6000, len(ufs))
    rng = np.random.default_rng(42)
    y = 0.6 + 0.00015 * x + rng.normal(0, 0.05, len(ufs))

    rowsA = [dict(geo_id=uf, geo_level="uf", year=2022, value=float(v)) for uf, v in zip(ufs, x)]
    rowsB = [dict(geo_id=uf, geo_level="uf", year=2022, value=float(v)) for uf, v in zip(ufs, y)]

    nA = upsert_observations(db, indA.id, rowsA)
    nB = upsert_observations(db, indB.id, rowsB)
    return {"inserted_A": nA, "inserted_B": nB}


@router.get("/correlation", summary="Correlation")
def correlation(
    indA: str = Query(..., description="code do indicador A (ex.: MOCK_A)"),
    indB: str = Query(..., description="code do indicador B (ex.: MOCK_B)"),
    year: int = 2022,
    level: str = "uf",
    db: Session = Depends(get_db),
):
    A = db.execute(select(models.Indicator).where(models.Indicator.code == indA)).scalar_one_or_none()
    B = db.execute(select(models.Indicator).where(models.Indicator.code == indB)).scalar_one_or_none()
    if not A or not B:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")

    obsA = db.execute(select(models.Observation).where(
        models.Observation.indicator_id == A.id,
        models.Observation.year == year,
        models.Observation.geo_level == level,
    )).scalars().all()
    obsB = db.execute(select(models.Observation).where(
        models.Observation.indicator_id == B.id,
        models.Observation.year == year,
        models.Observation.geo_level == level,
    )).scalars().all()

    mapA = {o.geo_id: o.value for o in obsA}
    mapB = {o.geo_id: o.value for o in obsB}
    keys = sorted(set(mapA) & set(mapB))
    x = np.array([mapA[k] for k in keys], dtype=float)
    y = np.array([mapB[k] for k in keys], dtype=float)
    if len(x) < 3:
        raise HTTPException(status_code=400, detail=f"Dados insuficientes para correlação (n={len(x)})")
    r = float(np.corrcoef(x, y)[0, 1])

    return {
        "year": year,
        "level": level,
        "indicatorA": indA,
        "indicatorB": indB,
        "n": int(len(x)),
        "pearson_r": r,
        "pairs": [{"geo_id": k, "x": float(mapA[k]), "y": float(mapB[k])} for k in keys],
    }


# ------------------------- IBGE: INSPECT + IMPORT -------------------------

@router.get("/ibge/inspect", summary="Inspeciona XLSX (sheets e colunas)")
def ibge_inspect(
    path: str = Query(..., description="Caminho do XLSX (ex.: app/data/raw/arquivo.xlsx)"),
    sheet: str | None = Query(None, description="Opcional: sheet específico (ex.: 'Tabela 1')"),
):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {p}")

    xls = pd.ExcelFile(p)
    sheets = xls.sheet_names

    if sheet and sheet not in sheets:
        raise HTTPException(status_code=400, detail=f"Sheet '{sheet}' não encontrado. Sheets: {sheets}")

    out = {"file": str(p), "sheets": sheets}
    if sheet:
        df_try = pd.read_excel(p, sheet_name=sheet, header=0, nrows=3)
        cols = [str(c).strip() for c in df_try.columns]
        out["preview_columns_guess"] = cols
    return out


@router.post("/ibge/import-xlsx/by-path", summary="Importa XLSX do IBGE informando o caminho")
def import_ibge_by_path(
    path: str = Query(..., description="Caminho do XLSX (ex.: app/data/raw/arquivo.xlsx)"),
    sheet: str = "Tabela 1",
    column: str = "Total",
    year: int = 2022,
    indicator_code: str = "IBGE_CENSO_PCD_PERCENT_TOTAL",
    indicator_name: str = "Percentual de pessoas com deficiência (Total)",
    unit: str = "%",
    db: Session = Depends(get_db),
):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {p}")

    try:
        df = read_ibge_uf_total_from_xlsx(p, sheet_name=sheet, col_label=column.strip(), year=year)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler planilha: {e}")

    src = get_or_create_source(
        db, "IBGE Censo 2022",
        url="https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html",
        description="Tabelas do Censo 2022",
    )
    ind = get_or_create_indicator(db, indicator_code, indicator_name, unit, src)

    rows = [
        dict(geo_id=r.geo_id, geo_level=r.geo_level, year=int(r.year), value=float(r.value))
        for r in df.itertuples(index=False)
    ]
    inserted = upsert_observations(db, ind.id, rows)

    return {
        "file": str(p),
        "sheet": sheet,
        "column": column,
        "rows_read": int(len(df)),
        "rows_inserted_or_updated": int(inserted),
        "indicator_code": indicator_code,
    }


@router.post("/ibge/import-xlsx/upload", summary="Importa XLSX do IBGE via upload multipart")
async def import_ibge_upload(
    file: UploadFile = File(..., description="Envie um arquivo .xlsx"),
    sheet: str = "Tabela 1",
    column: str = "Total",
    year: int = 2022,
    indicator_code: str = "IBGE_CENSO_PCD_PERCENT_TOTAL",
    indicator_name: str = "Percentual de pessoas com deficiência (Total)",
    unit: str = "%",
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .xlsx")

    # salva temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        df = read_ibge_uf_total_from_xlsx(tmp_path, sheet_name=sheet, col_label=column.strip(), year=year)
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Erro ao ler planilha: {e}")

    src = get_or_create_source(
        db, "IBGE Censo 2022",
        url="https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html",
        description="Tabelas do Censo 2022",
    )
    ind = get_or_create_indicator(db, indicator_code, indicator_name, unit, src)

    rows = [
        dict(geo_id=r.geo_id, geo_level=r.geo_level, year=int(r.year), value=float(r.value))
        for r in df.itertuples(index=False)
    ]
    inserted = upsert_observations(db, ind.id, rows)

    tmp_path.unlink(missing_ok=True)

    return {
        "file": file.filename,
        "sheet": sheet,
        "column": column,
        "rows_read": int(len(df)),
        "rows_inserted_or_updated": int(inserted),
        "indicator_code": indicator_code,
    }


# ------------------------- PLOT: SCATTER PNG -------------------------

@router.get("/plot/scatter", summary="Gera gráfico scatter (PNG) de dois indicadores")
def plot_scatter(
    indA: str = Query(..., description="code do indicador A (ex.: IBGE_CENSO_PCD_PERCENT_TOTAL)"),
    indB: str = Query(..., description="code do indicador B (ex.: MOCK_A)"),
    year: int = 2022,
    level: str = "uf",
    xlabel: str | None = None,
    ylabel: str | None = None,
    db: Session = Depends(get_db),
):
    # indicadores
    A = db.execute(select(models.Indicator).where(models.Indicator.code == indA)).scalar_one_or_none()
    B = db.execute(select(models.Indicator).where(models.Indicator.code == indB)).scalar_one_or_none()
    if not A or not B:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")

    # observações
    obsA = db.execute(select(models.Observation).where(
        models.Observation.indicator_id == A.id,
        models.Observation.year == year,
        models.Observation.geo_level == level,
    )).scalars().all()
    obsB = db.execute(select(models.Observation).where(
        models.Observation.indicator_id == B.id,
        models.Observation.year == year,
        models.Observation.geo_level == level,
    )).scalars().all()

    mapA = {o.geo_id: o.value for o in obsA}
    mapB = {o.geo_id: o.value for o in obsB}
    keys = sorted(set(mapA) & set(mapB))
    if len(keys) < 3:
        raise HTTPException(status_code=400, detail=f"Dados insuficientes para plot (n={len(keys)})")

    x = np.array([mapA[k] for k in keys], dtype=float)
    y = np.array([mapB[k] for k in keys], dtype=float)
    r = float(np.corrcoef(x, y)[0, 1])

    # plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x, y)
    ax.grid(True, linestyle="--", linewidth=0.5)
    ax.set_xlabel(xlabel or A.name)
    ax.set_ylabel(ylabel or B.name)
    ax.set_title(f"{A.code} x {B.code} — year={year}, r={r:.3f}")

    # anotar geo_id
    for k, xi, yi in zip(keys, x, y):
        ax.annotate(k, (xi, yi), fontsize=7, xytext=(3, 3), textcoords="offset points")

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")
