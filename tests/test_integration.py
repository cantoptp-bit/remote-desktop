"""Integration tests: host accepts client, protocol exchange over loopback."""
import socket
import sys
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.protocol import MSG_FRAME, MSG_INPUT, send_message, recv_message


def run_host_server(port, ready):
    """Start a minimal 'host' that sends one frame and reads one input."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", port))
    sock.listen(1)
    ready.set()
    conn, _ = sock.accept()
    try:
        send_message(conn, MSG_FRAME, b"\xff\xd8\xff\xff fake jpeg tail")
        msg_type, payload = recv_message(conn)
        assert msg_type == MSG_INPUT
        assert b"move" in payload or b"click" in payload or b"key" in payload
    finally:
        conn.close()
        sock.close()


class TestIntegration(unittest.TestCase):
    def test_client_can_connect_and_exchange(self):
        """Client connects to a minimal server, receives one frame, sends one input."""
        ready = threading.Event()
        port = 0
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        port = server_sock.getsockname()[1]
        server_sock.listen(1)
        ready.set()

        def accept_and_respond():
            conn, _ = server_sock.accept()
            try:
                send_message(conn, MSG_FRAME, b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9")
                msg_type, payload = recv_message(conn)
                assert msg_type == MSG_INPUT, (msg_type, payload)
            finally:
                conn.close()
            server_sock.close()

        t = threading.Thread(target=accept_and_respond, daemon=True)
        t.start()
        ready.wait(timeout=1)
        time.sleep(0.05)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", port))
        msg_type, payload = recv_message(client)
        self.assertEqual(msg_type, MSG_FRAME)
        self.assertGreater(len(payload), 0)
        send_message(client, MSG_INPUT, b'{"t":"move","x":100,"y":200}')
        client.close()
        t.join(timeout=2)
