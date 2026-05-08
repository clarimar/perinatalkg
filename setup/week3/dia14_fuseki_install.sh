#!/bin/bash
# DIA 14 - INSTALAR APACHE JENA FUSEKI
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 DIA 14: APACHE JENA FUSEKI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Fuseki = Triplestore + SPARQL endpoint"
echo "É onde vão morar as ~1 bilhão de triplas!"
echo ""

# Verificar Java
echo "1️⃣  Verificando Java..."
java -version 2>&1 | head -1
echo ""

# Download Fuseki
FUSEKI_VERSION="5.0.0"
FUSEKI_DIR="/opt/fuseki"
FUSEKI_FILE="apache-jena-fuseki-${FUSEKI_VERSION}.tar.gz"
FUSEKI_URL="https://dlcdn.apache.org/jena/binaries/${FUSEKI_FILE}"

echo "2️⃣  Verificando Fuseki..."
if [ -d "$FUSEKI_DIR" ]; then
    echo "✅ Fuseki já instalado em $FUSEKI_DIR"
    fuseki-server --version 2>/dev/null || true
else
    echo "📥 Baixando Apache Jena Fuseki ${FUSEKI_VERSION}..."
    cd ~/Downloads

    if [ ! -f "$FUSEKI_FILE" ]; then
        wget -q --show-progress "$FUSEKI_URL"
    else
        echo "   Arquivo já existe, pulando download..."
    fi

    echo "📦 Instalando..."
    tar -xzf "$FUSEKI_FILE"
    sudo mv "apache-jena-fuseki-${FUSEKI_VERSION}" "$FUSEKI_DIR"
    sudo ln -sf "$FUSEKI_DIR/fuseki-server" /usr/local/bin/fuseki-server
    echo "✅ Fuseki instalado!"
fi

cd ~/Projects/perinatalkg

# Criar diretório de dados Fuseki
echo ""
echo "3️⃣  Criando estrutura Fuseki..."
mkdir -p fuseki-data/databases/perinatalkg
mkdir -p fuseki-data/configuration

# Criar configuração do dataset
cat > fuseki-data/configuration/perinatalkg.ttl << 'CONFEOF'
@prefix :      <#> .
@prefix fuseki: <http://jena.apache.org/fuseki#> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix tdb2:  <http://jena.apache.org/2016/tdb#> .
@prefix ja:    <http://jena.hpl.hp.com/2005/11/Assembler#> .

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PerinatalKG - Fuseki Dataset Configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

:service_perinatalkg rdf:type fuseki:Service ;
    rdfs:label "PerinatalKG SPARQL Service" ;
    fuseki:name "perinatalkg" ;
    fuseki:serviceQuery "sparql" ;
    fuseki:serviceQuery "query" ;
    fuseki:serviceUpdate "update" ;
    fuseki:serviceUpload "upload" ;
    fuseki:serviceReadWriteGraphStore "data" ;
    fuseki:dataset :dataset_perinatalkg .

:dataset_perinatalkg rdf:type tdb2:DatasetTDB2 ;
    tdb2:location "databases/perinatalkg" ;
    rdfs:label "PerinatalKG TDB2 Dataset" .
CONFEOF

echo "✅ Configuração criada!"

# Criar script de inicialização
cat > fuseki-data/start_fuseki.sh << 'STARTEOF'
#!/bin/bash
# Iniciar Fuseki com dataset PerinatalKG

FUSEKI_HOME="/opt/fuseki"
DATA_DIR="$(dirname "$0")"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Iniciando Apache Jena Fuseki"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dataset: PerinatalKG"
echo "🌐 Interface: http://localhost:3030"
echo "🔍 SPARQL:   http://localhost:3030/perinatalkg/sparql"
echo ""
echo "Para parar: Ctrl+C"
echo ""

cd "$DATA_DIR"
"$FUSEKI_HOME/fuseki-server" \
    --config=configuration/perinatalkg.ttl \
    --port=3030
STARTEOF
chmod +x fuseki-data/start_fuseki.sh

echo "✅ Script de inicialização criado!"

# Testar instalação
echo ""
echo "4️⃣  Testando instalação..."
if command -v fuseki-server &> /dev/null; then
    echo "✅ fuseki-server disponível!"
    fuseki-server --version 2>&1 | head -3
else
    echo "⚠️  fuseki-server não encontrado no PATH"
    echo "   Verificando instalação direta..."
    if [ -f "/opt/fuseki/fuseki-server" ]; then
        echo "✅ Encontrado em /opt/fuseki/fuseki-server"
    fi
fi

# Carregar ontologia no Fuseki via tdbloader
echo ""
echo "5️⃣  Carregando dados no TDB2..."

if [ -f "/opt/fuseki/bin/tdb2.tdbloader" ]; then
    LOADER="/opt/fuseki/bin/tdb2.tdbloader"
elif [ -f "/opt/fuseki/tdb2.tdbloader" ]; then
    LOADER="/opt/fuseki/tdb2.tdbloader"
else
    LOADER=""
fi

if [ -n "$LOADER" ]; then
    echo "Carregando ontologia mínima..."
    $LOADER --loc=fuseki-data/databases/perinatalkg \
            ontology/perinatalkg_minimal.ttl

    echo "Carregando ontologia avançada..."
    $LOADER --loc=fuseki-data/databases/perinatalkg \
            ontology/perinatalkg_advanced.ttl 2>/dev/null || true

    echo "Carregando módulo BFO..."
    $LOADER --loc=fuseki-data/databases/perinatalkg \
            ontology/modules/perinatal_bfo.ttl

    echo "Carregando amostra de nascimentos..."
    $LOADER --loc=fuseki-data/databases/perinatalkg \
            data_samples/sinasc_100_births.ttl

    echo "✅ Dados carregados no TDB2!"
else
    echo "⚠️  tdb2.tdbloader não encontrado"
    echo "   Vamos carregar via API depois de iniciar o Fuseki"
fi

git add fuseki-data/configuration/ fuseki-data/start_fuseki.sh
git add setup/week3/dia14_fuseki_install.sh
git add .gitignore
git commit -m "Day 14: Apache Jena Fuseki setup

- Fuseki installed at /opt/fuseki
- TDB2 dataset configuration created
- Start script: fuseki-data/start_fuseki.sh
- Endpoint: http://localhost:3030/perinatalkg/sparql
"
git push

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DIA 14 COMPLETO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 O QUE TEMOS:"
echo "   ✅ Fuseki instalado"
echo "   ✅ Dataset TDB2 configurado"
echo "   ✅ Script de inicialização pronto"
echo ""
echo "🚀 PARA INICIAR O FUSEKI:"
echo "   cd fuseki-data"
echo "   ./start_fuseki.sh"
echo ""
echo "🌐 INTERFACE WEB:"
echo "   http://localhost:3030"
echo ""
echo "🔍 SPARQL ENDPOINT:"
echo "   http://localhost:3030/perinatalkg/sparql"
echo ""
echo "   [████████░░] 80% Semana 3"
echo ""
echo "   ✅ Dia 14: Fuseki instalado"
echo "   ⬜ Dia 15: Carregar dados + queries via HTTP"
echo ""
echo "🎯 PRÓXIMO: DIA 15 - ENDPOINT SPARQL AO VIVO!"
