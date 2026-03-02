"""
Client (viewer): runs on the Mac (or the machine that controls the host).
Connect to host IP:port, display stream and send mouse/keyboard.
"""
import socket
import sys
import threading
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

import cv2
import numpy as np

from client.display import recv_frame, DISPLAY_WIDTH, DISPLAY_HEIGHT
from client.input_sender import install_mouse_callback, key_to_event

DEFAULT_PORT = 8765
WINDOW_NAME = "Remote Desktop"


def _is_mostly_black(frame, threshold=15):
    """True if frame mean brightness is very low (host capture may have failed)."""
    return float(np.mean(frame)) < threshold


def _make_placeholder(width, height, text):
    """Gray image with text so the window is not solid black while waiting."""
    img = np.full((height, width, 3), 48, dtype=np.uint8)  # dark gray
    cv2.putText(
        img, text, (width // 4, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 200), 2, cv2.LINE_AA
    )
    return img


def frame_receiver_loop(sock, latest_frame_ref, frame_ready):
    """Background thread: receive frames and store latest."""
    try:
        while True:
            frame = recv_frame(sock)
            if frame is None:
                break
            with frame_ready:
                latest_frame_ref[0] = frame
                frame_ready.notify_all()
    except (ConnectionError, BrokenPipeError, OSError):
        pass
    with frame_ready:
        latest_frame_ref[0] = None
        frame_ready.notify_all()


def _is_localhost(host):
    return host in ("127.0.0.1", "localhost", "::1") or host.startswith("127.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m client.main <host_ip> [port]")
        print("Example: python -m client.main 192.168.1.100 8765")
        print("  Use the other computer's IP (run the host on that PC). Wired or Wi-Fi both work.")
        sys.exit(1)
    host = sys.argv[1].strip()
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    allow_local = "--allow-localhost" in sys.argv
    if _is_localhost(host) and not allow_local:
        print("You're connecting to this computer (localhost).")
        print("To control another PC: run the HOST on that PC, then run this CLIENT with that PC's IP.")
        print("Example: on the other PC run: python -m host.main")
        print("         then here run:       python -m client.main 192.168.1.XXX")
        print("To connect to this machine anyway (e.g. for testing), run with: --allow-localhost")
        sys.exit(1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except OSError as e:
        print(f"Cannot connect to {host}:{port} - {e}")
        sys.exit(1)
    print(f"Connected to {host}:{port}. Press 'q' or Escape in the window to quit.")
    window_title = f"Remote Desktop — {host}"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_title, DISPLAY_WIDTH, DISPLAY_HEIGHT + 28)  # extra for status bar
    install_mouse_callback(window_title, sock)
    install_mouse_callback(WINDOW_NAME, sock)
    latest_frame_ref = [None]
    frame_ready = threading.Condition()
    recv_thread = threading.Thread(
        target=frame_receiver_loop, args=(sock, latest_frame_ref, frame_ready), daemon=True
    )
    recv_thread.start()
    STATUS_BAR_H = 28
    placeholder = _make_placeholder(DISPLAY_WIDTH, DISPLAY_HEIGHT, "Connecting...")

    def add_ui_frame(img, status_text):
        """Add status bar and border for a cleaner UI."""
        h, w = img.shape[:2]
        bar = np.full((STATUS_BAR_H, w, 3), (40, 40, 40), dtype=np.uint8)
        cv2.putText(bar, status_text, (10, STATUS_BAR_H - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
        out = np.vstack([img, bar])
        cv2.rectangle(out, (0, 0), (w - 1, h - 1), (70, 70, 70), 1)
        return out

    try:
        while True:
            with frame_ready:
                frame_ready.wait(timeout=0.05)
                frame = latest_frame_ref[0]
            if frame is None and latest_frame_ref[0] is None and not recv_thread.is_alive():
                print("Connection lost.")
                break
            status = f"Connected to {host}  |  Wired or Wi-Fi OK  |  Q or Esc to quit"
            if frame is not None:
                if _is_mostly_black(frame):
                    overlay = placeholder.copy()
                    cv2.putText(
                        overlay, "No signal — check host screen permissions",
                        (50, DISPLAY_HEIGHT // 2 + 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (120, 120, 120), 1, cv2.LINE_AA
                    )
                    show = add_ui_frame(overlay, status)
                else:
                    show = add_ui_frame(frame, status)
            else:
                show = add_ui_frame(placeholder, "Connecting...")
            cv2.imshow(window_title, show)
            key = cv2.waitKey(1) & 0xFF
            if not key_to_event(sock, key):
                break
    finally:
        cv2.destroyAllWindows()
        sock.close()


if __name__ == "__main__":
    main()
