#!/bin/bash
# DIA 9 - SPARQL BÁSICO
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 DIA 9: APRENDENDO SPARQL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

source activate.sh
mkdir -p queries

cat > docs/tutorials/04_sparql_basics.py << 'PYEOF'
"""
Tutorial SPARQL - Consultando a Ontologia PerinatalKG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SPARQL é para RDF o que SQL é para bancos relacionais.

Estrutura básica:
    SELECT ?variavel
    WHERE {
        ?sujeito predicado ?variavel .
    }
"""
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS, OWL

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎓 TUTORIAL SPARQL - PerinatalKG")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# Carregar ontologia
g = Graph()
g.parse("ontology/perinatalkg_minimal.ttl", format="turtle")
print(f"✅ Ontologia carregada: {len(g)} triplas")
print()

# ════════════════════════════════════════
# QUERY 1: Listar todas as classes
# ════════════════════════════════════════
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 1: Listar todas as classes OWL")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q1 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?classe ?label_pt
WHERE {
    ?classe rdf:type owl:Class .
    OPTIONAL { ?classe rdfs:label ?label_pt .
               FILTER(LANG(?label_pt) = "pt") }
}
ORDER BY ?label_pt
"""

resultados = g.query(q1)
print(f"Classes encontradas: {len(resultados)}")
print()
for row in resultados:
    classe = str(row.classe).split("/")[-1]
    label = str(row.label_pt) if row.label_pt else "sem label pt"
    print(f"  {classe:30s} → {label}")

# ════════════════════════════════════════
# QUERY 2: Hierarquia de prematuridade
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 2: Hierarquia de Prematuridade")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q2 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subclasse ?label ?comentario
WHERE {
    ?subclasse rdfs:subClassOf pkg:PretermBirth .
    ?subclasse rdfs:label ?label .
    OPTIONAL { ?subclasse rdfs:comment ?comentario .
               FILTER(LANG(?comentario) = "pt") }
    FILTER(LANG(?label) = "pt")
}
ORDER BY ?label
"""

resultados = g.query(q2)
print(f"Subtipos de prematuridade: {len(resultados)}")
print()
for row in resultados:
    print(f"  📦 {row.label}")
    if row.comentario:
        print(f"     → {row.comentario}")

# ════════════════════════════════════════
# QUERY 3: Instâncias e suas propriedades
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 3: Nascimentos de exemplo")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q3 = """
PREFIX pkg: <http://perinatalkg.org/ontology/>
PREFIX pkgr: <http://perinatalkg.org/resource/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?nascimento ?peso ?ig ?municipio
WHERE {
    ?nascimento rdf:type ?tipo .
    ?tipo rdfs:subClassOf* pkg:Birth .
    OPTIONAL { ?nascimento pkg:birthWeight ?peso }
    OPTIONAL { ?nascimento pkg:gestationalAge ?ig }
    OPTIONAL { ?nascimento pkg:bornIn ?loc .
               ?loc rdfs:label ?municipio }
}
"""

resultados = g.query(q3)
print(f"Nascimentos encontrados: {len(resultados)}")
print()
for row in resultados:
    nasc = str(row.nascimento).split("/")[-1]
    peso = row.peso or "N/A"
    ig = row.ig or "N/A"
    mun = row.municipio or "N/A"
    print(f"  {nasc}: peso={peso}g, IG={ig}sem, município={mun}")

# ════════════════════════════════════════
# QUERY 4: Object Properties
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 4: Propriedades e seus domínios")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q4 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?label ?dominio ?range
WHERE {
    ?prop rdf:type owl:ObjectProperty .
    ?prop rdfs:label ?label .
    OPTIONAL { ?prop rdfs:domain ?dominio }
    OPTIONAL { ?prop rdfs:range ?range }
    FILTER(LANG(?label) = "en")
}
ORDER BY ?label
"""

resultados = g.query(q4)
print(f"Object Properties: {len(resultados)}")
print()
for row in resultados:
    dom = str(row.dominio).split("/")[-1] if row.dominio else "?"
    rng = str(row.range).split("/")[-1] if row.range else "?"
    print(f"  {row.label:20s} : {dom} → {rng}")

# ════════════════════════════════════════
# QUERY 5: Mapeamentos SNOMED-CT
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("QUERY 5: Mapeamentos para SNOMED-CT")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q5 = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?classe ?label ?snomed
WHERE {
    ?classe skos:exactMatch ?snomed .
    ?classe rdfs:label ?label .
    FILTER(LANG(?label) = "en")
}
"""

resultados = g.query(q5)
print(f"Classes com mapeamento SNOMED-CT: {len(resultados)}")
print()
for row in resultados:
    snomed_id = str(row.snomed).split("/")[-1]
    print(f"  {row.label:25s} → SNOMED: {snomed_id}")

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎉 TUTORIAL SPARQL CONCLUÍDO!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ Você aprendeu:")
print("   • SELECT ... WHERE { } - estrutura básica")
print("   • OPTIONAL { } - dados opcionais")
print("   • FILTER() - filtrar por língua/valor")
print("   • ORDER BY - ordenar resultados")
print("   • rdfs:subClassOf* - transitividade (hierarquia)")
print()
print("🎯 Próximo passo: Instalar Fuseki e executar SPARQL via HTTP!")
PYEOF

echo "✅ Tutorial SPARQL criado!"
echo ""
echo "🚀 Executando tutorial..."
python docs/tutorials/04_sparql_basics.py

git add docs/tutorials/04_sparql_basics.py setup/week2/dia9_sparql_basico.sh
git commit -m "Day 9: SPARQL tutorial - 5 queries on perinatal ontology"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 9 COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 SEMANA 2 - PROGRESSO:"
echo "   [████▌] 90% - Dias 6-9 completos"
echo ""
echo "   ✅ Dia 6: Protégé + Ontologia OWL"
echo "   ✅ Dia 7: SIM 203K óbitos (100%)"
echo "   ✅ Dia 8: IBGE População + IDH-M"
echo "   ✅ Dia 9: SPARQL básico (5 queries!)"
echo "   ⬜ Dia 10: Conversor parquet→RDF"
echo ""
echo "🎯 AMANHÃ: DIA 10 - Primeiro conversor parquet→RDF!"
echo ""
