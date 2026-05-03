#!/bin/bash
# PerinatalKG Environment Activation

VENV_PATH="$HOME/Projects/perinatalkg/climaterna_env"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at: $VENV_PATH"
    echo ""
    echo "Creating new environment..."
    python3 -m venv "$VENV_PATH"
    echo "✅ Environment created!"
fi

source "$VENV_PATH/bin/activate"

echo "✅ PerinatalKG environment activated!"
echo "   Python: $(which python)"
echo "   Path: $(pwd)"
