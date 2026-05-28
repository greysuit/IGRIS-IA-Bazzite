import sys
import os
import subprocess
import platform

def is_linux():
    return sys.platform.startswith("linux")

def linux_startfile(path):
    subprocess.run(["xdg-open", str(path)], check=False)

def get_linux_volume():
    """Obtiene el volumen usando wpctl (PipeWire)."""
    try:
        result = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True)
        # Output typical: Volume: 0.50 [MUTED]
        parts = result.stdout.strip().split()
        if len(parts) >= 2:
            return int(float(parts[1]) * 100)
    except:
        return 0
    return 0

def set_linux_volume(value):
    """Establece el volumen usando wpctl (0-100)."""
    try:
        scalar = max(0.0, min(1.0, value / 100.0))
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{scalar}"], check=False)
        return True
    except:
        return False

def mute_linux_volume():
    try:
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], check=False)
        return True
    except:
        return False

# Mock de clases de Windows para evitar errores de importación
class MockWin32:
    def __init__(self):
        self.kernel32 = self
        self.user32 = self
        self.shell32 = self
    
    def GetLastError(self): return 0
    def CreateMutexW(self, a, b, c): return 1
    def IsUserAnAdmin(self): return os.getuid() == 0
    def FindWindowW(self, a, b): return 0
    def ShowWindow(self, a, b): pass
    def SetForegroundWindow(self, a): pass

if is_linux():
    os.startfile = linux_startfile
    # Inyectar mocks si es necesario
    if not hasattr(sys, "frozen"):
        import ctypes
        if not hasattr(ctypes, "windll"):
            ctypes.windll = MockWin32()
