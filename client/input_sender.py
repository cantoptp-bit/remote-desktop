"""
Capture mouse and keyboard from OpenCV window and send as input events to host.
Coordinates are in stream/display space (1280x720); host scales to its screen.
"""
import cv2
from shared.protocol import MSG_INPUT, send_message, build_input_event

# Stream dimensions (must match host)
STREAM_WIDTH = 1280
STREAM_HEIGHT = 720

# OpenCV mouse callback state
_mouse_pos = [0, 0]
_sock = None


def _on_mouse(event, x, y, flags, param):
    global _mouse_pos
    _mouse_pos[0], _mouse_pos[1] = x, y
    if _sock is None:
        return
    # Clamp to display size
    x = max(0, min(x, STREAM_WIDTH - 1))
    y = max(0, min(y, STREAM_HEIGHT - 1))
    if event == cv2.EVENT_MOUSEMOVE:
        send_message(_sock, MSG_INPUT, build_input_event("move", x=x, y=y))
    elif event == cv2.EVENT_LBUTTONDOWN:
        send_message(_sock, MSG_INPUT, build_input_event("click", x=x, y=y, b=1))
    elif event == cv2.EVENT_RBUTTONDOWN:
        send_message(_sock, MSG_INPUT, build_input_event("click", x=x, y=y, b=2))
    elif event == cv2.EVENT_MBUTTONDOWN:
        send_message(_sock, MSG_INPUT, build_input_event("click", x=x, y=y, b=3))
    elif event == cv2.EVENT_MOUSEWHEEL:
        # flags: positive = scroll up, negative = scroll down (platform-dependent)
        delta = 1 if flags > 0 else -1
        send_message(_sock, MSG_INPUT, build_input_event("scroll", d=delta))


def install_mouse_callback(window_name: str, sock) -> None:
    """Register mouse callback for the OpenCV window and store socket for sending."""
    global _sock
    _sock = sock
    cv2.setMouseCallback(window_name, _on_mouse)


# Key name mapping: OpenCV key code / ord -> key string for host
_KEY_MAP = {
    8: "backspace",
    9: "tab",
    13: "enter",
    27: "escape",
    32: "space",
    63232: "up",
    63233: "down",
    63234: "left",
    63235: "right",
}


def key_to_event(sock, key_code: int) -> bool:
    """
    Handle key press from cv2.waitKey. Send key_down and key_up.
    Returns True if key was sent, False if quit (q or Escape to close).
    """
    if key_code in (-1, 255):
        return True  # no key
    if key_code == ord("q") or key_code == 27:  # q or Escape
        return False  # quit
    key_name = _KEY_MAP.get(key_code)
    if key_name is None:
        if 32 <= key_code < 127:
            key_name = chr(key_code)
        else:
            return True
    send_message(sock, MSG_INPUT, build_input_event("key_down", k=key_name))
    send_message(sock, MSG_INPUT, build_input_event("key_up", k=key_name))
    return True
