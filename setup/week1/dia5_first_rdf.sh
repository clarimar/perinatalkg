#!/bin/bash
#
# DIA 5 - PRIMEIRO CONTATO COM RDF
# Tempo estimado: 2 horas
#
# Este script:
# 1. Atualiza requirements.txt com stack RDF completo
# 2. Cria seu primeiro arquivo Turtle
# 3. Valida com RDFLib
# 4. Cria tutorial interativo
# 5. Documenta aprendizado

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎓 DIA 5: PRIMEIRO CONTATO COM RDF!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📦 PASSO 1: Atualizando requirements.txt com stack RDF..."
echo ""

cat > requirements.txt << 'REQEOF'
# ════════════════════════════════════════════════
# PERINATALKG - Python Dependencies
# ════════════════════════════════════════════════

# === Data Acquisition ===
pysus>=0.5.17                # DATASUS data (SINASC, SIM)
sidrapy>=0.1.5               # IBGE SIDRA API
requests>=2.31.0

# === Data Processing ===
pandas>=2.0.0
polars>=1.0.0                # High-performance DataFrames
pyarrow>=14.0.0              # Parquet support
numpy>=1.24.0

# === Record Linkage ===
recordlinkage>=0.16.0        # Probabilistic linkage SINASC-SIM

# === RDF/OWL Stack (NEW!) ===
rdflib>=7.0.0                # Core RDF library
SPARQLWrapper>=2.0.0         # SPARQL queries
owlrl>=6.0.3                 # OWL RL reasoner
pyshacl>=0.25.0              # SHACL validation

# === Utilities ===
loguru>=0.7.0                # Logging
tqdm>=4.66.0                 # Progress bars
python-dotenv>=1.0.0         # Environment variables

# === Development ===
pytest>=7.4.0
black>=23.0.0
isort>=5.12.0

# === Documentation ===
jupyter>=1.0.0
jupyterlab>=4.0.0
REQEOF

echo "✅ requirements.txt atualizado!"

echo ""
echo "📥 Instalando novas dependências RDF..."
source activate.sh
pip install -q rdflib SPARQLWrapper owlrl pyshacl

echo "✅ Dependências instaladas!"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 PASSO 2: Criando seu PRIMEIRO arquivo RDF!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

mkdir -p docs/tutorials

cat > docs/tutorials/01_first_rdf_triple.ttl << 'TTLEOF'
# ════════════════════════════════════════════════
# MEU PRIMEIRO ARQUIVO RDF/TURTLE! 🎉
# ════════════════════════════════════════════════
#
# Data: 2026-04-29
# Autor: Clarimar José Coelho
# Propósito: Aprender a sintaxe Turtle básica
#
# ════════════════════════════════════════════════

# --- PREFIXOS (atalhos para URIs) ---
@prefix ex: <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ════════════════════════════════════════════════
# MINHA PRIMEIRA TRIPLA!
# ════════════════════════════════════════════════

# Sujeito        Predicado    Objeto
ex:Clarimar      rdf:type     ex:Researcher .

# Isso significa: "Clarimar é do tipo Pesquisador"

# ════════════════════════════════════════════════
# MAIS INFORMAÇÕES SOBRE MIM
# ════════════════════════════════════════════════

ex:Clarimar ex:worksOn ex:PerinatalKG .
ex:Clarimar ex:affiliation "Federal University of Goiás" .
ex:Clarimar ex:email "clarimarc@gmail.com" .

# ════════════════════════════════════════════════
# INFORMAÇÕES SOBRE O PROJETO
# ════════════════════════════════════════════════

ex:PerinatalKG rdf:type ex:ResearchProject .
ex:PerinatalKG ex:title "PerinatalKG: Knowledge Graph for Perinatal Health" .
ex:PerinatalKG ex:targetJournal "Journal of Biomedical Informatics" .
ex:PerinatalKG ex:datasetSize 27000000 .  # 27 milhões de nascimentos!
ex:PerinatalKG ex:startDate "2026-04-29"^^xsd:date .

# ════════════════════════════════════════════════
# COLABORAÇÃO
# ════════════════════════════════════════════════

ex:Guilherme rdf:type ex:Researcher .
ex:Guilherme ex:affiliation "UNICAMP/FCM" .
ex:Guilherme ex:collaboratesWith ex:Clarimar .

# ════════════════════════════════════════════════
# TOTAL: 12 triplas RDF! 🎉
# ════════════════════════════════════════════════
TTLEOF

echo "✅ Primeiro arquivo Turtle criado!"
echo "   📄 docs/tutorials/01_first_rdf_triple.ttl"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 PASSO 3: Validando com RDFLib (Python)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > docs/tutorials/validate_first_rdf.py << 'PYEOF'
"""
Validar primeiro arquivo RDF/Turtle
"""
from rdflib import Graph
from pathlib import Path

print("🔍 Carregando arquivo Turtle...")
print()

g = Graph()
turtle_file = Path("docs/tutorials/01_first_rdf_triple.ttl")

try:
    g.parse(turtle_file, format="turtle")
    print(f"✅ ARQUIVO VÁLIDO!")
    print(f"   Triplas encontradas: {len(g)}")
    print()
    
    print("📊 Conteúdo do grafo:")
    print("━" * 70)
    for i, (s, p, o) in enumerate(g, 1):
        # Simplificar URIs para leitura
        subj = str(s).replace("http://example.org/", "ex:")
        pred = str(p).replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:")
        pred = pred.replace("http://example.org/", "ex:")
        obj = str(o).replace("http://example.org/", "ex:")
        
        print(f"{i:2d}. {subj:20s} → {pred:25s} → {obj}")
    
    print("━" * 70)
    print()
    print("🎉 PARABÉNS! Você criou e validou seu primeiro RDF!")
    print()
    
except Exception as e:
    print(f"❌ ERRO ao validar: {e}")
    exit(1)
PYEOF

echo "🐍 Executando validação Python..."
echo ""

python docs/tutorials/validate_first_rdf.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 PASSO 4: Criando tutorial interativo"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > docs/tutorials/README_RDF_Learning.md << 'MDEOF'
# 🎓 RDF Learning Journey - Week 1

## 📅 Day 5 (29 Apr 2026)

### ✅ O que aprendi hoje:

1. **RDF é baseado em TRIPLAS:**
   - Sujeito → Predicado → Objeto
   - Exemplo: `Clarimar → trabalha_em → PerinatalKG`

2. **Turtle é uma sintaxe legível para escrever RDF:**
   - Usa prefixos (@prefix) para encurtar URIs
   - Termina sentenças com ponto (.)
   - É case-sensitive!

3. **Cada "coisa" tem uma URI:**
   - `ex:Clarimar` = `http://example.org/Clarimar`
   - URIs são globalmente únicos

4. **RDFLib valida e processa RDF em Python:**
   - Carrega arquivos Turtle
   - Permite queries
   - Serializa em diferentes formatos

### 🎯 Próximos passos (Day 6-10):

- [ ] Aprender SPARQL (query language)
- [ ] Criar ontologia mínima com classes
- [ ] Usar Protégé (editor visual)
- [ ] Instalar Apache Jena Fuseki

### 📝 Notas importantes:

- URIs não precisam ser "resolvíveis" (não precisam abrir no navegador)
- Turtle é case-sensitive: `ex:Person` ≠ `ex:person`
- Todo RDF válido pode ser convertido para outros formatos (N-Triples, JSON-LD, etc.)

### 🔗 Recursos úteis:

- W3C Turtle Spec: https://www.w3.org/TR/turtle/
- RDFLib Docs: https://rdflib.readthedocs.io/
- Turtle Validator: http://ttl.summerofcode.be/

---

**Tempo gasto hoje:** 2 horas  
**Sensação:** 🎉 Empolgante! Finalmente entendi o básico de RDF!
MDEOF

echo "✅ Tutorial documentado!"
echo "   📄 docs/tutorials/README_RDF_Learning.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 PASSO 5: Recursos de aprendizado"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > docs/LEARNING_RESOURCES.md << 'MDEOF'
# 📚 Learning Resources - PerinatalKG

## 🎯 Week 1-4: RDF/OWL Fundamentals

### 📖 Books (Priority Order)

1. **"Semantic Web for the Working Ontologist"** - Allemang & Hendler
   - ISBN: 978-0123859655
   - Status: 🛒 To order
   - Chapters 1-6 for Week 1-4

2. **"Foundations of Semantic Web Technologies"** - Hitzler et al.
   - Advanced reference
   - For Weeks 5-8

### 🎓 Online Courses

1. **Stanford CS520: Knowledge Graphs**
   - https://web.stanford.edu/class/cs520/
   - FREE, high quality
   - Lectures 1-4 for Week 2

2. **Coursera: Knowledge Graphs** - Aidan Hogan
   - https://www.coursera.org/learn/knowledge-graphs
   - Optional, complements Stanford

### 🌐 W3C Tutorials

- RDF Primer: https://www.w3.org/TR/rdf-primer/
- SPARQL Tutorial: https://www.w3.org/TR/sparql11-query/
- OWL 2 Primer: https://www.w3.org/TR/owl2-primer/
- Turtle Spec: https://www.w3.org/TR/turtle/

### 🛠️ Tools

- **Protégé**: https://protege.stanford.edu/
  - Visual OWL editor
  - Download: Desktop version
  
- **Apache Jena**: https://jena.apache.org/
  - RDF toolkit for Java
  - Fuseki for SPARQL endpoint

- **RDFLib** (Python): https://rdflib.readthedocs.io/
  - Already installed!

### 💬 Communities

- Stack Overflow: [rdf] [owl] [sparql] [semantic-web]
- W3C Mailing Lists: https://lists.w3.org/
- BioPortal Community: https://bioportal.bioontology.org/

### 📊 Progress Tracking

Week 1: ████░ 80% (Day 5/5 in progress)
Week 2: ░░░░░ 0%
Week 3: ░░░░░ 0%
Week 4: ░░░░░ 0%

---

**Update this document weekly!**
MDEOF

echo "✅ Recursos documentados!"
echo "   📄 docs/LEARNING_RESOURCES.md"

echo ""
echo "💾 Commitando tudo..."

git add requirements.txt
git add docs/tutorials/
git add docs/LEARNING_RESOURCES.md
git commit -m "Day 5: First RDF tutorial + learning resources

- Updated requirements.txt with RDF/OWL stack
- Created first Turtle file (01_first_rdf_triple.ttl)
- Python validation script with RDFLib
- RDF learning journal started
- Comprehensive learning resources documented

Milestone: First working RDF triplet! 🎉
"

echo ""
echo "🚀 Fazendo push..."
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎊🎊🎊 DIA 5 CONCLUÍDO! 🎊🎊🎊"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✨ SEMANA 1 COMPLETA! ✨"
echo ""
echo "📊 Conquistas da Semana 1:"
echo ""
echo "   [█████] 100% - 5/5 dias completos!"
echo ""
echo "   ✅ Dia 1: Git setup"
echo "   ✅ Dia 2: GitHub remote + SSH"
echo "   ✅ Dia 3: Projeto reestruturado"
echo "   ✅ Dia 4: README profissional"
echo "   ✅ Dia 5: Primeiro RDF! 🎓"
echo ""
echo "🎯 O QUE VOCÊ CONSEGUIU:"
echo ""
echo "   • Repositório versionado e no GitHub"
echo "   • Estrutura profissional de projeto"
echo "   • Documentação publication-ready"
echo "   • Primeiro arquivo RDF válido criado!"
echo "   • RDFLib funcionando"
echo ""
echo "🌐 GitHub: https://github.com/clarimar/perinatalkg"
echo ""
echo "📚 Próxima Semana (Semana 2):"
echo "   • Baixar dados SIM e IBGE"
echo "   • Aprender SPARQL básico"
echo "   • Instalar Protégé"
echo "   • Criar ontologia mínima"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 PARABÉNS, CLARIMAR!"
echo ""
echo "Você completou a primeira semana do projeto mais"
echo "ambicioso da sua carreira! Take a bow! 🙌"
echo ""
echo "🏖️  DESCANSE no fim de semana!"
echo ""
echo "Segunda-feira começamos Semana 2! 🚀"
echo ""
