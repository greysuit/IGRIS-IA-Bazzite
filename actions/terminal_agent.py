"""terminal_agent.py — Native Bazzite/Linux command execution engine for JARVIS."""
import os
import subprocess
import tempfile
import time
from pathlib import Path

def terminal_agent(parameters: dict, player=None) -> str:
    """Execute bash commands on Bazzite/Linux with optional elevation."""
    command = parameters.get("command", "").strip()
    run_as_admin = parameters.get("run_as_admin", False)
    working_dir = parameters.get("working_dir", os.path.expanduser("~"))
    timeout_sec = parameters.get("timeout", 30)

    if not command:
        return "Error: No se proporcionó ningún comando para ejecutar."

    # Si estamos en Bazzite, a veces queremos ejecutar en el host desde el distrobox
    # Para eso el usuario debe usar 'distrobox-host-exec'
    
    # Preparar el comando para elevación en Linux (KDE/Bazzite)
    if run_as_admin:
        # pkexec abre un diálogo gráfico de contraseña en KDE
        command = f"pkexec bash -c '{command}'"

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Ejecución nativa en Bash
        result = subprocess.run(
            ["/bin/bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=working_dir,
            encoding="utf-8",
            errors="replace",
            env=env
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            if output:
                if len(output) > 3000:
                    output = output[:3000] + "\n...[Salida truncada]"
                return f"Comando ejecutado exitosamente:\n{output}"
            else:
                return "Comando ejecutado exitosamente (sin salida)."
        else:
            combined = ""
            if error:
                combined += f"ERROR (stderr):\n{error}\n"
            if output:
                combined += f"SALIDA (stdout):\n{output}"
            return f"El comando falló (Código {result.returncode}):\n{combined}"

    except subprocess.TimeoutExpired:
        return f"Error: El comando excedió el tiempo límite de {timeout_sec} segundos."
    except Exception as e:
        return f"Excepción ejecutando comando en Bazzite: {str(e)}"
