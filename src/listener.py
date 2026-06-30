from pynput import keyboard, mouse
import threading

class InputListener:
    def __init__(self, config, controller):
        self.config = config
        self.controller = controller
        
        # Load trigger configurations
        ac_cfg = self.config.get("autoclicker", {})
        self.ac_toggle_key = ac_cfg.get("toggle_key", "").lower()
        
        macro_cfg = self.config.get("macros", {})
        self.hold_toggle_key = macro_cfg.get("lbutton_hold_toggle_key", "").lower()
        self.w_shift_hold_toggle_key = macro_cfg.get("w_shift_hold_toggle_key", "").lower()
        
        ks_cfg = self.config.get("key_spammer", {})
        self.ks_toggle_key = ks_cfg.get("toggle_key", "").lower()

        remappings = self.config.get("remappings", {})
        self.key_remappings = remappings.get("keys", {})
        self.mouse_remappings = remappings.get("mouse", {})
        
        # Track currently physically pressed keys to ignore repeat/held keyboard events
        self.pressed_keys = set()

        # Initialize listeners to None
        self.keyboard_listener = None
        self.mouse_listener = None

    def key_to_str(self, key):
        """Converts a pynput key event object to a string representation."""
        if hasattr(key, 'name') and key.name:
            return key.name.lower()
        elif hasattr(key, 'char') and key.char:
            return key.char.lower()
        elif hasattr(key, 'vk') and key.vk:
            # Map Windows Virtual Key (VK) codes for F13-F24 (VK 124 to 135)
            if 124 <= key.vk <= 135:
                return f"f{13 + (key.vk - 124)}"
            return f"vk_{key.vk}"
        return str(key).lower().replace("'", "")

    def mouse_btn_to_str(self, button):
        """Converts a pynput mouse button object to a string representation."""
        btn_str = str(button).split('.')[-1].lower()
        # standard mapping for back/forward buttons:
        # x1 -> mouse4, x2 -> mouse5
        return btn_str

    def on_key_press(self, key):
        # Ignore events simulated by our own controller
        if getattr(self.controller, 'is_simulating', False):
            return

        key_str = self.key_to_str(key)
        
        # Debounce/Filter out repeating keystroke events sent by the OS
        if key_str in self.pressed_keys:
            return
        self.pressed_keys.add(key_str)

        # Check autoclicker toggle key
        if key_str == self.ac_toggle_key:
            self.controller.toggle_autoclicker()
            return
            
        # Check hold macro toggle key
        if key_str == self.hold_toggle_key:
            self.controller.toggle_left_click_hold()
            return

        # Check key spammer toggle key
        if key_str == self.ks_toggle_key:
            self.controller.toggle_key_spammer()
            return

        # Check key remappings
        if key_str in self.key_remappings:
            action = self.key_remappings[key_str]
            # Run action in a separate thread so we do not block pynput's hook thread
            threading.Thread(target=self.controller.execute_action, args=(action,), daemon=True).start()

    def on_key_release(self, key):
        # Ignore events simulated by our own controller
        if getattr(self.controller, 'is_simulating', False):
            return

        key_str = self.key_to_str(key)
        if key_str in self.pressed_keys:
            self.pressed_keys.remove(key_str)

    def on_mouse_click(self, x, y, button, pressed):
        # Ignore events simulated by our own controller
        if getattr(self.controller, 'is_simulating', False):
            return

        # We only trigger action on mouse button down (pressed == True)
        if not pressed:
            return

        btn_str = self.mouse_btn_to_str(button)

        # Debounce to prevent double-triggering (common with side buttons / Logitech drivers)
        import time
        now = time.time()
        if not hasattr(self, '_last_mouse_time'):
            self._last_mouse_time = {}
        last_time = self._last_mouse_time.get(btn_str, 0)
        if now - last_time < 0.15:  # 150ms debounce
            return
        self._last_mouse_time[btn_str] = now
        
        # Check if mouse button triggers autoclicker or macro hold
        if btn_str == self.ac_toggle_key:
            self.controller.toggle_autoclicker()
            return
            
        if btn_str == self.hold_toggle_key:
            self.controller.toggle_left_click_hold()
            return

        if btn_str == self.ks_toggle_key:
            self.controller.toggle_key_spammer()
            return

        # Check mouse button remappings
        if btn_str in self.mouse_remappings:
            action = self.mouse_remappings[btn_str]
            # Run action in a separate thread to avoid blocking mouse hook
            threading.Thread(target=self.controller.execute_action, args=(action,), daemon=True).start()

    def start(self):
        """Starts listeners on background threads."""
        print("[Listener] Starting keyboard and mouse listeners...")
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        """Stops listeners."""
        print("[Listener] Stopping listeners...")
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
