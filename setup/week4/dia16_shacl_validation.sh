#!/bin/bash
# DIA 16 - SHACL VALIDATION
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 16: SHACL VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "SHACL = Shapes Constraint Language"
echo "Valida se seus dados RDF obedecem às regras!"
echo ""

source activate.sh
mkdir -p ontology

cat > ontology/perinatalkg-shapes.ttl << 'TTLEOF'
# ════════════════════════════════════════════════
# PerinatalKG - SHACL Shapes
# ════════════════════════════════════════════════
# Autor: Clarimar José Coelho
# Data: 2026-05-20
#
# Valida que os dados RDF obedecem às regras
# clínicas e epidemiológicas do domínio perinatal
# ════════════════════════════════════════════════

@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix pkg:  <http://perinatalkg.org/ontology/> .
@prefix pkgr: <http://perinatalkg.org/resource/> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .

# ════════════════════════════════════════════════
# SHAPE 1: Birth - Validação de nascimento
# ════════════════════════════════════════════════

pkg:BirthShape
    rdf:type sh:NodeShape ;
    sh:targetClass pkg:Birth ;
    rdfs:label "Birth Validation Shape" ;
    rdfs:comment "Valida regras clínicas para nascimentos SINASC" ;

    # Peso ao nascer: obrigatório, entre 200g e 7000g
    sh:property [
        sh:path pkg:birthWeight ;
        sh:datatype xsd:integer ;
        sh:minInclusive 200 ;
        sh:maxInclusive 7000 ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Peso ao nascer deve ser inteiro entre 200g e 7000g" ;
        sh:severity sh:Violation ;
    ] ;

    # Idade gestacional: obrigatória, entre 20 e 45 semanas
    sh:property [
        sh:path pkg:gestationalAge ;
        sh:datatype xsd:integer ;
        sh:minInclusive 20 ;
        sh:maxInclusive 45 ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Idade gestacional deve ser inteiro entre 20 e 45 semanas" ;
        sh:severity sh:Violation ;
    ] ;

    # Município: obrigatório
    sh:property [
        sh:path pkg:bornIn ;
        sh:class pkg:Municipality ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Nascimento deve ter exatamente 1 município" ;
        sh:severity sh:Warning ;
    ] ;

    # Mãe: obrigatória
    sh:property [
        sh:path pkg:bornBy ;
        sh:class pkg:Mother ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Nascimento deve ter exatamente 1 mãe" ;
        sh:severity sh:Violation ;
    ] .

# ════════════════════════════════════════════════
# SHAPE 2: Mother - Validação de mãe
# ════════════════════════════════════════════════

pkg:MotherShape
    rdf:type sh:NodeShape ;
    sh:targetClass pkg:Mother ;
    rdfs:label "Mother Validation Shape" ;

    # Idade materna: entre 10 e 60 anos
    sh:property [
        sh:path pkg:maternalAge ;
        sh:datatype xsd:integer ;
        sh:minInclusive 10 ;
        sh:maxInclusive 60 ;
        sh:message "Idade materna deve ser entre 10 e 60 anos" ;
        sh:severity sh:Violation ;
    ] ;

    # Pré-natal: entre 0 e 42 consultas
    sh:property [
        sh:path pkg:prenatalVisits ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 42 ;
        sh:message "Consultas pré-natal deve ser entre 0 e 42" ;
        sh:severity sh:Warning ;
    ] .

# ════════════════════════════════════════════════
# SHAPE 3: ClimateExposure - Validação climática
# ════════════════════════════════════════════════

pkg:ClimateExposureShape
    rdf:type sh:NodeShape ;
    sh:targetClass pkg:ClimateExposure ;
    rdfs:label "Climate Exposure Validation Shape" ;

    # Temperatura: entre -20°C e 50°C (Brasil)
    sh:property [
        sh:path pkg:meanTemperature ;
        sh:datatype xsd:decimal ;
        sh:minInclusive -20 ;
        sh:maxInclusive 50 ;
        sh:message "Temperatura média deve ser entre -20°C e 50°C" ;
        sh:severity sh:Violation ;
    ] ;

    # Dias de calor extremo: entre 0 e 90 dias
    sh:property [
        sh:path pkg:extremeHeatDays ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 90 ;
        sh:message "Dias de calor extremo deve ser entre 0 e 90" ;
        sh:severity sh:Warning ;
    ] .

# ════════════════════════════════════════════════
# SHAPE 4: PretermBirth - Regra clínica
# ════════════════════════════════════════════════

pkg:PretermBirthShape
    rdf:type sh:NodeShape ;
    sh:targetClass pkg:PretermBirth ;
    rdfs:label "Preterm Birth Clinical Rule" ;

    # Prematuro: IG DEVE ser < 37 semanas
    sh:property [
        sh:path pkg:gestationalAge ;
        sh:maxExclusive 37 ;
        sh:message "PretermBirth DEVE ter idade gestacional < 37 semanas" ;
        sh:severity sh:Violation ;
    ] .

# ════════════════════════════════════════════════
# SHAPE 5: LowBirthWeight - Regra clínica
# ════════════════════════════════════════════════

pkg:LowBirthWeightShape
    rdf:type sh:NodeShape ;
    sh:targetClass pkg:LowBirthWeight ;
    rdfs:label "Low Birth Weight Clinical Rule" ;

    # Baixo peso: DEVE ser < 2500g
    sh:property [
        sh:path pkg:birthWeight ;
        sh:maxExclusive 2500 ;
        sh:message "LowBirthWeight DEVE ter peso < 2500g" ;
        sh:severity sh:Violation ;
    ] .
TTLEOF

echo "✅ SHACL shapes criadas!"
echo ""

cat > docs/tutorials/09_shacl_validation.py << 'PYEOF'
"""
Tutorial SHACL - Validação de dados RDF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SHACL valida se seus dados RDF obedecem
às regras definidas nas shapes.

Como SQL constraints, mas para RDF!
"""
from rdflib import Graph
from pyshacl import validate
from pathlib import Path

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✅ SHACL VALIDATION - PerinatalKG")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# Carregar dados e shapes
data_graph = Graph()
data_graph.parse("data_samples/sinasc_100_births.ttl", format="turtle")
data_graph.parse("ontology/perinatalkg_minimal.ttl", format="turtle")
print(f"Dados carregados: {len(data_graph)} triplas")

shapes_graph = Graph()
shapes_graph.parse("ontology/perinatalkg-shapes.ttl", format="turtle")
print(f"Shapes carregadas: {len(shapes_graph)} triplas")
print()

# ════════════════════════════════════════
# VALIDAÇÃO 1: Dados válidos (esperado passar)
# ════════════════════════════════════════
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("VALIDAÇÃO 1: Dados reais SINASC")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",
    abort_on_first=False,
    allow_infos=True,
    meta_shacl=False,
)

print(f"Dados conformes: {'✅ SIM' if conforms else '⚠️  NÃO (há violações)'}")
print()

# Analisar resultados
results = Graph()
results += results_graph

q_violations = """
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT ?severity ?message ?path ?value
WHERE {
    ?result sh:resultSeverity ?severity .
    ?result sh:resultMessage ?message .
    OPTIONAL { ?result sh:resultPath ?path }
    OPTIONAL { ?result sh:value ?value }
}
ORDER BY ?severity
"""

violations = list(results.query(q_violations))

if violations:
    print(f"Resultados SHACL: {len(violations)}")
    print()
    violations_count = 0
    warnings_count = 0
    for row in violations[:20]:
        sev = str(row.severity).split("#")[-1]
        msg = str(row.message) if row.message else "N/A"
        path = str(row.path).split("/")[-1] if row.path else "N/A"
        val = str(row.value)[:30] if row.value else "N/A"

        if sev == "Violation":
            violations_count += 1
            icon = "❌"
        elif sev == "Warning":
            warnings_count += 1
            icon = "⚠️ "
        else:
            icon = "ℹ️ "

        print(f"  {icon} [{sev}] {msg[:60]}")
        if path != "N/A":
            print(f"       Path: {path}, Value: {val}")

    print()
    print(f"  Violations: {violations_count}")
    print(f"  Warnings:   {warnings_count}")
else:
    print("✅ Nenhuma violação encontrada!")

# ════════════════════════════════════════
# VALIDAÇÃO 2: Dados inválidos (teste)
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("VALIDAÇÃO 2: Dados inválidos (teste proposital)")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# Criar dados inválidos para testar
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

PKG  = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")

invalid_graph = Graph()
invalid_graph.parse("ontology/perinatalkg_minimal.ttl", format="turtle")

# Nascimento com dados INVÁLIDOS
birth_invalid = URIRef(f"{PKGR}birth/INVALID_001")
invalid_graph.add((birth_invalid, RDF.type, PKG.Birth))
invalid_graph.add((birth_invalid, PKG.birthWeight,
                   Literal(99999, datatype=XSD.integer)))  # > 7000g!
invalid_graph.add((birth_invalid, PKG.gestationalAge,
                   Literal(5, datatype=XSD.integer)))    # < 20 semanas!

# Mãe com dados INVÁLIDOS
mother_invalid = URIRef(f"{PKGR}mother/INVALID_001_m")
invalid_graph.add((birth_invalid, PKG.bornBy, mother_invalid))
invalid_graph.add((mother_invalid, RDF.type, PKG.Mother))
invalid_graph.add((mother_invalid, PKG.maternalAge,
                   Literal(5, datatype=XSD.integer)))  # < 10 anos!

# Prematuro com IG = 40 semanas (INVÁLIDO!)
birth_preterm_invalid = URIRef(f"{PKGR}birth/INVALID_002")
invalid_graph.add((birth_preterm_invalid, RDF.type, PKG.PretermBirth))
invalid_graph.add((birth_preterm_invalid, PKG.gestationalAge,
                   Literal(40, datatype=XSD.integer)))  # >= 37! Não é prematuro!
invalid_graph.add((birth_preterm_invalid, PKG.birthWeight,
                   Literal(3500, datatype=XSD.integer)))
mother2 = URIRef(f"{PKGR}mother/INVALID_002_m")
invalid_graph.add((birth_preterm_invalid, PKG.bornBy, mother2))
invalid_graph.add((mother2, RDF.type, PKG.Mother))

print("Dados inválidos criados:")
print("  INVALID_001: peso=99999g, IG=5sem, mãe=5anos")
print("  INVALID_002: PretermBirth com IG=40sem (ERRO!)")
print()

conforms2, results_graph2, _ = validate(
    invalid_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",
    abort_on_first=False,
)

print(f"Dados inválidos conformes: {'SIM (bug!)' if conforms2 else '❌ NÃO (correto!)'}")
print()

results2 = Graph()
results2 += results_graph2

violations2 = list(results2.query(q_violations))
print(f"Violações detectadas: {len(violations2)}")
for row in violations2:
    sev = str(row.severity).split("#")[-1]
    msg = str(row.message) if row.message else "N/A"
    icon = "❌" if sev == "Violation" else "⚠️ "
    print(f"  {icon} {msg[:70]}")

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎉 SHACL VALIDATION CONCLUÍDA!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ Você aprendeu:")
print("   • SHACL shapes definem regras para RDF")
print("   • sh:NodeShape para classes")
print("   • sh:property para restrições")
print("   • Severidades: Violation, Warning, Info")
print("   • pyshacl valida dados automaticamente")
print()
print("✅ Para o paper:")
print('   "Data quality was validated using SHACL')
print('    shapes, enforcing clinical rules such as')
print('    gestational age (20-45 weeks) and birth')
print('    weight (200-7000g) constraints."')
PYEOF

echo "✅ Tutorial SHACL criado!"
echo ""
echo "🚀 Executando validação..."
python docs/tutorials/09_shacl_validation.py

git add ontology/perinatalkg-shapes.ttl
git add docs/tutorials/09_shacl_validation.py
git add setup/week4/dia16_shacl_validation.sh
git commit -m "Day 16: SHACL validation shapes for PerinatalKG

- 5 SHACL shapes covering Birth, Mother, ClimateExposure
- Clinical rules: birthWeight 200-7000g, gestationalAge 20-45
- PretermBirth must have IG < 37 (clinical constraint)
- LowBirthWeight must have weight < 2500g
- Tested with valid and invalid data
- pyshacl validates automatically
"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 16 COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   [██░░░░░░░░] 20% Semana 4"
echo ""
echo "   ✅ Dia 16: SHACL validation"
echo "   ⬜ Dia 17: Reasoner HermiT"
echo "   ⬜ Dia 18: Use Case 1"
echo "   ⬜ Dia 19: Use Case 2"
echo "   ⬜ Dia 20: Checkpoint Guilherme"
echo ""
echo "🎯 PRÓXIMO: DIA 17 - REASONER HERMIT!"
