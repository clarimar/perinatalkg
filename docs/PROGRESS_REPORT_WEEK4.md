# PerinatalKG - Relatório de Progresso
**Para:** Guilherme Coelho (UNICAMP/FCM)
**De:** Clarimar José Coelho (PUC Goiás)
**Data:** 12 de Maio de 2026

## RESUMO EXECUTIVO

4 semanas completas. Infraestrutura técnica operacional.
Status: NO PRAZO - PRONTO PARA PAPER 1

## DADOS INTEGRADOS

- SINASC: pipeline 27M nascimentos, 27 estados, 2015-2024
- SIM: 203.973 obitos neonatais (270/270 UF-ano = 100%)
- IBGE: 5.570 municipios (100%)
- IDH-M: 5.564 municipios (99.9%)
- Amostra RDF validada: 100 nascimentos GO-2020

## ONTOLOGIA OWL 2

- 18 classes com labels bilíngues pt/en
- BFO alignment: Birth->Occurrent, Mother->MaterialEntity
- HighRiskBirth = PretermBirth AND LowBirthWeight
- disjointWith, equivalentClass, intersectionOf

## INFRAESTRUTURA

- Apache Jena Fuseki 6.0.0: localhost:3030
- SPARQL Endpoint: /perinatalkg/sparql
- OWL RL Reasoner: +1.832 triplas inferidas em 0.77s
- SHACL Validation: 5 shapes clinicas
- GitHub: github.com/clarimar/perinatalkg (20 commits)

## USE CASE 1: EXPOSICAO CLIMATICA

Preterm (N=12): Peso=1.968g, IG=31.3sem, Calor=33%
Term   (N=88): Peso=3.269g, IG=38.6sem, Calor=47%
Total expostos a calor extremo T3: 45%

## USE CASE 2: HIERARQUIA GEOGRAFICA

Goiania -> Goias -> Regiao Centro-Oeste (funcionando)
28 estados + 10 regioes no triplestore
Navegacao multi-nivel SPARQL confirmada

## PROGRESSO

Semana 1: COMPLETA - Git, GitHub, RDF basico
Semana 2: COMPLETA - SIM 203K, IBGE, SPARQL
Semana 3: COMPLETA - OWL avancado, BFO, Fuseki
Semana 4: COMPLETA - SHACL, Reasoner, Use Cases
Semana 5: PENDENTE - Ontologia formal completa
Semana 6: PENDENTE - Linkage SINASC-SIM
Semana 7: PENDENTE - Escala 27M nascimentos RDF
Semana 8: PENDENTE - Manuscrito Paper 1

## QUESTOES PARA DISCUSSAO

1. CEP-FCM aprovado para linkage SINASC-SIM?
2. Servidor disponivel para deploy? (16GB RAM)
3. Autoria Paper 1: Clarimar 1o, Guilherme 2o?
4. Timeline Jun 2026 para submissao e realista?

## REPOSITORIO

https://github.com/clarimar/perinatalkg
Apache 2.0 - Clarimar Jose Coelho - PUC Goiás
