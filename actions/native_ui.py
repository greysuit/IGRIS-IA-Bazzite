import time
import pyautogui
import subprocess
import os

def native_ui(parameters: dict, player=None) -> str:
    """
    Automatización nativa para Linux/Bazzite.
    Usa pkill y atajos de teclado en lugar de pygetwindow.
    """
    action = parameters.get("action", "")
    window_title = parameters.get("window_title", "")
    text_to_type = parameters.get("text", "")
    
    if action == "list_windows":
        # En Linux/Bazzite, listamos procesos activos como alternativa
        try:
            result = subprocess.run(["ps", "-e", "-o", "comm"], capture_output=True, text=True)
            procs = sorted(list(set(result.stdout.splitlines())))[1:50] # Top 50 procs
            return "Aplicaciones/Procesos activos:\n" + "\n".join(procs)
        except:
            return "No se pudo listar procesos en este entorno."
        
    elif action == "focus_window" or action == "close_window":
        if not window_title:
            return "Error: Se requiere el nombre de la aplicación."
        # Intentar pkill para cerrar si se pidió close
        if action == "close_window":
            subprocess.run(["pkill", "-f", window_title])
            return f"Orden de cierre enviada a '{window_title}'."
        return "El enfoque de ventanas específico no es compatible con Wayland/Bazzite por seguridad."
            
    elif action == "type_in_window":
        # Escribir en el lugar actual (donde esté el foco)
        if not text_to_type: return "Error: Falta el texto."
        pyautogui.write(text_to_type, interval=0.01)
        return "Texto escrito en la aplicación actual."
            
    else:
        return f"Acción '{action}' no soportada en Bazzite."
