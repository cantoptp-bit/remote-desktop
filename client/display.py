"""
Receive frame messages (JPEG), decode and display in OpenCV window.
Returns the latest frame for the main loop; handles window and coordinate scaling for input.
"""
import cv2
import numpy as np

from shared.protocol import MSG_FRAME, recv_message

# Display window size (stream is 1280x720; we show at same size or scale)
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720


def decode_frame(payload: bytes):
    """Decode JPEG payload to BGR array for OpenCV display."""
    nparr = np.frombuffer(payload, dtype=np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def recv_frame(sock):
    """
    Read one frame message from socket. Returns frame (BGR array) or None on connection close.
    Skips non-frame messages.
    """
    while True:
        msg_type, payload = recv_message(sock)
        if msg_type == MSG_FRAME and payload:
            frame = decode_frame(payload)
            if frame is not None:
                return frame
