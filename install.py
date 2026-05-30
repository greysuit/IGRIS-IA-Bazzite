# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import time

def print_banner():
    cyan = "\033[36m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"
    reset = "\033[0m"
    
    print(f"{cyan}======================================================================={reset}")
    print(f"{cyan}      _____  ______  ____   _____  _____                           {reset}")
    print(f"{cyan}     |_   _||  ____||  _ \ |_   _|/ ____|                          {reset}")
    print(f"{cyan}       | |  | |__   | |_) |  | | | (___                            {reset}")
    print(f"{cyan}       | |  |  __|  |  _ <   | |  \___ \                           {reset}")
    print(f"{cyan}      _| |_ | |____ | |_) | _| |_ ____) |                          {reset}")
    print(f"{cyan}     |_____||______||____/ |_____|_____/                           {reset}")
    print("                                                                       ")
    print(f"{green}             SISTEMA DE INSTALACIÓN - BAZZITE NATIVE                   {reset}")
    print(f"{cyan}======================================================================={reset}")
    print()

def main():
    os.system("clear")
    print_banner()
    print("Este asistente preparará a IGRIS para funcionar en Bazzite/Linux.")
    print()
    print(" [1] Comenzar instalación limpia (Recomendado)")
    print(" [2] Salir")
    print()
    
    try:
        opt = input("Selecciona una opción (1-2): ").strip()
    except (KeyboardInterrupt, EOFError):
        opt = "2"
        
    if opt != "1":
        sys.exit(0)
        
    # FASE 1: Verificación
    os.system("clear")
    print_banner()
    print("\033[36m [FASE 1/4] - Verificando requisitos del sistema...\033[0m")
    print(f"[OK] Python detectado: {sys.version.split()[0]}")
    
    # FASE 2: Entorno Virtual
    print("\n\033[36m [FASE 2/4] - Configurando Entorno Virtual (.venv)...\033[0m")
    if not os.path.exists(".venv"):
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print("\033[32m[OK] Entorno virtual creado.\033[0m")
        except Exception as e:
            print(f"\033[31m[ERROR] No se pudo crear: {e}\033[0m")
            sys.exit(1)
            
    # FASE 3: Dependencias
    print("\n\033[36m [FASE 3/4] - Instalando dependencias nativas...\033[0m")
    venv_python = os.path.join(".venv", "bin", "python3")
    if not os.path.exists(venv_python): venv_python = "python3"
        
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("\033[32m[OK] Dependencias instaladas correctamente.\033[0m")
    except Exception as e:
        print(f"\033[31m[ERROR] Fallo en instalación: {e}\033[0m")
        sys.exit(1)
        
    # FASE 4: Configuración
    print("\n\033[36m [FASE 4/4] - Configuración Inicial...\033[0m")
    config_dir = "config"
    os.makedirs(config_dir, exist_ok=True)
    
    api_keys_path = os.path.join(config_dir, "api_keys.json")
    if not os.path.exists(api_keys_path):
        import json
        default_config = {
            "gemini_api_key": "",
            "os_system": "linux",
            "camera_index": 0,
            "mic_device": 0,
            "spk_device": 0,
            "timezone": "America/Mexico_City",
            "language": "es-MX",
            "igris_voice": "LOCAL_JARVIS",
            "openrouter_api_key": "",
            "jarvis_theme": "gold",
            "gpu_acceleration": True
        }
        with open(api_keys_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
        print("\033[32m[OK] Archivo de configuración base creado.\033[0m")

    os.system("clear")
    print_banner()
    print("\033[32m¡INSTALACIÓN COMPLETADA PARA BAZZITE!\033[0m")
    print("\nPuedes iniciar a IGRIS con: python3 main.py")
    print()

if __name__ == "__main__":
    main()
