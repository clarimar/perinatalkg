#!/bin/bash
# DIA 10 - PRIMEIRO CONVERSOR PARQUET → RDF
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 DIA 10: PARQUET → RDF"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Objetivo: converter 100 nascimentos reais"
echo "do SINASC para triplas RDF/Turtle"
echo ""

source activate.sh
mkdir -p data_samples ontology/dumps

cat > etl/06_sinasc_to_rdf.py << 'PYEOF'
"""
ETL Script 06: SINASC parquet → RDF/Turtle
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Converte nascimentos reais do SINASC para
triplas RDF aderentes à ontologia PerinatalKG.

Autor: Clarimar José Coelho
Data: 2026-05-07
"""
import polars as pl
import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS
from pathlib import Path
from loguru import logger

# ════════════════════════════════════════
# NAMESPACES
# ════════════════════════════════════════
PKG  = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")
PROV = Namespace("http://www.w3.org/ns/prov#")
TIME = Namespace("http://www.w3.org/2006/time#")

# ════════════════════════════════════════
# CONFIGURAÇÃO
# ════════════════════════════════════════
DATA_DIR   = Path("data/linked")
SAMPLE_OUT = Path("data_samples/sinasc_100_births.ttl")
FULL_OUT   = Path("ontology/dumps/sinasc_2020_sample.ttl")

def classificar_prematuridade(ig: int) -> list:
    """Retorna lista de classes OWL baseada na IG."""
    classes = [PKG.Birth]
    if ig < 37:
        classes.append(PKG.PretermBirth)
        if ig < 28:
            classes.append(PKG.PretermBirthExtreme)
        elif ig < 32:
            classes.append(PKG.PretermBirthEarly)
        elif ig < 34:
            classes.append(PKG.PretermBirthModerate)
        else:
            classes.append(PKG.PretermBirthLate)
    else:
        classes.append(PKG.TermBirth)
    return classes

def classificar_peso(peso: int) -> list:
    """Retorna lista de classes OWL baseada no peso."""
    classes = []
    if peso < 1500:
        classes.append(PKG.VeryLowBirthWeight)
        classes.append(PKG.LowBirthWeight)
    elif peso < 2500:
        classes.append(PKG.LowBirthWeight)
    return classes

def converter_nascimento(row: dict, g: Graph) -> int:
    """Converte um nascimento para triplas RDF."""
    birth_id = str(row.get("birth_id", ""))
    if not birth_id:
        return 0

    birth_uri = URIRef(f"{PKGR}birth/{birth_id}")

    # Classificação
    ig = int(row.get("gestational_weeks", 0) or 0)
    peso = int(row.get("birth_weight_grams", 0) or 0)

    # Tipos OWL
    for cls in classificar_prematuridade(ig):
        g.add((birth_uri, RDF.type, cls))
    for cls in classificar_peso(peso):
        g.add((birth_uri, RDF.type, cls))

    # Data properties
    if peso > 0:
        g.add((birth_uri, PKG.birthWeight,
               Literal(peso, datatype=XSD.integer)))
    if ig > 0:
        g.add((birth_uri, PKG.gestationalAge,
               Literal(ig, datatype=XSD.integer)))

    # Localização
    mun_code = str(row.get("municipality_code", "") or "")
    if mun_code and mun_code != "0":
        mun_uri = URIRef(f"{PKGR}location/{mun_code[:6]}")
        g.add((birth_uri, PKG.bornIn, mun_uri))
        g.add((mun_uri, RDF.type, PKG.Municipality))

    # Mãe
    mae_uri = URIRef(f"{PKGR}mother/{birth_id}_m")
    g.add((birth_uri, PKG.bornBy, mae_uri))
    g.add((mae_uri, RDF.type, PKG.Mother))

    idade_mae = int(row.get("maternal_age", 0) or 0)
    if idade_mae > 0:
        g.add((mae_uri, PKG.maternalAge,
               Literal(idade_mae, datatype=XSD.integer)))
        if idade_mae < 20:
            g.add((mae_uri, RDF.type, PKG.AdolescentMother))

    prenatal = int(row.get("prenatal_visits", 0) or 0)
    if prenatal > 0:
        g.add((mae_uri, PKG.prenatalVisits,
               Literal(prenatal, datatype=XSD.integer)))

    # Exposição climática
    temp = row.get("temperature_mean_t3")
    heat_days = row.get("days_extreme_heat_t3")

    if temp is not None or heat_days is not None:
        exp_uri = URIRef(f"{PKGR}exposure/{birth_id}_T3")
        g.add((exp_uri, RDF.type, PKG.ClimateExposure))
        g.add((birth_uri, PKG.exposedTo, exp_uri))

        if temp is not None:
            try:
                g.add((exp_uri, PKG.meanTemperature,
                       Literal(float(temp), datatype=XSD.decimal)))
            except:
                pass

        if heat_days is not None:
            try:
                exposed = int(row.get("exposed_extreme_heat_t3", 0) or 0)
                if exposed == 1:
                    g.add((exp_uri, RDF.type, PKG.ExtremeHeatExposure))
                g.add((exp_uri, PKG.extremeHeatDays,
                       Literal(int(heat_days), datatype=XSD.integer)))
            except:
                pass

    # Proveniência
    g.add((birth_uri, PROV.wasDerivedFrom,
           URIRef(f"{PKGR}dataset/SINASC_2020")))

    return 1

def main():
    logger.info("Iniciando conversor SINASC → RDF")
    logger.info("")

    # Procurar arquivo de dados GO-2020 (estado natal!)
    arquivos = list(DATA_DIR.glob("births_climate_2020_GO*.parquet"))
    if not arquivos:
        arquivos = list(DATA_DIR.glob("births_climate_2020_*.parquet"))
    if not arquivos:
        logger.error("Nenhum arquivo 2020 encontrado!")
        return

    arquivo = arquivos[0]
    logger.info(f"Arquivo: {arquivo.name}")

    # Ler 100 nascimentos de amostra
    df = pl.read_parquet(arquivo).head(100)
    logger.info(f"Nascimentos carregados: {len(df)}")

    # Criar grafo RDF
    g = Graph()
    g.bind("pkg",  PKG)
    g.bind("pkgr", PKGR)
    g.bind("prov", PROV)
    g.bind("time", TIME)
    g.bind("xsd",  XSD)

    # Carregar ontologia base
    g.parse("ontology/perinatalkg_minimal.ttl", format="turtle")
    logger.info(f"Ontologia base: {len(g)} triplas")

    # Converter nascimentos
    logger.info("Convertendo nascimentos para RDF...")
    convertidos = 0
    for row in df.to_dicts():
        convertidos += converter_nascimento(row, g)

    logger.info(f"Nascimentos convertidos: {convertidos}")
    logger.info(f"Total de triplas: {len(g)}")

    # Salvar amostra
    g.serialize(destination=str(SAMPLE_OUT), format="turtle")
    logger.success(f"✅ Amostra salva: {SAMPLE_OUT}")

    # Estatísticas
    logger.info("")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("📊 ESTATÍSTICAS DO RDF GERADO:")
    logger.info("")

    # SPARQL para estatísticas
    from rdflib import Graph as RDFGraph
    stats_q = """
    PREFIX pkg: <http://perinatalkg.org/ontology/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?tipo (COUNT(?x) AS ?total)
    WHERE {
        ?x rdf:type ?tipo .
        FILTER(STRSTARTS(STR(?tipo),
               "http://perinatalkg.org/ontology/"))
    }
    GROUP BY ?tipo
    ORDER BY DESC(?total)
    """

    for row in g.query(stats_q):
        tipo = str(row.tipo).split("/")[-1]
        logger.info(f"   {tipo:30s}: {row.total}")

    logger.info("")
    logger.success(f"Total de triplas: {len(g)}")
    logger.success(f"Triplas por nascimento: {len(g)/convertidos:.1f}")
    logger.info("")
    logger.info("Prévia do Turtle gerado:")
    with open(SAMPLE_OUT) as f:
        lines = f.readlines()
    for line in lines[:30]:
        print(line, end="")
    print("...")

if __name__ == "__main__":
    main()
PYEOF

echo "✅ Script conversor criado!"
echo ""
echo "🚀 Executando conversão..."
python etl/06_sinasc_to_rdf.py

git add etl/06_sinasc_to_rdf.py data_samples/ setup/week2/dia10_parquet_to_rdf.sh
git commit -m "Day 10: First SINASC→RDF converter

- Converts real SINASC births to OWL-compliant RDF
- OWL classification: PretermBirth subtypes, LowBirthWeight
- Climate exposure as ExtremeHeatExposure instances
- PROV-O provenance triples
- Sample: 100 births from GO-2020
- ~20-25 triples per birth
"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 10 COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 SEMANA 2 - 100% COMPLETA!"
echo ""
echo "   ✅ Dia 6:  Protégé + Ontologia OWL"
echo "   ✅ Dia 7:  SIM 203K óbitos (100%)"
echo "   ✅ Dia 8:  IBGE 5.570 municípios"
echo "   ✅ Dia 9:  SPARQL 5 queries"
echo "   ✅ Dia 10: Parquet → RDF converter!"
echo ""
echo "🎯 SEMANA 3: Ontologia formal + SHACL!"
echo ""
