"""
Tutorial OWL Avançado - Restrições e Axiomas
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Bloco 2 do guia Guilherme:
- OWL 2 DL: lógica de descrição
- Axiomas: equivalentClass, disjointWith, subClassOf
- Restrições: someValuesFrom, allValuesFrom, cardinalities
"""
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from rdflib.collection import Collection

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎓 OWL AVANÇADO - PerinatalKG")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# ════════════════════════════════════════
# PARTE 1: RESTRIÇÕES OWL
# ════════════════════════════════════════
print("PARTE 1: Restrições OWL")
print("─────────────────────────────────────────────")
print()
print("Em OWL, podemos definir classes por RESTRIÇÕES")
print("sobre propriedades.")
print()
print("Exemplo: PretermBirth = nascimento com IG < 37")
print()
print("""
# Em Turtle:
pkg:PretermBirth owl:equivalentClass [
    rdf:type owl:Class ;
    owl:intersectionOf (
        pkg:Birth
        [ rdf:type owl:Restriction ;
          owl:onProperty pkg:gestationalAge ;
          owl:someValuesFrom [
              rdf:type rdfs:Datatype ;
              owl:onDatatype xsd:integer ;
              owl:withRestrictions (
                  [ xsd:maxExclusive 37 ]
              )
          ]
        ]
    )
] .
""")

# ════════════════════════════════════════
# PARTE 2: TIPOS DE RESTRIÇÕES
# ════════════════════════════════════════
print("PARTE 2: Tipos de Restrições OWL 2")
print("─────────────────────────────────────────────")
print()

restricoes = {
    "someValuesFrom": {
        "desc": "Existe PELO MENOS UMA instância da propriedade",
        "exemplo": "Birth que bornIn ALGUM Municipality",
        "turtle": "pkg:Birth owl:equivalentClass [ owl:onProperty pkg:bornIn ; owl:someValuesFrom pkg:Municipality ]"
    },
    "allValuesFrom": {
        "desc": "TODOS os valores da propriedade são do tipo",
        "exemplo": "Birth onde TODOS os exposedTo são ClimateExposure",
        "turtle": "[ owl:onProperty pkg:exposedTo ; owl:allValuesFrom pkg:ClimateExposure ]"
    },
    "hasValue": {
        "desc": "Propriedade tem UM VALOR ESPECÍFICO",
        "exemplo": "Nascimento no Brasil",
        "turtle": "[ owl:onProperty pkg:country ; owl:hasValue pkgr:Brazil ]"
    },
    "minCardinality": {
        "desc": "Propriedade ocorre NO MÍNIMO N vezes",
        "exemplo": "Birth com pelo menos 1 exposedTo",
        "turtle": "[ owl:onProperty pkg:exposedTo ; owl:minCardinality 1 ]"
    },
    "maxCardinality": {
        "desc": "Propriedade ocorre NO MÁXIMO N vezes",
        "exemplo": "Birth com no máximo 1 mother",
        "turtle": "[ owl:onProperty pkg:bornBy ; owl:maxCardinality 1 ]"
    },
    "exactCardinality": {
        "desc": "Propriedade ocorre EXATAMENTE N vezes",
        "exemplo": "Birth com exatamente 1 município",
        "turtle": "[ owl:onProperty pkg:bornIn ; owl:cardinality 1 ]"
    }
}

for nome, info in restricoes.items():
    print(f"  🔹 {nome}")
    print(f"     Significado: {info['desc']}")
    print(f"     Exemplo: {info['exemplo']}")
    print()

# ════════════════════════════════════════
# PARTE 3: AXIOMAS DE CLASSE
# ════════════════════════════════════════
print("PARTE 3: Axiomas de Classe")
print("─────────────────────────────────────────────")
print()

axiomas = {
    "subClassOf": "Toda instância de A é também instância de B\nEx: PretermBirth subClassOf Birth",
    "equivalentClass": "A e B têm exatamente as mesmas instâncias\nEx: PretermBirth ≡ Birth ∩ gestationalAge < 37",
    "disjointWith": "A e B não compartilham instâncias\nEx: PretermBirth disjointWith TermBirth",
    "complementOf": "A = tudo que NÃO é B\nEx: TermBirth = Birth complementOf PretermBirth",
    "unionOf": "A = B ou C\nEx: Birth = PretermBirth ∪ TermBirth",
    "intersectionOf": "A = B e C\nEx: HighRisk = PretermBirth ∩ LowBirthWeight"
}

for nome, desc in axiomas.items():
    print(f"  🔷 owl:{nome}")
    print(f"     {desc}")
    print()

# ════════════════════════════════════════
# PARTE 4: APLICAR NA ONTOLOGIA
# ════════════════════════════════════════
print("PARTE 4: Criando ontologia com restrições reais")
print("─────────────────────────────────────────────")
print()

# Criar ontologia avançada
g = Graph()
PKG = Namespace("http://perinatalkg.org/ontology/")
PKGR = Namespace("http://perinatalkg.org/resource/")
g.bind("pkg", PKG)
g.bind("pkgr", PKGR)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# Carregar ontologia base
g.parse("ontology/perinatalkg_minimal.ttl", format="turtle")
print(f"Ontologia base carregada: {len(g)} triplas")

# AXIOMA 1: Disjunção entre PretermBirth e TermBirth
print()
print("Adicionando axioma: PretermBirth disjointWith TermBirth...")
g.add((PKG.PretermBirth, OWL.disjointWith, PKG.TermBirth))
print("✅ Adicionado!")

# AXIOMA 2: Cardinalidade - Birth nasce em exatamente 1 município
print("Adicionando restrição: Birth bornIn exatamente 1 Municipality...")
restriction = BNode()
g.add((restriction, RDF.type, OWL.Restriction))
g.add((restriction, OWL.onProperty, PKG.bornIn))
g.add((restriction, OWL.maxCardinality, Literal(1, datatype=XSD.nonNegativeInteger)))
g.add((PKG.Birth, RDFS.subClassOf, restriction))
print("✅ Adicionado!")

# AXIOMA 3: Birth deve ter pelo menos 1 gestationalAge
print("Adicionando restrição: Birth tem pelo menos 1 gestationalAge...")
restriction2 = BNode()
g.add((restriction2, RDF.type, OWL.Restriction))
g.add((restriction2, OWL.onProperty, PKG.gestationalAge))
g.add((restriction2, OWL.minCardinality, Literal(1, datatype=XSD.nonNegativeInteger)))
g.add((PKG.Birth, RDFS.subClassOf, restriction2))
print("✅ Adicionado!")

# AXIOMA 4: HighRiskBirth = PretermBirth ∩ LowBirthWeight
print("Criando classe: HighRiskBirth = PretermBirth ∩ LowBirthWeight...")
high_risk = PKG.HighRiskBirth
g.add((high_risk, RDF.type, OWL.Class))
g.add((high_risk, RDFS.label, Literal("High Risk Birth", lang="en")))
g.add((high_risk, RDFS.label, Literal("Nascimento de Alto Risco", lang="pt")))
g.add((high_risk, RDFS.comment, Literal(
    "Nascimento prematuro E com baixo peso - grupo de maior vulnerabilidade",
    lang="pt"
)))

# intersectionOf usando BNode
intersection = BNode()
g.add((high_risk, OWL.equivalentClass, intersection))
g.add((intersection, RDF.type, OWL.Class))
members = BNode()
g.add((intersection, OWL.intersectionOf, members))
col = Collection(g, members, [PKG.PretermBirth, PKG.LowBirthWeight])
print("✅ HighRiskBirth criada!")

# AXIOMA 5: AdolescentMother com restrição de idade
print("Adicionando restrição: AdolescentMother com maternalAge < 20...")
restriction3 = BNode()
g.add((restriction3, RDF.type, OWL.Restriction))
g.add((restriction3, OWL.onProperty, PKG.maternalAge))
g.add((PKG.AdolescentMother, RDFS.subClassOf, restriction3))
print("✅ Adicionado!")

# Salvar ontologia avançada
g.serialize("ontology/perinatalkg_advanced.ttl", format="turtle")
print()
print(f"✅ Ontologia avançada salva!")
print(f"   Total de triplas: {len(g)}")

# Verificar com SPARQL
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("SPARQL: Verificando axiomas adicionados")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Query: classes disjuntas
q_disjoint = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?classA ?classB
WHERE {
    ?classA owl:disjointWith ?classB .
}
"""
print()
print("Classes disjuntas:")
for row in g.query(q_disjoint):
    a = str(row.classA).split("/")[-1]
    b = str(row.classB).split("/")[-1]
    print(f"  {a} ⊥ {b}")

# Query: classes equivalentes
q_equiv = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?classe ?label
WHERE {
    ?classe owl:equivalentClass ?def .
    ?classe rdfs:label ?label .
    FILTER(LANG(?label) = "pt")
}
"""
print()
print("Classes com definição formal (equivalentClass):")
for row in g.query(q_equiv):
    classe = str(row.classe).split("/")[-1]
    print(f"  {classe}: {row.label}")

print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎉 TUTORIAL OWL AVANÇADO CONCLUÍDO!")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print("✅ Você aprendeu:")
print("   • someValuesFrom / allValuesFrom")
print("   • Cardinalidades (min, max, exact)")
print("   • disjointWith (classes exclusivas)")
print("   • equivalentClass (definição formal)")
print("   • intersectionOf (AND lógico)")
print("   • Criou HighRiskBirth como interseção!")
print()
print("🎯 Próximo: CS520 Lecture 1 online")
print("   https://web.stanford.edu/class/cs520/")
