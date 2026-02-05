# Claude Remote

Voice control for Claude Code from your phone. Push-to-talk microphone that types into your terminal.

## Overview

This is a split architecture application:
- **Web App** (`/web`): Static HTML/CSS/JS PWA that runs on your phone's browser
- **Server** (`/server`): Python WebSocket server that runs on your Mac (requires macOS-specific tools)

## Replit Setup

The Replit environment serves the static web app for phone access. The backend server is designed to run locally on a Mac since it requires:
- `whisper-cpp` for speech-to-text
- `osascript` for macOS keystroke injection

### Running on Replit

The web app is served on port 5000 via `serve_web.py`.

### Full Setup (on Mac)

1. Run `./install.sh` to install dependencies
2. Run `./run.sh` or `cd server && python main.py` to start the WebSocket server
3. Scan the QR code with your phone to connect

## Project Structure

```
/
├── serve_web.py      # Replit: serves static web app on port 5000
├── web/              # Static web app (HTML/CSS/JS PWA)
│   ├── index.html    # Main page
│   ├── app.js        # WebSocket client logic
│   ├── style.css     # Styles
│   ├── manifest.json # PWA manifest
│   └── sw.js         # Service worker
├── server/           # Python WebSocket server (for Mac)
│   ├── main.py       # WebSocket server
│   ├── transcribe.py # Whisper transcription
│   └── keystroke.py  # macOS keystroke injection
├── install.sh        # Mac installer script
└── run.sh           # Mac run script
```

## Architecture

```
Phone (Browser)          Mac (Python Server)
     │                         │
     │  WebSocket (audio)      │
     ├────────────────────────►│
     │                    whisper-cpp
     │  WebSocket (text)       │
     │◄────────────────────────┤
     │                    osascript (keystroke)
```

## Recent Changes

- 2026-02-05: Initial Replit import setup
  - Created serve_web.py to serve static web files
  - Configured workflow for port 5000
