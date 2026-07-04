import tkinter as tk
from ctypes import windll
import sys

# Win32 Window Styles Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

class StatusOverlay:
    def __init__(self, config):
        self.config = config.get("overlay", {})
        self.enabled = self.config.get("enabled", True)
        if not self.enabled:
            return

        self.root = tk.Tk()
        self.root.title("Remapper HUD")
        
        # Configure window window manager properties
        self.root.overrideredirect(True)  # Borderless
        self.root.attributes("-topmost", True)  # Always on top
        
        # Style configurations
        bg_color = self.config.get("bg_color", "#1e1e2e")
        self.text_color = self.config.get("text_color", "#cdd6f4")
        self.active_color = self.config.get("active_color", "#a6e3a1")
        font_family = self.config.get("font_family", "Segoe UI")
        font_size = self.config.get("font_size", 10)
        opacity = self.config.get("opacity", 0.85)

        self.root.configure(bg=bg_color)
        self.root.attributes("-alpha", opacity)

        # Labels for Autoclicker and Left Click Hold status
        self.font = (font_family, font_size, "bold")
        
        # Main layout frame
        self.frame = tk.Frame(self.root, bg=bg_color, padx=10, pady=5)
        self.frame.pack(expand=True, fill="both")

        self.ac_label = tk.Label(
            self.frame, 
            text="AC: OFF", 
            font=self.font, 
            fg=self.text_color, 
            bg=bg_color
        )
        self.ac_label.pack(side="left", padx=10)

        # Separator
        self.sep_label = tk.Label(
            self.frame, 
            text="|", 
            font=self.font, 
            fg="#585b70", 
            bg=bg_color
        )
        self.sep_label.pack(side="left")

        self.hold_label = tk.Label(
            self.frame, 
            text="HOLD: OFF", 
            font=self.font, 
            fg=self.text_color, 
            bg=bg_color
        )
        self.hold_label.pack(side="left", padx=10)

        # Separator 2
        self.sep_label2 = tk.Label(
            self.frame, 
            text="|", 
            font=self.font, 
            fg="#585b70", 
            bg=bg_color
        )
        self.sep_label2.pack(side="left")

        # Key Spammer label
        ks_cfg = config.get("key_spammer", {})
        self.ks_key_display = ks_cfg.get("key_to_spam", "f").upper()
        self.ks_label = tk.Label(
            self.frame, 
            text=f"KEY({self.ks_key_display}): OFF", 
            font=self.font, 
            fg=self.text_color, 
            bg=bg_color
        )
        self.ks_label.pack(side="left", padx=10)

        # Separator 3
        self.sep_label3 = tk.Label(
            self.frame, 
            text="|", 
            font=self.font, 
            fg="#585b70", 
            bg=bg_color
        )
        self.sep_label3.pack(side="left")

        # Auto Run label
        self.run_label = tk.Label(
            self.frame, 
            text="RUN: OFF", 
            font=self.font, 
            fg=self.text_color, 
            bg=bg_color
        )
        self.run_label.pack(side="left", padx=10)

        # Calculate position and set geometry
        self.width = 460
        self.height = 36
        self.set_window_position()

        # Apply Win32 click-through styles after the window is fully initialized
        self.root.after(100, self.make_click_through)

    def set_window_position(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        pos = self.config.get("position", "top_center")
        offset_x = self.config.get("offset_x", 0)
        offset_y = self.config.get("offset_y", 20)

        x, y = 0, 0

        if "," in pos:
            try:
                parts = pos.split(",")
                x = int(parts[0].strip())
                y = int(parts[1].strip())
            except ValueError:
                x = (screen_width - self.width) // 2
                y = offset_y
        else:
            pos = pos.lower()
            if pos == "top_left":
                x = offset_x
                y = offset_y
            elif pos == "top_center":
                x = (screen_width - self.width) // 2 + offset_x
                y = offset_y
            elif pos == "top_right":
                x = screen_width - self.width - offset_x
                y = offset_y
            elif pos == "bottom_left":
                x = offset_x
                y = screen_height - self.height - offset_y
            elif pos == "bottom_center":
                x = (screen_width - self.width) // 2 + offset_x
                y = screen_height - self.height - offset_y
            elif pos == "bottom_right":
                x = screen_width - self.width - offset_x
                y = screen_height - self.height - offset_y
            else:  # Fallback
                x = (screen_width - self.width) // 2
                y = offset_y

        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def make_click_through(self):
        if sys.platform == "win32":
            try:
                hwnd = self.root.winfo_id()
                parent = windll.user32.GetParent(hwnd)
                target_hwnd = parent if parent else hwnd
                
                # Get current extended window styles
                style = windll.user32.GetWindowLongW(target_hwnd, GWL_EXSTYLE)
                # Apply Layered and Transparent flags to enable click-through
                windll.user32.SetWindowLongW(target_hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            except Exception as e:
                print(f"[Overlay] Failed to apply click-through window styles: {e}", file=sys.stderr)

    def update_status(self, ac_active, hold_active, ks_active=False, run_active=False):
        """Thread-safe status update using Tkinter's root.after."""
        if not self.enabled:
            return
        
        self.root.after(0, self._perform_update, ac_active, hold_active, ks_active, run_active)

    def _perform_update(self, ac_active, hold_active, ks_active, run_active):
        if ac_active:
            self.ac_label.config(text="AC: ON", fg=self.active_color)
        else:
            self.ac_label.config(text="AC: OFF", fg=self.text_color)

        if hold_active:
            self.hold_label.config(text="HOLD: ON", fg=self.active_color)
        else:
            self.hold_label.config(text="HOLD: OFF", fg=self.text_color)

        if ks_active:
            self.ks_label.config(text=f"KEY({self.ks_key_display}): ON", fg=self.active_color)
        else:
            self.ks_label.config(text=f"KEY({self.ks_key_display}): OFF", fg=self.text_color)

        if run_active:
            self.run_label.config(text="RUN: ON", fg=self.active_color)
        else:
            self.run_label.config(text="RUN: OFF", fg=self.text_color)

    def start(self):
        if self.enabled:
            self.root.mainloop()

    def stop(self):
        if self.enabled:
            try:
                self.root.destroy()
            except Exception:
                pass
