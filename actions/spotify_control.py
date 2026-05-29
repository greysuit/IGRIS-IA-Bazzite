"""spotify_control.py — Clean Spotify/Media controller using Windows API hooks."""
import time

import time
import os
import subprocess

def spotify_control(parameters: dict, player=None) -> str:
    """Control Spotify or generic active media playback using system-native commands."""
    action = parameters.get("action", "").lower().strip()
    if not action:
        return "Action parameter is required."
        
    try:
        if os.name != "nt":
            # --- Lógica de Linux (playerctl) ---
            mapping = {
                "play": "play",
                "pause": "pause",
                "toggle": "play-pause",
                "next": "next",
                "skip": "next",
                "prev": "previous",
                "previous": "previous",
                "back": "previous"
            }
            
            if action in mapping:
                cmd = ["playerctl", mapping[action]]
                subprocess.run(cmd, capture_output=True)
                msg = f"Media action '{action}' sent via playerctl."
            elif action == "volume":
                value = parameters.get("value", "")
                vol_change = "0.05+" if "up" in str(value).lower() else "0.05-"
                subprocess.run(["playerctl", "volume", vol_change], capture_output=True)
                msg = f"Volume adjusted: {vol_change}"
            else:
                msg = f"Action '{action}' not recognized on Linux."
        else:
            # --- Lógica de Windows (pyautogui) ---
            import pyautogui
            if action in ("play", "pause", "toggle"):
                pyautogui.press("playpause")
                msg = "Media playback toggled."
            # ... rest of win logic ...
            
        if player:
            player.write_log(f"🎵 Spotify: {msg}")
        return msg
    except Exception as e:
        return f"Error executing media control action: {e}"
