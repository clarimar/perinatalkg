# PerinatalKG - Paper 1 Outline
# Target: Journal of Biomedical Informatics

## Title
PerinatalKG: An OWL 2 Knowledge Graph Integrating
Perinatal, Climatic and Socioeconomic Data in Brazil

## Authors
Clarimar Jose Coelho (UFG), Guilherme Coelho (UNICAMP/FCM)

## Abstract (draft)
We present PerinatalKG, a formal OWL 2 knowledge graph
integrating perinatal (SINASC), climatic (BR-DWGD) and
socioeconomic (IBGE) data from Brazil (2015-2024).
The ontology comprises 35 classes, 19 data properties,
8 object properties, aligned to BFO and mapped to
SNOMED-CT, ICD-10 and LOINC. A SPARQL endpoint enables
complex epidemiological queries. Two use cases demonstrate:
(1) climate exposure profiling during gestation, and
(2) geographic hierarchy navigation across 5,570 municipalities.

## 1. Introduction
1.1 Background: Brazil 2.7M births/year, SINASC, climate change
1.2 Gap: no formal KG integrating perinatal + climate data
1.3 Contributions:
    - First OWL 2 ontology for Brazilian perinatal data
    - SINASC + BR-DWGD + IBGE integration
    - SPARQL endpoint (Fuseki 6.0)
    - SHACL validation with clinical constraints
    - BFO alignment (OBO Foundry compatible)

## 2. Methods
2.1 Data Sources
    - SINASC: 27M births, 2015-2024, 27 states
    - SIM: 203,973 neonatal deaths (100% coverage)
    - BR-DWGD: gridded climate (0.1 x 0.1 degrees, daily)
    - IBGE: 5,570 municipalities + IDH-M

2.2 Ontology Design
    - OWL 2 DL, BFO alignment
    - 35 classes, 7 blocks (Birth, Mother, Delivery,
      ClimateExposure, Location, DataProps, ObjectProps)
    - Axioms: disjointWith, equivalentClass, intersectionOf
    - HighRiskBirth = PretermBirth AND LowBirthWeight

2.3 Terminology Mappings
    - SNOMED-CT: 16 exactMatch
    - ICD-10: 13 closeMatch
    - LOINC: 7 exactMatch (data properties)

2.4 ETL Pipeline
    - DBC -> R (microdatasus) -> Parquet (Polars)
    - Climate linkage: municipality centroid -> grid cell
    - Parquet -> RDF (rdflib, ~15 triples/birth)
    - Fuseki TDB2 loader

2.5 SPARQL Endpoint
    - Apache Jena Fuseki 6.0.0, TDB2
    - Response: < 0.1s (sample)

2.6 Data Quality
    - SHACL: 5 shapes, clinical constraints
    - OWL RL reasoning: owl:Nothing = 0 (consistent)

## 3. Results
3.1 Ontology Statistics [TABLE 1]
3.2 Dataset: 27M births, 203K deaths, 5,570 municipalities
3.3 Use Case 1: Climate exposure
    - 45% extreme heat T3, Preterm 33% vs Term 47%
3.4 Use Case 2: Geographic hierarchy
    - Municipality -> State -> Region traversal

## 4. Discussion
4.1 Advantages: multi-level aggregation, semantic reasoning
4.2 Limitations: ecological exposure, seasonal confounding
4.3 Future: SINASC-SIM linkage, BioPortal, public endpoint

## Figures
Fig 1: System architecture
Fig 2: Ontology class hierarchy
Fig 3: ETL pipeline
Fig 4: Use Case 1 results
Fig 5: Use Case 2 geographic traversal

## Tables
Table 1: Ontology statistics
Table 2: Dataset statistics
Table 3: SPARQL query examples
