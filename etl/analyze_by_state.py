"""
Análise estratificada por estado
"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "climaterna2025"))

print("\n" + "="*70)
print("📊 ANÁLISE POR ESTADO - CLIMATERNAKQ")
print("="*70)

with driver.session() as session:
    
    print("\n1️⃣  PESO AO NASCER POR ESTADO E EXPOSIÇÃO A CALOR")
    
    result = session.run("""
        MATCH (b:Birth)-[:BORN_IN]->(l:Location)
        MATCH (b)-[:EXPOSED_TO]->(c:ClimateExposure)
        WHERE c.trimester = 'T3' AND l.state <> 'UNK'
        WITH l.state as Estado,
             c.exposed_extreme_heat as Exp,
             b
        RETURN 
            Estado,
            CASE WHEN Exp = 1 THEN 'Exposto' ELSE 'Nao_Exp' END as Calor,
            AVG(b.birth_weight_grams) as Peso,
            COUNT(b) as N
        ORDER BY Estado, Calor
    """)
    
    print("\n   Estado | Exposição | Peso    |      N      | Diferença")
    print("   " + "-"*65)
    
    # Calcular diferenças por estado
    data_by_state = {}
    for r in result:
        estado = r['Estado']
        if estado not in data_by_state:
            data_by_state[estado] = {}
        data_by_state[estado][r['Calor']] = {'peso': r['Peso'], 'n': r['N']}
    
    # Mostrar com diferenças
    for estado in sorted(data_by_state.keys()):
        exp = data_by_state[estado].get('Exposto', {})
        nexp = data_by_state[estado].get('Nao_Exp', {})
        
        if exp and nexp:
            diff = nexp['peso'] - exp['peso']
            print(f"   {estado:6s} | Exposto   | {exp['peso']:7.1f}g | {exp['n']:10,} |")
            print(f"   {estado:6s} | Não Exp   | {nexp['peso']:7.1f}g | {nexp['n']:10,} | {diff:+6.1f}g")
            print("   " + "-"*65)
    
    # Top estados com maior efeito NEGATIVO do calor
    print("\n2️⃣  ESTADOS COM MAIOR EFEITO PROTETOR DO CALOR (paradoxo!)")
    
    diffs = []
    for estado, data in data_by_state.items():
        exp = data.get('Exposto', {})
        nexp = data.get('Nao_Exp', {})
        if exp and nexp:
            diff = nexp['peso'] - exp['peso']
            diffs.append((estado, diff, exp['n'] + nexp['n']))
    
    diffs.sort(key=lambda x: x[1])  # Menor (mais negativo) primeiro
    
    print("\n   Estado | Diferença | Total Nascimentos")
    print("   " + "-"*45)
    for estado, diff, total in diffs[:10]:
        print(f"   {estado:6s} | {diff:+8.1f}g | {total:10,}")

driver.close()

print("\n" + "="*70)
print("✅ ANÁLISE POR ESTADO CONCLUÍDA!")
print("="*70)
