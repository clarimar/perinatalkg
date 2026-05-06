"""
ETL Script 03: Download SIM 2015-2024 via PySUS 2.0
"""

import pandas as pd
import pysus
from pathlib import Path
from loguru import logger
import time

OUTPUT_DIR = Path("data/raw/sim")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ESTADOS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

ANOS = list(range(2015, 2025))

def filtrar_neonatal(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if "TIPOBITO" in df.columns:
        df = df[df["TIPOBITO"].astype(str) == "2"].copy()
    if df.empty:
        return df
    df["IDADE_STR"] = df["IDADE"].astype(str).str.zfill(3)
    df["IDADE_UNIDADE"] = df["IDADE_STR"].str[0]
    df["IDADE_VALOR"] = pd.to_numeric(df["IDADE_STR"].str[1:], errors="coerce")
    df["IDADE_DIAS"] = df.apply(
        lambda r: (
            r["IDADE_VALOR"] / 24 if r["IDADE_UNIDADE"] == "1"
            else r["IDADE_VALOR"] if r["IDADE_UNIDADE"] == "2"
            else r["IDADE_VALOR"] * 30 if r["IDADE_UNIDADE"] == "3"
            else r["IDADE_VALOR"] * 365 if r["IDADE_UNIDADE"] == "4"
            else None
        ), axis=1
    )
    df["NEONATAL_PRECOCE"] = df["IDADE_DIAS"] < 7
    df["NEONATAL_TARDIO"] = (df["IDADE_DIAS"] >= 7) & (df["IDADE_DIAS"] < 28)
    df["NEONATAL"] = df["IDADE_DIAS"] < 28
    return df[df["NEONATAL"] == True].copy()

def baixar_sim(estado: str, ano: int, retry: int = 3) -> pd.DataFrame:
    for tentativa in range(retry):
        try:
            df = pysus.sim(state=estado, year=ano)
            if df is not None and len(df) > 0:
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.warning(f"  Tentativa {tentativa+1}/3 falhou: {e}")
            time.sleep(5 * (tentativa + 1))
    return pd.DataFrame()

def main():
    logger.info("Iniciando download SIM 2015-2024 (PySUS 2.0)")
    logger.info(f"Estados: {len(ESTADOS)} | Anos: {ANOS[0]}-{ANOS[-1]}")

    total_geral = 0
    falhas = []

    for ano in ANOS:
        logger.info(f"Processando ano {ano}...")
        dfs_ano = []

        for estado in ESTADOS:
            logger.info(f"  Baixando {estado}-{ano}...")
            df = baixar_sim(estado, ano)

            if df.empty:
                falhas.append((estado, ano))
                logger.warning(f"  ❌ {estado}-{ano}: sem dados")
                continue

            df["UF"] = estado
            df["ANO"] = ano
            df_neonatal = filtrar_neonatal(df)

            if len(df_neonatal) > 0:
                dfs_ano.append(df_neonatal)
                logger.info(f"  ✅ {estado}-{ano}: {len(df_neonatal):,} óbitos neonatais")
            else:
                logger.info(f"  ⚠️  {estado}-{ano}: 0 óbitos neonatais")

        if dfs_ano:
            df_ano = pd.concat(dfs_ano, ignore_index=True)
            arquivo = OUTPUT_DIR / f"sim_neonatal_{ano}.parquet"
            df_ano.to_parquet(arquivo, index=False)
            total_geral += len(df_ano)
            logger.success(f"Ano {ano}: {len(df_ano):,} óbitos → {arquivo.name}")

    logger.success(f"DOWNLOAD COMPLETO! Total: {total_geral:,} óbitos neonatais")

    if falhas:
        logger.warning(f"Falhas: {len(falhas)} combinações UF-ano")
        with open(OUTPUT_DIR / "falhas_download.txt", "w") as f:
            for uf, ano in falhas:
                f.write(f"{uf},{ano}\n")

    arquivos = list(OUTPUT_DIR.glob("sim_neonatal_*.parquet"))
    logger.info(f"Arquivos gerados: {len(arquivos)}")
    for arq in sorted(arquivos):
        df_check = pd.read_parquet(arq)
        logger.info(f"  {arq.name}: {len(df_check):,} registros")

if __name__ == "__main__":
    main()
