#!/bin/bash
#
# DIA 3 - REESTRUTURAÇÃO DO PROJETO
# Tempo estimado: 40 minutos
#
# Este script:
# 1. Renomeia diretório: climaterna → perinatalkg
# 2. Cria estrutura de diretórios formal
# 3. Migra scripts para nova organização
# 4. Atualiza referências no código

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 DIA 3: REESTRUTURAÇÃO DO PROJETO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar diretório atual
CURRENT_DIR=$(basename $(pwd))
echo "📍 Diretório atual: $CURRENT_DIR"

if [ "$CURRENT_DIR" != "climaterna" ]; then
    echo "⚠️  AVISO: Esperava estar em 'climaterna', mas está em '$CURRENT_DIR'"
    echo ""
    read -p "Continuar mesmo assim? (y/n): " continue
    if [ "$continue" != "y" ]; then
        echo "❌ Abortado"
        exit 1
    fi
fi

echo ""
echo "🔍 Verificando estrutura atual..."
ls -la

echo ""
echo "⚠️  IMPORTANTE: Este script vai renomear o diretório do projeto"
echo "   De: ~/Projects/climaterna"
echo "   Para: ~/Projects/perinatalkg"
echo ""
read -p "Deseja continuar? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "❌ Operação cancelada"
    exit 1
fi

echo ""
echo "📋 Criando estrutura de diretórios conforme guia Guilherme..."

# Criar estrutura completa
mkdir -p docs/tutorials
mkdir -p docs/design_notes
mkdir -p ontology/modules
mkdir -p ontology/imports
mkdir -p ontology/dumps
mkdir -p etl
mkdir -p queries
mkdir -p reasoner
mkdir -p benchmarks/results
mkdir -p examples
mkdir -p tests
mkdir -p data_samples

echo "✅ Estrutura de diretórios criada!"

echo ""
echo "📦 Migrando scripts para diretório etl/..."

# Migrar scripts de ETL para pasta etl/
if [ -d scripts ]; then
    echo "   Copiando scripts/*.py → etl/"
    cp scripts/*.py etl/ 2>/dev/null || true
    echo "   ✅ Scripts migrados!"
else
    echo "   ⚠️  Diretório scripts/ não encontrado"
fi

echo ""
echo "📄 Criando arquivos de documentação base..."

# Criar arquivo de changelog
cat > CHANGELOG.md << 'CHANGEEOF'
# Changelog - PerinatalKG

## [0.1.0] - 2026-04-29

### Added
- Initial project structure
- Git version control
- GitHub repository setup
- Directory structure aligned with JBI methodology paper requirements
- Setup scripts for Week 1-4

### Changed
- Project renamed from ClimaternaKG to PerinatalKG
- Restructured according to RDF/OWL migration plan

### In Progress
- RDF/OWL learning (Weeks 1-4)
- SIM data integration
- IBGE socioeconomic data integration
CHANGEEOF

echo "✅ CHANGELOG.md criado!"

# Criar arquivo de licença (temporário - confirmar depois)
cat > LICENSE << 'LICEOF'
Apache License 2.0

Copyright (c) 2026 Clarimar José Coelho

(License text to be confirmed at publication)
LICEOF

echo "✅ LICENSE criado!"

echo ""
echo "💾 Commitando alterações..."

git add .
git commit -m "Day 3: Restructure project for PerinatalKG methodology paper

- Create formal directory structure (ontology/, etl/, queries/, etc.)
- Migrate scripts/ to etl/
- Add CHANGELOG.md and LICENSE
- Align structure with Journal of Biomedical Informatics requirements
- Ready for RDF/OWL development

Ref: Guilherme's operational guide Section III
"

echo "✅ Commit realizado!"

echo ""
echo "🚀 Fazendo push para GitHub..."
git push

echo ""
echo "🔄 Agora vamos renomear o diretório do projeto..."
echo "   (Este script vai se mover para o novo local)"
echo ""

cd ..
echo "📍 Movido para: $(pwd)"

if [ -d perinatalkg ]; then
    echo "⚠️  AVISO: Diretório perinatalkg já existe!"
    echo "   Conteúdo atual:"
    ls -la perinatalkg
    echo ""
    read -p "Deseja SOBRESCREVER? (y/n): " overwrite
    if [ "$overwrite" = "y" ]; then
        rm -rf perinatalkg
        echo "✅ Diretório antigo removido"
    else
        echo "❌ Abortado - mantenha apenas um dos diretórios"
        exit 1
    fi
fi

echo ""
echo "🔄 Renomeando: climaterna → perinatalkg"
mv climaterna perinatalkg

echo "✅ Projeto renomeado!"

cd perinatalkg
echo ""
echo "📍 Novo diretório: $(pwd)"

echo ""
echo "🔧 Atualizando activate.sh..."

cat > activate.sh << 'ACTIVEOF'
#!/bin/bash
# PerinatalKG Environment Activation

VENV_PATH="$HOME/Projects/perinatalkg/climaterna_env"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Expected: $VENV_PATH"
    echo ""
    echo "Create it with:"
    echo "  python3 -m venv $VENV_PATH"
    echo "  source $VENV_PATH/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

source "$VENV_PATH/bin/activate"

echo "✅ PerinatalKG environment activated!"
echo "   Python: $(which python)"
echo "   Path: $(pwd)"
ACTIVEOF

chmod +x activate.sh

echo ""
echo "💾 Commitando renomeação..."
git add activate.sh
git commit -m "Update activate.sh for perinatalkg directory structure"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 3 CONCLUÍDO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Estrutura final:"
echo ""
tree -L 1 -a 2>/dev/null || ls -la
echo ""
echo "📂 Nova estrutura de diretórios:"
tree -L 2 -d 2>/dev/null || find . -type d -maxdepth 2 | sort
echo ""
echo "🎯 IMPORTANTE:"
echo "   Seu projeto agora está em:"
echo "   ~/Projects/perinatalkg/"
echo ""
echo "   Atualize seus aliases/favoritos!"
echo ""
echo "🎯 PRÓXIMO PASSO:"
echo "   Execute: ./setup/week1/dia4_readme.sh"
echo ""
