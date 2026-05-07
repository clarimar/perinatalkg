#!/bin/bash
#
# DIA 7 - DOWNLOAD DADOS SIM
# Tempo estimado: 1-2 horas (download pesado)
#
# SIM = Sistema de Informação sobre Mortalidade
# Fonte: DATASUS via PySUS
# Filtro: apenas óbitos neonatais (<28 dias)

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 DIA 7: DOWNLOAD DADOS SIM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 O que vamos baixar:"
echo "   • SIM 2015-2024 (todos os estados)"
echo "   • Filtro: óbitos neonatais (<28 dias)"
echo "   • Esperado: ~300.000 registros"
echo "   • Formato saída: parquet"
echo ""

source activate.sh

echo "📦 Verificando dependências..."
python -c "import pysus" 2>/dev/null || pip install pysus -q
python -c "import pysus; print('✅ pysus OK')"

echo ""
echo "📁 Criando diretório de dados..."
mkdir -p data/raw/sim

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 Criando script de download..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > etl/03_sim_download.py << 'PYEOF'
"""
ETL Script 03: Download SIM 2015-2024 via PySUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sistema de Informação sobre Mortalidade (DATASUS)
Filtra automaticamente óbitos neonatais (<28 dias)

Autor: Clarimar José Coelho
Data: 2026-05-07
"""

import pandas as pd
from pathlib import Path
from loguru import logger
import time
import sys

# ════════════════════════════════════
# CONFIGURAÇÃO
# ════════════════════════════════════

OUTPUT_DIR = Path("data/raw/sim")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ESTADOS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

ANOS = list(range(2015, 2025))

COLUNAS_INTERESSE = [
    "NUMERODO", "TIPOBITO", "DTOBITO", "DTNASC", "IDADE",
    "SEXO", "CODMUNRES", "CODMUNOCOR",
    "PESO", "GESTACAO", "IDADEMAE", "ESCMAE",
    "CAUSABAS", "CAUSABAS_O", "LOCOCOR"
]

# ════════════════════════════════════
# FUNÇÕES
# ════════════════════════════════════

def baixar_sim(estado: str, ano: int, retry: int = 3) -> pd.DataFrame:
    """Baixa SIM de um estado/ano via PySUS."""
    for tentativa in range(retry):
        try:
            from pysus.online_data.SIM import download
            df = download(estado, ano)
            if df is not None and len(df) > 0:
                return df
            return pd.DataFrame()
        except Exception as e:
            logger.warning(f"  Tentativa {tentativa+1}/3 falhou: {e}")
            time.sleep(3 * (tentativa + 1))
    return pd.DataFrame()


def filtrar_neonatal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra óbitos neonatais (<28 dias).
    
    Codificação IDADE no SIM:
    - 1XX = horas (ex: 105 = 5 horas)
    - 2XX = dias  (ex: 215 = 15 dias)
    - 3XX = meses
    - 4XX = anos
    """
    if df.empty:
        return df

    # Apenas óbitos não-fetais
    if "TIPOBITO" in df.columns:
        df = df[df["TIPOBITO"].astype(str) == "2"].copy()

    if df.empty:
        return df

    # Calcular idade em dias
    df["IDADE_STR"] = df["IDADE"].astype(str).str.zfill(3)
    df["IDADE_UNIDADE"] = df["IDADE_STR"].str[0]
    df["IDADE_VALOR"] = pd.to_numeric(
        df["IDADE_STR"].str[1:], errors="coerce"
    )

    df["IDADE_DIAS"] = df.apply(
        lambda r: (
            r["IDADE_VALOR"] / 24 if r["IDADE_UNIDADE"] == "1"
            else r["IDADE_VALOR"] if r["IDADE_UNIDADE"] == "2"
            else r["IDADE_VALOR"] * 30 if r["IDADE_UNIDADE"] == "3"
            else r["IDADE_VALOR"] * 365 if r["IDADE_UNIDADE"] == "4"
            else None
        ), axis=1
    )

    # Classificar tipo de óbito neonatal
    df["NEONATAL_PRECOCE"] = df["IDADE_DIAS"] < 7
    df["NEONATAL_TARDIO"] = (
        (df["IDADE_DIAS"] >= 7) & (df["IDADE_DIAS"] < 28)
    )
    df["NEONATAL"] = df["IDADE_DIAS"] < 28

    return df[df["NEONATAL"] == True].copy()


def main():
    logger.info("🚀 Iniciando download SIM 2015-2024")
    logger.info(f"   Estados: {len(ESTADOS)}")
    logger.info(f"   Anos: {ANOS[0]}-{ANOS[-1]}")
    logger.info("")

    total_geral = 0
    falhas = []

    for ano in ANOS:
        logger.info(f"📅 Processando ano {ano}...")
        dfs_ano = []

        for estado in ESTADOS:
            logger.info(f"   ⬇️  {estado}-{ano}...")
            df = baixar_sim(estado, ano)

            if df.empty:
                falhas.append((estado, ano))
                logger.warning(f"   ❌ {estado}-{ano}: sem dados")
                continue

            # Selecionar colunas disponíveis
            cols = [c for c in COLUNAS_INTERESSE if c in df.columns]
            df = df[cols].copy()
            df["UF"] = estado
            df["ANO"] = ano

            # Filtrar neonatais
            df_neonatal = filtrar_neonatal(df)

            if len(df_neonatal) > 0:
                dfs_ano.append(df_neonatal)
                logger.info(
                    f"   ✅ {estado}-{ano}: "
                    f"{len(df_neonatal):,} óbitos neonatais"
                )

        if dfs_ano:
            df_ano = pd.concat(dfs_ano, ignore_index=True)
            arquivo = OUTPUT_DIR / f"sim_neonatal_{ano}.parquet"
            df_ano.to_parquet(arquivo, index=False)
            total_geral += len(df_ano)
            logger.success(
                f"✅ Ano {ano}: {len(df_ano):,} óbitos neonatais "
                f"→ {arquivo.name}"
            )

    # Relatório final
    logger.info("")
    logger.success(f"🎉 DOWNLOAD COMPLETO!")
    logger.success(f"   Total: {total_geral:,} óbitos neonatais")
    logger.success(f"   Arquivos: data/raw/sim/")

    if falhas:
        logger.warning(f"   Falhas: {len(falhas)} combinações UF-ano")
        falhas_file = OUTPUT_DIR / "falhas_download.txt"
        with open(falhas_file, "w") as f:
            for uf, ano in falhas:
                f.write(f"{uf},{ano}\n")
        logger.warning(f"   Log de falhas: {falhas_file}")

    # Verificação final
    arquivos = list(OUTPUT_DIR.glob("sim_neonatal_*.parquet"))
    logger.info(f"   Arquivos gerados: {len(arquivos)}")
    for arq in sorted(arquivos):
        df = pd.read_parquet(arq)
        logger.info(f"   📄 {arq.name}: {len(df):,} registros")


if __name__ == "__main__":
    main()
PYEOF

echo "✅ Script ETL criado: etl/03_sim_download.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  ANTES DE EXECUTAR:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "O download vai demorar 1-2 horas!"
echo "Recomendações:"
echo "  • Conecte no cabo (não WiFi)"
echo "  • Não desligue o computador"
echo "  • Pode deixar rodando em segundo plano"
echo ""
echo "Deseja iniciar o download AGORA? (y/n)"
read -p "> " start

if [ "$start" = "y" ]; then
    echo ""
    echo "🚀 Iniciando download SIM..."
    echo "   Acompanhe o progresso abaixo:"
    echo ""
    python etl/03_sim_download.py
else
    echo ""
    echo "✅ Script salvo!"
    echo "   Execute quando quiser:"
    echo "   python etl/03_sim_download.py"
fi

# Commitar script
git add etl/03_sim_download.py
git commit -m "Day 7: Add SIM download script (etl/03_sim_download.py)

- Downloads neonatal deaths 2015-2024 via PySUS
- Filters: non-fetal deaths < 28 days of life
- Classifies: early neonatal (0-6d) and late (7-27d)
- Output: data/raw/sim/sim_neonatal_YYYY.parquet
- Expected: ~300K neonatal deaths
"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 7 CONFIGURADO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Status:"
echo "   ✅ Script ETL criado e commitado"
echo "   ✅ Diretório data/raw/sim/ criado"
echo ""
echo "🎯 PRÓXIMO: DIA 8 (IBGE) enquanto SIM baixa!"
echo ""
