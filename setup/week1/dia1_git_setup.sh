#!/bin/bash
#
# DIA 1 - SETUP GIT LOCAL
# Tempo estimado: 30 minutos
#
# Este script:
# 1. Inicializa repositório Git
# 2. Cria .gitignore
# 3. Faz commit inicial

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 DIA 1: SETUP GIT LOCAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar diretório
echo "📍 Diretório atual: $(pwd)"
echo ""

# Verificar se já existe .git
if [ -d .git ]; then
    echo "⚠️  Repositório Git já existe!"
    echo "   Verificando status..."
    git status
    echo ""
    read -p "Deseja continuar? (y/n): " continue
    if [ "$continue" != "y" ]; then
        echo "❌ Abortado pelo usuário"
        exit 1
    fi
else
    echo "🔧 Inicializando repositório Git..."
    git init
    echo "✅ Git inicializado!"
fi

echo ""
echo "📝 Criando .gitignore..."

cat > .gitignore << 'GITEOF'
# ================================
# PERINATALKG .gitignore
# ================================

# === Dados Sensíveis (LGPD) ===
data/raw/sinasc/*.dbc
data/raw/sinasc/*.dbf
data/raw/sim/*.dbc
data/raw/sim/*.dbf
data/linkage/*_nominais.parquet

# === Dados Grandes ===
*.parquet
data/processed/*.parquet
data/linked/*.parquet
ontology/dumps/*.ttl
ontology/dumps/*.nt
ontology/dumps/*.rdf

# EXCEÇÕES: manter samples pequenos
!data_samples/*.parquet
!data_samples/*.ttl

# === Neo4j ===
neo4j/
*.db

# === Python ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
climaterna_env/
*.egg-info/
dist/
build/

# === Logs ===
*.log
logs/

# === Credenciais ===
.env
.env.*
credentials/
*.key
*.pem

# === IDEs ===
.vscode/
.idea/
*.swp
*.swo
*~

# === OS ===
.DS_Store
Thumbs.db

# === Temporários ===
*.tmp
*.bak
*.cache
.pytest_cache/

# === Jupyter ===
.ipynb_checkpoints/
*.ipynb_checkpoints

# === RDF Temporários ===
*.ttl.tmp
*.rdf.tmp

# === Fuseki Data ===
fuseki-data/
tdb2/
GITEOF

echo "✅ .gitignore criado!"

echo ""
echo "📋 Adicionando arquivos ao Git..."

# Adicionar estrutura básica
git add .gitignore
git add *.md 2>/dev/null || true
git add requirements.txt 2>/dev/null || true
git add activate.sh 2>/dev/null || true

# Adicionar scripts
git add setup/ 2>/dev/null || true
git add scripts/*.py 2>/dev/null || true

# Adicionar documentação
git add docs/ 2>/dev/null || true
git add knowledge_graph/ 2>/dev/null || true

# Adicionar notebooks (sem outputs)
git add notebooks/*.ipynb 2>/dev/null || true

echo ""
echo "💾 Fazendo commit inicial..."
git commit -m "Initial commit: ClimaternaKG v0.1 (pre-RDF migration)

- Initialize Git repository
- Add .gitignore (LGPD-compliant)
- Current state: Neo4j property graph with 27M births
- Next: Migration to RDF/OWL (PerinatalKG Scenario B)

Structure:
- data/: Raw and processed data
- scripts/: ETL and analysis scripts
- knowledge_graph/: Neo4j KG documentation
- docs/: Documentation
- notebooks/: Jupyter analysis notebooks
"

echo ""
echo "✅ COMMIT INICIAL COMPLETO!"
echo ""
echo "📊 Status do repositório:"
echo ""
git log --oneline -n 1
echo ""
echo "📁 Arquivos versionados:"
git ls-files | head -20
echo "   ..."
echo "   Total: $(git ls-files | wc -l) arquivos"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 1 CONCLUÍDO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo ""
echo "1. Criar repositório no GitHub:"
echo "   - Acesse: https://github.com/new"
echo "   - Nome: perinatalkg"
echo "   - Privado: ✓"
echo "   - NÃO adicione README, .gitignore ou licença"
echo ""
echo "2. Depois execute:"
echo "   ./setup/week1/dia2_github_remote.sh"
echo ""
