# Claude Remote

Voice control for Claude Code from your phone. Push-to-talk microphone that types into your terminal.

## Quick Start

### 1. Install Dependencies

```bash
./install.sh
```

This installs:
- whisper-cpp (speech-to-text)
- ffmpeg (audio conversion)
- Python packages (websockets, qrcode)
- Whisper model (~150MB)

### 2. Start the Server

```bash
cd server
python3 main.py
```

You'll see a QR code in your terminal.

### 3. Connect Your Phone

Option A: **Scan the QR code** with your phone camera

Option B: Open the web app and paste the WebSocket URL manually

### 4. Grant Permissions

First time setup requires:
- **Microphone access** on your phone
- **Accessibility permissions** on your Mac (System Preferences → Privacy & Security → Accessibility → Terminal)

## Usage

1. **Hold the red button** to record voice
2. **Release** to transcribe and type into your active window
3. **Tap Enter** to submit the command

Make sure Claude Code is in the foreground when using voice commands.

## Hosting the Web App

The web app in `/web` can be hosted on any static file server:

**Replit:**
1. Create a new Repl (HTML/CSS/JS)
2. Upload the contents of `/web`
3. Your phone accesses the Repl URL

**Local (for testing):**
```bash
cd web
python3 -m http.server 8080
```

## Architecture

```
Phone (Browser)          Mac (Python Server)
     │                         │
     │  WebSocket (audio)      │
     ├────────────────────────►│
     │                         │
     │                    whisper-cpp
     │                         │
     │  WebSocket (text)       │
     │◄────────────────────────┤
     │                         │
     │                    osascript
     │                    (keystroke)
     │                         │
     │                    Terminal
```

## Troubleshooting

### "Microphone access denied"
- iOS: Settings → Safari → Microphone → Allow
- Android: Chrome settings → Site settings → Microphone

### "Connection failed"
- Ensure phone and Mac are on same WiFi network
- Check that port 8765 isn't blocked by firewall
- Try the IP address shown in the QR code URL

### "Transcription not working"
- Check whisper model exists: `ls ~/.cache/whisper/`
- Test whisper: `whisper-cpp --help`

### "Text not typing"
- Grant Accessibility permission to Terminal
- Make sure target app is in foreground

## Configuration

Edit `server/main.py` to change:
- `PORT` - WebSocket port (default: 8765)
- Model path in `transcribe.py` for different Whisper models

## Performance

| Stage | Typical Latency |
|-------|-----------------|
| Audio capture → server | ~20ms |
| Whisper transcription | 200-400ms |
| Keystroke injection | ~10ms |
| **Total** | **~400ms** |

## License

MIT
