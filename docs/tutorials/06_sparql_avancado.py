"""
Tutorial SPARQL Avançado
GROUP BY, FILTER, HAVING, UNION, OPTIONAL
Queries sobre dados reais do PerinatalKG
"""
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD

PKG  = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🔍 SPARQL AVANÇADO - PerinatalKG")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# Carregar dados reais (100 nascimentos)
g = Graph()
g.bind("pkg", PKG)
g.bind("pkgr", PKGR)
g.parse("data_samples/sinasc_100_births.ttl", format="turtle")
print(f"Dados carregados: {len(g)} triplas")
print()

# ════════════════════════════════════════
# QUERY 1: COUNT - Total de nascimentos
# ════════════════════════════════════════
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 1: COUNT - Contando nascimentos")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q1 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT (COUNT(?b) AS ?total_nascimentos)
WHERE {
    ?b rdf:type pkg:Birth .
}
"""
for row in g.query(q1):
    print(f"Total de nascimentos: {row.total_nascimentos}")

# ════════════════════════════════════════
# QUERY 2: FILTER - Nascimentos prematuros
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 2: FILTER - Nascimentos prematuros (IG < 37)")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q2 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?nascimento ?ig ?peso
WHERE {
    ?nascimento pkg:gestationalAge ?ig .
    ?nascimento pkg:birthWeight ?peso .
    FILTER (?ig < 37)
}
ORDER BY ?ig
"""
resultados = list(g.query(q2))
print(f"Prematuros encontrados: {len(resultados)}")
print()
for row in resultados:
    nasc = str(row.nascimento).split("/")[-1]
    print(f"  {nasc}: IG={row.ig}sem, Peso={row.peso}g")

# ════════════════════════════════════════
# QUERY 3: FILTER duplo - Alto risco
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 3: FILTER duplo - Alto Risco (IG<37 E Peso<2500)")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q3 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>

SELECT ?nascimento ?ig ?peso
WHERE {
    ?nascimento pkg:gestationalAge ?ig .
    ?nascimento pkg:birthWeight ?peso .
    FILTER (?ig < 37 && ?peso < 2500)
}
ORDER BY ?ig ?peso
"""
resultados = list(g.query(q3))
print(f"Alto risco (prematuro + baixo peso): {len(resultados)}")
for row in resultados:
    nasc = str(row.nascimento).split("/")[-1]
    print(f"  {nasc}: IG={row.ig}sem, Peso={row.peso}g")

# ════════════════════════════════════════
# QUERY 4: GROUP BY - Contagem por tipo
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 4: GROUP BY - Nascimentos por tipo OWL")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q4 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tipo (COUNT(?b) AS ?total)
WHERE {
    ?b rdf:type ?tipo .
    FILTER(STRSTARTS(STR(?tipo),
           "http://perinatalkg.org/ontology/"))
    FILTER(?tipo != pkg:Birth)
}
GROUP BY ?tipo
ORDER BY DESC(?total)
"""
print()
for row in g.query(q4):
    tipo = str(row.tipo).split("/")[-1]
    print(f"  {tipo:30s}: {row.total}")

# ════════════════════════════════════════
# QUERY 5: Estatísticas de peso
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 5: Estatísticas de peso ao nascer")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q5 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>

SELECT
    (COUNT(?b) AS ?n)
    (AVG(?peso) AS ?media)
    (MIN(?peso) AS ?minimo)
    (MAX(?peso) AS ?maximo)
WHERE {
    ?b pkg:birthWeight ?peso .
}
"""
for row in g.query(q5):
    print(f"  N:      {row.n}")
    print(f"  Média:  {float(row.media):.0f}g")
    print(f"  Mínimo: {row.minimo}g")
    print(f"  Máximo: {row.maximo}g")

# ════════════════════════════════════════
# QUERY 6: Mães adolescentes + prematuros
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 6: Mães adolescentes com prematuros")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q6 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?nascimento ?idade_mae ?ig ?peso
WHERE {
    ?nascimento rdf:type pkg:PretermBirth .
    ?nascimento pkg:gestationalAge ?ig .
    ?nascimento pkg:birthWeight ?peso .
    ?nascimento pkg:bornBy ?mae .
    ?mae rdf:type pkg:AdolescentMother .
    ?mae pkg:maternalAge ?idade_mae .
}
ORDER BY ?idade_mae
"""
resultados = list(g.query(q6))
print(f"Adolescentes com prematuros: {len(resultados)}")
for row in resultados:
    nasc = str(row.nascimento).split("/")[-1]
    print(f"  {nasc}: Mãe={row.idade_mae}anos, IG={row.ig}sem, Peso={row.peso}g")

# ════════════════════════════════════════
# QUERY 7: Exposição calor em prematuros
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 7: Exposição a calor extremo em prematuros")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q7 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?nascimento ?ig ?peso ?temp ?dias_calor
WHERE {
    ?nascimento rdf:type pkg:PretermBirth .
    ?nascimento pkg:gestationalAge ?ig .
    ?nascimento pkg:birthWeight ?peso .
    ?nascimento pkg:exposedTo ?exp .
    ?exp rdf:type pkg:ExtremeHeatExposure .
    OPTIONAL { ?exp pkg:meanTemperature ?temp }
    OPTIONAL { ?exp pkg:extremeHeatDays ?dias_calor }
}
ORDER BY ?ig
"""
resultados = list(g.query(q7))
print(f"Prematuros expostos a calor extremo: {len(resultados)}")
for row in resultados:
    nasc = str(row.nascimento).split("/")[-1]
    temp = f"{float(row.temp):.1f}°C" if row.temp else "N/A"
    dias = row.dias_calor if row.dias_calor else "N/A"
    print(f"  {nasc}: IG={row.ig}sem, Peso={row.peso}g, Temp={temp}, Dias calor={dias}")

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎉 SPARQL AVANÇADO CONCLUÍDO!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ Você domina agora:")
print("   • COUNT, AVG, MIN, MAX")
print("   • FILTER com && (AND) e || (OR)")
print("   • GROUP BY + ORDER BY DESC")
print("   • Queries multi-hop (nascimento→mãe→tipo)")
print("   • Queries epidemiológicas reais!")
print()
print("🎯 Próximo: Ontologia formal com BFO (Dia 13)")
