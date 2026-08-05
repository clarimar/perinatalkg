[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20601255.svg)](https://doi.org/10.5281/zenodo.20601255)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

# PerinatalKG

An OWL 2 knowledge graph integrating Brazilian population-level birth records (SINASC) with gridded climate data (BR-DWGD) and municipal socioeconomic indicators (IBGE) under a formal ontology aligned with the Basic Formal Ontology (BFO) and mapped to SNOMED-CT, ICD-10, and LOINC.

**Proof-of-concept deployment:** Goiás state, Brazil, 2015–2024 — 934,806 births, 13,334,157 RDF triples, Apache Jena Fuseki 6.0.0.

## Citation

> Coelho CJ, Charles M'poca C, Kassada DS, França BBN, Pacagnella RC, Coelho G. PerinatalKG: design and evaluation of an OWL 2 architecture for integrating population-level birth records with climate and socioeconomic data. *Journal of Biomedical Informatics* (under review, 2026).

Software: Coelho CJ et al. PerinatalKG v0.3.0 [Software]. Zenodo; 2026. https://doi.org/10.5281/zenodo.20601255

## Repository contents

    ontology/
      perinatalkg_full.ttl        OWL 2 ontology (35 classes, v0.3.0)
      perinatalkg-shapes.ttl      SHACL validation shapes (6 node shapes)
    etl/
      07_batch_rdf_pipeline.py    RDF conversion pipeline (Goiás 2015-2024)
    examples/
      usecase_01_climate_exposure.py
      usecase_02_multidimensional_query.sparql
    scripts/
      bench_perinatalkg.py        SPARQL vs DuckDB benchmark
    results/
      benchmark_results_*.csv/.json
    docs/
      figures/    Figure1.svg, Figure2.svg
      tables/     Supplementary_Table_S1.docx
      manuscript/

## Knowledge graph (Goiás state, 2015–2024)

| Metric | Value |
|---|---|
| Birth records | 934,806 |
| RDF triples | 13,334,157 |
| Municipalities | 246 |
| Preterm births (<37w) | 101,287 (10.8%) |
| Term births (37-41w) | 815,094 (87.2%) |
| Post-term births (>=42w) | 18,425 (2.0%) |
| Low birth weight (<2,500 g) | 83,660 (8.9%) |
| Extreme heat exposure T3 | 387,012 (41.4%) |
| Mean birth weight | 3,141 g |

## Dependencies

| Software | Version |
|---|---|
| Python | 3.13.9 |
| rdflib | 7.6.0 |
| Polars | 1.40.1 |
| owlrl | 7.1.4 |
| DuckDB | 1.5.2 |
| Apache Jena Fuseki | 6.0.0 |

External pipeline dependencies (not in this repository):
- 12_harmonize_climate_v2.py — BR-DWGD harmonisation
- 10_harmonize_sinasc_v2.py — SINASC harmonisation

## Authors

- Clarimar José Coelho — PUC Goiás, Goiânia, GO, Brazil (0000-0002-5163-2986)
- Charles M'poca Charles — UNICAMP, Campinas, SP, Brazil
- Danielle Satie Kassada — UNICAMP, Campinas, SP, Brazil
- Breno Bernard Nicolau de França — UNICAMP (0000-0002-4531-1473)
- Rodolfo de Carvalho Pacagnella — UNICAMP (0000-0002-5739-0009)
- Guilherme Coelho — UNICAMP/FCM (0000-0003-3649-9825)

## Licence

Apache 2.0 — see LICENSE.
