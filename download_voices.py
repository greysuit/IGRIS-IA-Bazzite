import os
import subprocess
import sys

def download_voice_models():
    """Descarga los modelos de voz de Jarvis si no existen."""
    models_dir = os.path.join(os.getcwd(), "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    onnx_path = os.path.join(models_dir, "jarvis.onnx")
    json_path = os.path.join(models_dir, "jarvis.onnx.json")
    
    # URLs de modelos de alta calidad (Jarvis/British Sophisticated)
    # Usaremos una versión optimizada de Piper
    urls = {
        onnx_path: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx",
        json_path: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
    }
    
    for path, url in urls.items():
        if not os.path.exists(path):
            print(f"[IGRIS] Descargando modelo de voz: {os.path.basename(path)}...")
            try:
                subprocess.run(["curl", "-L", "-o", path, url], check=True)
            except Exception as e:
                print(f"[IGRIS] Error descargando voz: {e}")

if __name__ == "__main__":
    download_voice_models()
