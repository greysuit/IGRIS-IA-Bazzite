"""computer_settings.py — Native Bazzite/Linux system settings controls."""
import os
import sys
import subprocess

def run_on_host(command_list):
    """Ejecuta un comando en el host si estamos dentro de un Distrobox."""
    # Comprobar si estamos en distrobox (común en Bazzite)
    if os.path.exists("/run/.containerenv") or os.path.exists("/.dockerenv"):
        return ["distrobox-host-exec"] + command_list
    return command_list

def computer_settings(parameters: dict, response=None, player=None) -> str:
    """Adjust system settings like volume, brightness, or active window states in Bazzite."""
    action = parameters.get("action", "").lower()
    value = parameters.get("value", "")
    
    if action == "volume":
        try:
            if str(value).isdigit():
                target = int(value)
                cmd = run_on_host(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{target/100}"])
                subprocess.run(cmd, capture_output=True)
                msg = f"Volumen ajustado al {target}%."
            else:
                v_lower = str(value).lower()
                if "mute" in v_lower or "silenciar" in v_lower:
                    cmd = run_on_host(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
                    subprocess.run(cmd, capture_output=True)
                    msg = "Silencio alternado."
                elif "up" in v_lower or "subir" in v_lower:
                    cmd = run_on_host(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"])
                    subprocess.run(cmd, capture_output=True)
                    msg = "Volumen aumentado."
                else:
                    cmd = run_on_host(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"])
                    subprocess.run(cmd, capture_output=True)
                    msg = "Volumen disminuido."
            
            if player: player.write_log(f"🔊 {msg}")
            return msg
        except Exception as e:
            return f"Error en audio: {e}"

    elif action == "brightness" or action == "brillo":
        try:
            val = f"{value}%" if str(value).isdigit() else ("+10%" if "up" in str(value).lower() else "10%-")
            cmd = run_on_host(["brightnessctl", "s", val])
            subprocess.run(cmd, capture_output=True)
            return f"Brillo ajustado: {val}"
        except Exception as e:
            return f"Error en brillo: {e}."

    elif action in ("minimize", "window_minimize", "minimizar"):
        try:
            # Minimizar todo en el host
            cmd = run_on_host(["xdotool", "key", "super+d"])
            subprocess.run(cmd, capture_output=True)
            return "Escritorio mostrado (Host)."
        except:
            return "Error al intentar minimizar en el Host."

    elif action in ("close_app", "cerrar_app", "kill", "taskkill"):
        if not value: return "Error: Se necesita el nombre de la app."
        try:
            app = value.lower()
            # Mapeo agresivo para Brave y otros
            targets = [app]
            if "brave" in app: targets = ["brave", "brave-browser", "com.brave.Browser"]
            if "chrome" in app: targets = ["chrome", "google-chrome", "google-chrome-stable"]
            
            results = []
            for t in targets:
                # El equivalente de taskkill /F en Linux es pkill -9
                cmd_pkill = run_on_host(["pkill", "-9", "-f", t])
                subprocess.run(cmd_pkill, capture_output=True)
                
                # Si es un Flatpak (como suele ser en Bazzite)
                if "brave" in app or "com." in t:
                    subprocess.run(run_on_host(["flatpak", "kill", "com.brave.Browser"]), capture_output=True)
                
                results.append(t)
            
            return f"Taskkill (pkill -9) ejecutado en el Host para: {', '.join(results)}"
        except Exception as e:
            return f"Error al cerrar en Host: {e}"

    return f"Acción '{action}' no soportada."
