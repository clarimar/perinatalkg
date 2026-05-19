"""
Adicionar Location nodes ao ClimaternaKG
"""
from neo4j import GraphDatabase
from tqdm import tqdm

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.getenv("NEO4J_PASSWORD", "changeme")))

print("🗺️  Extraindo municípios únicos dos dados...")

with driver.session() as session:
    # Extrair todos os municipality_code únicos
    result = session.run("""
        MATCH (b:Birth)
        WHERE b.municipality_code IS NOT NULL
        RETURN DISTINCT 
            b.municipality_code as code,
            b.state as state
    """)
    
    locations = []
    for record in result:
        if record['code']:
            locations.append({
                'code': str(record['code']),
                'state': record['state'] if record['state'] else 'UNK'
            })
    
    print(f"📊 {len(locations)} municípios únicos encontrados")
    
    # Criar Location nodes
    print("\n🏗️  Criando Location nodes...")
    for loc in tqdm(locations, desc="Criando Locations"):
        session.run("""
            MERGE (l:Location {municipality_code: $code})
            SET l.state = $state
        """, code=loc['code'], state=loc['state'])
    
    # Criar relacionamento BORN_IN
    print("\n🔗 Criando relacionamentos BORN_IN...")
    session.run("""
        MATCH (b:Birth), (l:Location)
        WHERE b.municipality_code = l.municipality_code
        CREATE (b)-[:BORN_IN]->(l)
    """)
    
    # Verificar
    result = session.run("""
        MATCH (l:Location)
        RETURN count(l) as total
    """)
    print(f"\n✅ {result.single()['total']} Location nodes criados!")
    
    result = session.run("""
        MATCH ()-[r:BORN_IN]->()
        RETURN count(r) as total
    """)
    print(f"✅ {result.single()['total']:,} relacionamentos BORN_IN criados!")

driver.close()
