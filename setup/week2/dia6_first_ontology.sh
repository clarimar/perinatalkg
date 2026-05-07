#!/bin/bash
#
# DIA 6 - PRIMEIRA ONTOLOGIA PERINATAL
# Tempo estimado: 45 minutos
#
# Cria ontologia OWL mínima do domínio perinatal
# e abre no Protégé para exploração visual

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧬 DIA 6: PRIMEIRA ONTOLOGIA PERINATAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p ontology/modules
mkdir -p data_samples

echo "📝 Criando ontologia perinatal mínima..."
echo ""

cat > ontology/perinatalkg_minimal.ttl << 'TTLEOF'
# ════════════════════════════════════════════════
# PerinatalKG - Ontologia Mínima (Week 2)
# ════════════════════════════════════════════════
#
# Autor: Clarimar José Coelho
# Data: 2026-05-06
# Propósito: Primeira ontologia OWL do domínio
#
# ════════════════════════════════════════════════

@prefix pkg:  <http://perinatalkg.org/ontology/> .
@prefix pkgr: <http://perinatalkg.org/resource/> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

# ════════════════════════════════════════════════
# DECLARAÇÃO DA ONTOLOGIA
# ════════════════════════════════════════════════

pkg:PerinatalKGOntology rdf:type owl:Ontology ;
    rdfs:label "PerinatalKG Ontology"@en ;
    rdfs:label "Ontologia PerinatalKG"@pt ;
    rdfs:comment "Ontologia para integração de dados perinatais, climáticos e socioeconômicos no Brasil"@pt ;
    owl:versionInfo "0.1.0-dev" .

# ════════════════════════════════════════════════
# HIERARQUIA DE CLASSES - NASCIMENTO
# ════════════════════════════════════════════════

# Classe raiz
pkg:Birth rdf:type owl:Class ;
    rdfs:label "Birth"@en ;
    rdfs:label "Nascimento"@pt ;
    rdfs:comment "Um evento de nascimento vivo registrado no SINASC"@pt .

# Nascimento a termo (≥37 semanas)
pkg:TermBirth rdf:type owl:Class ;
    rdfs:subClassOf pkg:Birth ;
    rdfs:label "Term Birth"@en ;
    rdfs:label "Nascimento a Termo"@pt ;
    rdfs:comment "Nascimento com idade gestacional ≥ 37 semanas"@pt .

# Nascimento prematuro (<37 semanas)
pkg:PretermBirth rdf:type owl:Class ;
    rdfs:subClassOf pkg:Birth ;
    rdfs:label "Preterm Birth"@en ;
    rdfs:label "Nascimento Prematuro"@pt ;
    rdfs:comment "Nascimento com idade gestacional < 37 semanas (OMS)"@pt ;
    skos:exactMatch <http://snomed.info/id/395122000> .

# Subtipos de prematuridade (OMS)
pkg:PretermBirthLate rdf:type owl:Class ;
    rdfs:subClassOf pkg:PretermBirth ;
    rdfs:label "Late Preterm Birth"@en ;
    rdfs:label "Prematuro Tardio"@pt ;
    rdfs:comment "34+0 a 36+6 semanas"@pt .

pkg:PretermBirthModerate rdf:type owl:Class ;
    rdfs:subClassOf pkg:PretermBirth ;
    rdfs:label "Moderate Preterm Birth"@en ;
    rdfs:label "Prematuro Moderado"@pt ;
    rdfs:comment "32+0 a 33+6 semanas"@pt .

pkg:PretermBirthEarly rdf:type owl:Class ;
    rdfs:subClassOf pkg:PretermBirth ;
    rdfs:label "Early Preterm Birth"@en ;
    rdfs:label "Prematuro Muito Precoce"@pt ;
    rdfs:comment "28+0 a 31+6 semanas"@pt .

pkg:PretermBirthExtreme rdf:type owl:Class ;
    rdfs:subClassOf pkg:PretermBirth ;
    rdfs:label "Extreme Preterm Birth"@en ;
    rdfs:label "Prematuro Extremo"@pt ;
    rdfs:comment "< 28 semanas"@pt .

# ════════════════════════════════════════════════
# PESO AO NASCER
# ════════════════════════════════════════════════

pkg:LowBirthWeight rdf:type owl:Class ;
    rdfs:subClassOf pkg:Birth ;
    rdfs:label "Low Birth Weight"@en ;
    rdfs:label "Baixo Peso ao Nascer"@pt ;
    rdfs:comment "Peso ao nascer < 2500g (OMS)"@pt ;
    skos:exactMatch <http://snomed.info/id/276610007> .

pkg:VeryLowBirthWeight rdf:type owl:Class ;
    rdfs:subClassOf pkg:LowBirthWeight ;
    rdfs:label "Very Low Birth Weight"@en ;
    rdfs:label "Muito Baixo Peso ao Nascer"@pt ;
    rdfs:comment "Peso ao nascer < 1500g"@pt .

# ════════════════════════════════════════════════
# HIERARQUIA DE CLASSES - MÃE
# ════════════════════════════════════════════════

pkg:Mother rdf:type owl:Class ;
    rdfs:label "Mother"@en ;
    rdfs:label "Mãe"@pt ;
    rdfs:comment "Mãe do nascido vivo registrada no SINASC"@pt .

pkg:AdolescentMother rdf:type owl:Class ;
    rdfs:subClassOf pkg:Mother ;
    rdfs:label "Adolescent Mother"@en ;
    rdfs:label "Mãe Adolescente"@pt ;
    rdfs:comment "Mãe com idade < 20 anos"@pt .

# ════════════════════════════════════════════════
# HIERARQUIA DE CLASSES - EXPOSIÇÃO CLIMÁTICA
# ════════════════════════════════════════════════

pkg:ClimateExposure rdf:type owl:Class ;
    rdfs:label "Climate Exposure"@en ;
    rdfs:label "Exposição Climática"@pt ;
    rdfs:comment "Exposição a condição climática durante a gestação"@pt .

pkg:HeatExposure rdf:type owl:Class ;
    rdfs:subClassOf pkg:ClimateExposure ;
    rdfs:label "Heat Exposure"@en ;
    rdfs:label "Exposição ao Calor"@pt ;
    rdfs:comment "Exposição a temperatura elevada durante gestação"@pt .

pkg:ExtremeHeatExposure rdf:type owl:Class ;
    rdfs:subClassOf pkg:HeatExposure ;
    rdfs:label "Extreme Heat Exposure"@en ;
    rdfs:label "Exposição a Calor Extremo"@pt ;
    rdfs:comment "Exposição a temperatura acima do percentil 95 local"@pt .

# ════════════════════════════════════════════════
# HIERARQUIA DE CLASSES - LOCALIZAÇÃO
# ════════════════════════════════════════════════

pkg:Location rdf:type owl:Class ;
    rdfs:label "Location"@en ;
    rdfs:label "Localização"@pt .

pkg:Municipality rdf:type owl:Class ;
    rdfs:subClassOf pkg:Location ;
    rdfs:label "Municipality"@en ;
    rdfs:label "Município"@pt ;
    rdfs:comment "Município brasileiro (código IBGE 6 dígitos)"@pt .

pkg:State rdf:type owl:Class ;
    rdfs:subClassOf pkg:Location ;
    rdfs:label "State"@en ;
    rdfs:label "Estado"@pt .

pkg:Region rdf:type owl:Class ;
    rdfs:subClassOf pkg:Location ;
    rdfs:label "Region"@en ;
    rdfs:label "Região"@pt ;
    rdfs:comment "Uma das 5 regiões do Brasil"@pt .

# ════════════════════════════════════════════════
# PROPRIEDADES DE DADOS (Data Properties)
# ════════════════════════════════════════════════

# Peso ao nascer
pkg:birthWeight rdf:type owl:DatatypeProperty ;
    rdfs:domain pkg:Birth ;
    rdfs:range xsd:integer ;
    rdfs:label "birth weight (grams)"@en ;
    rdfs:label "peso ao nascer (gramas)"@pt ;
    rdfs:comment "Peso ao nascer em gramas (SINASC: PESO)"@pt .

# Idade gestacional
pkg:gestationalAge rdf:type owl:DatatypeProperty ;
    rdfs:domain pkg:Birth ;
    rdfs:range xsd:integer ;
    rdfs:label "gestational age (weeks)"@en ;
    rdfs:label "idade gestacional (semanas)"@pt ;
    rdfs:comment "Idade gestacional em semanas completas (SINASC: SEMAGESTAC)"@pt .

# Temperatura média
pkg:meanTemperature rdf:type owl:DatatypeProperty ;
    rdfs:domain pkg:ClimateExposure ;
    rdfs:range xsd:decimal ;
    rdfs:label "mean temperature (°C)"@en ;
    rdfs:label "temperatura média (°C)"@pt .

# Dias de calor extremo
pkg:extremeHeatDays rdf:type owl:DatatypeProperty ;
    rdfs:domain pkg:ClimateExposure ;
    rdfs:range xsd:integer ;
    rdfs:label "extreme heat days"@en ;
    rdfs:label "dias de calor extremo"@pt .

# Idade materna
pkg:maternalAge rdf:type owl:DatatypeProperty ;
    rdfs:domain pkg:Mother ;
    rdfs:range xsd:integer ;
    rdfs:label "maternal age (years)"@en ;
    rdfs:label "idade materna (anos)"@pt .

# Consultas pré-natal
pkg:prenatalVisits rdf:type owl:DatatypeProperty ;
    rdfs:domain pkg:Mother ;
    rdfs:range xsd:integer ;
    rdfs:label "prenatal visits"@en ;
    rdfs:label "consultas pré-natal"@pt .

# ════════════════════════════════════════════════
# PROPRIEDADES DE OBJETO (Object Properties)
# ════════════════════════════════════════════════

pkg:bornBy rdf:type owl:ObjectProperty ;
    rdfs:domain pkg:Birth ;
    rdfs:range pkg:Mother ;
    rdfs:label "born by"@en ;
    rdfs:label "nascido de"@pt .

pkg:bornIn rdf:type owl:ObjectProperty ;
    rdfs:domain pkg:Birth ;
    rdfs:range pkg:Municipality ;
    rdfs:label "born in"@en ;
    rdfs:label "nascido em"@pt .

pkg:exposedTo rdf:type owl:ObjectProperty ;
    rdfs:domain pkg:Birth ;
    rdfs:range pkg:ClimateExposure ;
    rdfs:label "exposed to"@en ;
    rdfs:label "exposto a"@pt .

pkg:locatedIn rdf:type owl:ObjectProperty ;
    rdfs:domain pkg:Municipality ;
    rdfs:range pkg:State ;
    rdfs:label "located in"@en ;
    rdfs:label "localizado em"@pt .

pkg:partOf rdf:type owl:ObjectProperty ;
    rdfs:domain pkg:State ;
    rdfs:range pkg:Region ;
    rdfs:label "part of"@en ;
    rdfs:label "parte de"@pt .

# ════════════════════════════════════════════════
# INSTÂNCIAS EXEMPLO (para testar)
# ════════════════════════════════════════════════

# Regiões do Brasil
pkgr:RegionNorth rdf:type pkg:Region ;
    rdfs:label "North Region"@en ;
    rdfs:label "Região Norte"@pt .

pkgr:RegionNortheast rdf:type pkg:Region ;
    rdfs:label "Northeast Region"@en ;
    rdfs:label "Região Nordeste"@pt .

pkgr:RegionCenterWest rdf:type pkg:Region ;
    rdfs:label "Center-West Region"@en ;
    rdfs:label "Região Centro-Oeste"@pt .

pkgr:RegionSoutheast rdf:type pkg:Region ;
    rdfs:label "Southeast Region"@en ;
    rdfs:label "Região Sudeste"@pt .

pkgr:RegionSouth rdf:type pkg:Region ;
    rdfs:label "South Region"@en ;
    rdfs:label "Região Sul"@pt .

# Estado exemplo
pkgr:StateGO rdf:type pkg:State ;
    rdfs:label "Goiás"@pt ;
    pkg:partOf pkgr:RegionCenterWest .

# Município exemplo
pkgr:MunicipalityGoiania rdf:type pkg:Municipality ;
    rdfs:label "Goiânia"@pt ;
    pkg:locatedIn pkgr:StateGO .

# Nascimento exemplo
pkgr:Birth_Example_001 rdf:type pkg:Birth ;
    pkg:birthWeight 3200 ;
    pkg:gestationalAge 39 ;
    pkg:bornIn pkgr:MunicipalityGoiania .

# Nascimento prematuro exemplo
pkgr:Birth_Example_002 rdf:type pkg:PretermBirthLate ;
    pkg:birthWeight 2100 ;
    pkg:gestationalAge 35 ;
    pkg:bornIn pkgr:MunicipalityGoiania .

# ════════════════════════════════════════════════
# TOTAL: ~80 triplas!
# ════════════════════════════════════════════════
TTLEOF

echo "✅ Ontologia criada!"
echo "   📄 ontology/perinatalkg_minimal.ttl"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 Validando ontologia com Python..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

source activate.sh

python << 'PYEOF'
from rdflib import Graph, Namespace, RDF, RDFS, OWL

g = Graph()
g.parse("ontology/perinatalkg_minimal.ttl", format="turtle")

PKG = Namespace("http://perinatalkg.org/ontology/")

print(f"✅ Ontologia válida!")
print(f"   Total de triplas: {len(g)}")
print()

# Contar classes
classes = list(g.subjects(RDF.type, OWL.Class))
print(f"📊 Estatísticas:")
print(f"   Classes OWL:              {len(classes)}")

# Contar propriedades
data_props = list(g.subjects(RDF.type, OWL.DatatypeProperty))
obj_props = list(g.subjects(RDF.type, OWL.ObjectProperty))
print(f"   Data Properties:          {len(data_props)}")
print(f"   Object Properties:        {len(obj_props)}")

# Contar instâncias
instances = list(g.subjects(RDF.type, None))
instances = [i for i in instances if str(i).startswith("http://perinatalkg.org/resource/")]
print(f"   Instâncias exemplo:       {len(instances)}")
print()

# Listar hierarquia de classes
print("🌳 Hierarquia de Classes:")
print()

def get_subclasses(graph, parent):
    return list(graph.subjects(RDFS.subClassOf, parent))

root_classes = [PKG.Birth, PKG.Mother, PKG.ClimateExposure, PKG.Location]

for root in root_classes:
    label = g.value(root, RDFS.label)
    print(f"   📦 {label}")
    for sub in get_subclasses(g, root):
        sub_label = g.value(sub, RDFS.label)
        print(f"      └─ {sub_label}")
        for subsub in get_subclasses(g, sub):
            subsub_label = g.value(subsub, RDFS.label)
            print(f"         └─ {subsub_label}")
    print()

print("🎉 Sua primeira ontologia OWL está pronta!")
print()
print("📖 Agora abra no Protégé para ver visualmente!")
PYEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 ABRINDO NO PROTÉGÉ..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Execute os passos abaixo:"
echo ""
echo "1. Abra o Protégé:"
echo "   protege"
echo ""
echo "2. Vá em: File → Open"
echo ""
echo "3. Navegue até:"
echo "   ~/Projects/perinatalkg/ontology/perinatalkg_minimal.ttl"
echo ""
echo "4. Explore as abas:"
echo "   • Classes → Ver hierarquia"
echo "   • Object Properties → Ver relações"
echo "   • Data Properties → Ver atributos"
echo "   • Individuals → Ver instâncias"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Commitar ontologia
git add ontology/perinatalkg_minimal.ttl
git commit -m "Day 6: Add minimal perinatal OWL ontology

- Birth hierarchy (Term, Preterm with subtypes)
- Mother hierarchy (AdolescentMother)
- ClimateExposure hierarchy (Heat, ExtremeHeat)
- Location hierarchy (Municipality, State, Region)
- Data properties: birthWeight, gestationalAge, etc.
- Object properties: bornBy, bornIn, exposedTo, etc.
- Example instances for testing
- ~80 RDF triples
- SNOMED-CT mappings for key classes
"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 6 COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 CONQUISTAS DE HOJE:"
echo ""
echo "   ✅ Protégé instalado"
echo "   ✅ Ontologia OWL criada (~80 triplas)"
echo "   ✅ Hierarquias: Birth, Mother, Climate, Location"
echo "   ✅ Data + Object properties definidas"
echo "   ✅ Mapeamentos SNOMED-CT"
echo "   ✅ Instâncias exemplo"
echo "   ✅ Validada com RDFLib"
echo "   ✅ Commitada no GitHub"
echo ""
echo "🎯 PRÓXIMO PASSO (DIA 7 - Amanhã):"
echo "   📥 Baixar dados SIM (mortalidade neonatal)"
echo "   🐍 ./setup/week2/dia7_sim_download.sh"
echo ""
