"""
Carregar TODOS os dados do ClimaternaKG para Neo4j
Versão otimizada para 27M nascimentos
"""
from neo4j import GraphDatabase
import polars as pl
from pathlib import Path
from tqdm import tqdm
import os
import time
from datetime import datetime

class ClimaternaKGFullLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stats = {
            'files_processed': 0,
            'births_loaded': 0,
            'errors': 0,
            'start_time': None
        }
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Limpar banco de dados"""
        print("\n🗑️  Limpando banco de dados...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Banco limpo!")
    
    def create_constraints(self):
        """Criar constraints e índices para performance"""
        print("\n📐 Criando constraints e índices...")
        
        with self.driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT birth_id_unique IF NOT EXISTS FOR (b:Birth) REQUIRE b.birth_id IS UNIQUE",
                "CREATE CONSTRAINT location_code_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.municipality_code IS UNIQUE",
                "CREATE CONSTRAINT quartile_unique IF NOT EXISTS FOR (q:TemperatureQuartile) REQUIRE q.quartile IS UNIQUE",
                "CREATE INDEX birth_weight IF NOT EXISTS FOR (b:Birth) ON (b.birth_weight_grams)",
                "CREATE INDEX exposed_heat IF NOT EXISTS FOR (c:ClimateExposure) ON (c.exposed_extreme_heat)",
                "CREATE INDEX trimester IF NOT EXISTS FOR (c:ClimateExposure) ON (c.trimester)",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✓ {constraint.split('IF NOT EXISTS')[0].strip()}")
                except Exception as e:
                    print(f"  ⚠ Já existe ou erro")
        
        print("✅ Constraints e índices criados!")
    
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
    
    def load_file(self, filepath, batch_size=5000):
        """Carregar um arquivo parquet"""
        try:
            # Ler arquivo
            df = pl.read_parquet(filepath)
            
            if len(df) == 0:
                return 0
            
            records = df.to_dicts()
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            # Processar em batches
            with self.driver.session() as session:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    
                    session.run("""
                        UNWIND $batch AS row
                        
                        // Criar Birth
                        MERGE (b:Birth {birth_id: row.birth_id})
                        SET b.birth_weight_grams = row.birth_weight_grams,
                            b.gestational_weeks = row.gestational_weeks,
                            b.is_preterm = row.is_preterm,
                            b.is_low_birth_weight = (row.birth_weight_grams < 2500)
                        
                        // Criar Mother
                        MERGE (m:Mother {maternal_id: row.birth_id + '_mother'})
                        SET m.age = row.maternal_age,
                            m.education_years = row.maternal_education_years,
                            m.prenatal_visits = row.prenatal_visits
                        
                        // Criar Location
                        MERGE (l:Location {municipality_code: toString(row.municipality_code)})
                        SET l.state = row.state
                        
                        // Criar ClimateExposure T3
                        MERGE (c:ClimateExposure {
                            birth_id: row.birth_id,
                            trimester: 'T3'
                        })
                        SET c.mean_temperature = row.temperature_mean_t3,
                            c.extreme_heat_days = row.days_extreme_heat_t3,
                            c.exposed_extreme_heat = row.exposed_extreme_heat_t3
                        
                        // Relacionamentos
                        MERGE (b)-[:BORN_BY]->(m)
                        MERGE (b)-[:BORN_IN]->(l)
                        MERGE (b)-[:EXPOSED_TO]->(c)
                    """, batch=batch)
            
            return len(records)
            
        except Exception as e:
            print(f"\n❌ Erro ao processar {filepath.name}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def load_all_files(self, data_path):
        """Carregar todos os arquivos"""
        files = sorted(list(Path(data_path).glob("births_climate_*.parquet")))
        
        print(f"\n📊 Total de arquivos: {len(files)}")
        print(f"Começando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.stats['start_time'] = time.time()
        
        # Progress bar para arquivos
        with tqdm(total=len(files), desc="Processando arquivos", unit="arquivo") as pbar:
            for filepath in files:
                # Mostrar arquivo atual
                pbar.set_description(f"Processando {filepath.name[:30]}")
                
                # Carregar arquivo
                births_loaded = self.load_file(filepath)
                
                # Atualizar estatísticas
                self.stats['files_processed'] += 1
                self.stats['births_loaded'] += births_loaded
                
                # Atualizar progress bar
                pbar.update(1)
                
                # Mostrar estatísticas a cada 10 arquivos
                if self.stats['files_processed'] % 10 == 0:
                    elapsed = time.time() - self.stats['start_time']
                    rate = self.stats['files_processed'] / elapsed
                    remaining = (len(files) - self.stats['files_processed']) / rate
                    
                    print(f"\n  📊 Progresso:")
                    print(f"     Arquivos: {self.stats['files_processed']}/{len(files)}")
                    print(f"     Nascimentos: {self.stats['births_loaded']:,}")
                    print(f"     Tempo decorrido: {elapsed/60:.1f} min")
                    print(f"     Tempo restante: {remaining/60:.1f} min")
        
        elapsed_total = time.time() - self.stats['start_time']
        
        print(f"\n✅ Carregamento concluído!")
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   Arquivos processados: {self.stats['files_processed']}")
        print(f"   Nascimentos carregados: {self.stats['births_loaded']:,}")
        print(f"   Erros: {self.stats['errors']}")
        print(f"   Tempo total: {elapsed_total/60:.1f} minutos ({elapsed_total/3600:.2f} horas)")
        print(f"   Taxa: {self.stats['births_loaded']/elapsed_total:.0f} nascimentos/segundo")
    
    def verify_load(self):
        """Verificar carregamento"""
        print(f"\n🔍 Verificando dados carregados...")
        
        with self.driver.session() as session:
            # Contar nós
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            print(f"\n📊 Nós criados:")
            for record in result:
                print(f"   {record['type']:20s}: {record['count']:,}")
            
            # Estatísticas de nascimentos
            result = session.run("""
                MATCH (b:Birth)
                RETURN 
                    COUNT(b) as total,
                    AVG(b.birth_weight_grams) as avg_weight,
                    SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as low_weight
            """)
            
            record = result.single()
            print(f"\n📈 Estatísticas:")
            print(f"   Total de nascimentos: {record['total']:,}")
            print(f"   Peso médio: {record['avg_weight']:.0f}g")
            print(f"   Baixo peso: {record['low_weight']:,} ({record['low_weight']/record['total']*100:.1f}%)")

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "changeme")
    
    data_path = Path.home() / "Projects/climaterna/data/linked"
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 CLIMATERNAKQ - CARREGAMENTO COMPLETO")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    loader = ClimaternaKGFullLoader(uri, user, password)
    
    try:
        loader.clear_database()
        loader.create_constraints()
        loader.load_temperature_quartiles()
        loader.load_all_files(data_path)
        loader.verify_load()
        
        print("\n" + "="*60)
        print("✅ CLIMATERNAKQ KNOWLEDGE GRAPH COMPLETO CRIADO!")
        print("="*60)
        print("\n🌐 Acesse: http://localhost:7474")
        print("   User: neo4j")
        print("   Pass: [set NEO4J_PASSWORD env var]")
        
    finally:
        loader.close()

if __name__ == "__main__":
    main()
