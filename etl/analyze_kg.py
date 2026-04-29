"""
Análises principais do ClimaternaKG
"""
from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "climaterna2025")

print("🔍 Conectando ao Neo4j...")
driver = GraphDatabase.driver(uri, auth=(user, password))

print("\n" + "="*70)
print("📊 ANÁLISES DO CLIMATERNAKQ KNOWLEDGE GRAPH")
print("="*70)

with driver.session() as session:
    
    # Análise 1: Resumo geral
    print("\n1️⃣  RESUMO GERAL DO GRAFO:")
    result = session.run("""
        MATCH (b:Birth)
        OPTIONAL MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        RETURN 
          COUNT(DISTINCT b) as TotalNascimentos,
          AVG(b.birth_weight_grams) as PesoMedio,
          SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso,
          SUM(CASE WHEN c.exposed_extreme_heat = 1 THEN 1 ELSE 0 END) as ExpostosCalor
    """)
    
    record = result.single()
    if record:
        print(f"   Total de nascimentos: {record['TotalNascimentos']:,}")
        print(f"   Peso médio: {record['PesoMedio']:.0f}g")
        print(f"   Baixo peso (<2500g): {record['BaixoPeso']:,}")
        print(f"   Expostos a calor extremo: {record['ExpostosCalor']:,}")
    
    # Análise 2: Peso por exposição
    print("\n2️⃣  PESO AO NASCER POR EXPOSIÇÃO A CALOR EXTREMO:")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        RETURN 
          CASE WHEN c.exposed_extreme_heat = 1 THEN 'Exposto' ELSE 'Não Exposto' END as Grupo,
          AVG(b.birth_weight_grams) as PesoMedio,
          COUNT(b) as Total
        ORDER BY Grupo
    """)
    
    for record in result:
        print(f"   {record['Grupo']:15s}: {record['PesoMedio']:7.1f}g (n={record['Total']:,})")
    
    # Análise 3: Taxa de baixo peso
    print("\n3️⃣  TAXA DE BAIXO PESO POR EXPOSIÇÃO:")
    result = session.run("""
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
    """)
    
    for record in result:
        print(f"   {record['Grupo']:15s}: {record['BaixoPeso']:,}/{record['Total']:,} = {record['TaxaBaixoPeso']:.2f}%")
    
    # Análise 4: Distribuição de dias de calor
    print("\n4️⃣  DISTRIBUIÇÃO DE DIAS DE CALOR EXTREMO:")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND c.extreme_heat_days > 0
        WITH c.extreme_heat_days as Dias, COUNT(b) as Total
        WHERE Dias <= 10
        RETURN Dias, Total
        ORDER BY Dias
        LIMIT 10
    """)
    
    for record in result:
        bar = "█" * int(record['Total'] / 100)
        print(f"   {record['Dias']:2d} dias: {record['Total']:5,} {bar}")
    
    # Análise 5: Idade materna
    print("\n5️⃣  PESO AO NASCER POR IDADE MATERNA:")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        WITH 
          CASE 
            WHEN m.age < 20 THEN '<20 anos'
            WHEN m.age < 35 THEN '20-34 anos'
            ELSE '35+ anos'
          END as FaixaEtaria,
          b.birth_weight_grams as Peso
        RETURN 
          FaixaEtaria,
          AVG(Peso) as PesoMedio,
          COUNT(*) as Total
        ORDER BY FaixaEtaria
    """)
    
    for record in result:
        print(f"   {record['FaixaEtaria']:15s}: {record['PesoMedio']:7.1f}g (n={record['Total']:,})")

driver.close()

print("\n" + "="*70)
print("✅ Análises concluídas!")
print("="*70)
print("\n💡 Para mais análises, veja:")
print("   knowledge_graph/cypher_queries/exploratory_queries.md")
