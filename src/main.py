import os
import json
import sys
import signal
from overlay import StatusOverlay
from controller import InputController
from listener import InputListener

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    if not os.path.exists(config_path):
        print(f"[Main] config.json not found at {config_path}. Creating a default one.")
        default_config = {
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
                    "f14": "scroll_up",
                    "f15": "scroll_down"
                },
                "mouse": {
                    "x2": "ctrl+c"
                }
            },
            "overlay": {
                "enabled": True,
                "position": "top_center",
                "offset_x": 0,
                "offset_y": 20,
                "opacity": 0.85,
                "font_family": "Segoe UI",
                "font_size": 10,
                "bg_color": "#1e1e2e",
                "text_color": "#cdd6f4",
                "active_color": "#a6e3a1"
            }
        }
        try:
            with open(config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config
        except Exception as e:
            print(f"[Main] Error creating default config.json: {e}")
            return default_config
            
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Main] Error reading config.json: {e}. Using fallback defaults.")
        sys.exit(1)

def main():
    print("=== Logitech MX Autoclicker & Remapper Starting ===")
    config = load_config()

    # Initialize components
    overlay = StatusOverlay(config)
    
    # Controller receives status update callback to notify the overlay
    controller = InputController(config, status_callback=overlay.update_status)
    
    # Listener captures inputs and forwards commands to the controller
    listener = InputListener(config, controller)

    # Set up exit/cleanup handlers
    def shutdown(*args):
        print("\n[Main] Shutting down gracefully...")
        listener.stop()
        controller.release_all()
        overlay.stop()
        print("[Main] Cleanup complete. Goodbye!")
        sys.exit(0)

    # Attach window close handler to Tkinter root if overlay is enabled
    if overlay.enabled:
        overlay.root.protocol("WM_DELETE_WINDOW", shutdown)

    # Handle Ctrl+C (SIGINT)
    signal.signal(signal.SIGINT, shutdown)

    # Start listener threads
    listener.start()

    # Start background thread to watch for 'q' in terminal stdin
    import threading
    def terminal_watcher():
        while True:
            try:
                line = input()
                if line.strip().lower() == 'q':
                    shutdown()
                    break
            except (KeyboardInterrupt, EOFError):
                shutdown()
                break

    watcher_thread = threading.Thread(target=terminal_watcher, daemon=True)
    watcher_thread.start()

    print("[Main] Ready! Use the configured hotkeys to toggle macros or trigger remappings.")
    print("[Main] Press 'q' followed by Enter in this terminal window to exit.")
    
    # Start GUI on main thread or keep main thread alive if GUI is disabled
    if overlay.enabled:
        overlay.start()
    else:
        print("[Main] Overlay HUD is disabled. Press Ctrl+C in terminal to exit.")
        try:
            # Wait for listener keyboard thread to keep main thread alive
            if listener.keyboard_listener:
                listener.keyboard_listener.join()
        except KeyboardInterrupt:
            shutdown()

if __name__ == "__main__":
    main()
