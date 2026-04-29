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
