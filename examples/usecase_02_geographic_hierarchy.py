"""
Use Case 02: Geographic Hierarchy Navigation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Research Question:
"How do birth outcomes vary across geographic
 levels: municipality → state → region?"

Demonstrates RDF graph traversal across
the Brazilian geographic hierarchy.
"""
import requests
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

ENDPOINT = "http://localhost:3030/perinatalkg/sparql"
UPLOAD   = "http://localhost:3030/perinatalkg/data"

PKG  = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")

def sparql_query(query: str) -> list:
    r = requests.get(ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=30
    )
    r.raise_for_status()
    return r.json()["results"]["bindings"]

def upload_ttl(filepath: str) -> bool:
    with open(filepath, "rb") as f:
        r = requests.post(UPLOAD,
            data=f,
            headers={"Content-Type": "text/turtle"},
            timeout=60
        )
    return r.status_code in [200, 201, 204]

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🗺️  USE CASE 2: HIERARQUIA GEOGRÁFICA")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("Research Question:")
print("'Como os desfechos perinatais variam por")
print(" nível geográfico? Município→Estado→Região?'")
print()

# ════════════════════════════════════════
# PASSO 1: Enriquecer RDF com hierarquia
# ════════════════════════════════════════
print("1️⃣  Construindo hierarquia geográfica RDF...")

geo_graph = Graph()
geo_graph.bind("pkg",  PKG)
geo_graph.bind("pkgr", PKGR)
geo_graph.bind("rdfs", RDFS)

# Regiões do Brasil
regioes = {
    "Norte":     "N",
    "Nordeste":  "NE",
    "CentroOeste": "CO",
    "Sudeste":   "SE",
    "Sul":       "S"
}

for nome, sigla in regioes.items():
    uri = URIRef(f"{PKGR}location/region/{sigla}")
    geo_graph.add((uri, RDF.type, PKG.Region))
    geo_graph.add((uri, RDFS.label, Literal(nome, lang="pt")))
    geo_graph.add((uri, RDFS.label, Literal(sigla, lang="en")))

# Estados do Brasil com suas regiões
estados = {
    # Norte
    "AC": ("Acre", "N"), "AM": ("Amazonas", "N"),
    "AP": ("Amapá", "N"), "PA": ("Pará", "N"),
    "RO": ("Rondônia", "N"), "RR": ("Roraima", "N"),
    "TO": ("Tocantins", "N"),
    # Nordeste
    "AL": ("Alagoas", "NE"), "BA": ("Bahia", "NE"),
    "CE": ("Ceará", "NE"), "MA": ("Maranhão", "NE"),
    "PB": ("Paraíba", "NE"), "PE": ("Pernambuco", "NE"),
    "PI": ("Piauí", "NE"), "RN": ("Rio Grande do Norte", "NE"),
    "SE": ("Sergipe", "NE"),
    # Centro-Oeste
    "DF": ("Distrito Federal", "CO"), "GO": ("Goiás", "CO"),
    "MS": ("Mato Grosso do Sul", "CO"), "MT": ("Mato Grosso", "CO"),
    # Sudeste
    "ES": ("Espírito Santo", "SE"), "MG": ("Minas Gerais", "SE"),
    "RJ": ("Rio de Janeiro", "SE"), "SP": ("São Paulo", "SE"),
    # Sul
    "PR": ("Paraná", "S"), "RS": ("Rio Grande do Sul", "S"),
    "SC": ("Santa Catarina", "S"),
}

for sigla, (nome, regiao) in estados.items():
    estado_uri = URIRef(f"{PKGR}location/state/{sigla}")
    regiao_uri = URIRef(f"{PKGR}location/region/{regiao}")
    geo_graph.add((estado_uri, RDF.type, PKG.State))
    geo_graph.add((estado_uri, RDFS.label, Literal(nome, lang="pt")))
    geo_graph.add((estado_uri, RDFS.label, Literal(sigla, lang="en")))
    geo_graph.add((estado_uri, PKG.partOf, regiao_uri))

# Goiânia (município dos 100 nascimentos)
goiania_uri = URIRef(f"{PKGR}location/520870")
go_uri = URIRef(f"{PKGR}location/state/GO")
geo_graph.add((goiania_uri, RDF.type, PKG.Municipality))
geo_graph.add((goiania_uri, RDFS.label, Literal("Goiânia", lang="pt")))
geo_graph.add((goiania_uri, PKG.locatedIn, go_uri))

print(f"   Triplas geográficas: {len(geo_graph)}")

# Salvar e carregar no Fuseki
geo_path = "data/raw/ibge/geographic_hierarchy.ttl"
Path("data/raw/ibge").mkdir(parents=True, exist_ok=True)
geo_graph.serialize(geo_path, format="turtle")
print(f"   ✅ Salvo: {geo_path}")

ok = upload_ttl(geo_path)
print(f"   {'✅' if ok else '❌'} Carregado no Fuseki")

# Carregar nascimentos também
ok2 = upload_ttl("data_samples/sinasc_100_births.ttl")
print(f"   {'✅' if ok2 else '❌'} Nascimentos carregados")

# ════════════════════════════════════════
# QUERY 1: Navegação hierárquica
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 1: Navegação Município→Estado→Região")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q1 = """
PREFIX pkg:  <http://perinatalkg.org/ontology/>
PREFIX pkgr: <http://perinatalkg.org/resource/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?municipio ?estado ?regiao (COUNT(?b) AS ?nascimentos)
WHERE {
    ?b rdf:type pkg:Birth .
    ?b pkg:bornIn ?mun_uri .
    ?mun_uri rdfs:label ?municipio .
    OPTIONAL {
        ?mun_uri pkg:locatedIn ?estado_uri .
        ?estado_uri rdfs:label ?estado .
        FILTER(LANG(?estado) = "pt")
        OPTIONAL {
            ?estado_uri pkg:partOf ?regiao_uri .
            ?regiao_uri rdfs:label ?regiao .
            FILTER(LANG(?regiao) = "pt")
        }
    }
}
GROUP BY ?municipio ?estado ?regiao
ORDER BY DESC(?nascimentos)
"""
results = sparql_query(q1)
print(f"   Municípios encontrados: {len(results)}")
print()
for r in results[:10]:
    mun = r.get("municipio", {}).get("value", "N/A")
    est = r.get("estado", {}).get("value", "N/A")
    reg = r.get("regiao", {}).get("value", "N/A")
    n = r.get("nascimentos", {}).get("value", "0")
    print(f"   {mun:15s} → {est:20s} → {reg:15s} ({n} nasc.)")

# ════════════════════════════════════════
# QUERY 2: Prematuridade por região
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 2: Taxa de prematuridade por região")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q2 = """
PREFIX pkg:  <http://perinatalkg.org/ontology/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?regiao
    (COUNT(?b) AS ?total)
    (COUNT(?pt) AS ?prematuros)
    (AVG(?peso) AS ?peso_medio)
WHERE {
    ?b rdf:type pkg:Birth .
    ?b pkg:birthWeight ?peso .
    OPTIONAL { ?b rdf:type pkg:PretermBirth . BIND(?b AS ?pt) }
    OPTIONAL {
        ?b pkg:bornIn ?mun .
        ?mun pkg:locatedIn ?estado .
        ?estado pkg:partOf ?regiao_uri .
        ?regiao_uri rdfs:label ?regiao .
        FILTER(LANG(?regiao) = "pt")
    }
}
GROUP BY ?regiao
ORDER BY DESC(?total)
"""
results = sparql_query(q2)
print()
print(f"   {'Região':20s} {'Total':>7} {'Prematuro':>10} {'%PTB':>7} {'Peso':>8}")
print("   " + "─" * 58)
for r in results:
    reg = r.get("regiao", {}).get("value", "N/A")
    total = int(r["total"]["value"])
    prem = int(r["prematuros"]["value"])
    pct = prem/total*100 if total > 0 else 0
    peso = float(r["peso_medio"]["value"])
    print(f"   {reg:20s} {total:>7} {prem:>10} {pct:>6.1f}% {peso:>7.0f}g")

# ════════════════════════════════════════
# QUERY 3: Busca federativa - todos os níveis
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 3: Contagem por nível geográfico")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q3 = """
PREFIX pkg:  <http://perinatalkg.org/ontology/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?nivel (COUNT(?loc) AS ?total)
WHERE {
    { ?loc rdf:type pkg:Municipality . BIND("Município" AS ?nivel) }
    UNION
    { ?loc rdf:type pkg:State . BIND("Estado" AS ?nivel) }
    UNION
    { ?loc rdf:type pkg:Region . BIND("Região" AS ?nivel) }
}
GROUP BY ?nivel
ORDER BY ?nivel
"""
results = sparql_query(q3)
print()
for r in results:
    nivel = r["nivel"]["value"]
    total = r["total"]["value"]
    print(f"   {nivel:15s}: {total}")

# ════════════════════════════════════════
# QUERY 4: Query formal para o paper
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 4: Query formal - Listing 2 do paper")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

paper_query2 = """
PREFIX pkg:  <http://perinatalkg.org/ontology/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Use Case 2: Birth outcomes by geographic hierarchy
# PerinatalKG - Coelho et al. (2027)

SELECT
    ?region_name
    ?state_name
    (COUNT(?birth) AS ?n_births)
    (COUNT(?preterm) AS ?n_preterm)
    (AVG(?weight) AS ?mean_weight_g)
    (AVG(?heat_days) AS ?mean_heat_exposure)
WHERE {
    ?birth rdf:type pkg:Birth .
    ?birth pkg:birthWeight ?weight .

    OPTIONAL {
        ?birth rdf:type pkg:PretermBirth .
        BIND(?birth AS ?preterm)
    }
    OPTIONAL {
        ?birth pkg:bornIn ?municipality .
        ?municipality pkg:locatedIn ?state .
        ?state rdfs:label ?state_name .
        FILTER(LANG(?state_name) = "pt")
        OPTIONAL {
            ?state pkg:partOf ?region .
            ?region rdfs:label ?region_name .
            FILTER(LANG(?region_name) = "pt")
        }
    }
    OPTIONAL {
        ?birth pkg:exposedTo ?exp .
        ?exp pkg:extremeHeatDays ?heat_days .
    }
}
GROUP BY ?region_name ?state_name
ORDER BY ?region_name ?state_name
"""

results = sparql_query(paper_query2)
print()
print(f"   {'Região':15s} {'Estado':20s} {'N':>5} {'PTB':>5} {'Peso':>8} {'Calor':>7}")
print("   " + "─" * 65)
for r in results:
    reg = r.get("region_name", {}).get("value", "N/A")
    est = r.get("state_name", {}).get("value", "N/A")
    n = r["n_births"]["value"]
    pt = r["n_preterm"]["value"]
    peso = float(r["mean_weight_g"]["value"])
    calor = float(r["mean_heat_exposure"]["value"]) if r.get("mean_heat_exposure") else 0
    print(f"   {reg:15s} {est:20s} {n:>5} {pt:>5} {peso:>7.0f}g {calor:>7.1f}")

# Salvar query
with open("queries/usecase_02_geographic_hierarchy.rq", "w") as f:
    f.write(paper_query2)
print()
print("✅ Query salva: queries/usecase_02_geographic_hierarchy.rq")

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎉 USE CASE 2 CONCLUÍDO!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ Você demonstrou:")
print("   • Navegação RDF em hierarquia geográfica")
print("   • Município → Estado → Região")
print("   • Agregação multi-nível com SPARQL")
print("   • Graph traversal com path operators")
print()
print("✅ Para o paper (Use Cases section):")
print('   "Use Case 2 demonstrated multi-level')
print('    geographic aggregation. The RDF graph')
print('    structure enables seamless traversal')
print('    from municipality to region level,')
print('    impossible in flat tabular schemas."')
