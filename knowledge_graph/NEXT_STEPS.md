# ClimaternaKG - Próximos Passos Técnicos

## 🎯 PRIORIDADE 1: Corrigir Confundimento Geográfico

### Passo 1: Adicionar Nós de Location
```python
# Script: add_locations.py
# Criar nós Location para cada município único
# Adicionar propriedades: state, region, lat, lon
```

### Passo 2: Criar Relacionamento BORN_IN
```cypher
MATCH (b:Birth), (l:Location)
WHERE b.municipality_code = l.municipality_code
CREATE (b)-[:BORN_IN]->(l)
```

### Passo 3: Calcular Quartis de Temperatura
```python
# Para cada município: calcular temperatura média anual
# Classificar em Q1 (frio) a Q4 (quente)
# Criar nós TemperatureQuartile
```

### Passo 4: Análises Estratificadas
```cypher
MATCH (b:Birth)-[:BORN_IN]->(l:Location)-[:IN_QUARTILE]->(q:TempQuartile)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3' AND q.quartile = 'Q1'  // Só regiões frias
RETURN ...
```

## 🔧 SCRIPTS A DESENVOLVER

1. `add_location_nodes.py` - Criar Location a partir de municipality_code
2. `link_births_to_locations.py` - Criar relacionamento BORN_IN
3. `calculate_temp_quartiles.py` - Classificar municípios
4. `stratified_analyses.py` - Análises por quartil

## 📊 ANÁLISES PENDENTES

- [ ] Gradiente de adaptação (Q1 vs Q4)
- [ ] Efeitos regionais (Norte vs Sul)
- [ ] Séries temporais (2015-2024)
- [ ] Subgrupos vulneráveis por região

## 📄 DOCUMENTAÇÃO

- [ ] README.md do projeto
- [ ] Guia de instalação
- [ ] Tutorial de queries
- [ ] Paper metodológico
