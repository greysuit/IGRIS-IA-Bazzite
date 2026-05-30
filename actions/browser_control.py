import webbrowser
import pyautogui
import os

def browser_control(parameters: dict, player=None) -> str:
    """Control browser actions in Bazzite/Linux."""
    action = parameters.get("action", "").lower()
    url = parameters.get("url", "")

    if action == "open":
        if not url: return "Error: URL requerida."
        webbrowser.open(url)
        return f"Abriendo URL: {url}"
    
    elif action == "close_tab":
        pyautogui.hotkey('ctrl', 'w')
        return "Pestaña cerrada."
    
    elif action == "new_tab":
        pyautogui.hotkey('ctrl', 't')
        return "Nueva pestaña abierta."
        
    elif action == "refresh":
        pyautogui.hotkey('ctrl', 'r')
        return "Página actualizada."

    return f"Acción '{action}' no soportada en el navegador bajo Linux."
