# ClimaternaKG - Queries Exploratórias

## QUERIES BÁSICAS

### 1. Visão geral do grafo
```cypher
// Contar nós por tipo
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC
```

### 2. Contar relacionamentos
```cypher
// Contar relacionamentos por tipo
MATCH ()-[r]->()
RETURN type(r) as RelationType, count(r) as Count
ORDER BY Count DESC
```

### 3. Ver estrutura do grafo
```cypher
// Ver amostra de cada tipo de nó
MATCH (n)
WITH labels(n)[0] as Type, collect(n)[0] as Sample
RETURN Type, Sample
```

## ANÁLISES EPIDEMIOLÓGICAS

### 4. Peso médio por exposição a calor
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
RETURN 
  CASE 
    WHEN c.exposed_extreme_heat = 1 THEN 'Exposto' 
    ELSE 'Não Exposto' 
  END as Exposicao,
  AVG(b.birth_weight_grams) as PesoMedio,
  STDEV(b.birth_weight_grams) as DesvioPadrao,
  COUNT(b) as Total
ORDER BY Exposicao
```

### 5. Taxa de baixo peso por exposição
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
WITH c.exposed_extreme_heat as Exposicao,
     COUNT(b) as Total,
     SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso
RETURN 
  CASE WHEN Exposicao = 1 THEN 'Exposto' ELSE 'Não Exposto' END as Grupo,
  Total,
  BaixoPeso,
  round(BaixoPeso * 100.0 / Total, 2) as TaxaBaixoPeso
```

### 6. Distribuição de dias de calor extremo
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3' AND c.extreme_heat_days > 0
RETURN 
  c.extreme_heat_days as DiasCalorExtremo,
  COUNT(b) as Nascimentos,
  AVG(b.birth_weight_grams) as PesoMedio
ORDER BY DiasCalorExtremo
```

### 7. Prematuridade e calor
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
RETURN 
  c.exposed_extreme_heat as Exposicao,
  b.is_preterm as Prematuro,
  COUNT(b) as Total
ORDER BY Exposicao, Prematuro
```

## ANÁLISES MATERNAS

### 8. Peso ao nascer por idade materna
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
WITH 
  CASE 
    WHEN m.age < 20 THEN '<20'
    WHEN m.age < 35 THEN '20-34'
    ELSE '35+'
  END as FaixaEtaria,
  b.birth_weight_grams as Peso
RETURN 
  FaixaEtaria,
  AVG(Peso) as PesoMedio,
  COUNT(*) as Total
ORDER BY FaixaEtaria
```

### 9. Educação materna e outcomes
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
WITH 
  CASE 
    WHEN m.education_years < 8 THEN 'Fundamental'
    WHEN m.education_years < 12 THEN 'Médio'
    ELSE 'Superior'
  END as Escolaridade,
  b
RETURN 
  Escolaridade,
  AVG(b.birth_weight_grams) as PesoMedio,
  SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso,
  COUNT(b) as Total
ORDER BY Escolaridade
```

### 10. Adequação do pré-natal
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
WITH 
  CASE 
    WHEN m.prenatal_visits < 7 THEN 'Inadequado'
    ELSE 'Adequado'
  END as PreNatal,
  b
RETURN 
  PreNatal,
  AVG(b.birth_weight_grams) as PesoMedio,
  COUNT(b) as Total
```

## PADRÕES COMPLEXOS

### 11. Nascimentos de alto risco (múltiplos fatores)
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
  AND c.exposed_extreme_heat = 1
  AND m.age < 20
  AND m.prenatal_visits < 7
RETURN 
  COUNT(b) as NascimentosAltoRisco,
  AVG(b.birth_weight_grams) as PesoMedio,
  SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso
```

### 12. Caminho completo (Birth → Mother, Location, Climate)
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
MATCH (b)-[:BORN_IN]->(l:Location)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
RETURN b, m, l, c
LIMIT 10
```

### 13. Temperatura e peso - relação dose-resposta
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3' AND c.mean_temperature IS NOT NULL
WITH 
  round(c.mean_temperature) as TempArredondada,
  b.birth_weight_grams as Peso
RETURN 
  TempArredondada as Temperatura,
  AVG(Peso) as PesoMedio,
  COUNT(*) as Nascimentos
ORDER BY Temperatura
```

## VISUALIZAÇÕES

### 14. Subgrafo de nascimentos com baixo peso
```cypher
MATCH (b:Birth)-[r1:BORN_BY]->(m:Mother)
MATCH (b)-[r2:EXPOSED_TO]->(c:ClimateExposure)
WHERE b.is_low_birth_weight = true
  AND c.trimester = 'T3'
RETURN b, m, c, r1, r2
LIMIT 25
```

### 15. Rede de exposições extremas
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.extreme_heat_days > 5
RETURN b, c
LIMIT 50
```

## ESTATÍSTICAS DO SISTEMA

### 16. Resumo completo do Knowledge Graph
```cypher
MATCH (b:Birth)
OPTIONAL MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
RETURN 
  COUNT(DISTINCT b) as TotalNascimentos,
  AVG(b.birth_weight_grams) as PesoMedio,
  SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso,
  SUM(CASE WHEN b.is_preterm THEN 1 ELSE 0 END) as Prematuros,
  SUM(CASE WHEN c.exposed_extreme_heat = 1 THEN 1 ELSE 0 END) as ExpostosCalor
```
