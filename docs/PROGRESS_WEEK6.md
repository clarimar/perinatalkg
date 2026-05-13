# Semana 6 - Relatório de Progresso
**Data:** 9 Jun 2026

## Resumo
Linkage probabilístico SINASC-SIM implementado e validado.

## Resultados

### Linkage GO-2020
- SINASC: 92,585 nascimentos
- SIM: 667 óbitos neonatais
- Linkados: 568 (85.2%) — excelente!
- Score médio: 6.1/7

### Qualidade
- Confiança alta (score 6-7): 414 (72.9%)
- Concordância peso exata: verificada
- owl:Nothing = 0 (KG consistente)

### RDF gerado
- 4,038 triplas incluindo óbitos
- Novas classes: NeonatalDeath, EarlyNeonatalDeath
- 400/514 = 78% óbitos precoces (0-7 dias)

### Top causas (GO-2020)
- P369: Sepse neonatal (76 casos)
- P220: Angústia respiratória (44 casos)
- P77:  Enterocolite necrosante (17 casos)

## Semana 7
- Conversão RDF completa: 27M nascimentos
- Deploy Fuseki em servidor
- Endpoint público

## Semana 8
- Manuscrito Paper 1
- Submissão JBI
