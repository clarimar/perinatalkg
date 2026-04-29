#!/bin/bash
#
# DIA 2 - CONECTAR AO GITHUB
# Tempo estimado: 20 minutos
#
# Este script:
# 1. Configura remote do GitHub
# 2. Faz primeiro push
# 3. Configura branch main

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐙 DIA 2: CONECTAR AO GITHUB"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar se Git está inicializado
if [ ! -d .git ]; then
    echo "❌ ERRO: Repositório Git não inicializado!"
    echo "   Execute primeiro: ./setup/week1/dia1_git_setup.sh"
    exit 1
fi

echo "📍 Diretório atual: $(pwd)"
echo ""

# Solicitar informações do GitHub
echo "⚙️  CONFIGURAÇÃO DO GITHUB"
echo ""
echo "Antes de continuar, você precisa:"
echo "1. Acessar: https://github.com/new"
echo "2. Criar repositório com:"
echo "   - Nome: perinatalkg"
echo "   - Privado: ✓"
echo "   - NÃO adicionar README, .gitignore ou license"
echo ""
read -p "Já criou o repositório no GitHub? (y/n): " created

if [ "$created" != "y" ]; then
    echo ""
    echo "❌ Por favor, crie o repositório primeiro e execute novamente."
    echo ""
    echo "Passos:"
    echo "1. Acesse: https://github.com/new"
    echo "2. Nome: perinatalkg"
    echo "3. Marque 'Private'"
    echo "4. Clique 'Create repository'"
    echo "5. NÃO siga as instruções mostradas (vamos fazer aqui)"
    echo ""
    exit 1
fi

echo ""
read -p "Digite seu USERNAME do GitHub: " github_user

if [ -z "$github_user" ]; then
    echo "❌ ERRO: Username não pode estar vazio!"
    exit 1
fi

REPO_URL="git@github.com:${github_user}/perinatalkg.git"

echo ""
echo "🔗 URL do repositório: $REPO_URL"
echo ""

# Verificar se já existe remote
if git remote | grep -q "^origin$"; then
    echo "⚠️  Remote 'origin' já existe!"
    echo "   URL atual: $(git remote get-url origin)"
    echo ""
    read -p "Deseja substituir? (y/n): " replace
    
    if [ "$replace" = "y" ]; then
        echo "🔧 Removendo remote antigo..."
        git remote remove origin
        echo "✅ Remote removido!"
    else
        echo "❌ Abortado pelo usuário"
        exit 1
    fi
fi

echo ""
echo "🔗 Adicionando remote 'origin'..."
git remote add origin "$REPO_URL"
echo "✅ Remote adicionado!"

echo ""
echo "📋 Verificando branch..."
CURRENT_BRANCH=$(git branch --show-current)
echo "   Branch atual: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 Renomeando branch para 'main'..."
    git branch -M main
    echo "✅ Branch renomeada!"
fi

echo ""
echo "🚀 Fazendo push inicial para GitHub..."
echo "   (Isso pode demorar alguns minutos na primeira vez)"
echo ""

# Verificar autenticação SSH
echo "🔑 Testando autenticação SSH..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ Autenticação SSH OK!"
else
    echo "⚠️  Autenticação SSH pode ter problemas."
    echo "   Se o push falhar, você precisa configurar SSH keys."
    echo ""
    echo "   Guia: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    echo ""
    read -p "Tentar push mesmo assim? (y/n): " try_push
    
    if [ "$try_push" != "y" ]; then
        echo "❌ Push cancelado"
        echo ""
        echo "Configure SSH e execute novamente:"
        echo "  ./setup/week1/dia2_github_remote.sh"
        exit 1
    fi
fi

echo ""
git push -u origin main

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 2 CONCLUÍDO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Status:"
git remote -v
echo ""
echo "🌐 Repositório GitHub:"
echo "   https://github.com/${github_user}/perinatalkg"
echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo ""
echo "1. Acesse seu repositório no GitHub"
echo "2. Verifique se os arquivos estão lá"
echo "3. Execute o próximo script:"
echo "   ./setup/week1/dia3_restructure.sh"
echo ""
