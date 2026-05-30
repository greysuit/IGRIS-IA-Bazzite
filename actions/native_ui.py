import time
import pyautogui
import subprocess
import os

def native_ui(parameters: dict, player=None) -> str:
    """
    Automatización nativa para Linux (X11 optimizado).
    Usa wmctrl para gestión de ventanas real si está disponible.
    """
    action = parameters.get("action", "")
    window_title = parameters.get("window_title", "")
    text_to_type = parameters.get("text", "")
    
    # Verificar si estamos en X11
    is_x11 = os.environ.get("XDG_SESSION_TYPE") == "x11" or os.environ.get("DISPLAY") is not None

    if action == "list_windows":
        try:
            # Intentar listar ventanas reales via wmctrl
            result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                return "Ventanas activas (X11):\n" + result.stdout
            else:
                # Fallback a procesos
                result = subprocess.run(["ps", "-e", "-o", "comm"], capture_output=True, text=True)
                procs = sorted(list(set(result.stdout.splitlines())))[1:40]
                return "Procesos activos (Fallback):\n" + "\n".join(procs)
        except:
            return "No se pudo listar ventanas/procesos."

    elif action == "focus_window":
        if not window_title: return "Error: Falta window_title."
        try:
            # -a: switch to the desktop containing the window and raise it
            subprocess.run(["wmctrl", "-a", window_title], check=True)
            return f"Ventana '{window_title}' enfocada y traída al frente."
        except:
            return f"No se pudo enfocar '{window_title}'. ¿Está instalado 'wmctrl'?"

    elif action == "close_window":
        if not window_title: return "Error: Falta window_title."
        try:
            # -c: close the window gracefully
            subprocess.run(["wmctrl", "-c", window_title], check=True)
            return f"Solicitud de cierre enviada a la ventana: {window_title}"
        except:
            # Fallback a pkill si wmctrl falla
            subprocess.run(["pkill", "-f", window_title])
            return f"Cerrando proceso por nombre: {window_title}"

    elif action == "type_in_window":
        if not text_to_type: return "Error: Falta el texto."
        if window_title:
            subprocess.run(["wmctrl", "-a", window_title])
            time.sleep(0.3)
        pyautogui.write(text_to_type, interval=0.01)
        return f"Texto escrito en '{window_title or 'ventana actual'}'."

    else:
        return f"Acción '{action}' no soportada o requiere X11."
