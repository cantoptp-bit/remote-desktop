"""
Shared protocol for remote desktop: framing (type + length + payload).
- Type 0: frame (payload = raw JPEG bytes)
- Type 1: input (payload = JSON: mouse/keyboard events)
"""
import json
import struct

MSG_FRAME = 0
MSG_INPUT = 1

HEADER_SIZE = 5  # 1 byte type + 4 bytes length (big-endian)


def send_message(sock, msg_type: int, payload: bytes) -> None:
    """Send one message: 1 byte type, 4 byte length (big-endian), then payload."""
    length = len(payload)
    sock.sendall(struct.pack(">BI", msg_type, length) + payload)


def recv_exact(sock, n: int) -> bytes:
    """Read exactly n bytes from socket."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed")
        buf += chunk
    return buf


def recv_message(sock):
    """
    Read one message from socket. Returns (msg_type, payload).
    """
    header = recv_exact(sock, HEADER_SIZE)
    msg_type = header[0]
    length = struct.unpack(">I", header[1:5])[0]
    if length > 0:
        payload = recv_exact(sock, length)
    else:
        payload = b""
    return msg_type, payload


def build_input_event(event_type: str, **kwargs) -> bytes:
    """Build input event JSON payload. event_type: move, click, scroll, key_down, key_up."""
    obj = {"t": event_type, **kwargs}
    return json.dumps(obj).encode("utf-8")


def parse_input_event(payload: bytes) -> dict:
    """Parse input event JSON payload."""
    return json.loads(payload.decode("utf-8"))
