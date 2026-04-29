"""
Verificar dados no Knowledge Graph
"""
from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "climaterna2025")

print("🔍 Conectando ao Neo4j...")
driver = GraphDatabase.driver(uri, auth=(user, password))

with driver.session() as session:
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DO KNOWLEDGE GRAPH")
    print("="*60)
    
    # Contagem de nós
    print("\n🔢 Nós por tipo:")
    result = session.run("""
        MATCH (n)
        RETURN labels(n)[0] as type, count(n) as count
        ORDER BY count DESC
    """)
    for record in result:
        print(f"   {record['type']:25s}: {record['count']:,}")
    
    # Contagem de relacionamentos
    print("\n🔗 Relacionamentos:")
    result = session.run("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    for record in result:
        print(f"   {record['rel_type']:25s}: {record['count']:,}")
    
    # Estatísticas de nascimentos
    print("\n👶 Estatísticas de Nascimentos:")
    result = session.run("""
        MATCH (b:Birth)
        RETURN 
            COUNT(b) as total,
            AVG(b.birth_weight_grams) as avg_weight,
            MIN(b.birth_weight_grams) as min_weight,
            MAX(b.birth_weight_grams) as max_weight
    """)
    record = result.single()
    print(f"   Total: {record['total']:,}")
    print(f"   Peso médio: {record['avg_weight']:.0f}g")
    print(f"   Peso mín: {record['min_weight']:.0f}g")
    print(f"   Peso máx: {record['max_weight']:.0f}g")
    
    # Exposição
    print("\n🌡️  Exposição a Calor Extremo:")
    result = session.run("""
        MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
        WITH c.exposed_extreme_heat as exposed, COUNT(b) as total
        RETURN exposed, total
        ORDER BY exposed
    """)
    for record in result:
        status = "Exposto" if record['exposed'] == 1 else "Não exposto"
        print(f"   {status:15s}: {record['total']:,}")

driver.close()
print("\n" + "="*60)
