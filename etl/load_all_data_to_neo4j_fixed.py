"""
Carregar TODOS os dados do ClimaternaKG para Neo4j
Versão CORRIGIDA - lida com valores NULL
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
            'births_skipped': 0,
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
                    print(f"  ✓ {constraint.split('IF NOT EXISTS')[0].strip()[:50]}...")
                except:
                    print(f"  ⚠ Já existe")
        
        print("✅ Constraints e índices criados!")
    
    def load_temperature_quartiles(self):
        """Criar nós de quartis de temperatura"""
        print("\n🌡️  Criando quartis de temperatura...")
        
        with self.driver.session() as session:
            quartiles = [
                {'quartile': 'Q1', 'mean_temp': 19.6},
                {'quartile': 'Q2', 'mean_temp': 23.2},
                {'quartile': 'Q3', 'mean_temp': 25.8},
                {'quartile': 'Q4', 'mean_temp': 28.0},
            ]
            
            for q in quartiles:
                session.run("""
                    MERGE (q:TemperatureQuartile {quartile: $quartile})
                    SET q.mean_regional_temp = $mean_temp
                """, **q)
        
        print("✅ Quartis criados!")
    
    def load_file(self, filepath, batch_size=5000):
        """Carregar um arquivo parquet - VERSÃO CORRIGIDA"""
        try:
            # Ler arquivo
            df = pl.read_parquet(filepath)
            
            if len(df) == 0:
                return 0
            
            # FILTRAR registros com dados essenciais válidos
            df_clean = df.filter(
                pl.col('birth_id').is_not_null() &
                pl.col('birth_weight_grams').is_not_null() &
                pl.col('gestational_weeks').is_not_null()
            )
            
            skipped = len(df) - len(df_clean)
            if skipped > 0:
                self.stats['births_skipped'] += skipped
            
            if len(df_clean) == 0:
                return 0
            
            records = df_clean.to_dicts()
            
            # Processar em batches
            with self.driver.session() as session:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    
                    # Query CORRIGIDA - trata NULLs
                    session.run("""
                        UNWIND $batch AS row
                        
                        // Criar Birth (sempre válido)
                        MERGE (b:Birth {birth_id: row.birth_id})
                        SET b.birth_weight_grams = row.birth_weight_grams,
                            b.gestational_weeks = row.gestational_weeks,
                            b.is_preterm = COALESCE(row.is_preterm, false),
                            b.is_low_birth_weight = (row.birth_weight_grams < 2500)
                        
                        // Criar Mother (com dados opcionais)
                        WITH b, row
                        MERGE (m:Mother {maternal_id: row.birth_id + '_mother'})
                        SET m.age = COALESCE(row.maternal_age, 0),
                            m.education_years = COALESCE(row.maternal_education_years, 0),
                            m.prenatal_visits = COALESCE(row.prenatal_visits, 0)
                        
                        // Criar Location APENAS se municipality_code não for NULL
                        WITH b, m, row
                        FOREACH (ignoreMe IN CASE WHEN row.municipality_code IS NOT NULL THEN [1] ELSE [] END |
                            MERGE (l:Location {municipality_code: toString(row.municipality_code)})
                            SET l.state = COALESCE(row.state, 'UNKNOWN')
                            MERGE (b)-[:BORN_IN]->(l)
                        )
                        
                        // Criar ClimateExposure T3 (com dados opcionais)
                        WITH b, m, row
                        MERGE (c:ClimateExposure {
                            birth_id: row.birth_id,
                            trimester: 'T3'
                        })
                        SET c.mean_temperature = COALESCE(row.temperature_mean_t3, 0),
                            c.extreme_heat_days = COALESCE(row.days_extreme_heat_t3, 0),
                            c.exposed_extreme_heat = COALESCE(row.exposed_extreme_heat_t3, 0)
                        
                        // Relacionamentos básicos
                        MERGE (b)-[:BORN_BY]->(m)
                        MERGE (b)-[:EXPOSED_TO]->(c)
                    """, batch=batch)
            
            return len(records)
            
        except Exception as e:
            print(f"\n❌ Erro ao processar {filepath.name}: {str(e)[:100]}")
            self.stats['errors'] += 1
            return 0
    
    def load_all_files(self, data_path, start_from=0):
        """Carregar todos os arquivos - com opção de retomar"""
        files = sorted(list(Path(data_path).glob("births_climate_*.parquet")))
        
        print(f"\n📊 Total de arquivos: {len(files)}")
        if start_from > 0:
            print(f"⏭️  Retomando do arquivo #{start_from}")
            files = files[start_from:]
        
        print(f"Começando em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.stats['start_time'] = time.time()
        
        # Progress bar
        with tqdm(total=len(files), desc="Processando arquivos", unit="arq") as pbar:
            for idx, filepath in enumerate(files, start=start_from):
                pbar.set_description(f"[{idx+1}/{len(files)+start_from}] {filepath.name[:25]}")
                
                births_loaded = self.load_file(filepath)
                
                self.stats['files_processed'] += 1
                self.stats['births_loaded'] += births_loaded
                
                pbar.update(1)
                
                # Estatísticas a cada 10 arquivos
                if self.stats['files_processed'] % 10 == 0:
                    self.print_progress(len(files) + start_from, idx + 1)
        
        self.print_final_stats()
    
    def print_progress(self, total_files, current_file):
        """Imprimir progresso"""
        elapsed = time.time() - self.stats['start_time']
        rate = self.stats['files_processed'] / elapsed
        remaining = (total_files - current_file) / rate if rate > 0 else 0
        
        print(f"\n  📊 Progresso:")
        print(f"     Arquivos: {current_file}/{total_files} ({current_file/total_files*100:.1f}%)")
        print(f"     Nascimentos carregados: {self.stats['births_loaded']:,}")
        print(f"     Nascimentos pulados (dados faltantes): {self.stats['births_skipped']:,}")
        print(f"     Erros: {self.stats['errors']}")
        print(f"     Tempo decorrido: {elapsed/60:.1f} min")
        print(f"     Tempo restante estimado: {remaining/60:.1f} min")
        print(f"     Taxa: {self.stats['births_loaded']/elapsed:.0f} nascimentos/seg")
    
    def print_final_stats(self):
        """Estatísticas finais"""
        elapsed_total = time.time() - self.stats['start_time']
        
        print(f"\n" + "="*70)
        print(f"✅ CARREGAMENTO CONCLUÍDO!")
        print(f"="*70)
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   Arquivos processados: {self.stats['files_processed']}")
        print(f"   Nascimentos carregados: {self.stats['births_loaded']:,}")
        print(f"   Nascimentos pulados: {self.stats['births_skipped']:,}")
        print(f"   Erros: {self.stats['errors']}")
        print(f"   Tempo total: {elapsed_total/60:.1f} min ({elapsed_total/3600:.2f} horas)")
        print(f"   Taxa média: {self.stats['births_loaded']/elapsed_total:.0f} nascimentos/seg")
    
    def verify_load(self):
        """Verificar dados carregados"""
        print(f"\n🔍 Verificando dados no Knowledge Graph...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            print(f"\n📊 Nós criados:")
            for record in result:
                print(f"   {record['type']:20s}: {record['count']:,}")
            
            result = session.run("""
                MATCH (b:Birth)
                RETURN 
                    COUNT(b) as total,
                    AVG(b.birth_weight_grams) as avg_weight,
                    SUM(CASE WHEN b.is_low_birth_weight THEN 1 ELSE 0 END) as low_weight
            """)
            
            record = result.single()
            if record and record['total']:
                print(f"\n📈 Estatísticas de Nascimentos:")
                print(f"   Total: {record['total']:,}")
                print(f"   Peso médio: {record['avg_weight']:.0f}g")
                print(f"   Baixo peso: {record['low_weight']:,} ({record['low_weight']/record['total']*100:.1f}%)")

def main():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "changeme")
    data_path = Path.home() / "Projects/climaterna/data/linked"
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 CLIMATERNAKQ - CARREGAMENTO COMPLETO (CORRIGIDO)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    loader = ClimaternaKGFullLoader(uri, user, password)
    
    try:
        # Perguntar se quer limpar banco ou retomar
        print("\nO banco já tem dados. O que fazer?")
        print("1) Limpar e recomeçar do zero")
        print("2) Continuar de onde parou (não implementado ainda)")
        choice = input("Escolha (1 ou 2): ")
        
        if choice == "1":
            loader.clear_database()
            loader.create_constraints()
            loader.load_temperature_quartiles()
            loader.load_all_files(data_path, start_from=0)
        else:
            print("Continuando...")
            loader.load_all_files(data_path, start_from=17)  # Continuar de PR
        
        loader.verify_load()
        
        print("\n" + "="*70)
        print("✅ CLIMATERNAKQ KNOWLEDGE GRAPH CRIADO!")
        print("="*70)
        print("\n🌐 Neo4j Browser: http://localhost:7474")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERROMPIDO PELO USUÁRIO")
        loader.print_final_stats()
        loader.verify_load()
        print("\nVocê pode retomar depois editando start_from= no script")
    
    finally:
        loader.close()

if __name__ == "__main__":
    main()
