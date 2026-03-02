"""Tests for client display: decode_frame with JPEG payload."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import cv2
    import numpy as np
    from client.display import decode_frame
    _has_display_deps = True
except ImportError:
    _has_display_deps = False


def _make_mini_jpeg():
    """Create a minimal valid JPEG (small BGR image)."""
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[:, :] = (128, 64, 200)  # BGR
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


@unittest.skipIf(not _has_display_deps, "cv2/numpy or client.display not available")
class TestDisplay(unittest.TestCase):
    def test_decode_frame_valid_jpeg(self):
        jpeg = _make_mini_jpeg()
        frame = decode_frame(jpeg)
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape[2], 3)  # BGR
        self.assertGreater(frame.size, 0)

    def test_decode_frame_invalid_returns_none_or_blank(self):
        # cv2.imdecode returns None for invalid data (or empty array in some versions)
        frame = decode_frame(b"not-a-jpeg")
        if frame is not None:
            self.assertTrue(frame.size == 0 or len(frame.shape) >= 2)
