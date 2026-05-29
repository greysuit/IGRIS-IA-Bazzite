# -*- coding: utf-8 -*-
import subprocess
import os
import psutil

def set_master_volume(volume_percent: int) -> bool:
    """Ajusta el volumen maestro en Bazzite usando wpctl."""
    try:
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{volume_percent/100}"], capture_output=True)
        return True
    except Exception:
        return False

def set_brightness(percent: int) -> bool:
    """Ajusta el brillo usando brightnessctl."""
    try:
        subprocess.run(["brightnessctl", "s", f"{percent}%"], capture_output=True)
        return True
    except Exception:
        return False

def set_power_plan(plan_name: str) -> bool:
    """Cambia el perfil de energía usando powerprofilesctl."""
    # powerprofilesctl: performance, balanced, power-saver
    mapping = {
        "balanced": "balanced",
        "high_performance": "performance",
        "power_saver": "power-saver"
    }
    target = mapping.get(plan_name.lower(), "balanced")
    try:
        subprocess.run(["powerprofilesctl", "set", target], capture_output=True)
        return True
    except Exception:
        return False

def set_focus_assist(active: bool) -> bool:
    """Ajusta el modo 'No Molestar' en KDE Plasma via DBus."""
    state = "true" if active else "false"
    try:
        # Comando DBus para KDE Plasma (DND)
        cmd = [
            "dbus-send", "--session", "--dest=org.freedesktop.Notifications",
            "--type=method_call", "/org/freedesktop/Notifications",
            "org.freedesktop.Notifications.SetDoNotDisturbMode", f"boolean:{state}"
        ]
        subprocess.run(cmd, capture_output=True)
        return True
    except Exception:
        return False

def contextual_control(parameters: dict, player=None) -> str:
    """Control Contextual de Entorno para Bazzite."""
    action = parameters.get("action", "adjust_context").lower()
    
    if action == "set_volume":
        vol = int(parameters.get("volume", 50))
        set_master_volume(vol)
        return f"Volumen ajustado al {vol}%."

    elif action == "set_brightness":
        bri = int(parameters.get("brightness", 70))
        set_brightness(bri)
        return f"Brillo ajustado al {bri}%."

    elif action == "set_power_plan":
        plan = parameters.get("power_plan", "balanced")
        set_power_plan(plan)
        return f"Perfil de energía: {plan}."

    elif action == "set_dnd":
        state = parameters.get("state", "off").lower() == "on"
        set_focus_assist(state)
        return f"Modo No Molestar: {'Activado' if state else 'Desactivado'}."

    elif action == "adjust_context":
        # Detección por procesos en ejecución (más fiable en Linux Wayland que capturar ventana activa)
        active_procs = []
        for proc in psutil.process_iter(['name']):
            try:
                active_procs.append(proc.info['name'].lower())
            except Exception: pass
        procs_str = " ".join(active_procs)

        if any(w in procs_str for w in ["zoom", "discord", "teams", "whatsapp", "telegram"]):
            set_master_volume(40); set_brightness(60); set_power_plan("balanced"); set_focus_assist(True)
            return "Modo Comunicación: Ajustes de reunión aplicados."
            
        elif any(w in procs_str for w in ["steam", "heroic", "lutris", "cyberpunk", "csgo"]):
            set_master_volume(70); set_brightness(90); set_power_plan("high_performance"); set_focus_assist(True)
            return "Modo Gaming: Alto rendimiento y sin distracciones."

        elif any(w in procs_str for w in ["vlc", "spotify", "firefox", "chrome"]):
            set_master_volume(80); set_brightness(80); set_power_plan("balanced"); set_focus_assist(False)
            return "Modo Multimedia: Volumen alto y brillo optimizado."

        else:
            set_master_volume(50); set_brightness(70); set_power_plan("balanced"); set_focus_assist(False)
            return "Contexto General: Ajustes equilibrados restaurados."

    return "Acción no soportada."
