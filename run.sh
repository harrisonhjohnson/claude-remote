#!/bin/bash
# Start Claude Remote server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/server"

source venv/bin/activate
python -u main.py
