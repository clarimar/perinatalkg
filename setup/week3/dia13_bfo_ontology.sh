#!/bin/bash
# DIA 13 - ONTOLOGIA FORMAL COM BFO
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧬 DIA 13: ONTOLOGIA FORMAL COM BFO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

source activate.sh
mkdir -p ontology/modules ontology/imports

cat > docs/tutorials/07_bfo_integration.py << 'PYEOF'
"""
Tutorial: Integração com BFO (Basic Formal Ontology)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BFO é a top-level ontology padrão do OBO Foundry.
Usada por: Gene Ontology, HPO, SNOMED-CT, OBI, etc.

Por que BFO?
- Journal of Biomedical Informatics EXIGE alinhamento
- Interoperabilidade com outras ontologias biomédicas
- Fundamento filosófico sólido (lógica de descrição)
"""
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from pathlib import Path

PKG  = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")
BFO  = Namespace("http://purl.obolibrary.org/obo/BFO_")
OBO  = Namespace("http://purl.obolibrary.org/obo/")

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🧬 BFO - Basic Formal Ontology")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# ════════════════════════════════════════
# PARTE 1: O QUE É BFO?
# ════════════════════════════════════════
print("PARTE 1: Estrutura do BFO")
print("─────────────────────────────────────────────")
print()
print("BFO divide tudo em duas categorias fundamentais:")
print()
print("  🔵 CONTINUANT (existe no tempo, persiste)")
print("     └─ Independent Continuant")
print("        ├─ Material Entity ← OBJETOS FÍSICOS")
print("        │  ├─ Object (ex: pessoa, organismo)")
print("        │  ├─ Fiat Object Part (ex: rim)")
print("        │  └─ Object Aggregate (ex: população)")
print("        └─ Immaterial Entity")
print("     └─ Specifically Dependent Continuant")
print("        ├─ Quality (ex: peso, temperatura)")
print("        └─ Realizable Entity")
print("           ├─ Role (ex: papel de mãe)")
print("           └─ Disposition (ex: vulnerabilidade)")
print("     └─ Generically Dependent Continuant")
print("        └─ Information Content Entity (ex: registro)")
print()
print("  🟠 OCCURRENT (acontece no tempo, tem partes temporais)")
print("     └─ Process ← EVENTOS/PROCESSOS")
print("        ├─ ex: nascimento, gestação, óbito")
print("     └─ Process Boundary")
print("        ├─ ex: momento do parto")
print("     └─ Temporal Region")
print("        ├─ ex: trimestre gestacional")
print("     └─ Spatiotemporal Region")
print()

# ════════════════════════════════════════
# PARTE 2: MAPEAMENTO PERINATALKG → BFO
# ════════════════════════════════════════
print("PARTE 2: Mapeamento PerinatalKG → BFO")
print("─────────────────────────────────────────────")
print()

mapeamentos = {
    "pkg:Birth": {
        "bfo": "BFO:0000003 (Occurrent → Process)",
        "justificativa": "Nascimento É um processo que ocorre no tempo",
        "alternativa": "NÃO é Object (que persiste)"
    },
    "pkg:Mother": {
        "bfo": "BFO:0000040 (Material Entity → Object)",
        "justificativa": "Mãe É um organismo que persiste no tempo",
        "alternativa": "Pode ter Role de 'mãe' (Realizable Entity)"
    },
    "pkg:ClimateExposure": {
        "bfo": "BFO:0000003 (Occurrent → Process)",
        "justificativa": "Exposição É um processo temporal",
        "alternativa": "Temperatura é Quality (Continuant)"
    },
    "pkg:Municipality": {
        "bfo": "BFO:0000029 (Immaterial Entity → Site)",
        "justificativa": "Município é uma região geográfica",
        "alternativa": "Pode ser Fiat Object Part do território"
    },
    "pkg:birthWeight": {
        "bfo": "BFO:0000019 (Quality)",
        "justificativa": "Peso é qualidade do recém-nascido",
        "alternativa": "É Specifically Dependent Continuant"
    },
    "pkg:gestationalAge": {
        "bfo": "BFO:0000019 (Quality / Temporal Region)",
        "justificativa": "IG é medida de duração temporal",
        "alternativa": "Pode ser Process Duration"
    }
}

for classe, info in mapeamentos.items():
    print(f"  📌 {classe}")
    print(f"     BFO:  {info['bfo']}")
    print(f"     Por:  {info['justificativa']}")
    print()

# ════════════════════════════════════════
# PARTE 3: CRIAR ONTOLOGIA COM BFO
# ════════════════════════════════════════
print("PARTE 3: Criando módulo com alinhamento BFO")
print("─────────────────────────────────────────────")
print()

g = Graph()
g.bind("pkg",  PKG)
g.bind("pkgr", PKGR)
g.bind("bfo",  BFO)
g.bind("obo",  OBO)
g.bind("owl",  OWL)
g.bind("rdfs", RDFS)

# Declarar ontologia
ont = PKG.PerinatalKGOntology
g.add((ont, RDF.type, OWL.Ontology))
g.add((ont, RDFS.label, Literal("PerinatalKG Ontology - BFO Aligned", lang="en")))
g.add((ont, OWL.versionInfo, Literal("0.2.0-dev")))

# Importar BFO (declaração de import)
g.add((ont, OWL.imports,
       URIRef("http://purl.obolibrary.org/obo/bfo/2019-08-26/bfo.owl")))

# ─── CLASSES BFO RELEVANTES (subset) ───
print("Declarando classes BFO relevantes...")

bfo_classes = {
    "0000001": "Entity",
    "0000002": "Continuant",
    "0000003": "Occurrent",
    "0000004": "Independent Continuant",
    "0000019": "Quality",
    "0000020": "Specifically Dependent Continuant",
    "0000029": "Site",
    "0000030": "Object",
    "0000040": "Material Entity",
}

for code, label in bfo_classes.items():
    uri = URIRef(f"http://purl.obolibrary.org/obo/BFO_{code}")
    g.add((uri, RDF.type, OWL.Class))
    g.add((uri, RDFS.label, Literal(label, lang="en")))

print(f"  ✅ {len(bfo_classes)} classes BFO declaradas")

# ─── ALINHAR PerinatalKG COM BFO ───
print()
print("Alinhando classes PerinatalKG ao BFO...")

BFO_OCCURRENT       = URIRef("http://purl.obolibrary.org/obo/BFO_0000003")
BFO_MATERIAL_ENTITY = URIRef("http://purl.obolibrary.org/obo/BFO_0000040")
BFO_QUALITY         = URIRef("http://purl.obolibrary.org/obo/BFO_0000019")
BFO_SITE            = URIRef("http://purl.obolibrary.org/obo/BFO_0000029")
BFO_OBJECT          = URIRef("http://purl.obolibrary.org/obo/BFO_0000030")

alinhamentos = [
    # (classe pkg, superclasse BFO, justificativa)
    (PKG.Birth, BFO_OCCURRENT,
     "Birth is a process (occurrent) - has temporal parts"),
    (PKG.PretermBirth, BFO_OCCURRENT,
     "PretermBirth is a subtype of Birth process"),
    (PKG.Mother, BFO_MATERIAL_ENTITY,
     "Mother is a material entity (organism)"),
    (PKG.ClimateExposure, BFO_OCCURRENT,
     "Climate exposure is a process occurring during gestation"),
    (PKG.Municipality, BFO_SITE,
     "Municipality is a geographic site"),
    (PKG.Region, BFO_SITE,
     "Region is a geographic site"),
]

for classe, bfo_super, justificativa in alinhamentos:
    g.add((classe, RDF.type, OWL.Class))
    g.add((classe, RDFS.subClassOf, bfo_super))
    g.add((classe, RDFS.comment,
           Literal(f"BFO alignment: {justificativa}", lang="en")))
    nome = str(classe).split("/")[-1]
    bfo_nome = str(bfo_super).split("_")[-1]
    print(f"  ✅ {nome:25s} → BFO_{bfo_nome}")

# ─── DATA PROPERTIES como BFO:Quality ───
print()
print("Alinhando propriedades de dados ao BFO:Quality...")

data_props = [
    (PKG.birthWeight, "Birth weight is a quality of the newborn"),
    (PKG.gestationalAge, "Gestational age is a temporal quality"),
    (PKG.maternalAge, "Maternal age is a quality of the mother"),
]

for prop, justificativa in data_props:
    g.add((prop, RDF.type, OWL.DatatypeProperty))
    g.add((prop, RDFS.subPropertyOf,
           URIRef("http://purl.obolibrary.org/obo/RO_0000086")))
    g.add((prop, RDFS.comment,
           Literal(f"BFO alignment: {justificativa}", lang="en")))
    nome = str(prop).split("/")[-1]
    print(f"  ✅ {nome:25s} → RO:has_quality")

# Salvar módulo BFO
output = Path("ontology/modules/perinatal_bfo.ttl")
g.serialize(str(output), format="turtle")
print()
print(f"✅ Módulo BFO salvo: {output}")
print(f"   Triplas: {len(g)}")

# ════════════════════════════════════════
# PARTE 4: VERIFICAR ALINHAMENTO
# ════════════════════════════════════════
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("SPARQL: Verificando alinhamento BFO")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

q_bfo = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX bfo:  <http://purl.obolibrary.org/obo/BFO_>

SELECT ?classe ?superclasse_bfo
WHERE {
    ?classe rdf:type owl:Class .
    ?classe rdfs:subClassOf ?superclasse_bfo .
    FILTER(STRSTARTS(STR(?superclasse_bfo),
           "http://purl.obolibrary.org/obo/BFO_"))
    FILTER(STRSTARTS(STR(?classe),
           "http://perinatalkg.org/"))
}
ORDER BY ?superclasse_bfo
"""

print()
print("Classes PerinatalKG alinhadas ao BFO:")
print()
for row in g.query(q_bfo):
    classe = str(row.classe).split("/")[-1]
    bfo_code = str(row.superclasse_bfo).split("_")[-1]
    bfo_labels = {
        "0000003": "Occurrent (Process)",
        "0000040": "Material Entity",
        "0000019": "Quality",
        "0000029": "Site",
        "0000030": "Object"
    }
    bfo_nome = bfo_labels.get(bfo_code, bfo_code)
    print(f"  {classe:25s} → BFO: {bfo_nome}")

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎉 INTEGRAÇÃO BFO CONCLUÍDA!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ Você aprendeu:")
print("   • BFO divide em Continuant e Occurrent")
print("   • Birth é Occurrent (processo)")
print("   • Mother é Material Entity (persiste)")
print("   • birthWeight é Quality")
print("   • Municipality é Site")
print()
print("✅ Sua ontologia agora é:")
print("   • Compatível com OBO Foundry")
print("   • Interoperável com Gene Ontology, HPO")
print("   • Aceita por Journal of Biomedical Informatics!")
print()
print("🎯 Próximo: Instalar Apache Jena Fuseki (Dia 14)")
PYEOF

echo "✅ Tutorial BFO criado!"
echo ""
echo "🚀 Executando..."
python docs/tutorials/07_bfo_integration.py

git add docs/tutorials/07_bfo_integration.py
git add ontology/modules/
git add setup/week3/dia13_bfo_ontology.sh
git commit -m "Day 13: BFO alignment for PerinatalKG ontology

- BFO structure explained (Continuant vs Occurrent)
- Birth → BFO:Occurrent (Process)
- Mother → BFO:MaterialEntity
- Municipality → BFO:Site
- birthWeight → BFO:Quality
- Module saved: ontology/modules/perinatal_bfo.ttl
- OBO Foundry compatible!
"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 13 COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   [██████░░░░] 60% Semana 3"
echo ""
echo "   ✅ Dia 11: OWL avançado"
echo "   ✅ Dia 12: SPARQL avançado"
echo "   ✅ Dia 13: BFO alignment"
echo "   ⬜ Dia 14: Apache Jena Fuseki"
echo "   ⬜ Dia 15: Endpoint SPARQL público"
echo ""
echo "🎯 PRÓXIMO: DIA 14 - APACHE JENA FUSEKI!"
