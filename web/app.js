// Claude Remote - Voice control for Claude Code

class ClaudeRemote {
    constructor() {
        this.ws = null;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.isRecording = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;

        this.initElements();
        this.initEventListeners();
        this.checkUrlParams();
    }

    initElements() {
        // Screens
        this.connectScreen = document.getElementById('connect-screen');
        this.mainScreen = document.getElementById('main-screen');

        // Connect screen
        this.wsUrlInput = document.getElementById('ws-url');
        this.connectBtn = document.getElementById('connect-btn');

        // Main screen
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
        this.transcriptText = document.getElementById('transcript-text');
        this.pttBtn = document.getElementById('ptt-btn');
        this.pttLabel = this.pttBtn.querySelector('.ptt-label');
        this.enterBtn = document.getElementById('enter-btn');
        this.disconnectBtn = document.getElementById('disconnect-btn');
    }

    initEventListeners() {
        // Connect button
        this.connectBtn.addEventListener('click', () => this.connect());
        this.wsUrlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.connect();
        });

        // PTT button - handle both touch and mouse
        this.pttBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.pttBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });
        this.pttBtn.addEventListener('touchcancel', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // Mouse fallback for testing on desktop
        this.pttBtn.addEventListener('mousedown', () => this.startRecording());
        this.pttBtn.addEventListener('mouseup', () => this.stopRecording());
        this.pttBtn.addEventListener('mouseleave', () => {
            if (this.isRecording) this.stopRecording();
        });

        // Enter button
        this.enterBtn.addEventListener('click', () => this.sendEnter());

        // Disconnect button
        this.disconnectBtn.addEventListener('click', () => this.disconnect());
    }

    checkUrlParams() {
        // Check if URL was passed via query params (from QR code)
        const params = new URLSearchParams(window.location.search);
        const wsUrl = params.get('ws');
        if (wsUrl) {
            this.wsUrlInput.value = decodeURIComponent(wsUrl);
            // Auto-connect if URL provided
            setTimeout(() => this.connect(), 500);
        }
    }

    async connect() {
        const url = this.wsUrlInput.value.trim();
        if (!url) {
            alert('Please enter a WebSocket URL');
            return;
        }

        this.setStatus('connecting', 'Connecting...');

        try {
            this.ws = new WebSocket(url);

            this.ws.onopen = () => {
                console.log('Connected');
                this.reconnectAttempts = 0;
                this.setStatus('connected', 'Connected');
                this.showMainScreen();
                this.startPingLoop();
            };

            this.ws.onclose = (event) => {
                console.log('Disconnected', event.code, event.reason);
                this.setStatus('disconnected', 'Disconnected');
                this.handleDisconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error', error);
                this.setStatus('disconnected', 'Connection error');
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };

        } catch (error) {
            console.error('Connection failed', error);
            this.setStatus('disconnected', 'Connection failed');
        }
    }

    handleMessage(data) {
        console.log('Received:', data);

        switch (data.type) {
            case 'processing':
                this.setStatus('processing', 'Processing...');
                this.transcriptText.textContent = 'Transcribing...';
                this.transcriptText.classList.remove('active', 'error');
                break;

            case 'transcribed':
                this.setStatus('connected', 'Connected');
                this.transcriptText.textContent = data.text;
                this.transcriptText.classList.add('active');
                this.transcriptText.classList.remove('error');
                this.vibrate([50]);
                break;

            case 'error':
                this.setStatus('connected', 'Connected');
                this.transcriptText.textContent = data.message;
                this.transcriptText.classList.add('error');
                this.transcriptText.classList.remove('active');
                this.vibrate([100, 50, 100]);
                break;

            case 'enter_sent':
                this.vibrate([30]);
                break;

            case 'pong':
                // Keep-alive response
                break;
        }
    }

    async startRecording() {
        if (this.isRecording || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            return;
        }

        try {
            // Request microphone access
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true,
                }
            });

            // Create MediaRecorder with Opus codec
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
                ? 'audio/webm;codecs=opus'
                : 'audio/webm';

            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: mimeType,
                audioBitsPerSecond: 24000
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(event.data);
                }
            };

            this.mediaRecorder.start(250); // Send chunks every 250ms
            this.isRecording = true;

            // Update UI
            this.pttBtn.classList.add('recording');
            this.pttLabel.textContent = 'Recording...';
            this.transcriptText.textContent = 'Listening...';
            this.transcriptText.classList.remove('active', 'error');

            this.vibrate([50]);

        } catch (error) {
            console.error('Failed to start recording', error);
            alert('Microphone access denied. Please allow microphone access.');
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.isRecording = false;

        // Stop MediaRecorder
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }

        // Stop audio stream
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }

        // Signal end of audio
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'audio_end' }));
        }

        // Update UI
        this.pttBtn.classList.remove('recording');
        this.pttLabel.textContent = 'Hold to Talk';

        this.vibrate([30]);
    }

    sendEnter() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'enter' }));
        }
    }

    disconnect() {
        this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
        if (this.ws) {
            this.ws.close();
        }
        this.showConnectScreen();
    }

    handleDisconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.setStatus('connecting', `Reconnecting (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => {
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.connect();
                }
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }

    startPingLoop() {
        // Send ping every 30 seconds to keep connection alive
        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000);
    }

    setStatus(state, text) {
        this.statusIndicator.className = state;
        this.statusText.textContent = text;
    }

    showMainScreen() {
        this.connectScreen.classList.add('hidden');
        this.mainScreen.classList.remove('hidden');
    }

    showConnectScreen() {
        this.mainScreen.classList.add('hidden');
        this.connectScreen.classList.remove('hidden');
        this.setStatus('disconnected', 'Disconnected');
    }

    vibrate(pattern) {
        if ('vibrate' in navigator) {
            navigator.vibrate(pattern);
        }
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ClaudeRemote();
});

// Register service worker for PWA
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(() => {
        // Service worker registration failed, app still works
    });
}
