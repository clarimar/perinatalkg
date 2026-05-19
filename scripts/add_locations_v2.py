"""
Adicionar Location nodes - VERSÃO 2 (com Birth tendo municipality_code)
"""
from neo4j import GraphDatabase
from tqdm import tqdm

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.getenv("NEO4J_PASSWORD", "changeme")))

print("🗺️  Extraindo municípios únicos...")

with driver.session() as session:
    # Extrair municípios únicos
    result = session.run("""
        MATCH (b:Birth)
        WHERE b.municipality_code IS NOT NULL 
          AND b.municipality_code <> '0'
        RETURN DISTINCT 
            b.municipality_code as code,
            b.state as state
    """)
    
    locations = []
    for record in result:
        locations.append({
            'code': record['code'],
            'state': record['state'] if record['state'] else 'UNK'
        })
    
    print(f"✅ {len(locations):,} municípios únicos encontrados")
    
    # Criar Location nodes
    print("\n🏗️  Criando Location nodes...")
    for loc in tqdm(locations, desc="Locations"):
        session.run("""
            MERGE (l:Location {municipality_code: $code})
            SET l.state = $state
        """, code=loc['code'], state=loc['state'])
    
    # Criar relacionamento BORN_IN em batches
    print("\n🔗 Criando relacionamentos BORN_IN...")
    
    # Fazer em batches para não estourar memória
    batch_size = 100000
    
    result = session.run("MATCH (b:Birth) RETURN count(b) as total")
    total = result.single()['total']
    
    print(f"   Total de nascimentos: {total:,}")
    
    with tqdm(total=total, desc="Linkando", unit="nascimentos") as pbar:
        skip = 0
        while skip < total:
            session.run("""
                MATCH (b:Birth)
                WHERE b.municipality_code IS NOT NULL 
                  AND b.municipality_code <> '0'
                WITH b
                SKIP $skip LIMIT $limit
                MATCH (l:Location {municipality_code: b.municipality_code})
                MERGE (b)-[:BORN_IN]->(l)
            """, skip=skip, limit=batch_size)
            
            skip += batch_size
            pbar.update(batch_size)
    
    # Verificar
    print("\n✅ Verificando...")
    
    result = session.run("MATCH (l:Location) RETURN count(l) as total")
    print(f"   Locations criados: {result.single()['total']:,}")
    
    result = session.run("MATCH ()-[r:BORN_IN]->() RETURN count(r) as total")
    print(f"   Relacionamentos BORN_IN: {result.single()['total']:,}")
    
    # Estatísticas por estado
    print("\n📊 Nascimentos por estado:")
    result = session.run("""
        MATCH (b:Birth)-[:BORN_IN]->(l:Location)
        WHERE l.state <> 'UNK'
        RETURN l.state as estado, count(b) as total
        ORDER BY total DESC
        LIMIT 10
    """)
    
    for r in result:
        print(f"   {r['estado']:3s}: {r['total']:8,}")

driver.close()
print("\n🎉 LOCATIONS ADICIONADOS COM SUCESSO!")
