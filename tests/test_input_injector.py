"""Tests for host input_injector: parse and dispatch events (with mocked pyautogui)."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    import pyautogui  # noqa: F401
    from host.input_injector import inject_event
    _has_input_deps = True
except ImportError:
    _has_input_deps = False
    inject_event = None


@unittest.skipIf(not _has_input_deps, "pyautogui or host.input_injector not available")
class TestInputInjector(unittest.TestCase):
    @patch("host.input_injector.pyautogui")
    def test_inject_move(self, mock_pyautogui):
        mock_pyautogui.size.return_value = (1920, 1080)
        inject_event(b'{"t":"move","x":640,"y":360}', stream_width=1280, stream_height=720)
        mock_pyautogui.moveTo.assert_called_once()
        # 640 * (1920/1280) = 960, 360 * (1080/720) = 540
        args = mock_pyautogui.moveTo.call_args[0]
        self.assertEqual(args[0], 960)
        self.assertEqual(args[1], 540)

    @patch("host.input_injector.pyautogui")
    def test_inject_click(self, mock_pyautogui):
        mock_pyautogui.size.return_value = (1920, 1080)
        inject_event(b'{"t":"click","x":0,"y":0,"b":1}', stream_width=1280, stream_height=720)
        mock_pyautogui.click.assert_called_once()
        self.assertEqual(mock_pyautogui.click.call_args[1]["button"], "left")
        inject_event(b'{"t":"click","x":100,"y":100,"b":2}')
        self.assertEqual(mock_pyautogui.click.call_args[1]["button"], "right")

    @patch("host.input_injector.pyautogui")
    def test_inject_scroll(self, mock_pyautogui):
        mock_pyautogui.size.return_value = (1920, 1080)
        inject_event(b'{"t":"scroll","d":1}')
        mock_pyautogui.scroll.assert_called_once_with(1)

    @patch("host.input_injector.pyautogui")
    def test_inject_key_down_up(self, mock_pyautogui):
        mock_pyautogui.size.return_value = (1920, 1080)
        inject_event(b'{"t":"key_down","k":"a"}')
        mock_pyautogui.keyDown.assert_called_once_with("a")
        inject_event(b'{"t":"key_up","k":"a"}')
        mock_pyautogui.keyUp.assert_called_once_with("a")

    def test_inject_invalid_json_no_raise(self):
        inject_event(b"not json")
        inject_event(b"")
