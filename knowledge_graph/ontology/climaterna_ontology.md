# ClimaternaKG Ontology

## CLASSES (Node Types)

### 1. Birth (Nascimento)
- Representa um nascimento individual
- Propriedades:
  - birth_id (único)
  - birth_date
  - birth_weight_grams
  - gestational_weeks
  - is_preterm (boolean)
  - is_low_birth_weight (boolean)

### 2. Mother (Mãe)
- Representa uma mãe
- Propriedades:
  - maternal_id (derivado)
  - age
  - education_years
  - prenatal_visits

### 3. Location (Localização)
- Representa um município
- Propriedades:
  - municipality_code
  - municipality_name
  - state
  - region
  - latitude
  - longitude

### 4. ClimateExposure (Exposição Climática)
- Representa exposição ao clima durante a gestação
- Propriedades:
  - trimester (T1, T2, T3, FULL)
  - mean_temperature
  - max_temperature
  - min_temperature
  - precipitation
  - extreme_heat_days (>35°C)
  - heat_wave_days

### 5. TemperatureQuartile (Quartil de Temperatura)
- Representa classificação regional por temperatura
- Propriedades:
  - quartile (Q1-Q4)
  - mean_regional_temp
  - temp_range_min
  - temp_range_max

## RELATIONSHIPS (Edge Types)

### 1. BORN_BY
- Birth → Mother
- Uma mãe pode ter múltiplos nascimentos

### 2. BORN_IN
- Birth → Location
- Nascimento ocorreu em um município

### 3. EXPOSED_TO
- Birth → ClimateExposure
- Nascimento foi exposto a condições climáticas específicas

### 4. LOCATED_IN_QUARTILE
- Location → TemperatureQuartile
- Município pertence a um quartil de temperatura

### 5. HAS_CLIMATE
- Location → ClimateExposure
- Município teve determinadas condições climáticas

## EXEMPLOS DE QUERIES

### Query 1: Encontrar nascimentos com baixo peso em regiões quentes
```cypher
MATCH (b:Birth)-[:BORN_IN]->(l:Location)-[:LOCATED_IN_QUARTILE]->(q:TemperatureQuartile)
WHERE b.is_low_birth_weight = true AND q.quartile = 'Q4'
RETURN b, l, q
LIMIT 100
```

### Query 2: Calcular média de peso por quartil de temperatura
```cypher
MATCH (b:Birth)-[:BORN_IN]->(l:Location)-[:LOCATED_IN_QUARTILE]->(q:TemperatureQuartile)
RETURN q.quartile, 
       AVG(b.birth_weight_grams) as avg_weight,
       COUNT(b) as total_births
ORDER BY q.quartile
```

### Query 3: Nascimentos expostos a calor extremo
```cypher
MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
WHERE c.extreme_heat_days > 0 AND c.trimester = 'T3'
RETURN b, c
LIMIT 100
```
