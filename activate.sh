#!/bin/bash
# Script para ativar ambiente ClimaternaKG

source ~/Projects/climaterna/climaterna_env/bin/activate
source ~/Projects/climaterna/.env

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌍 ClimaternaKG Environment Activated"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Python: $(python --version)"
echo "Working Directory: $(pwd)"
echo "Neo4j Status:"
sudo systemctl status neo4j --no-pager | head -3
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Comandos úteis:"
echo "  jupyter notebook    - Iniciar Jupyter"
echo "  neo4j status        - Ver status do Neo4j"
echo "  neo4j start/stop    - Controlar Neo4j"
echo ""
