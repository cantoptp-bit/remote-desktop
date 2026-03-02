"""
Screen capture and JPEG encode. Uses mss for capture, OpenCV for resize/encode.
"""
import cv2
import numpy as np
import mss

from shared.stream_config import STREAM_WIDTH, STREAM_HEIGHT

# Quality: 82 for sharper image (was 70)
JPEG_QUALITY = 82


def _frame_mean_brightness(frame):
    """Mean pixel value (0–255). Very low = likely black/capture failed."""
    return float(np.mean(frame))


def _frame_hash(frame, size=64):
    """Fast hash of downscaled frame for change detection."""
    small = cv2.resize(frame, (size, size), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return hash(gray.tobytes())


def capture_frame(quality: int = JPEG_QUALITY, max_width: int = STREAM_WIDTH, max_height: int = STREAM_HEIGHT):
    """
    Capture the primary screen, scale to stream size, encode as JPEG.
    Returns (jpeg_bytes, frame_bgr). frame_bgr is for change detection; can be None to skip.
    """
    with mss.mss() as sct:
        order = [1, 0] if len(sct.monitors) > 1 else [0]
        frame = None
        for idx in order:
            if idx >= len(sct.monitors):
                continue
            monitor = sct.monitors[idx]
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            if _frame_mean_brightness(frame) >= 10:
                break
        if frame is None:
            frame = np.zeros((max_height, max_width, 3), dtype=np.uint8)

    frame = cv2.resize(frame, (max_width, max_height), interpolation=cv2.INTER_LINEAR)
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, jpeg_bytes = cv2.imencode(".jpg", frame, encode_params)
    return jpeg_bytes.tobytes(), frame
