#!/usr/bin/env python3
"""
bench_perinatalkg.py — PerinatalKG SPARQL vs DuckDB benchmark
Runs 8 queries × N repetitions on both engines and writes CSV results.

Usage:
  python bench_perinatalkg.py \
    --endpoint http://localhost:3030/perinatalkg/sparql \
    --parquet-dir data/linked \
    --reps 10 --warmup 3 --seed 20260803 \
    --out results/
"""

import argparse, time, csv, os, glob, statistics, json, sys
from pathlib import Path
from datetime import datetime

import requests
import polars as pl
import duckdb

# ── QUERY DEFINITIONS ────────────────────────────────────────────────────────

PKG = "http://perinatalkg.org/ontology/"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

SPARQL_PREFIX = f"""
PREFIX rdf: <{RDF}>
PREFIX pkg: <{PKG}>
"""

SPARQL_QUERIES = {
    "Q1_total_triples": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }",
        "sql": "SELECT COUNT(*) AS n FROM births",
        "description": "Total count (triples vs rows)"
    },
    "Q2_birth_count": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(?b) AS ?n) WHERE { ?b rdf:type pkg:Birth }",
        "sql": "SELECT COUNT(*) AS n FROM births",
        "description": "COUNT of Birth individuals"
    },
    "Q3_preterm_count": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(?b) AS ?n) WHERE { ?b rdf:type pkg:PretermBirth }",
        "sql": "SELECT COUNT(*) AS n FROM births WHERE gestational_weeks < 37 AND gestational_weeks IS NOT NULL",
        "description": "COUNT of preterm births (<37w)"
    },
    "Q4_term_count": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(?b) AS ?n) WHERE { ?b rdf:type pkg:TermBirth }",
        "sql": "SELECT COUNT(*) AS n FROM births WHERE gestational_weeks >= 37 AND gestational_weeks < 42",
        "description": "COUNT of term births (37-41w)"
    },
    "Q5_postterm_count": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(?b) AS ?n) WHERE { ?b rdf:type pkg:PostTermBirth }",
        "sql": "SELECT COUNT(*) AS n FROM births WHERE gestational_weeks >= 42",
        "description": "COUNT of post-term births (>=42w)"
    },
    "Q6_lbw_count": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(?b) AS ?n) WHERE { ?b rdf:type pkg:LowBirthWeight }",
        "sql": "SELECT COUNT(*) AS n FROM births WHERE birth_weight_grams < 2500 AND birth_weight_grams IS NOT NULL",
        "description": "COUNT of low birth weight (<2500g)"
    },
    "Q7_extreme_heat": {
        "sparql": SPARQL_PREFIX + "SELECT (COUNT(?b) AS ?n) WHERE { ?b rdf:type pkg:ExtremeHeatExposure }",
        "sql": "SELECT COUNT(*) AS n FROM births WHERE exposed_extreme_heat_t3 = 1",
        "description": "COUNT of extreme heat exposure T3"
    },
    "Q8_avg_birthweight": {
        "sparql": SPARQL_PREFIX + "SELECT (AVG(?w) AS ?mean) WHERE { ?b pkg:birthWeight ?w }",
        "sql": "SELECT AVG(birth_weight_grams) AS mean FROM births WHERE birth_weight_grams IS NOT NULL",
        "description": "AVG birth weight"
    },
}

# ── SPARQL RUNNER ─────────────────────────────────────────────────────────────

def run_sparql(endpoint, query, timeout=120):
    t0 = time.perf_counter()
    r = requests.post(
        endpoint,
        data={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=timeout
    )
    elapsed = time.perf_counter() - t0
    r.raise_for_status()
    bindings = r.json()["results"]["bindings"]
    result = bindings[0][list(bindings[0].keys())[0]]["value"] if bindings else None
    return elapsed, result

# ── DUCKDB RUNNER ─────────────────────────────────────────────────────────────

def load_duckdb(parquet_dir):
    """Load all GO Parquet files into DuckDB in-memory."""
    con = duckdb.connect()
    files = sorted(glob.glob(os.path.join(parquet_dir, "births_climate_*_GO_linked.parquet")))
    if not files:
        # Try any parquet files
        files = sorted(glob.glob(os.path.join(parquet_dir, "*.parquet")))
    if not files:
        raise FileNotFoundError(f"No Parquet files found in {parquet_dir}")
    print(f"Loading {len(files)} Parquet file(s) into DuckDB...")
    con.execute(f"CREATE VIEW births AS SELECT * FROM read_parquet({files!r})")
    n = con.execute("SELECT COUNT(*) FROM births").fetchone()[0]
    print(f"DuckDB: {n:,} rows loaded")
    return con

def run_sql(con, query, timeout=120):
    t0 = time.perf_counter()
    result = con.execute(query).fetchone()[0]
    elapsed = time.perf_counter() - t0
    return elapsed, result

# ── BENCHMARK RUNNER ──────────────────────────────────────────────────────────

def benchmark(endpoint, con, reps, warmup, skip_sql=False):
    results = []
    
    for qid, qdata in SPARQL_QUERIES.items():
        print(f"\n── {qid}: {qdata['description']}")
        
        # ── SPARQL ──
        sparql_times = []
        sparql_result = None
        print(f"  SPARQL warmup ({warmup} reps)...", end="", flush=True)
        for _ in range(warmup):
            try:
                _, _ = run_sparql(endpoint, qdata["sparql"])
            except Exception as e:
                print(f" ERROR: {e}")
                break
        print(" done")
        
        print(f"  SPARQL benchmark ({reps} reps)...", end="", flush=True)
        for i in range(reps):
            try:
                t, r = run_sparql(endpoint, qdata["sparql"])
                sparql_times.append(t)
                sparql_result = r
                print(f".", end="", flush=True)
            except Exception as e:
                print(f"\n  SPARQL error on rep {i}: {e}")
                break
        print(f" done — result={sparql_result}")
        
        # ── SQL ──
        sql_times = []
        sql_result = None
        if not skip_sql and qdata.get("sql"):
            print(f"  SQL warmup ({warmup} reps)...", end="", flush=True)
            for _ in range(warmup):
                try:
                    _, _ = run_sql(con, qdata["sql"])
                except Exception as e:
                    print(f" ERROR: {e}")
                    break
            print(" done")
            
            print(f"  SQL benchmark ({reps} reps)...", end="", flush=True)
            for i in range(reps):
                try:
                    t, r = run_sql(con, qdata["sql"])
                    sql_times.append(t)
                    sql_result = r
                    print(f".", end="", flush=True)
                except Exception as e:
                    print(f"\n  SQL error on rep {i}: {e}")
                    break
            print(f" done — result={sql_result}")
        
        def stats(times):
            if not times:
                return {"n": 0, "mean": None, "median": None, "sd": None, "min": None, "max": None}
            return {
                "n": len(times),
                "mean": round(statistics.mean(times), 4),
                "median": round(statistics.median(times), 4),
                "sd": round(statistics.stdev(times), 4) if len(times) > 1 else 0.0,
                "min": round(min(times), 4),
                "max": round(max(times), 4),
            }
        
        ss = stats(sparql_times)
        qs = stats(sql_times)
        
        row = {
            "query_id": qid,
            "description": qdata["description"],
            "sparql_result": sparql_result,
            "sparql_n": ss["n"],
            "sparql_mean_s": ss["mean"],
            "sparql_median_s": ss["median"],
            "sparql_sd_s": ss["sd"],
            "sparql_min_s": ss["min"],
            "sparql_max_s": ss["max"],
            "sql_result": sql_result,
            "sql_n": qs["n"],
            "sql_mean_s": qs["mean"],
            "sql_median_s": qs["median"],
            "sql_sd_s": qs["sd"],
            "sql_min_s": qs["min"],
            "sql_max_s": qs["max"],
            "speedup_sparql_vs_sql": (
                round(ss["mean"] / qs["mean"], 2)
                if ss["mean"] and qs["mean"] and qs["mean"] > 0 else None
            )
        }
        results.append(row)
        print(f"  SPARQL: {ss['mean']}s ± {ss['sd']}s | SQL: {qs['mean']}s ± {qs['sd']}s")
    
    return results

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PerinatalKG benchmark: SPARQL vs DuckDB/SQL")
    parser.add_argument("--endpoint", default="http://localhost:3030/perinatalkg/sparql")
    parser.add_argument("--parquet-dir", default="data/linked")
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260803)
    parser.add_argument("--out", default="results/")
    parser.add_argument("--skip-sql", action="store_true", help="Skip DuckDB/SQL benchmark")
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    
    print("=" * 60)
    print("PerinatalKG Benchmark — SPARQL vs DuckDB/SQL")
    print(f"Endpoint:    {args.endpoint}")
    print(f"Parquet dir: {args.parquet_dir}")
    print(f"Repetitions: {args.reps} + {args.warmup} warmup")
    print(f"Timestamp:   {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Test SPARQL connectivity
    print("\nTesting SPARQL endpoint...", end="", flush=True)
    try:
        r = requests.get(args.endpoint.replace("/sparql", "/$/ping"), timeout=10)
        print(f" OK ({r.status_code})")
    except Exception as e:
        print(f" WARNING: {e} — continuing anyway")
    
    # Load DuckDB
    con = None
    if not args.skip_sql:
        try:
            con = load_duckdb(args.parquet_dir)
        except Exception as e:
            print(f"\nDuckDB load error: {e}")
            print("Continuing with --skip-sql")
            args.skip_sql = True
    
    # Run benchmark
    results = benchmark(args.endpoint, con, args.reps, args.warmup, args.skip_sql)
    
    # Write CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(args.out, f"benchmark_results_{ts}.csv")
    
    fieldnames = list(results[0].keys())
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*60}")
    print(f"Results saved: {csv_path}")
    
    # Print summary table
    print(f"\n{'Query':<25} {'SPARQL mean':>12} {'SPARQL SD':>10} {'SQL mean':>10} {'Speedup':>8}")
    print("-" * 70)
    for r in results:
        sparql = f"{r['sparql_mean_s']}s" if r['sparql_mean_s'] else "—"
        sd = f"±{r['sparql_sd_s']}s" if r['sparql_sd_s'] is not None else "—"
        sql = f"{r['sql_mean_s']}s" if r['sql_mean_s'] else "—"
        spdup = f"{r['speedup_sparql_vs_sql']}×" if r['speedup_sparql_vs_sql'] else "—"
        print(f"{r['query_id']:<25} {sparql:>12} {sd:>10} {sql:>10} {spdup:>8}")
    
    # Also save JSON for programmatic use
    json_path = os.path.join(args.out, f"benchmark_results_{ts}.json")
    with open(json_path, "w") as f:
        json.dump({
            "metadata": {
                "endpoint": args.endpoint,
                "parquet_dir": args.parquet_dir,
                "reps": args.reps,
                "warmup": args.warmup,
                "timestamp": datetime.now().isoformat(),
                "software": {
                    "python": sys.version,
                    "duckdb": duckdb.__version__,
                    "polars": pl.__version__,
                    "fuseki": "6.0.0"
                }
            },
            "results": results
        }, f, indent=2)
    print(f"JSON saved:  {json_path}")
    
    return csv_path

if __name__ == "__main__":
    main()
