"""
Screen capture and JPEG encode. Uses mss for capture, OpenCV for resize/encode.
"""
import cv2
import numpy as np
import mss


# Default scale for lower bandwidth (plan: 1280x720)
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
JPEG_QUALITY = 70  # 0-100, lower = smaller size, more compression


def _frame_mean_brightness(frame):
    """Mean pixel value (0–255). Very low = likely black/capture failed."""
    return float(np.mean(frame))


def capture_frame(quality: int = JPEG_QUALITY, max_width: int = DEFAULT_WIDTH, max_height: int = DEFAULT_HEIGHT) -> bytes:
    """
    Capture the primary screen, optionally scale down, encode as JPEG.
    Returns JPEG bytes. Tries primary monitor first, then fallback if capture is black.
    """
    with mss.mss() as sct:
        # Try primary physical monitor (1) first, then 0 (all-in-one)
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
            frame = np.zeros((max_height, max_width, 3), dtype=np.uint8)  # fallback

    height, width = frame.shape[:2]
    frame = cv2.resize(frame, (max_width, max_height), interpolation=cv2.INTER_AREA)

    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, jpeg_bytes = cv2.imencode(".jpg", frame, encode_params)
    return jpeg_bytes.tobytes()
