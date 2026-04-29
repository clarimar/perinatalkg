"""
Versão OTIMIZADA - 10x mais rápida
Estratégia: CREATE em vez de MERGE onde possível
"""
from neo4j import GraphDatabase
import polars as pl
from pathlib import Path
from tqdm import tqdm
import os
import time
from datetime import datetime

class FastLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stats = {'files': 0, 'births': 0, 'skipped': 0, 'start': None}
    
    def close(self):
        self.driver.close()
    
    def clear_db(self):
        print("🗑️  Limpando banco...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("✅ Limpo!")
    
    def create_indexes(self):
        print("📐 Criando índices...")
        with self.driver.session() as session:
            # Índices apenas - sem constraints que travam
            session.run("CREATE INDEX birth_id_idx IF NOT EXISTS FOR (b:Birth) ON (b.birth_id)")
            session.run("CREATE INDEX mun_code_idx IF NOT EXISTS FOR (l:Location) ON (l.municipality_code)")
        print("✅ Índices criados!")
    
    def load_file_fast(self, filepath, batch_size=10000):
        """Carregamento RÁPIDO - usa CREATE"""
        try:
            df = pl.read_parquet(filepath)
            
            if len(df) == 0:
                return 0
            
            # Filtrar NULLs essenciais
            df = df.filter(
                pl.col('birth_id').is_not_null() &
                pl.col('birth_weight_grams').is_not_null() &
                pl.col('gestational_weeks').is_not_null()
            )
            
            if len(df) == 0:
                return 0
            
            # Preencher NULLs com defaults
            df = df.with_columns([
                pl.col('maternal_age').fill_null(0),
                pl.col('maternal_education_years').fill_null(0),
                pl.col('prenatal_visits').fill_null(0),
                pl.col('temperature_mean_t3').fill_null(0),
                pl.col('days_extreme_heat_t3').fill_null(0),
                pl.col('exposed_extreme_heat_t3').fill_null(0),
                pl.col('state').fill_null('UNK'),
                pl.col('is_preterm').fill_null(False),
            ])
            
            # Remover registros sem município
            df = df.filter(pl.col('municipality_code').is_not_null())
            
            records = df.to_dicts()
            
            # Processar em batches GRANDES
            with self.driver.session() as session:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    
                    # Query SIMPLIFICADA - usa CREATE (muito mais rápido)
                    session.run("""
                        UNWIND $batch AS row
                        
                        CREATE (b:Birth {
                            birth_id: row.birth_id,
                            birth_weight_grams: row.birth_weight_grams,
                            gestational_weeks: row.gestational_weeks,
                            is_preterm: row.is_preterm,
                            is_low_birth_weight: (row.birth_weight_grams < 2500)
                        })
                        
                        CREATE (m:Mother {
                            maternal_id: row.birth_id + '_mother',
                            age: row.maternal_age,
                            education_years: row.maternal_education_years,
                            prenatal_visits: row.prenatal_visits
                        })
                        
                        CREATE (l:Location {
                            municipality_code: toString(row.municipality_code),
                            state: row.state
                        })
                        
                        CREATE (c:ClimateExposure {
                            birth_id: row.birth_id,
                            trimester: 'T3',
                            mean_temperature: row.temperature_mean_t3,
                            extreme_heat_days: row.days_extreme_heat_t3,
                            exposed_extreme_heat: row.exposed_extreme_heat_t3
                        })
                        
                        CREATE (b)-[:BORN_BY]->(m)
                        CREATE (b)-[:BORN_IN]->(l)
                        CREATE (b)-[:EXPOSED_TO]->(c)
                    """, batch=batch)
            
            return len(records)
            
        except Exception as e:
            print(f"\n❌ Erro: {str(e)[:80]}")
            return 0
    
    def load_all(self, data_path):
        files = sorted(list(Path(data_path).glob("births_climate_*.parquet")))
        print(f"\n📊 {len(files)} arquivos")
        
        self.stats['start'] = time.time()
        
        with tqdm(total=len(files), desc="Carregando", unit="arq") as pbar:
            for idx, f in enumerate(files):
                pbar.set_description(f"[{idx+1}/{len(files)}] {f.name[:20]}")
                
                loaded = self.load_file_fast(f)
                self.stats['files'] += 1
                self.stats['births'] += loaded
                pbar.update(1)
                
                if (idx + 1) % 10 == 0:
                    elapsed = time.time() - self.stats['start']
                    rate = self.stats['files'] / elapsed
                    remaining = (len(files) - idx - 1) / rate
                    print(f"\n  [{idx+1}/{len(files)}] {self.stats['births']:,} nascimentos | "
                          f"{elapsed/60:.0f}min | resta: {remaining/60:.0f}min")
        
        elapsed = time.time() - self.stats['start']
        print(f"\n✅ {self.stats['births']:,} nascimentos em {elapsed/60:.0f} min ({elapsed/3600:.1f}h)")
    
    def verify(self):
        print("\n🔍 Verificando...")
        with self.driver.session() as session:
            result = session.run("MATCH (b:Birth) RETURN count(b) as total")
            total = result.single()['total']
            print(f"   Nascimentos: {total:,}")

def main():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "climaterna2025"
    data_path = Path.home() / "Projects/climaterna/data/linked"
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 CARREGAMENTO ULTRA-OTIMIZADO")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n⚠️  Usa CREATE (não MERGE) = 10x mais rápido")
    print("⚠️  Terá Locations duplicadas (normal)")
    print("\nContinuar? (y/n): ", end='')
    
    if input().lower() != 'y':
        return
    
    loader = FastLoader(uri, user, password)
    
    try:
        loader.clear_db()
        loader.create_indexes()
        loader.load_all(data_path)
        loader.verify()
        
        print("\n✅ CONCLUÍDO!")
        print("🌐 http://localhost:7474")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrompido")
        loader.verify()
    finally:
        loader.close()

if __name__ == "__main__":
    main()
