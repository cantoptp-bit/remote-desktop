"""
Host (server): runs on the PC being controlled.
Listens on port 8765, accepts one client. Sends screen frames; receives and injects input events.
"""
import socket
import sys
import threading
import time
from pathlib import Path

# Project root for imports
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
from shared.protocol import MSG_FRAME, MSG_INPUT, send_message, recv_message

from host.capture import capture_frame
from host.input_injector import inject_event, STREAM_WIDTH, STREAM_HEIGHT

DEFAULT_PORT = 8765
FPS = 12  # Target frames per second


def input_receiver_loop(conn: socket.socket) -> None:
    """Read input messages and inject on host."""
    try:
        while True:
            msg_type, payload = recv_message(conn)
            if msg_type == MSG_INPUT and payload:
                inject_event(payload, STREAM_WIDTH, STREAM_HEIGHT)
    except (ConnectionError, BrokenPipeError, OSError):
        pass


def frame_sender_loop(conn: socket.socket) -> None:
    """Capture screen and send JPEG frames."""
    interval = 1.0 / FPS
    try:
        while True:
            t0 = time.monotonic()
            jpeg = capture_frame()
            send_message(conn, MSG_FRAME, jpeg)
            elapsed = time.monotonic() - t0
            time.sleep(max(0, interval - elapsed))
    except (ConnectionError, BrokenPipeError, OSError):
        pass


def main() -> None:
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(1)
    print(f"Host listening on 0.0.0.0:{port}. Start the client on your Mac and connect to this PC's IP.")
    conn, addr = server.accept()
    print(f"Client connected from {addr}")
    # Two threads: one sends frames, one receives input
    t1 = threading.Thread(target=frame_sender_loop, args=(conn,), daemon=True)
    t2 = threading.Thread(target=input_receiver_loop, args=(conn,), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    conn.close()
    server.close()


if __name__ == "__main__":
    main()
