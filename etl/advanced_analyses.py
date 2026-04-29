"""
Análises científicas avançadas do ClimaternaKG
"""
from neo4j import GraphDatabase
import pandas as pd

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "climaterna2025"))

print("\n" + "="*70)
print("🔬 ANÁLISES CIENTÍFICAS AVANÇADAS - CLIMATERNAKQ")
print("="*70)

with driver.session() as session:
    
    # Análise 1: Dose-resposta
    print("\n📊 1. RELAÇÃO DOSE-RESPOSTA (Dias de calor × Peso)")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND c.extreme_heat_days BETWEEN 1 AND 20
        WITH c.extreme_heat_days as Dias, AVG(b.birth_weight_grams) as Peso, COUNT(b) as N
        WHERE N > 1000
        RETURN Dias, Peso, N
        ORDER BY Dias
    """)
    
    print("\n   Dias | Peso Médio |   N")
    print("   " + "-"*30)
    for r in result:
        print(f"   {r['Dias']:3d}  |  {r['Peso']:7.1f}g | {r['N']:7,}")
    
    # Análise 2: Interação com idade materna
    print("\n📊 2. INTERAÇÃO CALOR × IDADE MATERNA")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        WITH 
          CASE WHEN m.age < 20 THEN 'Adolescente'
               WHEN m.age < 35 THEN 'Adulta'
               ELSE 'Idade Avançada' END as Grupo,
          c.exposed_extreme_heat as Exp,
          b
        RETURN 
          Grupo,
          CASE WHEN Exp = 1 THEN 'Exposta' ELSE 'Não Exposta' END as Calor,
          AVG(b.birth_weight_grams) as Peso,
          COUNT(b) as N
        ORDER BY Grupo, Calor
    """)
    
    print("\n   Grupo Etário      | Exposição    | Peso    |      N")
    print("   " + "-"*60)
    for r in result:
        print(f"   {r['Grupo']:17s} | {r['Calor']:12s} | {r['Peso']:7.1f}g | {r['N']:8,}")
    
    # Análise 3: Alto risco
    print("\n📊 3. NASCIMENTOS DE ALTO RISCO")
    print("      (Calor + Adolescente + Pré-natal inadequado)")
    
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
          AND c.exposed_extreme_heat = 1
          AND m.age < 20
          AND m.prenatal_visits < 7
        RETURN 
          COUNT(b) as Total,
          AVG(b.birth_weight_grams) as Peso,
          SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso,
          SUM(CASE WHEN b.is_preterm THEN 1 ELSE 0 END) as Prematuro
    """)
    
    r = result.single()
    print(f"\n   Total de nascimentos: {r['Total']:,}")
    print(f"   Peso médio: {r['Peso']:.1f}g")
    print(f"   Baixo peso: {r['BaixoPeso']:,} ({r['BaixoPeso']/r['Total']*100:.1f}%)")
    print(f"   Prematuros: {r['Prematuro']:,} ({r['Prematuro']/r['Total']*100:.1f}%)")
    
    # Análise 4: Pré-natal como protetor
    print("\n📊 4. PRÉ-NATAL COMO MODIFICADOR DE EFEITO")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        WITH 
          CASE WHEN m.prenatal_visits < 7 THEN 'Inadequado' ELSE 'Adequado' END as PN,
          c.exposed_extreme_heat as Exp,
          b
        RETURN 
          PN,
          CASE WHEN Exp = 1 THEN 'Exposta' ELSE 'Não Exposta' END as Calor,
          AVG(b.birth_weight_grams) as Peso,
          COUNT(b) as N
        ORDER BY PN, Calor
    """)
    
    print("\n   Pré-natal   | Exposição    | Peso    |      N")
    print("   " + "-"*55)
    for r in result:
        print(f"   {r['PN']:11s} | {r['Calor']:12s} | {r['Peso']:7.1f}g | {r['N']:8,}")

driver.close()

print("\n" + "="*70)
print("✅ ANÁLISES CONCLUÍDAS!")
print("="*70)
