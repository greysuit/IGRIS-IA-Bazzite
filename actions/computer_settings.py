"""computer_settings.py — Native Bazzite/Linux system settings controls."""
import os
import sys
import subprocess

def computer_settings(parameters: dict, response=None, player=None) -> str:
    """Adjust system settings like volume, brightness, or active window states in Bazzite."""
    action = parameters.get("action", "").lower()
    value = parameters.get("value", "")
    
    if action == "volume":
        try:
            if str(value).isdigit():
                target = int(value)
                # wpctl set-volume @DEFAULT_AUDIO_SINK@ 50%
                subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{target/100}"], capture_output=True)
                msg = f"Volumen ajustado al {target}% via wpctl."
            else:
                v_lower = str(value).lower()
                if "mute" in v_lower or "silenciar" in v_lower:
                    subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], capture_output=True)
                    msg = "Silencio activado/desactivado."
                elif "up" in v_lower or "subir" in v_lower:
                    subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%+"], capture_output=True)
                    msg = "Volumen aumentado."
                elif "down" in v_lower or "bajar" in v_lower:
                    subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "5%-"], capture_output=True)
                    msg = "Volumen disminuido."
                else:
                    msg = f"Valor de volumen no reconocido: {value}"
            
            if player: player.write_log(f"🔊 {msg}")
            return msg
        except Exception as e:
            return f"Error al ajustar volumen en Linux: {e}"

    elif action == "brightness" or action == "brillo":
        try:
            # Usar brightnessctl (común en Bazzite)
            if str(value).isdigit():
                target = int(value)
                subprocess.run(["brightnessctl", "s", f"{target}%"], capture_output=True)
                msg = f"Brillo ajustado al {target}%."
            else:
                v_lower = str(value).lower()
                if "up" in v_lower or "subir" in v_lower:
                    subprocess.run(["brightnessctl", "s", "+10%"], capture_output=True)
                    msg = "Brillo aumentado."
                else:
                    subprocess.run(["brightnessctl", "s", "10%-"], capture_output=True)
                    msg = "Brillo disminuido."
            return msg
        except Exception as e:
            return f"Error al ajustar brillo: {e}. Asegúrate de tener 'brightnessctl' instalado."

    elif action in ("minimize", "window_minimize", "minimizar"):
        try:
            import pyautogui
            # Atajo estándar de KDE para mostrar escritorio / minimizar todo
            pyautogui.hotkey('win', 'd') 
            return "Comando de minimización enviado al sistema."
        except Exception as e:
            return f"Error al minimizar: {e}"
