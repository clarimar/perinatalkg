"""
Recarga rápida com todos os campos
"""
from neo4j import GraphDatabase
import polars as pl
from pathlib import Path
from tqdm import tqdm
import time

class FastReloader:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "climaterna2025")
        )
        self.stats = {'files': 0, 'births': 0, 'start': time.time()}
    
    def load_file(self, filepath):
        try:
            df = pl.read_parquet(filepath)
            
            required = ['birth_id', 'birth_weight_grams', 'gestational_weeks']
            if not all(c in df.columns for c in required):
                return 0
            
            df = df.filter(
                pl.col('birth_id').is_not_null() &
                pl.col('birth_weight_grams').is_not_null() &
                pl.col('gestational_weeks').is_not_null()
            )
            
            # Defaults
            defaults = {
                'maternal_age': 0, 'maternal_education_years': 0,
                'prenatal_visits': 0, 'temperature_mean_t3': 0.0,
                'days_extreme_heat_t3': 0, 'exposed_extreme_heat_t3': 0,
                'state': 'UNK', 'is_preterm': False, 'municipality_code': 0
            }
            
            for col, val in defaults.items():
                if col not in df.columns:
                    df = df.with_columns(pl.lit(val).alias(col))
                else:
                    df = df.with_columns(pl.col(col).fill_null(val))
            
            records = df.to_dicts()
            
            with self.driver.session() as session:
                for i in range(0, len(records), 10000):
                    batch = records[i:i+10000]
                    
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
        except:
            return 0
    
    def load_all(self):
        data_path = Path.home() / "Projects/climaterna/data/linked"
        files = sorted(list(data_path.glob("births_climate_*.parquet")))
        
        print(f"📊 {len(files)} arquivos\n")
        
        with tqdm(total=len(files), desc="Carregando") as pbar:
            for idx, f in enumerate(files):
                pbar.set_description(f"{f.name[:25]}")
                loaded = self.load_file(f)
                self.stats['files'] += 1
                self.stats['births'] += loaded
                pbar.update(1)
                
                if (idx + 1) % 50 == 0:
                    elapsed = time.time() - self.stats['start']
                    print(f"\n[{idx+1}/{len(files)}] {self.stats['births']:,} | {elapsed/60:.1f}min")
        
        elapsed = time.time() - self.stats['start']
        print(f"\n✅ {self.stats['births']:,} nascimentos em {elapsed/60:.1f} min")
    
    def close(self):
        self.driver.close()

loader = FastReloader()
try:
    loader.load_all()
finally:
    loader.close()

print("\n🎉 RECARGA COMPLETA COM TODOS OS CAMPOS!")
