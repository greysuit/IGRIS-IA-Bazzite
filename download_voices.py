import os
import subprocess
import sys

def download_voice_models():
    """Descarga los modelos de voz de Jarvis en Español Latino si no existen."""
    models_dir = os.path.join(os.getcwd(), "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    onnx_path = os.path.join(models_dir, "jarvis.onnx")
    json_path = os.path.join(models_dir, "jarvis.onnx.json")
    
    # URLs de modelos en ESPAÑOL LATINO (es-MX)
    urls = {
        onnx_path: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/low/es_MX-claude-low.onnx",
        json_path: "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/low/es_MX-claude-low.onnx.json"
    }
    
    for path, url in urls.items():
        # Forzar descarga si el usuario quiere cambiar de idioma
        print(f"[IGRIS] Descargando/Actualizando modelo de voz Latino: {os.path.basename(path)}...")
        try:
            subprocess.run(["curl", "-L", "-o", path, url], check=True)
        except Exception as e:
            print(f"[IGRIS] Error descargando voz: {e}")

if __name__ == "__main__":
    download_voice_models()
