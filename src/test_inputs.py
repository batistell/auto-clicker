import sys
import unittest
from unittest.mock import MagicMock
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

# Add src folder to path
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller import InputController
from listener import InputListener

class TestAutoclickerLogic(unittest.TestCase):
    def setUp(self):
        self.mock_config = {
            "autoclicker": {
                "toggle_key": "f6",
                "interval_ms": 100,
                "target_button": "left"
            },
            "macros": {
                "lbutton_hold_toggle_key": "f7"
            },
            "remappings": {
                "keys": {
                    "f13": "left_click",
                    "f14": "scroll_up"
                },
                "mouse": {
                    "x2": "ctrl+c"
                }
            },
            "overlay": {
                "enabled": False
            }
        }
        # Mock status callback
        self.status_cb = MagicMock()
        # Initialize controller with status callback and test config
        self.controller = InputController(self.mock_config, status_callback=self.status_cb)
        self.listener = InputListener(self.mock_config, self.controller)

    def tearDown(self):
        # Stop background thread
        self.controller.release_all()

    def test_controller_initial_states(self):
        self.assertFalse(self.controller.ac_active)
        self.assertFalse(self.controller.hold_active)
        self.assertEqual(self.controller.ac_button, Button.left)

    def test_toggle_autoclicker(self):
        self.controller.toggle_autoclicker()
        self.assertTrue(self.controller.ac_active)
        self.status_cb.assert_called_with(True, False)

        self.controller.toggle_autoclicker()
        self.assertFalse(self.controller.ac_active)
        self.status_cb.assert_called_with(False, False)

    def test_toggle_left_click_hold(self):
        # Mock mouse controller press and release to avoid actual OS clicks during unit test
        self.controller.mouse.press = MagicMock()
        self.controller.mouse.release = MagicMock()

        self.controller.toggle_left_click_hold()
        self.assertTrue(self.controller.hold_active)
        self.controller.mouse.press.assert_called_with(Button.left)
        self.status_cb.assert_called_with(False, True)

        self.controller.toggle_left_click_hold()
        self.assertFalse(self.controller.hold_active)
        self.controller.mouse.release.assert_called_with(Button.left)
        self.status_cb.assert_called_with(False, False)

    def test_key_to_str_resolution(self):
        self.assertEqual(self.listener.key_to_str(Key.f6), "f6")
        self.assertEqual(self.listener.key_to_str(KeyCode(char='a')), "a")
        
        # Test virtual key code resolving for F13 (VK code 124)
        vk_key = KeyCode.from_vk(124)
        self.assertEqual(self.listener.key_to_str(vk_key), "f13")
        
        # Test non-F13-24 virtual key code
        vk_other = KeyCode.from_vk(99)
        self.assertEqual(self.listener.key_to_str(vk_other), "vk_99")

    def test_mouse_btn_to_str_resolution(self):
        self.assertEqual(self.listener.mouse_btn_to_str(Button.left), "left")
        self.assertEqual(self.listener.mouse_btn_to_str(Button.right), "right")
        self.assertEqual(self.listener.mouse_btn_to_str(Button.middle), "middle")
        self.assertEqual(self.listener.mouse_btn_to_str(Button.x1), "x1")
        self.assertEqual(self.listener.mouse_btn_to_str(Button.x2), "x2")

if __name__ == "__main__":
    unittest.main()
