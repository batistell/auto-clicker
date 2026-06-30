import threading
import time
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button

# Mapping modifier names to pynput Key objects
MODIFIERS = {
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "win": Key.cmd,
    "cmd": Key.cmd
}

class InputController:
    def __init__(self, config, status_callback=None):
        self.config = config
        self.status_callback = status_callback
        
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
        # Autoclicker configuration
        ac_cfg = self.config.get("autoclicker", {})
        self.ac_interval = ac_cfg.get("interval_ms", 100) / 1000.0
        target_btn_str = ac_cfg.get("target_button", "left").lower()
        
        if target_btn_str == "right":
            self.ac_button = Button.right
        elif target_btn_str == "middle":
            self.ac_button = Button.middle
        else:
            self.ac_button = Button.left

        # Thread-safe flags
        self.ac_active = False
        self.hold_active = False
        self.running = True
        
        # Start background thread for Autoclicker
        self.ac_thread = threading.Thread(target=self._autoclick_worker, daemon=True)
        self.ac_thread.start()

    def _autoclick_worker(self):
        """Background thread executing fast clicks when active."""
        while self.running:
            if self.ac_active:
                try:
                    self.mouse.click(self.ac_button)
                except Exception as e:
                    print(f"[Controller] Error during autoclick: {e}")
                time.sleep(self.ac_interval)
            else:
                time.sleep(0.01)  # Sleep small amount to prevent high CPU utilization

    def toggle_autoclicker(self):
        """Toggles the autoclicker on/off."""
        self.ac_active = not self.ac_active
        print(f"[Controller] Autoclicker: {'ON' if self.ac_active else 'OFF'}")
        self._notify_status()

    def toggle_left_click_hold(self):
        """Toggles keeping the Left Mouse Button held down."""
        self.hold_active = not self.hold_active
        print(f"[Controller] Left Click Hold: {'ON' if self.hold_active else 'OFF'}")
        
        try:
            if self.hold_active:
                self.mouse.press(Button.left)
            else:
                self.mouse.release(Button.left)
        except Exception as e:
            print(f"[Controller] Error during mouse hold toggle: {e}")
            
        self._notify_status()

    def release_all(self):
        """Releases the hold state if active, useful for shutdown."""
        if self.hold_active:
            try:
                self.mouse.release(Button.left)
            except Exception:
                pass
            self.hold_active = False
        self.ac_active = False
        self.running = False

    def _notify_status(self):
        """Notify status overlay if callback is registered."""
        if self.status_callback:
            self.status_callback(self.ac_active, self.hold_active)

    def execute_action(self, action_str):
        """Parses and executes a remapped action."""
        action_str = action_str.strip().lower()
        
        # Standard mouse click actions
        if action_str == "left_click":
            self.mouse.click(Button.left)
        elif action_str == "right_click":
            self.mouse.click(Button.right)
        elif action_str == "middle_click":
            self.mouse.click(Button.middle)
        elif action_str == "double_left_click":
            self.mouse.click(Button.left, 2)
        elif action_str == "scroll_up":
            self.mouse.scroll(0, 1)
        elif action_str == "scroll_down":
            self.mouse.scroll(0, -1)
        elif action_str == "toggle_autoclicker":
            self.toggle_autoclicker()
        elif action_str == "toggle_hold":
            self.toggle_left_click_hold()
        else:
            # Key combinations, e.g., "ctrl+c", "alt+tab"
            self.execute_key_combo(action_str)

    def execute_key_combo(self, combo_str):
        """Simulates pressing a key combination, e.g. ctrl+c."""
        parts = combo_str.split("+")
        pressed_mods = []
        target_key = None
        
        try:
            for part in parts:
                part = part.strip()
                if part in MODIFIERS:
                    mod = MODIFIERS[part]
                    self.keyboard.press(mod)
                    pressed_mods.append(mod)
                else:
                    target_key = part

            if target_key:
                # Resolve special keys (like 'enter', 'tab', 'f13', etc.)
                special_key = getattr(Key, target_key, None)
                if special_key:
                    self.keyboard.press(special_key)
                    self.keyboard.release(special_key)
                elif len(target_key) > 1 and target_key.startswith('f'):
                    # Custom handling for F13-F24 which might not be direct Key attributes in some older pynput versions
                    # But pynput supports VK codes or standard string characters.
                    # We can try getting it from Key, or send it directly.
                    try:
                        # Let's resolve standard F1-F24 key codes
                        f_num = int(target_key[1:])
                        # In Windows, F13-F24 have standard VK codes starting from 0x7C (F13 is 0x7C, F24 is 0x87)
                        if 13 <= f_num <= 24:
                            vk_code = 0x7C + (f_num - 13)
                            # Create a KeyCode with vk
                            from pynput.keyboard import KeyCode
                            vk_key = KeyCode.from_vk(vk_code)
                            self.keyboard.press(vk_key)
                            self.keyboard.release(vk_key)
                        else:
                            # Standard F1-F12
                            key_obj = getattr(Key, target_key, None)
                            if key_obj:
                                self.keyboard.press(key_obj)
                                self.keyboard.release(key_obj)
                    except Exception:
                        pass
                else:
                    # Single character key
                    self.keyboard.press(target_key)
                    self.keyboard.release(target_key)
        except Exception as e:
            print(f"[Controller] Error sending key combination '{combo_str}': {e}")
        finally:
            # Release modifiers in reverse order
            for mod in reversed(pressed_mods):
                try:
                    self.keyboard.release(mod)
                except Exception:
                    pass
