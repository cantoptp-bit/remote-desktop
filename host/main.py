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

from host.capture import capture_frame, _frame_hash
from host.input_injector import inject_event, STREAM_WIDTH, STREAM_HEIGHT

DEFAULT_PORT = 8765
FPS = 60  # Target frames per second


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
    """Capture screen and send JPEG frames. Skip sending when frame unchanged (saves bandwidth)."""
    interval = 1.0 / FPS
    last_hash = None
    try:
        while True:
            t0 = time.monotonic()
            jpeg, frame = capture_frame()
            frame_hash = _frame_hash(frame) if frame is not None else None
            if frame_hash != last_hash or last_hash is None:
                send_message(conn, MSG_FRAME, jpeg)
                last_hash = frame_hash
            elapsed = time.monotonic() - t0
            time.sleep(max(0, interval - elapsed))
    except (ConnectionError, BrokenPipeError, OSError):
        pass


def _get_local_ips() -> list[str]:
    """
    Best‑effort list of local IPv4 addresses you can use from another computer.
    Filters out 127.x.x.x.
    """
    ips: set[str] = set()
    # Primary guess: outbound interface (works on most home networks)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        if not ip.startswith("127."):
            ips.add(ip)
        s.close()
    except OSError:
        pass

    # Fallback: all addresses bound to hostname
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                ips.add(ip)
    except OSError:
        pass

    return sorted(ips)


def main() -> None:
    args = sys.argv[1:]

    # Utility mode: just show local IPs and exit
    if args and args[0] in {"ip", "show-ip", "--ip", "--show-ip"}:
        ips = _get_local_ips()
        if ips:
            print("Local IP addresses on this computer (use one of these from your other machine):")
            for ip in ips:
                print(f"  {ip}")
            print("Example on the other computer: python -m client.main <ip_above>")
        else:
            print("Could not automatically determine a local IP address.")
            print("You can still run: python -m client.main <this_pc_ip> once you know it.")
        return

    port = DEFAULT_PORT
    if args:
        try:
            port = int(args[0])
        except ValueError:
            pass

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(1)

    ips = _get_local_ips()
    if ips:
        print(f"Host listening on 0.0.0.0:{port}.")
        print("From your other computer, connect to one of:")
        for ip in ips:
            print(f"  {ip}:{port}")
        print("Example on other computer: python -m client.main", ips[0])
    else:
        print(f"Host listening on 0.0.0.0:{port}. Start the client on your other computer and connect to this PC's IP.")

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
