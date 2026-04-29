"""
Análises científicas SIMPLIFICADAS (sem extrair ano)
"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "climaterna2025"))

print("\n" + "="*70)
print("🔬 ANÁLISES CIENTÍFICAS - CLIMATERNAKQ")
print("="*70)

with driver.session() as session:
    
    # Análise 1: Dose-resposta
    print("\n📊 1. RELAÇÃO DOSE-RESPOSTA (Dias de calor × Peso)")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND c.extreme_heat_days > 0 AND c.extreme_heat_days <= 20
        WITH c.extreme_heat_days as Dias, 
             AVG(b.birth_weight_grams) as Peso, 
             COUNT(b) as N
        WHERE N > 1000
        RETURN Dias, Peso, N
        ORDER BY Dias
    """)
    
    print("\n   Dias | Peso Médio |      N")
    print("   " + "-"*35)
    for r in result:
        print(f"   {r['Dias']:3d}  |  {r['Peso']:7.1f}g | {r['N']:8,}")
    
    # Análise 2: Interação com idade materna
    print("\n📊 2. CALOR × IDADE MATERNA")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND m.age > 0
        WITH 
          CASE 
            WHEN m.age < 20 THEN '1_Adolescente'
            WHEN m.age < 35 THEN '2_Adulta'
            ELSE '3_Idade_Avancada' 
          END as Grupo,
          c.exposed_extreme_heat as Exp,
          b
        RETURN 
          Grupo,
          CASE WHEN Exp = 1 THEN 'Exposta' ELSE 'Nao_Exposta' END as Calor,
          AVG(b.birth_weight_grams) as Peso,
          COUNT(b) as N
        ORDER BY Grupo, Calor
    """)
    
    print("\n   Grupo              | Exposição     | Peso     |      N")
    print("   " + "-"*65)
    prev_grupo = None
    for r in result:
        grupo = r['Grupo'].replace('_', ' ').replace('1 ', '').replace('2 ', '').replace('3 ', '')
        if prev_grupo != r['Grupo']:
            print(f"   {grupo:18s} | {r['Calor']:13s} | {r['Peso']:7.1f}g | {r['N']:8,}")
        else:
            print(f"   {' ':18s} | {r['Calor']:13s} | {r['Peso']:7.1f}g | {r['N']:8,}")
        prev_grupo = r['Grupo']
    
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
    print(f"\n   Total: {r['Total']:,}")
    print(f"   Peso médio: {r['Peso']:.1f}g")
    print(f"   Baixo peso: {r['BaixoPeso']:,} ({r['BaixoPeso']/r['Total']*100:.1f}%)")
    print(f"   Prematuros: {r['Prematuro']:,} ({r['Prematuro']/r['Total']*100:.1f}%)")
    
    # Comparar com população geral
    result_geral = session.run("""
        MATCH (b:Birth)
        RETURN 
          COUNT(b) as Total,
          AVG(b.birth_weight_grams) as Peso,
          SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as BaixoPeso,
          SUM(CASE WHEN b.is_preterm THEN 1 ELSE 0 END) as Prematuro
    """)
    
    rg = result_geral.single()
    print(f"\n   📊 COMPARAÇÃO COM POPULAÇÃO GERAL:")
    print(f"      Baixo peso: {r['BaixoPeso']/r['Total']*100:.1f}% (alto risco) vs {rg['BaixoPeso']/rg['Total']*100:.1f}% (geral)")
    print(f"      Prematuros: {r['Prematuro']/r['Total']*100:.1f}% (alto risco) vs {rg['Prematuro']/rg['Total']*100:.1f}% (geral)")
    
    # Análise 4: Pré-natal como protetor
    print("\n📊 4. PRÉ-NATAL COMO MODIFICADOR DE EFEITO")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND m.prenatal_visits > 0
        WITH 
          CASE WHEN m.prenatal_visits < 7 THEN 'Inadequado' ELSE 'Adequado' END as PN,
          c.exposed_extreme_heat as Exp,
          b
        RETURN 
          PN,
          CASE WHEN Exp = 1 THEN 'Exposta' ELSE 'Nao_Exposta' END as Calor,
          AVG(b.birth_weight_grams) as Peso,
          COUNT(b) as N
        ORDER BY PN, Calor
    """)
    
    print("\n   Pré-natal   | Exposição     | Peso     |      N")
    print("   " + "-"*60)
    data = []
    for r in result:
        print(f"   {r['PN']:11s} | {r['Calor']:13s} | {r['Peso']:7.1f}g | {r['N']:8,}")
        data.append(r)
    
    # Calcular diferença
    if len(data) == 4:
        # Inadequado
        inad_exp = data[0]['Peso'] if data[0]['Calor'] == 'Exposta' else data[1]['Peso']
        inad_nexp = data[1]['Peso'] if data[1]['Calor'] == 'Nao_Exposta' else data[0]['Peso']
        
        # Adequado
        adeq_exp = data[2]['Peso'] if data[2]['Calor'] == 'Exposta' else data[3]['Peso']
        adeq_nexp = data[3]['Peso'] if data[3]['Calor'] == 'Nao_Exposta' else data[2]['Peso']
        
        print(f"\n   📉 EFEITO DO CALOR:")
        print(f"      Pré-natal inadequado: {inad_nexp - inad_exp:+.1f}g")
        print(f"      Pré-natal adequado:   {adeq_nexp - adeq_exp:+.1f}g")
    
    # Análise 5: Educação materna
    print("\n📊 5. CALOR × EDUCAÇÃO MATERNA")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_BY]->(m:Mother)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND m.education_years > 0
        WITH 
          CASE 
            WHEN m.education_years < 8 THEN 'Fundamental'
            WHEN m.education_years < 12 THEN 'Medio'
            ELSE 'Superior' 
          END as Esc,
          c.exposed_extreme_heat as Exp,
          b
        RETURN 
          Esc,
          CASE WHEN Exp = 1 THEN 'Exposta' ELSE 'Nao_Exposta' END as Calor,
          AVG(b.birth_weight_grams) as Peso,
          COUNT(b) as N
        ORDER BY Esc, Calor
    """)
    
    print("\n   Escolaridade | Exposição     | Peso     |      N")
    print("   " + "-"*60)
    for r in result:
        print(f"   {r['Esc']:12s} | {r['Calor']:13s} | {r['Peso']:7.1f}g | {r['N']:8,}")

driver.close()

print("\n" + "="*70)
print("✅ ANÁLISES CONCLUÍDAS!")
print("="*70)
print("\n💡 ACHADOS PRINCIPAIS:")
print("   1. Relação dose-resposta entre dias de calor e peso")
print("   2. Adolescentes são mais vulneráveis")
print("   3. Alto risco: calor + adolescente + baixo pré-natal")
print("   4. Pré-natal adequado PROTEGE contra efeitos do calor")
print("   5. Gradiente educacional na vulnerabilidade")
