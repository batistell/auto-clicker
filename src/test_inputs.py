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
from main import apply_profile

class TestAutoclickerLogic(unittest.TestCase):
    def setUp(self):
        self.mock_config = {
            "autoclicker": {
                "toggle_key": "f6",
                "interval_ms": 100,
                "target_button": "left"
            },
            "macros": {
                "lbutton_hold_toggle_key": "f7",
                "w_shift_hold_toggle_key": "f4"
            },
            "key_spammer": {
                "toggle_key": "f3",
                "key_to_spam": "f",
                "interval_ms": 100
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
        self.assertFalse(self.controller.ks_active)
        self.assertFalse(self.controller.w_shift_hold_active)
        self.assertEqual(self.controller.ac_button, Button.left)
        self.assertEqual(self.controller.ks_key, "f")

    def test_toggle_autoclicker(self):
        self.controller.toggle_autoclicker()
        self.assertTrue(self.controller.ac_active)
        self.status_cb.assert_called_with(True, False, False, False)

        self.controller.toggle_autoclicker()
        self.assertFalse(self.controller.ac_active)
        self.status_cb.assert_called_with(False, False, False, False)

    def test_toggle_key_spammer(self):
        self.controller.toggle_key_spammer()
        self.assertTrue(self.controller.ks_active)
        self.status_cb.assert_called_with(False, False, True, False)

        self.controller.toggle_key_spammer()
        self.assertFalse(self.controller.ks_active)
        self.status_cb.assert_called_with(False, False, False, False)

    def test_toggle_left_click_hold(self):
        # Mock mouse controller press and release to avoid actual OS clicks during unit test
        self.controller.mouse.press = MagicMock()
        self.controller.mouse.release = MagicMock()

        self.controller.toggle_left_click_hold()
        self.assertTrue(self.controller.hold_active)
        self.controller.mouse.press.assert_called_with(Button.left)
        self.status_cb.assert_called_with(False, True, False, False)

        self.controller.toggle_left_click_hold()
        self.assertFalse(self.controller.hold_active)
        self.controller.mouse.release.assert_called_with(Button.left)
        self.status_cb.assert_called_with(False, False, False, False)

    def test_toggle_w_shift_hold(self):
        # Mock keyboard press and release
        self.controller.keyboard.press = MagicMock()
        self.controller.keyboard.release = MagicMock()

        self.controller.toggle_w_shift_hold()
        self.assertTrue(self.controller.w_shift_hold_active)
        self.controller.keyboard.press.assert_any_call('w')
        self.controller.keyboard.press.assert_any_call(Key.shift)
        self.status_cb.assert_called_with(False, False, False, True)

        self.controller.toggle_w_shift_hold()
        self.assertFalse(self.controller.w_shift_hold_active)
        self.controller.keyboard.release.assert_any_call('w')
        self.controller.keyboard.release.assert_any_call(Key.shift)
        self.status_cb.assert_called_with(False, False, False, False)

    def test_w_shift_hold_cancel_on_w(self):
        # Turn it on
        self.controller.w_shift_hold_active = True
        self.controller.keyboard.press = MagicMock()
        self.controller.keyboard.release = MagicMock()

        # Simulate user pressing 'w'
        self.listener.on_key_press(KeyCode(char='w'))

        # Verify it got toggled off
        self.assertFalse(self.controller.w_shift_hold_active)
        self.controller.keyboard.release.assert_any_call('w')
        self.controller.keyboard.release.assert_any_call(Key.shift)
        self.status_cb.assert_called_with(False, False, False, False)

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

class TestProfileConfig(unittest.TestCase):
    def test_apply_profile_palworld(self):
        config = {
            "remappings": {
                "mouse": {
                    "x1": "f",
                    "x2": "ctrl+c"
                }
            }
        }
        res = apply_profile(config, "1")
        self.assertIn("x1", res["remappings"]["mouse"])
        self.assertIn("x2", res["remappings"]["mouse"])
        self.assertEqual(res["remappings"]["mouse"]["x1"], "f")

    def test_apply_profile_normal(self):
        config = {
            "autoclicker": {
                "toggle_key": "x1"
            },
            "macros": {
                "lbutton_hold_toggle_key": "x2",
                "w_shift_hold_toggle_key": "f4"
            },
            "remappings": {
                "mouse": {
                    "x1": "f",
                    "x2": "ctrl+c",
                    "middle": "space"
                }
            }
        }
        res = apply_profile(config, "2")
        # Mouse remappings for x1/x2 should be removed
        self.assertNotIn("x1", res["remappings"]["mouse"])
        self.assertNotIn("x2", res["remappings"]["mouse"])
        self.assertIn("middle", res["remappings"]["mouse"])
        
        # Toggle keys set to x1/x2 should be cleared
        self.assertEqual(res["autoclicker"]["toggle_key"], "")
        self.assertEqual(res["macros"]["lbutton_hold_toggle_key"], "")
        self.assertEqual(res["macros"]["w_shift_hold_toggle_key"], "f4")

class TestKeyComboTriggers(unittest.TestCase):
    def setUp(self):
        self.mock_config = {
            "autoclicker": {
                "toggle_key": "ctrl+alt+a"
            },
            "macros": {
                "lbutton_hold_toggle_key": "alt+w",
                "w_shift_hold_toggle_key": "shift+f"
            },
            "key_spammer": {
                "toggle_key": "f3"
            }
        }
        self.controller = MagicMock()
        self.listener = InputListener(self.mock_config, self.controller)

    def test_is_modifier_pressed(self):
        # By default, no keys are in self.pressed_keys
        self.assertFalse(self.listener.is_modifier_pressed("alt"))
        self.assertFalse(self.listener.is_modifier_pressed("ctrl"))
        
        # Simulating alt_l pressed
        self.listener.pressed_keys.add("alt_l")
        self.assertTrue(self.listener.is_modifier_pressed("alt"))
        self.assertFalse(self.listener.is_modifier_pressed("ctrl"))
        
        # Simulating ctrl_r pressed
        self.listener.pressed_keys.add("ctrl_r")
        self.assertTrue(self.listener.is_modifier_pressed("ctrl"))

    def test_is_trigger_active_single_key(self):
        self.assertTrue(self.listener.is_trigger_active("f3", "f3"))
        self.assertFalse(self.listener.is_trigger_active("f4", "f3"))

    def test_is_trigger_active_combo(self):
        # Triggers for "alt+w"
        # 1. Base key not matched
        self.assertFalse(self.listener.is_trigger_active("a", "alt+w"))
        
        # 2. Base key matched but modifier not pressed
        self.assertFalse(self.listener.is_trigger_active("w", "alt+w"))
        
        # 3. Base key matched and modifier pressed
        self.listener.pressed_keys.add("alt_l")
        self.assertTrue(self.listener.is_trigger_active("w", "alt+w"))
        
        # 4. Multi-modifier "ctrl+alt+a"
        self.assertFalse(self.listener.is_trigger_active("a", "ctrl+alt+a"))
        self.listener.pressed_keys.add("ctrl_l")
        self.assertTrue(self.listener.is_trigger_active("a", "ctrl+alt+a"))

class TestPendingRelease(unittest.TestCase):
    def test_toggle_w_shift_hold_immediate_for_f4(self):
        config = {
            "macros": {
                "w_shift_hold_toggle_key": "f4"
            }
        }
        controller = InputController(config, status_callback=MagicMock())
        controller.keyboard.press = MagicMock()
        controller.keyboard.release = MagicMock()
        
        # Activating
        controller.toggle_w_shift_hold()
        self.assertTrue(controller.w_shift_hold_active)
        self.assertFalse(controller.w_press_pending_release)
        controller.keyboard.press.assert_any_call('w')
        controller.keyboard.press.assert_any_call(Key.shift)
        
        controller.release_all()

    def test_toggle_w_shift_hold_pending_for_alt_w(self):
        config = {
            "macros": {
                "w_shift_hold_toggle_key": "alt+w"
            }
        }
        controller = InputController(config, status_callback=MagicMock())
        controller.keyboard.press = MagicMock()
        controller.keyboard.release = MagicMock()
        
        # Activating - should go pending
        controller.toggle_w_shift_hold()
        self.assertTrue(controller.w_shift_hold_active)
        self.assertTrue(controller.w_press_pending_release)
        # Should not call press yet
        controller.keyboard.press.assert_not_called()
        
        # Call release hook
        controller.start_w_shift_hold_after_release()
        self.assertFalse(controller.w_press_pending_release)
        controller.keyboard.press.assert_any_call('w')
        controller.keyboard.press.assert_any_call(Key.shift)
        
        controller.release_all()

class TestWShiftHoldTriggerBehavior(unittest.TestCase):
    def setUp(self):
        self.config = {
            "macros": {
                "w_shift_hold_toggle_key": "alt+w"
            }
        }
        self.controller = InputController(self.config, status_callback=MagicMock())
        self.listener = InputListener(self.config, self.controller)
        self.controller.keyboard.press = MagicMock()
        self.controller.keyboard.release = MagicMock()

    def tearDown(self):
        self.controller.release_all()

    def test_alt_w_enables_but_does_not_disable(self):
        # 1. Start with inactive
        self.assertFalse(self.controller.w_shift_hold_active)

        # Simulate user pressing 'alt+w' to enable
        self.listener.pressed_keys.add("alt_l")
        self.listener.on_key_press(KeyCode(char='w'))
        
        # Should now be active
        self.assertTrue(self.controller.w_shift_hold_active)
        self.assertTrue(self.controller.w_press_pending_release)
        
        # Start hold synchronously
        self.controller.start_w_shift_hold_after_release()
        
        # Simulate user releasing 'w'
        self.listener.on_key_release(KeyCode(char='w'))
        self.listener.pressed_keys.discard("alt_l")
        
        # Reset expected simulated presses since we mock keyboard calls
        self.controller.expected_simulated_w_presses = 0
        
        # Reset mocks
        self.controller.keyboard.press.reset_mock()
        self.controller.keyboard.release.reset_mock()
        
        # Simulate pressing 'alt+w' again while active
        self.listener.pressed_keys.add("alt_l")
        self.listener.on_key_press(KeyCode(char='w'))
        
        # Should STILL be active (alt+w does not disable it)
        self.assertTrue(self.controller.w_shift_hold_active)
        self.controller.keyboard.release.assert_not_called()

        # Simulate user releasing 'w'
        self.listener.on_key_release(KeyCode(char='w'))
        # Release 'alt' modifier
        self.listener.pressed_keys.discard("alt_l")

        # Reset expected simulated presses
        self.controller.expected_simulated_w_presses = 0

        # Simulate pressing 'w' (without alt)
        self.listener.on_key_press(KeyCode(char='w'))

        # Should now be disabled
        self.assertFalse(self.controller.w_shift_hold_active)

if __name__ == "__main__":
    unittest.main()

