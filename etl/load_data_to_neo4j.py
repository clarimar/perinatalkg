"""
Carregar dados do ClimaternaKG para Neo4j
Versão: Amostra inicial (10,000 nascimentos para teste)
"""
from neo4j import GraphDatabase
import polars as pl
from pathlib import Path
from tqdm import tqdm
import os

class ClimaternaKGLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Limpar banco para recomeçar"""
        print("🗑️  Limpando banco de dados...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Banco limpo!")
    
    def create_constraints(self):
        """Criar constraints e índices"""
        print("📐 Criando constraints e índices...")
        
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT birth_id IF NOT EXISTS FOR (b:Birth) REQUIRE b.birth_id IS UNIQUE",
                "CREATE CONSTRAINT municipality_code IF NOT EXISTS FOR (l:Location) REQUIRE l.municipality_code IS UNIQUE",
                "CREATE CONSTRAINT quartile_id IF NOT EXISTS FOR (q:TemperatureQuartile) REQUIRE q.quartile IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✓ {constraint.split('FOR')[1].split('REQUIRE')[0].strip()}")
                except Exception as e:
                    print(f"  ⚠ Constraint já existe")
        
        print("✅ Constraints criadas!")
    
    def load_sample_births(self, data_path, sample_size=10000):
        """Carregar amostra de nascimentos"""
        print(f"\n📊 Carregando amostra de {sample_size:,} nascimentos...")
        
        files = list(Path(data_path).glob("births_climate_2020_*.parquet"))
        
        if not files:
            print(f"❌ Nenhum arquivo encontrado em {data_path}")
            return
        
        df = pl.read_parquet(files[0]).head(sample_size)
        
        print(f"✓ Carregados {len(df):,} registros de {files[0].name}")
        
        records = df.to_dicts()
        
        batch_size = 1000
        
        with self.driver.session() as session:
            for i in tqdm(range(0, len(records), batch_size), desc="Carregando batches"):
                batch = records[i:i+batch_size]
                
                session.run("""
                    UNWIND $batch AS row
                    
                    MERGE (b:Birth {birth_id: row.birth_id})
                    SET b.birth_weight_grams = row.birth_weight_grams,
                        b.gestational_weeks = row.gestational_weeks,
                        b.is_preterm = row.is_preterm,
                        b.is_low_birth_weight = (row.birth_weight_grams < 2500)
                    
                    MERGE (m:Mother {maternal_id: row.birth_id + '_mother'})
                    SET m.age = row.maternal_age,
                        m.education_years = row.maternal_education_years,
                        m.prenatal_visits = row.prenatal_visits
                    
                    MERGE (l:Location {municipality_code: 'MUN_' + toString(row.birth_id)})
                    
                    MERGE (c:ClimateExposure {
                        birth_id: row.birth_id,
                        trimester: 'T3'
                    })
                    SET c.mean_temperature = row.temperature_mean_t3,
                        c.extreme_heat_days = row.days_extreme_heat_t3,
                        c.exposed_extreme_heat = row.exposed_extreme_heat_t3
                    
                    MERGE (b)-[:BORN_BY]->(m)
                    MERGE (b)-[:BORN_IN]->(l)
                    MERGE (b)-[:EXPOSED_TO]->(c)
                """, batch=batch)
        
        print(f"✅ {len(records):,} nascimentos carregados!")
    
    def load_temperature_quartiles(self):
        """Criar nós de quartis de temperatura"""
        print("\n🌡️  Criando quartis de temperatura...")
        
        with self.driver.session() as session:
            quartiles = [
                {'quartile': 'Q1', 'mean_temp': 19.6, 'range': '11-22°C', 'description': 'Cold'},
                {'quartile': 'Q2', 'mean_temp': 23.2, 'range': '22-24°C', 'description': 'Medium-Cold'},
                {'quartile': 'Q3', 'mean_temp': 25.8, 'range': '24-27°C', 'description': 'Medium-Hot'},
                {'quartile': 'Q4', 'mean_temp': 28.0, 'range': '27-32°C', 'description': 'Hot'},
            ]
            
            for q in quartiles:
                session.run("""
                    MERGE (q:TemperatureQuartile {quartile: $quartile})
                    SET q.mean_regional_temp = $mean_temp,
                        q.temp_range = $range,
                        q.description = $description
                """, **q)
        
        print("✅ Quartis criados!")
    
    def create_sample_queries(self):
        """Executar queries de exemplo"""
        print("\n🔍 Executando queries de exemplo...")
        
        with self.driver.session() as session:
            # Query 1: Count por tipo de nó
            print("\n1️⃣  Contagem de nós:")
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            for record in result:
                print(f"   {record['type']:20s}: {record['count']:,}")
            
            # Query 2: Média de peso por exposição
            print("\n2️⃣  Peso médio por exposição a calor extremo:")
            result = session.run("""
                MATCH (b:Birth)-[:EXPOSED_TO]->(c:ClimateExposure)
                WHERE c.trimester = 'T3'
                RETURN c.exposed_extreme_heat as exposed,
                       AVG(b.birth_weight_grams) as avg_weight,
                       COUNT(b) as total
                ORDER BY exposed
            """)
            for record in result:
                exposed = "Exposto" if record['exposed'] == 1 else "Não exposto"
                print(f"   {exposed:15s}: {record['avg_weight']:.1f}g (n={record['total']:,})")
            
            # Query 3: Baixo peso (CORRIGIDO)
            print("\n3️⃣  Taxa de baixo peso:")
            result = session.run("""
                MATCH (b:Birth)
                WITH COUNT(b) as total_births,
                     SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as low_weight_births
                RETURN total_births, low_weight_births
            """)
            
            record = result.single()
            if record and record['total_births'] > 0:
                total = record['total_births']
                low = record['low_weight_births']
                print(f"   Baixo peso: {low:,} / {total:,} ({low/total*100:.1f}%)")
            else:
                print("   Nenhum dado encontrado")

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "climaterna2025")
    
    data_path = Path.home() / "Projects/climaterna/data/linked"
    
    if not data_path.exists():
        print(f"⚠️  Dados não encontrados em {data_path}")
        return
    
    print("🚀 Iniciando ClimaternaKG Loader...")
    loader = ClimaternaKGLoader(uri, user, password)
    
    try:
        loader.clear_database()
        loader.create_constraints()
        loader.load_temperature_quartiles()
        loader.load_sample_births(data_path, sample_size=10000)
        loader.create_sample_queries()
        
        print("\n" + "="*60)
        print("✅ KNOWLEDGE GRAPH CRIADO COM SUCESSO!")
        print("="*60)
        print("\n🌐 Acesse: http://localhost:7474")
        print("   User: neo4j")
        print("   Pass: climaterna2025")
        
    finally:
        loader.close()

if __name__ == "__main__":
    main()
