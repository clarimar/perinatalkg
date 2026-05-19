"""
Carregar dados com DEBUG ativo
"""
from neo4j import GraphDatabase
import polars as pl
from pathlib import Path
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "changeme")

print("🔌 Conectando ao Neo4j...")
driver = GraphDatabase.driver(uri, auth=(user, password))

print("✅ Conectado!")

# Limpar banco
print("\n🗑️  Limpando banco...")
with driver.session() as session:
    session.run("MATCH (n) DETACH DELETE n")
print("✅ Banco limpo!")

# Encontrar dados
data_path = Path.home() / "Projects/climaterna/data/linked"
files = list(data_path.glob("births_climate_2020_*.parquet"))

print(f"\n📁 Arquivos encontrados: {len(files)}")

if not files:
    print("❌ NENHUM ARQUIVO ENCONTRADO!")
    print(f"Procurado em: {data_path}")
    driver.close()
    exit(1)

print(f"Usando: {files[0]}")

# Ler dados
print("\n📊 Lendo dados...")
df = pl.read_parquet(files[0]).head(100)  # Começar com só 100 para debug
print(f"✅ Lidos {len(df):,} registros")

print(f"\nColunas: {df.columns[:10]}")

# Converter para dicts
records = df.to_dicts()
print(f"✅ Convertidos para dicts")

print(f"\nPrimeiro registro (sample):")
print(f"  birth_id: {records[0].get('birth_id')}")
print(f"  birth_weight_grams: {records[0].get('birth_weight_grams')}")
print(f"  temperature_mean_t3: {records[0].get('temperature_mean_t3')}")

# Criar nós manualmente (SEM MERGE, só CREATE)
print(f"\n📝 Criando nós...")

with driver.session() as session:
    for i, row in enumerate(records[:10], 1):  # Só 10 primeiro
        
        # Birth
        session.run("""
            CREATE (b:Birth {
                birth_id: $birth_id,
                birth_weight_grams: $birth_weight_grams,
                gestational_weeks: $gestational_weeks
            })
        """, 
        birth_id=row['birth_id'],
        birth_weight_grams=row['birth_weight_grams'],
        gestational_weeks=row['gestational_weeks']
        )
        
        print(f"  ✓ Birth {i}/10 criado")

print(f"\n✅ Nós criados!")

# Verificar
print(f"\n🔍 Verificando...")
with driver.session() as session:
    result = session.run("MATCH (b:Birth) RETURN count(b) as total")
    record = result.single()
    print(f"   Total de Births: {record['total']}")

driver.close()
print("\n✅ TESTE CONCLUÍDO!")
