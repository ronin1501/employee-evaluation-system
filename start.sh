#!/bin/bash
set -e

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

if ! python3 -c "import flask, flask_sqlalchemy, matplotlib, numpy, reportlab, sqlalchemy" >/dev/null 2>&1; then
    echo "[*] Installing dependencies..."
    python3 -m pip install -r requirements.txt
fi

echo "[*] Starting Flask server..."
python3 app.py
