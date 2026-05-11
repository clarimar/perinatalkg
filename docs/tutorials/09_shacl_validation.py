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
