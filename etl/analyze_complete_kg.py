"""
Análises do ClimaternaKG COMPLETO (27M nascimentos)
"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "climaterna2025"))

print("\n" + "="*70)
print("📊 CLIMATERNAKQ - KNOWLEDGE GRAPH COMPLETO")
print("="*70)

with driver.session() as session:
    
    # 1. Resumo geral
    print("\n1️⃣  ESTATÍSTICAS GERAIS:")
    result = session.run("""
        MATCH (b:Birth)
        RETURN 
            COUNT(b) as total,
            AVG(b.birth_weight_grams) as avg_weight,
            MIN(b.birth_weight_grams) as min_weight,
            MAX(b.birth_weight_grams) as max_weight,
            SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as low_weight,
            SUM(CASE WHEN b.is_preterm THEN 1 ELSE 0 END) as preterm
    """)
    
    r = result.single()
    print(f"   Total de nascimentos: {r['total']:,}")
    print(f"   Peso médio: {r['avg_weight']:.1f}g")
    print(f"   Peso mínimo: {r['min_weight']:.0f}g")
    print(f"   Peso máximo: {r['max_weight']:.0f}g")
    print(f"   Baixo peso (<2500g): {r['low_weight']:,} ({r['low_weight']/r['total']*100:.2f}%)")
    print(f"   Prematuros (<37sem): {r['preterm']:,} ({r['preterm']/r['total']*100:.2f}%)")
    
    # 2. Exposição a calor
    print("\n2️⃣  EXPOSIÇÃO A CALOR EXTREMO:")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        RETURN 
            SUM(CASE WHEN c.exposed_extreme_heat = 1 THEN 1 ELSE 0 END) as exposed,
            COUNT(b) as total
    """)
    
    r = result.single()
    print(f"   Expostos a calor extremo (T3): {r['exposed']:,} ({r['exposed']/r['total']*100:.2f}%)")
    print(f"   Não expostos: {r['total']-r['exposed']:,} ({(r['total']-r['exposed'])/r['total']*100:.2f}%)")
    
    # 3. Peso por exposição
    print("\n3️⃣  PESO AO NASCER POR EXPOSIÇÃO A CALOR:")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        WITH c.exposed_extreme_heat as exp, b
        RETURN 
            CASE WHEN exp = 1 THEN 'Exposto' ELSE 'Não Exposto' END as grupo,
            AVG(b.birth_weight_grams) as peso_medio,
            COUNT(b) as total
        ORDER BY grupo
    """)
    
    for r in result:
        print(f"   {r['grupo']:15s}: {r['peso_medio']:7.1f}g (n={r['total']:,})")
    
    # 4. Diferença de peso
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3'
        WITH 
            AVG(CASE WHEN c.exposed_extreme_heat = 1 THEN b.birth_weight_grams ELSE null END) as peso_exposto,
            AVG(CASE WHEN c.exposed_extreme_heat = 0 THEN b.birth_weight_grams ELSE null END) as peso_nao_exposto
        RETURN peso_exposto, peso_nao_exposto, (peso_nao_exposto - peso_exposto) as diferenca
    """)
    
    r = result.single()
    print(f"\n   📉 Diferença de peso: {r['diferenca']:.1f}g")
    print(f"      (Não expostos têm {r['diferenca']:.1f}g A MAIS que expostos)")
    
    # 5. Distribuição de dias de calor
    print("\n4️⃣  DISTRIBUIÇÃO DE DIAS DE CALOR EXTREMO:")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND c.extreme_heat_days > 0
        WITH c.extreme_heat_days as dias, COUNT(b) as total
        WHERE dias <= 20
        RETURN dias, total
        ORDER BY dias
        LIMIT 15
    """)
    
    for r in result:
        bar = "█" * int(r['total'] / 50000)
        print(f"   {r['dias']:2d} dias: {r['total']:7,} {bar}")
    
    # 6. Idade materna
    print("\n5️⃣  DISTRIBUIÇÃO POR IDADE MATERNA:")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        WITH 
            CASE 
                WHEN m.age < 20 THEN '<20'
                WHEN m.age < 25 THEN '20-24'
                WHEN m.age < 30 THEN '25-29'
                WHEN m.age < 35 THEN '30-34'
                ELSE '35+'
            END as faixa,
            b
        RETURN 
            faixa,
            AVG(b.birth_weight_grams) as peso_medio,
            COUNT(b) as total
        ORDER BY faixa
    """)
    
    for r in result:
        print(f"   {r['faixa']:10s}: {r['peso_medio']:7.1f}g (n={r['total']:,})")

driver.close()

print("\n" + "="*70)
print("✅ ANÁLISES CONCLUÍDAS!")
print("="*70)
print("\n🌐 Explore no Neo4j Browser: http://localhost:7474")
print("\n💡 Queries sugeridas:")
print("   MATCH (b:Birth)-[r]->(x) RETURN b,r,x LIMIT 100")
print("   MATCH (b:Birth) WHERE b.birth_weight_grams < 1000 RETURN b LIMIT 50")
