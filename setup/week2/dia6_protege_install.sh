#!/bin/bash
#
# DIA 6 - INSTALAR PROTÉGÉ
# Tempo estimado: 30 minutos
#
# Protégé é o editor visual de ontologias OWL
# Desenvolvido pela Stanford University
# Gratuito e open source

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 DIA 6: INSTALANDO PROTÉGÉ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar Java (Protégé precisa de Java 11+)
echo "1️⃣  Verificando Java..."
if java -version 2>&1 | grep -q "version"; then
    echo "✅ Java encontrado:"
    java -version 2>&1
else
    echo "❌ Java não encontrado! Instalando..."
    sudo apt update
    sudo apt install -y openjdk-17-jdk
    echo "✅ Java instalado!"
fi

echo ""
echo "2️⃣  Baixando Protégé 5.6.3..."
echo "   (Pode demorar alguns minutos)"
echo ""

cd ~/Downloads

if [ -f "Protege-5.6.3-linux.tar.gz" ]; then
    echo "⚠️  Arquivo já existe, pulando download..."
else
    wget -q --show-progress \
        "https://github.com/protegeproject/protege-distribution/releases/download/protege-5.6.3/Protege-5.6.3-linux.tar.gz"
    echo "✅ Download completo!"
fi

echo ""
echo "3️⃣  Instalando Protégé em /opt/protege..."

if [ -d "/opt/protege" ]; then
    echo "⚠️  Protégé já instalado, pulando..."
else
    tar -xzf Protege-5.6.3-linux.tar.gz
    sudo mv Protege-5.6.3 /opt/protege
    echo "✅ Protégé instalado!"
fi

echo ""
echo "4️⃣  Criando atalho..."

cat > ~/.local/share/applications/protege.desktop << 'DESKEOF'
[Desktop Entry]
Name=Protégé
Comment=OWL Ontology Editor
Exec=/opt/protege/run.sh
Icon=/opt/protege/icon.png
Terminal=false
Type=Application
Categories=Science;Education;
DESKEOF

# Criar script de inicialização simples
sudo bash -c 'cat > /usr/local/bin/protege << RUNEOF
#!/bin/bash
cd /opt/protege
./run.sh &
RUNEOF'
sudo chmod +x /usr/local/bin/protege

echo "✅ Atalho criado!"

echo ""
echo "5️⃣  Testando instalação..."
if [ -f "/opt/protege/run.sh" ]; then
    echo "✅ Protégé instalado corretamente!"
    echo "   Local: /opt/protege/"
else
    echo "❌ Problema na instalação!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PROTÉGÉ INSTALADO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Para abrir o Protégé:"
echo ""
echo "   Opção 1: protege"
echo "   Opção 2: /opt/protege/run.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎓 PRÓXIMO PASSO:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Vou criar sua primeira ontologia perinatal"
echo "no Protégé via arquivo Turtle!"
echo ""
echo "Execute: ./setup/week2/dia6_first_ontology.sh"
echo ""
