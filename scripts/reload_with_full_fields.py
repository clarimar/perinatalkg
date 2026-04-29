"""
Recarregar com TODOS os campos incluindo municipality_code e state
"""
from neo4j import GraphDatabase
import polars as pl
from pathlib import Path
from tqdm import tqdm
import time

class FullFieldsLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.stats = {'files': 0, 'births': 0, 'start': None}
    
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
            session.run("CREATE INDEX birth_id_idx IF NOT EXISTS FOR (b:Birth) ON (b.birth_id)")
            session.run("CREATE INDEX mun_code_idx IF NOT EXISTS FOR (b:Birth) ON (b.municipality_code)")
        print("✅ Índices OK!")
    
    def load_file(self, filepath, batch_size=10000):
        try:
            df = pl.read_parquet(filepath)
            
            if len(df) == 0:
                return 0
            
            # Filtrar essenciais
            required = ['birth_id', 'birth_weight_grams', 'gestational_weeks']
            if not all(c in df.columns for c in required):
                return 0
            
            df = df.filter(
                pl.col('birth_id').is_not_null() &
                pl.col('birth_weight_grams').is_not_null() &
                pl.col('gestational_weeks').is_not_null()
            )
            
            # Adicionar defaults
            defaults = {
                'maternal_age': 0,
                'maternal_education_years': 0,
                'prenatal_visits': 0,
                'temperature_mean_t3': 0.0,
                'days_extreme_heat_t3': 0,
                'exposed_extreme_heat_t3': 0,
                'state': 'UNK',
                'is_preterm': False,
                'municipality_code': 0
            }
            
            for col, default in defaults.items():
                if col not in df.columns:
                    df = df.with_columns(pl.lit(default).alias(col))
                else:
                    df = df.with_columns(pl.col(col).fill_null(default))
            
            records = df.to_dicts()
            
            with self.driver.session() as session:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    
                    # AGORA COM municipality_code e state!
                    session.run("""
                        UNWIND $batch AS row
                        
                        CREATE (b:Birth {
                            birth_id: row.birth_id,
                            birth_weight_grams: row.birth_weight_grams,
                            gestational_weeks: row.gestational_weeks,
                            is_preterm: row.is_preterm,
                            is_low_birth_weight: (row.birth_weight_grams < 2500),
                            municipality_code: toString(row.municipality_code),
                            state: row.state
                        })
                        
                        CREATE (m:Mother {
                            maternal_id: row.birth_id + '_m',
                            age: row.maternal_age,
                            education_years: row.maternal_education_years,
                            prenatal_visits: row.prenatal_visits
                        })
                        
                        CREATE (c:ClimateExposure {
                            birth_id: row.birth_id,
                            trimester: 'T3',
                            mean_temperature: row.temperature_mean_t3,
                            extreme_heat_days: row.days_extreme_heat_t3,
                            exposed_extreme_heat: row.exposed_extreme_heat_t3
                        })
                        
                        CREATE (b)-[:BORN_BY]->(m)
                        CREATE (b)-[:EXPOSED_TO]->(c)
                    """, batch=batch)
            
            return len(records)
            
        except Exception as e:
            return 0
    
    def load_all(self, data_path):
        files = sorted(list(Path(data_path).glob("births_climate_*.parquet")))
        print(f"\n📊 {len(files)} arquivos")
        
        self.stats['start'] = time.time()
        
        with tqdm(total=len(files), desc="Carregando", unit="arq") as pbar:
            for idx, f in enumerate(files):
                pbar.set_description(f"{f.name[:25]}")
                
                loaded = self.load_file(f)
                self.stats['files'] += 1
                self.stats['births'] += loaded
                pbar.update(1)
                
                if (idx + 1) % 50 == 0:
                    elapsed = time.time() - self.stats['start']
                    print(f"\n  [{idx+1}/{len(files)}] {self.stats['births']:,} | {elapsed/60:.1f}min")
        
        elapsed = time.time() - self.stats['start']
        print(f"\n✅ {self.stats['births']:,} em {elapsed/60:.1f} min")

loader = FullFieldsLoader("bolt://localhost:7687", "neo4j", "climaterna2025")

print("⚠️  ATENÇÃO: Isso vai limpar o banco e recarregar tudo (~2h)")
print("Continuar? (y/n):", end=' ')
response = input()

if response.lower() == 'y':
    try:
        loader.clear_db()
        loader.create_indexes()
        loader.load_all(Path.home() / "Projects/climaterna/data/linked")
        
        print("\n✅ RECARREGAMENTO COMPLETO!")
        
    finally:
        loader.close()
else:
    print("Cancelado")
