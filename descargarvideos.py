import os
import yt_dlp
import logging
import sys
import traceback

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def progress_hook(d):
    """Captura el progreso de yt_dlp y lo imprime."""
    if d['status'] == 'downloading':
        percentage = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        speed = d.get('speed', 0) or 0
        eta = d.get('eta', 'Unknown')
        print(f"[download] {percentage:.1f}% of {d.get('total_bytes', 0)/1024/1024:.2f}MiB at {speed/1024/1024:.2f}MiB/s ETA {eta}", flush=True)
    elif d['status'] == 'finished':
        print("[download] Completado", flush=True)

def descargar_video():
    try:
        print("Iniciando descargarvideos.py...", flush=True)
        logger.info("Iniciando descargarvideos.py...")

        # Verificar video_url.txt
        if not os.path.exists("video_url.txt"):
            logger.error("No se encontró video_url.txt")
            print("No se encontró video_url.txt", flush=True)
            return False

        print("Leyendo video_url.txt...", flush=True)
        with open("video_url.txt", "r", encoding="utf-8") as f:
            url = f.read().strip()

        if not url:
            logger.error("URL vacía")
            print("URL vacía", flush=True)
            return False

        if not url.startswith(('http://', 'https://')):
            logger.error("URL inválida (no empieza con http:// o https://)")
            print("URL inválida (no empieza con http:// o https://)", flush=True)
            return False

        logger.info(f"Descargando video de: {url}")
        print(f"Descargando video de: {url}", flush=True)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
        }

        print("Iniciando descarga con yt_dlp...", flush=True)
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                archivo = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp4'
        except Exception as e:
            logger.error(f"Error en yt_dlp: {e}")
            print(f"Error en yt_dlp: {e}", flush=True)
            return False

        print("Verificando archivo descargado...", flush=True)
        if not os.path.exists(archivo):
            logger.error("Video no descargado")
            print("Video no descargado", flush=True)
            return False

        logger.info("Video descargado con éxito")
        print("[OK] Video descargado con éxito", flush=True)
        return True

    except Exception as e:
        logger.error(f"Error general: {e}\n{traceback.format_exc()}")
        print(f"Error general: {e}", flush=True)
        return False

if __name__ == "__main__":
    success = descargar_video()
    print(f"descargarvideos.py finalizado con éxito: {success}", flush=True)
    sys.exit(0 if success else 1)