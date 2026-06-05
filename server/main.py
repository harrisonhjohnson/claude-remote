#!/usr/bin/env python3
"""Claude Remote - Voice-to-terminal server for Claude Code."""

import asyncio
import json
import secrets
import socket
from pathlib import Path
from urllib.parse import quote

import qrcode
import websockets

from transcribe import transcribe
from keystroke import type_text, press_enter

# Configuration
PORT = 8765
TOKEN_LENGTH = 32

# Generate session token
session_token = secrets.token_urlsafe(TOKEN_LENGTH)


def get_local_ip() -> str:
    """Get the local IP address."""
    try:
        # Connect to external address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def display_qr(url: str):
    """Display QR code in terminal."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Print ASCII QR code
    qr.print_ascii(invert=True)


async def handle_connection(websocket):
    """Handle a WebSocket connection from the phone."""
    # Validate token from query params
    path = websocket.request.path if hasattr(websocket, 'request') else websocket.path

    # Parse token from path (format: /?token=xyz)
    token = None
    if "?" in path:
        query = path.split("?", 1)[1]
        for param in query.split("&"):
            if param.startswith("token="):
                token = param.split("=", 1)[1]
                break

    if token != session_token:
        print(f"Invalid token received: {token[:8]}..." if token else "No token")
        await websocket.close(1008, "Invalid token")
        return

    print("Client connected!")

    audio_buffer = bytearray()

    try:
        async for message in websocket:
            if isinstance(message, bytes):
                # Audio chunk received
                audio_buffer.extend(message)

            elif isinstance(message, str):
                data = json.loads(message)
                msg_type = data.get("type")

                if msg_type == "audio_end":
                    # Process accumulated audio
                    if audio_buffer:
                        print(f"Processing {len(audio_buffer)} bytes of audio...")
                        await websocket.send(json.dumps({"type": "processing"}))

                        try:
                            text = transcribe(bytes(audio_buffer))
                            print(f"Transcribed: {text}")

                            if text:
                                # Type the text
                                type_text(text)
                                await websocket.send(json.dumps({
                                    "type": "transcribed",
                                    "text": text
                                }))
                            else:
                                await websocket.send(json.dumps({
                                    "type": "error",
                                    "message": "No speech detected"
                                }))

                        except Exception as e:
                            print(f"Transcription error: {e}")
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": str(e)
                            }))

                        audio_buffer.clear()

                elif msg_type == "enter":
                    # Press enter key
                    press_enter()
                    await websocket.send(json.dumps({"type": "enter_sent"}))

                elif msg_type == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))

    except websockets.ConnectionClosed:
        print("Client disconnected")


async def main():
    """Start the WebSocket server."""
    local_ip = get_local_ip()
    ws_url = f"ws://{local_ip}:{PORT}/?token={session_token}"
    web_url = f"http://{local_ip}:5000/?ws={quote(ws_url, safe='')}"

    print("\n" + "=" * 50, flush=True)
    print("  CLAUDE REMOTE SERVER", flush=True)
    print("=" * 50, flush=True)
    print(f"\nLocal IP: {local_ip}", flush=True)
    print(f"Port: {PORT}", flush=True)
    print(f"\nScan QR code to open the web app and connect:\n", flush=True)

    display_qr(web_url)

    print(f"\nOr open: {web_url}", flush=True)
    print("\nWaiting for connection...", flush=True)
    print("=" * 50 + "\n", flush=True)

    async with websockets.serve(
        handle_connection,
        "0.0.0.0",
        PORT,
        max_size=10 * 1024 * 1024,  # 10MB max message
    ):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
