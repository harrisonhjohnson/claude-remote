"""macOS keystroke injection using osascript."""

import subprocess
import shlex


def type_text(text: str) -> bool:
    """
    Type text into the active application using osascript.
    Returns True on success, False on failure.
    """
    if not text:
        return True

    # Escape for AppleScript string
    escaped = text.replace('\\', '\\\\').replace('"', '\\"')

    script = f'tell application "System Events" to keystroke "{escaped}"'

    try:
        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True
    except subprocess.SubprocessError as e:
        print(f"Keystroke error: {e}")
        return False


def press_enter() -> bool:
    """Press the Enter/Return key."""
    script = 'tell application "System Events" to key code 36'
    try:
        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True
    except subprocess.SubprocessError as e:
        print(f"Enter key error: {e}")
        return False


def press_key(key_code: int) -> bool:
    """Press a specific key by key code."""
    script = f'tell application "System Events" to key code {key_code}'
    try:
        subprocess.run(
            ['osascript', '-e', script],
            check=True,
            capture_output=True,
            timeout=5
        )
        return True
    except subprocess.SubprocessError as e:
        print(f"Key press error: {e}")
        return False


if __name__ == "__main__":
    # Test
    import time
    print("Testing in 3 seconds... click on a text field!")
    time.sleep(3)
    type_text("Hello from Claude Remote!")
    press_enter()
