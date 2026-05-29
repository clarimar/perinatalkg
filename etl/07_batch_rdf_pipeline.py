"""
ETL Script 07: Pipeline Batch RDF - GO Completo
Converte todos os nascimentos de GO (2015-2024) para RDF
Estratégia: batch por ano, ~95K nascimentos por arquivo
"""
import polars as pl
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from pathlib import Path
from loguru import logger
import time

PKG  = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")
PROV = Namespace("http://www.w3.org/ns/prov#")

OUTPUT_DIR = Path("data/rdf/go")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def classificar_prematuridade(ig):
    if ig is None or ig == 0: return [PKG.Birth]
    classes = [PKG.Birth]
    if ig < 37:
        classes.append(PKG.PretermBirth)
        if ig < 28:   classes.append(PKG.PretermBirthExtreme)
        elif ig < 32: classes.append(PKG.PretermBirthEarly)
        elif ig < 34: classes.append(PKG.PretermBirthModerate)
        else:         classes.append(PKG.PretermBirthLate)
    else:
        if ig >= 42: classes.append(PKG.PostTermBirth)
        else: classes.append(PKG.TermBirth)
    return classes

def classificar_peso(peso):
    if peso is None or peso == 0: return []
    if peso < 1000:  return [PKG.ExtremeLowBirthWeight,
                              PKG.VeryLowBirthWeight,
                              PKG.LowBirthWeight]
    if peso < 1500:  return [PKG.VeryLowBirthWeight, PKG.LowBirthWeight]
    if peso < 2500:  return [PKG.LowBirthWeight]
    if peso > 4000:  return [PKG.MacrosomicBirth]
    return []

def converter_batch(df: pl.DataFrame, ano: int) -> Graph:
    g = Graph()
    g.bind("pkg", PKG); g.bind("pkgr", PKGR); g.bind("prov", PROV)

    for row in df.iter_rows(named=True):
        bid = row.get("birth_id", "")
        if not bid: continue

        birth_uri = URIRef(f"{PKGR}birth/{bid}")

        ig   = row.get("gestational_weeks")
        peso = row.get("birth_weight_grams")

        try: ig   = int(ig)   if ig   else None
        except: ig = None
        try: peso = int(peso) if peso else None
        except: peso = None

        # Tipos OWL
        for cls in classificar_prematuridade(ig):
            g.add((birth_uri, RDF.type, cls))
        for cls in classificar_peso(peso):
            g.add((birth_uri, RDF.type, cls))

        # Data properties
        if peso: g.add((birth_uri, PKG.birthWeight,
                        Literal(peso, datatype=XSD.integer)))
        if ig:   g.add((birth_uri, PKG.gestationalAge,
                        Literal(ig, datatype=XSD.integer)))

        # Idade materna
        idade_mae = row.get("maternal_age")
        try: idade_mae = int(idade_mae) if idade_mae else None
        except: idade_mae = None
        if idade_mae:
            mae_uri = URIRef(f"{PKGR}mother/{bid}_m")
            g.add((birth_uri, PKG.bornBy, mae_uri))
            g.add((mae_uri, RDF.type, PKG.Mother))
            g.add((mae_uri, PKG.maternalAge,
                   Literal(idade_mae, datatype=XSD.integer)))
            if idade_mae < 20:
                g.add((mae_uri, RDF.type, PKG.AdolescentMother))
            if idade_mae >= 35:
                g.add((mae_uri, RDF.type, PKG.ElderlyMother))

        # Municipio
        mun = row.get("municipality_id", "")
        if mun:
            mun_uri = URIRef(f"{PKGR}location/{str(mun)[:6]}")
            g.add((birth_uri, PKG.bornIn, mun_uri))
            g.add((mun_uri, RDF.type, PKG.Municipality))

        # Exposição climática T3
        temp  = row.get("temperature_mean_t3")
        dias  = row.get("days_extreme_heat_t3")
        expos = row.get("exposed_extreme_heat_t3")

        if temp is not None or dias is not None:
            exp_uri = URIRef(f"{PKGR}exposure/{bid}_T3")
            g.add((exp_uri, RDF.type, PKG.ClimateExposure))
            g.add((birth_uri, PKG.exposedTo, exp_uri))
            if temp:
                try:
                    g.add((exp_uri, PKG.meanTemperature,
                           Literal(float(temp), datatype=XSD.decimal)))
                except: pass
            if dias:
                try:
                    g.add((exp_uri, PKG.extremeHeatDays,
                           Literal(int(dias), datatype=XSD.integer)))
                except: pass
            if expos == 1:
                g.add((exp_uri, RDF.type, PKG.ExtremeHeatExposure))

        # Prenatal
        prenatal = row.get("prenatal_visits")
        try: prenatal = int(prenatal) if prenatal else None
        except: prenatal = None
        if prenatal and idade_mae:
            g.add((mae_uri, PKG.prenatalVisits,
                   Literal(prenatal, datatype=XSD.integer)))

        # Proveniência
        g.add((birth_uri, PROV.wasDerivedFrom,
               URIRef(f"{PKGR}dataset/SINASC_{ano}")))

    return g

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("DIA 32: PIPELINE BATCH RDF - GO COMPLETO")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    linked_dir = Path("data/linked")
    go_files = sorted(linked_dir.glob("births_climate_*_GO_linked.parquet"))

    total_nascimentos = 0
    total_triplas = 0
    total_tempo = 0
    resultados = []

    for f in go_files:
        ano = int(f.stem.split("_")[2])
        output_ttl = OUTPUT_DIR / f"go_{ano}.ttl"

        if output_ttl.exists():
            logger.info(f"{ano}: já existe, pulando...")
            df_check = pl.read_parquet(f)
            total_nascimentos += len(df_check)
            continue

        logger.info(f"Processando GO-{ano}...")
        df = pl.read_parquet(f)
        n = len(df)

        start = time.time()
        g = converter_batch(df, ano)
        elapsed = time.time() - start

        triplas = len(g)
        g.serialize(str(output_ttl), format="turtle")

        size_mb = output_ttl.stat().st_size / 1e6

        total_nascimentos += n
        total_triplas += triplas
        total_tempo += elapsed

        resultado = {
            "ano": ano, "nascimentos": n,
            "triplas": triplas, "tempo": elapsed,
            "size_mb": size_mb,
            "triplas_por_nasc": triplas/n
        }
        resultados.append(resultado)

        logger.success(
            f"GO-{ano}: {n:,} nasc → {triplas:,} triplas "
            f"em {elapsed:.1f}s ({size_mb:.1f}MB)"
        )

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("RESULTADO FINAL:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Total nascimentos: {total_nascimentos:,}")
    print(f"  Total triplas:     {total_triplas:,}")
    print(f"  Tempo total:       {total_tempo:.1f}s")
    if total_nascimentos > 0:
        print(f"  Taxa:              {total_nascimentos/max(total_tempo,0.1):.0f} nasc/s")

    print()
    print("Arquivos gerados:")
    for ttl in sorted(OUTPUT_DIR.glob("go_*.ttl")):
        size = ttl.stat().st_size / 1e6
        print(f"  {ttl.name}: {size:.1f}MB")

    total_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("go_*.ttl")) / 1e6
    print(f"  TOTAL: {total_size:.1f}MB")

    print()
    print("Pipeline GO completo finalizado!")
    print("Projecao Brasil: ~27M nasc em ~20 min (paralelo)")

if __name__ == "__main__":
    main()
