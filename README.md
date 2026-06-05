# Claude Remote

Voice control for Claude Code from your phone. Push-to-talk microphone that transcribes locally and types directly into your terminal.

**Mac-only** — keystroke injection uses `osascript`. Phone and Mac must be on the same WiFi network.

## Quick Start

### 1. Install

```bash
./install.sh
```

Installs whisper-cpp, ffmpeg, Python packages, and the Whisper base model (~150MB).

### 2. Start both servers

In one terminal — the WebSocket server:
```bash
./run.sh
```

In a second terminal — the web app your phone opens:
```bash
python3 serve_web.py
```

### 3. Connect your phone

The WebSocket server prints a QR code. **Scan it** — it opens the web app on your phone and auto-fills the connection URL.

Or open `http://[your-mac-ip]:5000` manually and paste the WebSocket URL shown in the terminal.

### 4. Grant permissions (first run)

- **Microphone** on your phone (browser will prompt)
- **Accessibility** on your Mac: System Preferences → Privacy & Security → Accessibility → enable Terminal

## Usage

1. Hold the red button to record
2. Release to transcribe and type into your active window
3. Make sure Claude Code (or your terminal) is in the foreground

## Architecture

```
Phone (Browser)           Mac (Python servers)
     │                          │
     │  open web app            │
     ├─────────────────────────►│ serve_web.py :5000
     │                          │
     │  WebSocket (audio)       │
     ├─────────────────────────►│ run.sh :8765
     │                          │
     │                     whisper-cpp
     │                          │
     │  WebSocket (transcript)  │
     │◄─────────────────────────┤
     │                          │
     │                     osascript
     │                     (keystroke injection)
     │                          │
     │                     Terminal / Claude Code
```

## Troubleshooting

**"Microphone access denied"**
- iOS: Settings → Safari → Microphone → Allow
- Android: Chrome → Site settings → Microphone

**"Connection failed"**
- Phone and Mac must be on the same WiFi
- Check port 8765 isn't blocked by your firewall
- Use the IP shown in the QR code, not `localhost`

**"Transcription not working"**
- Check model exists: `ls ~/.cache/whisper/`
- Test binary: `whisper-cpp --help`

**"Text not typing"**
- Re-check Accessibility permission in System Preferences
- Make sure the target window is in the foreground

## Configuration

Edit `server/main.py`:
- `PORT` — WebSocket port (default: 8765)

Edit `server/transcribe.py`:
- Model path for a larger/different Whisper model

## Performance

| Stage | Typical latency |
|---|---|
| Audio capture → server | ~20ms |
| Whisper transcription | 200–400ms |
| Keystroke injection | ~10ms |
| **Total** | **~400ms** |

## License

MIT
