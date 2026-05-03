from rdflib import Graph

print("🔍 Carregando arquivo Turtle...")
print()

g = Graph()
g.parse("docs/tutorials/01_first_rdf_triple.ttl", format="turtle")

print(f"✅ ARQUIVO VÁLIDO!")
print(f"   Triplas encontradas: {len(g)}")
print()

print("📊 Conteúdo do grafo:")
print("━" * 70)
for i, (s, p, o) in enumerate(g, 1):
    subj = str(s).replace("http://example.org/", "ex:")
    pred = str(p).replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
    pred = pred.replace("http://example.org/", "ex:")
    obj = str(o).replace("http://example.org/", "ex:")
    print(f"{i:2d}. {subj:20s} → {pred:25s} → {obj}")

print("━" * 70)
print()
print("🎉 PARABÉNS! Você criou e validou seu primeiro RDF!")
