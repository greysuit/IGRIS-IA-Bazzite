# -*- coding: utf-8 -*-
"""
open_app.py — Intelligent heuristic application finder and launcher for JARVIS.
"""
import os
import sys
import subprocess
import webbrowser
import traceback

import json

def scan_linux_apps():
    """Escanea los archivos .desktop y aplicaciones Flatpak para indexar aplicaciones en Bazzite/Linux."""
    apps_found = {}
    
    # 1. Escaneo de archivos .desktop tradicionales y de Flatpak
    search_paths = [
        "/usr/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/flatpak/exports/share/applications",
        os.path.expanduser("~/.local/share/flatpak/exports/share/applications")
    ]
    
    for path in search_paths:
        if not os.path.exists(path): continue
        for file in os.listdir(path):
            if file.endswith(".desktop"):
                try:
                    with open(os.path.join(path, file), 'r', errors='ignore') as f:
                        name, exec_cmd = None, None
                        for line in f:
                            if line.startswith("Name=") and not name:
                                name = line.split("=")[1].strip().lower()
                            if line.startswith("Exec=") and not exec_cmd:
                                # Limpiar parámetros de Exec (como %U, %F)
                                raw_exec = line.split("=")[1].strip()
                                exec_cmd = raw_exec.split(" %")[0].replace('"', '').strip()
                        if name and exec_cmd:
                            # Si ya existe, preferimos la versión que no sea de sistema si es posible
                            if name not in apps_found or "/usr/share" in apps_found[name]:
                                apps_found[name] = exec_cmd
                except: continue

    # 2. Refuerzo con comando flatpak para asegurar IDs correctos
    try:
        result = subprocess.run(["flatpak", "list", "--columns=name,application"], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "\t" in line:
                    fp_name, fp_id = line.split("\t")
                    apps_found[fp_name.lower().strip()] = f"flatpak run {fp_id.strip()}"
    except: pass
    
    return apps_found

def find_linux_app(app_name: str) -> str:
    """Busca aplicaciones usando el índice escaneado del sistema con búsqueda difusa."""
    app_lower = app_name.lower().strip()
    apps = scan_linux_apps()
    
    # 1. Búsqueda por nombre exacto
    if app_lower in apps:
        return apps[app_lower]
    
    # 2. Búsqueda por palabra clave (ej: "discord" en "com.discordapp.Discord")
    for name, cmd in apps.items():
        if app_lower in name:
            return cmd
            
    # 3. Búsqueda en el comando mismo (útil para IDs de Flatpak o Waydroid)
    for name, cmd in apps.items():
        if app_lower in cmd.lower():
            return cmd

    # 4. Mapeos manuales de emergencia actualizados para Bazzite
    linux_mappings = {
        "spotify": "flatpak run com.spotify.Client",
        "discord": "flatpak run com.discordapp.Discord",
        "brave": "flatpak run com.brave.Browser",
        "terminal": "konsole", # En Bazzite suele ser Konsole o Ptyxis
        "ajustes": "systemsettings",
        "botellas": "flatpak run com.usebottles.bottles"
    }
    # ... resto del código anterior
    
    mapped = linux_mappings.get(app_lower)
    if mapped:
        # Verificar si es un Flatpak
        try:
            check_flatpak = subprocess.run(["flatpak", "info", mapped], capture_output=True)
            if check_flatpak.returncode == 0:
                return f"flatpak run {mapped}"
        except:
            pass
        return mapped

    return None

def find_executable(app_name: str) -> str:
    """Scan standard system folders recursively to find executable..."""
    if sys.platform != "win32":
        return find_linux_app(app_name)
    
    exe_search_dirs = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files")),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")),
        os.path.join(os.environ.get("LocalAppData", ""), "Programs"),
        "C:\\Windows\\System32",
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs")
    ]
    
    doc_search_dirs = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Downloads")
    ]
    
    app_lower = app_name.lower().strip()
    
    # First search: standard programs (.exe, .lnk)
    for base_dir in exe_search_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
            
        for root, dirs, files in os.walk(base_dir):
            depth = root.count(os.sep) - base_dir.count(os.sep)
            if depth > 3:
                dirs.clear()
                continue
                
            for file in files:
                if file.lower().endswith(".exe") or file.lower().endswith(".lnk"):
                    file_name_no_ext = os.path.splitext(file)[0].lower()
                    if app_lower == file_name_no_ext or app_lower in file_name_no_ext:
                        full_path = os.path.join(root, file)
                        if "redist" not in full_path.lower() and "uninstall" not in full_path.lower():
                            return full_path

    # Second search: user documents (.docx, .xlsx, .pptx, .pdf, .txt, .csv, .zip, etc.)
    doc_extensions = [".docx", ".xlsx", ".pptx", ".pdf", ".txt", ".csv", ".zip", ".png", ".jpg"]
    for base_dir in doc_search_dirs:
        if not base_dir or not os.path.exists(base_dir):
            continue
            
        for root, dirs, files in os.walk(base_dir):
            depth = root.count(os.sep) - base_dir.count(os.sep)
            if depth > 3:
                dirs.clear()
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in doc_extensions:
                    file_name_no_ext = os.path.splitext(file)[0].lower()
                    if app_lower == file_name_no_ext or app_lower in file_name_no_ext:
                        return os.path.join(root, file)
                        
    return None

def open_app(parameters: dict, response=None, player=None) -> str:
    """Launch local desktop applications, folders, or web URLs heuristically based on app_name."""
    app_name = parameters.get("app_name", "").strip()
    if not app_name:
        return "Error: Se requiere el parámetro 'app_name'."

    app_lower = app_name.lower().strip()

    try:
        # 1. Check if it's a URL
        if app_lower.startswith("http://") or app_lower.startswith("https://") or app_lower.endswith(".com") or app_lower.endswith(".org") or app_lower.endswith(".net") or app_lower.endswith(".es") or app_lower.endswith(".cl"):
            url = app_name if app_lower.startswith("http") else f"https://{app_name}"
            webbrowser.open(url)
            msg = f"Abriendo el sitio web: '{url}'."
            if player:
                player.write_log(f"🌐 {msg}")
            return msg

        # 2. Check if it is a directory path or drive letter
        if os.path.exists(app_name) and os.path.isdir(app_name):
            if sys.platform == "win32":
                os.startfile(app_name)
            else:
                subprocess.Popen(["xdg-open", app_name])
            msg = f"Abriendo la carpeta local: '{app_name}'."
            if player:
                player.write_log(f"📁 {msg}")
            return msg

        # 3. Check virtual directories
        home = os.path.expanduser("~")
        virtual_folders = {
            "desktop": os.path.join(home, "Desktop"),
            "escritorio": os.path.join(home, "Desktop"),
            "downloads": os.path.join(home, "Downloads"),
            "descargas": os.path.join(home, "Downloads"),
            "documents": os.path.join(home, "Documents"),
            "documentos": os.path.join(home, "Documents"),
            "pictures": os.path.join(home, "Pictures"),
            "imagenes": os.path.join(home, "Pictures"),
            "music": os.path.join(home, "Music"),
            "musica": os.path.join(home, "Music"),
            "videos": os.path.join(home, "Videos")
        }
        if app_lower in virtual_folders:
            folder_path = virtual_folders[app_lower]
            if sys.platform == "win32":
                os.startfile(folder_path)
            else:
                subprocess.Popen(["xdg-open", folder_path])
            msg = f"Abriendo carpeta del sistema: '{app_lower}'."
            if player:
                player.write_log(f"📁 {msg}")
            return msg

        # 4. Standard Static mappings dictionary
        mappings = {
            "notepad": "notepad.exe",
            "bloc de notas": "notepad.exe",
            "calculator": "calc.exe",
            "calculadora": "calc.exe",
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "explorer": "explorer.exe",
            "explorador de archivos": "explorer.exe",
            "cmd": "cmd.exe",
            "terminal": "powershell.exe",
            "powershell": "powershell.exe",
            "paint": "mspaint.exe",
            "taskmgr": "taskmgr.exe",
            "administrador de tareas": "taskmgr.exe"
        }

        executable = mappings.get(app_lower, None)
        
        # 5. If not in static mappings, use our heuristics search
        if not executable:
            executable = find_executable(app_name)

        # 6. Fallback to trying to run it directly if still not found
        if not executable:
            executable = app_name

        # Launch the resolved application safely
        try:
            if sys.platform != "win32":
                # En Linux, ejecutamos el comando directamente (puede ser un binario o 'flatpak run ...')
                # Si el usuario está en un contenedor y necesita salir al host, puede configurar la app para usar distrobox-host-exec
                subprocess.Popen(executable, shell=True)
            else:
                os.startfile(executable)
        except Exception:
            # Fallback for raw commands
            subprocess.Popen(executable, shell=True)

        msg = f"Abriendo la aplicación: '{app_name}'."
        if player:
            player.write_log(f"🚀 {msg}")
        return f"Aplicación '{app_name}' iniciada correctamente (Ruta: {executable})."

    except Exception as e:
        traceback.print_exc()
        return f"Error intentando abrir '{app_name}': {str(e)}"
