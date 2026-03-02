"""Tests for shared protocol: framing, send_message/recv_message, input events."""
import socket
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.protocol import (
    MSG_FRAME,
    MSG_INPUT,
    HEADER_SIZE,
    send_message,
    recv_message,
    recv_exact,
    build_input_event,
    parse_input_event,
)


class TestProtocolFraming(unittest.TestCase):
    def test_send_recv_roundtrip(self):
        """Send and receive messages over loopback TCP."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(("127.0.0.1", port))
        server_sock, _ = server.accept()
        try:
            # Frame
            send_message(client_sock, MSG_FRAME, b"fake-jpeg-data")
            msg_type, payload = recv_message(server_sock)
            self.assertEqual(msg_type, MSG_FRAME)
            self.assertEqual(payload, b"fake-jpeg-data")
            # Input
            send_message(server_sock, MSG_INPUT, b'{"t":"move","x":100,"y":200}')
            msg_type, payload = recv_message(client_sock)
            self.assertEqual(msg_type, MSG_INPUT)
            self.assertEqual(payload, b'{"t":"move","x":100,"y":200}')
            # Empty payload
            send_message(client_sock, MSG_FRAME, b"")
            msg_type, payload = recv_message(server_sock)
            self.assertEqual(msg_type, MSG_FRAME)
            self.assertEqual(payload, b"")
        finally:
            client_sock.close()
            server_sock.close()
            server.close()

    def test_build_parse_input_event(self):
        """build_input_event and parse_input_event roundtrip."""
        payload = build_input_event("move", x=50, y=75)
        self.assertIsInstance(payload, bytes)
        data = parse_input_event(payload)
        self.assertEqual(data["t"], "move")
        self.assertEqual(data["x"], 50)
        self.assertEqual(data["y"], 75)

    def test_header_size(self):
        self.assertEqual(HEADER_SIZE, 5)
