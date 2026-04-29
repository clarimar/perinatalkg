# ClimaternaKG - Análises Científicas Avançadas

## ANÁLISE 1: Estratificação por Trimestre

### Comparar exposição T1, T2, T3
```cypher
// Peso médio por trimestre de exposição
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.exposed_extreme_heat = 1
RETURN 
  c.trimester as Trimestre,
  AVG(b.birth_weight_grams) as PesoMedio,
  COUNT(b) as Total
ORDER BY Trimestre
```

## ANÁLISE 2: Dose-Resposta

### Relação entre número de dias de calor e peso
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3' AND c.extreme_heat_days BETWEEN 1 AND 30
WITH c.extreme_heat_days as Dias, AVG(b.birth_weight_grams) as PesoMedio, COUNT(b) as N
WHERE N > 1000
RETURN Dias, PesoMedio, N
ORDER BY Dias
```

## ANÁLISE 3: Interação com Idade Materna

### Calor + Idade materna
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
WITH 
  CASE WHEN m.age < 20 THEN 'Adolescente'
       WHEN m.age < 35 THEN 'Adulta'
       ELSE 'Idosa' END as IdadeGrupo,
  c.exposed_extreme_heat as Exposta,
  b
RETURN 
  IdadeGrupo,
  CASE WHEN Exposta = 1 THEN 'Exposta' ELSE 'Não Exposta' END as ExposicaoCalor,
  AVG(b.birth_weight_grams) as PesoMedio,
  COUNT(b) as Total
ORDER BY IdadeGrupo, ExposicaoCalor
```

## ANÁLISE 4: Extremos (Muito Baixo Peso)

### Calor e MBPN (<1500g)
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3' AND b.birth_weight_grams < 1500
RETURN 
  c.exposed_extreme_heat as Exposto,
  COUNT(b) as TotalMBPN,
  AVG(b.birth_weight_grams) as PesoMedio
```

## ANÁLISE 5: Pré-natal como Modificador

### Interação calor x pré-natal
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
WITH 
  CASE WHEN m.prenatal_visits < 7 THEN 'Inadequado' ELSE 'Adequado' END as PreNatal,
  c.exposed_extreme_heat as Exposta,
  b
RETURN 
  PreNatal,
  CASE WHEN Exposta = 1 THEN 'Exposta' ELSE 'Não Exposta' END as Calor,
  AVG(b.birth_weight_grams) as PesoMedio,
  COUNT(b) as Total
ORDER BY PreNatal, Calor
```

## ANÁLISE 6: Múltiplos Fatores de Risco

### Alto risco (calor + adolescente + baixo pré-natal)
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
  AND c.exposed_extreme_heat = 1
  AND m.age < 20
  AND m.prenatal_visits < 7
RETURN 
  COUNT(b) as AltoRisco,
  AVG(b.birth_weight_grams) as PesoMedio,
  SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso,
  SUM(CASE WHEN b.is_preterm THEN 1 ELSE 0 END) as Prematuro
```

## ANÁLISE 7: Temporal (Anos)

### Tendência ao longo dos anos
```cypher
// Extrair ano do birth_id (assumindo formato: YYYYMMDD...)
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3'
WITH 
  toInteger(substring(b.birth_id, 0, 4)) as Ano,
  c.exposed_extreme_heat as Exposto,
  b
WHERE Ano >= 2015 AND Ano <= 2024
RETURN 
  Ano,
  SUM(CASE WHEN Exposto = 1 THEN 1 ELSE 0 END) as Expostos,
  COUNT(b) as Total,
  AVG(b.birth_weight_grams) as PesoMedio
ORDER BY Ano
```

## ANÁLISE 8: Educação Materna

### Gradiente educacional
```cypher
MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.trimester = 'T3' AND m.education_years > 0
WITH 
  CASE WHEN m.education_years < 8 THEN 'Fundamental'
       WHEN m.education_years < 12 THEN 'Médio'
       ELSE 'Superior' END as Escolaridade,
  c.exposed_extreme_heat as Exposta,
  b
RETURN 
  Escolaridade,
  CASE WHEN Exposta = 1 THEN 'Exposta' ELSE 'Não Exposta' END as Calor,
  AVG(b.birth_weight_grams) as PesoMedio,
  COUNT(b) as Total
ORDER BY Escolaridade, Calor
```
