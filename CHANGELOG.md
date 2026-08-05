# Changelog — PerinatalKG

All notable changes are documented here.
Format: Keep a Changelog. Versioning: Semantic Versioning.

---

## [0.3.0] — 2026-06-08

### Added
- ontology/perinatalkg-shapes.ttl: 6 SHACL node shapes (BirthShape, MotherShape,
  ClimateExposureShape, ApgarShape, PretermBirthShape, LowBirthWeightShape)
- examples/usecase_02_multidimensional_query.sparql: Q8 JOIN across birth x
  climate x municipality (245 municipalities, 1.13 s)
- scripts/bench_perinatalkg.py: SPARQL vs DuckDB benchmark (8 queries, 10 reps)
- results/benchmark_results_20260805_093838.csv/.json: benchmark results
- docs/figures/Figure1.svg: OWL 2 ontology class hierarchy
- docs/figures/Figure2.svg: ETL pipeline diagram
- docs/tables/Supplementary_Table_S1.docx: SPARQL vs SQL benchmark table
- Zenodo release DOI: 10.5281/zenodo.20601255
- CITATION.cff with 6 authors and ORCIDs
- knowledge_graph/README.md: deprecation notice for Neo4j legacy phase

### Changed
- etl/07_batch_rdf_pipeline.py: added PostTermBirth classification (IG >= 42w);
  previously all >= 37w were TermBirth
- Ontology ExtremeHeatExposure IAO:0000115 corrected: "90th percentile" ->
  "Tmax > 35 degrees C absolute threshold (BR-DWGD)"
- All hardcoded Neo4j credentials removed from scripts/ and etl/
- README: corrected scope (Goias PoC, not national), updated author list

### Fixed
- Birth count: 934,806 distinct Birth nodes (TDB2 deduplicates 1 duplicate birth_id)
- Total triples updated to 13,334,157 (post-PostTermBirth reprocessing)
- Throughput corrected to 4,439 births/s

### Knowledge graph statistics (v0.3.0, Goias 2015-2024)
- Births: 934,806 | Triples: 13,334,157 | Municipalities: 246
- PretermBirth: 101,287 | TermBirth: 815,094 | PostTermBirth: 18,425
- LowBirthWeight: 83,660 | ExtremeHeatExposure T3: 387,012

---

## [0.2.0] — 2026-05-15

### Added
- Full ETL pipeline for Goias state (2015-2024): 934,806 births ->
  13,334,157 RDF triples in Apache Jena Fuseki 6.0.0 (TDB2)
- Probabilistic SINASC-SIM record linkage (Fellegi-Sunter framework):
  85.2% recall, Goias 2020 (568/667 neonatal deaths linked)
- SPARQL endpoint benchmark (8 queries, single run): 0.03-7.58 s
- etl/07_batch_rdf_pipeline.py: batch RDF conversion, 4,439 births/s
- examples/usecase_01_climate_exposure.py
- OWL 2 ontology v0.2.0: 35 classes, 36 terminology mappings
- docs/manuscript/manuscript_perinatalkg_v2.docx: Paper 1 manuscript

---

## [0.1.0] — 2026-04-29

### Added
- Initial project structure (renamed from ClimaternaKG to PerinatalKG)
- GitHub repository and version control
- OWL 2 ontology scaffold (35 classes, BFO alignment)
- Setup scripts for pipeline infrastructure
