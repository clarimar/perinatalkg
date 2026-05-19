"""
Inspecionar propriedades dos Birth nodes
"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", os.getenv("NEO4J_PASSWORD", "changeme")))

with driver.session() as session:
    # Ver propriedades de um Birth node
    result = session.run("""
        MATCH (b:Birth)
        RETURN b LIMIT 1
    """)
    
    birth = result.single()['b']
    print("📊 Propriedades de um Birth node:")
    for key, value in birth.items():
        print(f"   {key}: {value}")

driver.close()
