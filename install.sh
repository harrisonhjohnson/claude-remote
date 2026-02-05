#!/bin/bash
# Claude Remote - Installation Script

set -e

echo "=========================================="
echo "  Claude Remote Installer"
echo "=========================================="
echo ""

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is required. Install from https://brew.sh"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    brew install python
fi

# Install whisper-cpp
echo "Installing whisper-cpp..."
brew install whisper-cpp

# Download whisper model
echo ""
echo "Downloading Whisper model (base.en - ~150MB)..."
mkdir -p ~/.cache/whisper

if [ ! -f ~/.cache/whisper/ggml-base.en.bin ]; then
    curl -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" \
        -o ~/.cache/whisper/ggml-base.en.bin
    echo "Model downloaded!"
else
    echo "Model already exists."
fi

# Install ffmpeg (for audio conversion)
echo ""
echo "Installing ffmpeg..."
brew install ffmpeg

# Create virtual environment and install Python dependencies
echo ""
echo "Setting up Python virtual environment..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/server"

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo ""
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
echo "To start the server:"
echo "  cd $SCRIPT_DIR"
echo "  ./run.sh"
echo ""
echo "Then scan the QR code with your phone!"
echo ""
