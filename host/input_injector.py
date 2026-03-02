"""
Receive input events (JSON) and inject them via pyautogui.
Cross-platform: works on Windows and macOS for bidirectional use later.
"""
import json
import pyautogui

# Reduce pyautogui safety delay for more responsive control
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True  # Move mouse to corner to abort

# Stream dimensions (must match host capture size for correct coordinate scaling)
STREAM_WIDTH = 1280
STREAM_HEIGHT = 720


def inject_event(payload: bytes, stream_width: int = STREAM_WIDTH, stream_height: int = STREAM_HEIGHT) -> None:
    """
    Parse one input event (JSON) and perform the action.
    Events: move {x,y}, click {x,y,b}, scroll {d}, key_down {k}, key_up {k}.
    """
    try:
        data = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    screen_w, screen_h = pyautogui.size()
    def scale_x(x): return int(x * screen_w / stream_width) if stream_width else x
    def scale_y(y): return int(y * screen_h / stream_height) if stream_height else y

    t = data.get("t")
    if t == "move":
        x = scale_x(data.get("x", 0))
        y = scale_y(data.get("y", 0))
        pyautogui.moveTo(x, y)
    elif t == "click":
        x = scale_x(data.get("x", 0))
        y = scale_y(data.get("y", 0))
        b = data.get("b", 1)  # 1=left, 2=right, 3=middle
        pyautogui.click(x, y, button=_button_name(b))
    elif t == "scroll":
        d = data.get("d", 0)  # positive = up, negative = down
        pyautogui.scroll(d)
    elif t == "key_down":
        k = data.get("k")
        if k:
            pyautogui.keyDown(_normalize_key(k))
    elif t == "key_up":
        k = data.get("k")
        if k:
            pyautogui.keyUp(_normalize_key(k))


def _button_name(b: int) -> str:
    if b == 2:
        return "right"
    if b == 3:
        return "middle"
    return "left"


def _normalize_key(k) -> str:
    """Normalize key name for pyautogui (lowercase, special names)."""
    if isinstance(k, int):
        # Virtual key code: use character if printable, else leave as-is for pyautogui
        try:
            return chr(k).lower() if 32 <= k < 127 else str(k)
        except ValueError:
            return str(k)
    s = str(k).lower()
    # Map common names pyautogui understands
    key_map = {
        "return": "enter",
        "ret": "enter",
        "backspace": "backspace",
        "tab": "tab",
        "escape": "escape",
        "esc": "escape",
        "space": "space",
        "control": "ctrl",
        "cmd": "command",
        "meta": "command",
        "option": "alt",
        "arrowleft": "left",
        "arrowright": "right",
        "arrowup": "up",
        "arrowdown": "down",
    }
    return key_map.get(s, s)
