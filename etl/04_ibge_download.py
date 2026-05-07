"""
ETL Script 04: Download IBGE via API SIDRA
"""
import requests
import pandas as pd
from pathlib import Path
from loguru import logger

OUTPUT_DIR = Path("data/raw/ibge")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def consultar_sidra(tabela: int, variavel: str, periodo: str) -> pd.DataFrame:
    url = (
        f"https://servicodados.ibge.gov.br/api/v3/agregados/"
        f"{tabela}/periodos/{periodo}/variaveis/{variavel}"
        f"?localidades=N6[all]"
    )
    logger.info(f"Consultando tabela {tabela}...")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    data = response.json()

    registros = []
    for var_data in data:
        for resultado in var_data.get("resultados", []):
            for serie in resultado.get("series", []):
                loc = serie["localidade"]
                for per, val in serie["serie"].items():
                    registros.append({
                        "codigo_municipio": loc["id"],
                        "nome_municipio": loc["nome"],
                        "periodo": per,
                        "valor": val,
                        "variavel": var_data.get("variavel", ""),
                        "unidade": var_data.get("unidade", ""),
                    })
    return pd.DataFrame(registros)

def baixar_idhm() -> pd.DataFrame:
    """IDH-M via Atlas Brasil"""
    url = "http://www.atlasbrasil.org.br/acervo/atlas/view/pt/home_upgrade"
    urls_csv = [
        "https://raw.githubusercontent.com/tbrugz/ribge/master/data/idhm_municipios_2010.csv",
        "http://www.atlasbrasil.org.br/acervo/biblioteca/baseidhm/IDHM_BR_municipios.csv"
    ]
    for u in urls_csv:
        try:
            df = pd.read_csv(u, encoding="latin-1", sep=";")
            logger.success(f"IDH-M baixado: {len(df):,} municípios")
            return df
        except Exception as e:
            logger.warning(f"Falha em {u}: {e}")
    return pd.DataFrame()

def main():
    logger.info("Iniciando download IBGE")

    # 1. População 2022 (Censo - tabela 4709, variável 93)
    logger.info("1/3 - População municipal 2022...")
    try:
        df_pop = consultar_sidra(tabela=4709, variavel="93", periodo="2022")
        df_pop.to_parquet(OUTPUT_DIR / "populacao_municipios_2022.parquet", index=False)
        logger.success(f"  ✅ População: {len(df_pop):,} municípios")
    except Exception as e:
        logger.error(f"  ❌ Erro população: {e}")

    # 2. Renda per capita 2010 (tabela 3548, variável 1041)
    logger.info("2/3 - Renda per capita 2010...")
    try:
        df_renda = consultar_sidra(tabela=3548, variavel="1041", periodo="2010")
        df_renda.to_parquet(OUTPUT_DIR / "renda_municipios_2010.parquet", index=False)
        logger.success(f"  ✅ Renda: {len(df_renda):,} municípios")
    except Exception as e:
        logger.error(f"  ❌ Erro renda: {e}")

    # 3. IDH-M
    logger.info("3/3 - IDH-M...")
    df_idhm = baixar_idhm()
    if not df_idhm.empty:
        df_idhm.to_parquet(OUTPUT_DIR / "idhm_municipios.parquet", index=False)
        logger.success(f"  ✅ IDH-M: {len(df_idhm):,} municípios")
    else:
        logger.warning("  ⚠️  IDH-M não disponível via URL direta")
        logger.info("  💡 Alternativa: https://www.atlasbrasil.org.br/")

    # Relatório final
    logger.info("")
    logger.info("ARQUIVOS GERADOS:")
    total = 0
    for arq in sorted(OUTPUT_DIR.glob("*.parquet")):
        df = pd.read_parquet(arq)
        total += len(df)
        logger.info(f"  {arq.name}: {len(df):,} registros")
    logger.success("Download IBGE concluído!")

if __name__ == "__main__":
    main()
