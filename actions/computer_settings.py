"""computer_settings.py — Clean Win32/system settings controls."""
import os
import sys
import subprocess
try:
    from compat import set_linux_volume, mute_linux_volume, is_linux
except ImportError:
    def is_linux(): return False

def computer_settings(parameters: dict, response=None, player=None) -> str:
    """Adjust system settings like volume, brightness, or active window states."""
    action = parameters.get("action", "").lower()
    value = parameters.get("value", "")
    
    if action == "volume":
        try:
            if is_linux():
                if str(value).isdigit():
                    target = int(value)
                    if set_linux_volume(target):
                        msg = f"Master volume adjusted to {target}% (Linux)."
                    else:
                        msg = "Failed to adjust volume using wpctl."
                else:
                    v_lower = value.lower()
                    if "mute" in v_lower or "silenciar" in v_lower:
                        mute_linux_volume()
                        msg = "Volume muted/unmuted."
                    else:
                        # Fallback to pyautogui for simple up/down
                        import pyautogui
                        if "up" in v_lower or "subir" in v_lower:
                            pyautogui.press("volumeup", presses=5)
                            msg = "Volume increased."
                        else:
                            pyautogui.press("volumedown", presses=5)
                            msg = "Volume decreased."
                if player: player.write_log(f"🔊 {msg}")
                return msg

            import pyautogui
            if str(value).isdigit():
                target = int(value)
                try:
                    from ctypes import cast, POINTER
                    from comtypes import CoInitialize, CoUninitialize
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    CoInitialize()
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
                    volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
                    scalar_vol = max(0.0, min(1.0, target / 100.0))
                    volume_ctrl.SetMasterVolumeLevelScalar(scalar_vol, None)
                    CoUninitialize()
                    msg = f"Master volume adjusted to {target}%."
                except Exception as e:
                    msg = f"Could not set absolute volume: {e}"
            else:
                if "up" in value.lower() or "subir" in value.lower():
                    pyautogui.press("volumeup", presses=5)
                    msg = "Volume increased."
                elif "down" in value.lower() or "bajar" in value.lower():
                    pyautogui.press("volumedown", presses=5)
                    msg = "Volume decreased."
                elif "mute" in value.lower() or "silenciar" in value.lower():
                    pyautogui.press("volumemute")
                    msg = "Volume muted."
                else:
                    msg = f"Unrecognized volume value: {value}"
            if player:
                player.write_log(f"🔊 {msg}")
            return msg
        except Exception as e:
            return f"Failed to adjust volume: {e}"
            
    elif action in ("minimize", "window_minimize"):
        try:
            import pygetwindow as gw
            if gw:
                window = gw.getActiveWindow()
                if window:
                    window.minimize()
                    return "Active window minimized."
            return "No active window found or not supported on Linux."
        except (Exception, NotImplementedError) as e:
            return f"Failed to minimize window: {e}"

    elif action in ("maximize", "window_maximize"):
        try:
            import pygetwindow as gw
            if gw:
                window = gw.getActiveWindow()
                if window:
                    window.maximize()
                    return "Active window maximized."
            return "No active window found or not supported on Linux."
        except (Exception, NotImplementedError) as e:
            return f"Failed to maximize window: {e}"

    return f"Settings action '{action}' is not supported yet, sir."
