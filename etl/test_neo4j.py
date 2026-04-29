"""
Testar conexão com Neo4j
"""
from neo4j import GraphDatabase
import os

# Credenciais
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "climaterna2025")

print(f"🔌 Conectando ao Neo4j...")
print(f"   URI: {uri}")
print(f"   User: {user}")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        result = session.run("RETURN 'Conexão bem-sucedida!' AS message")
        for record in result:
            print(f"\n✅ {record['message']}")
        
        # Info do banco
        result = session.run("""
            CALL dbms.components() 
            YIELD name, versions 
            RETURN name, versions[0] AS version
        """)
        
        print("\n📊 Informações do Neo4j:")
        for record in result:
            print(f"   {record['name']}: {record['version']}")
    
    driver.close()
    print("\n✅ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    print("\nVerifique se o Neo4j está rodando:")
    print("   sudo systemctl status neo4j")
