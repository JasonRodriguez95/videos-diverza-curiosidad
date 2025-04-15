import os
import logging
import sys
import traceback
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.fx.all import loop
import re
import shutil

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carpeta destino
DESTINO = r"C:\Users\jeisson.rodriguez\Documents\Software-personal\project diverza curiosidad"
PRUEBA_DIR = r"C:\Users\jeisson.rodriguez\Documents\Software-personal\prueba"

def sanitizar_nombre(nombre):
    """Sanitiza el nombre del archivo reemplazando caracteres no permitidos."""
    return re.sub(r'[^\w\s-]', '', nombre.replace(' ', '_')).lower()

def cortar_video(video_path, duracion_objetivo=10):
    """Corta el video a una duración objetivo (default 10 segundos)."""
    try:
        clip = VideoFileClip(video_path)
        duracion = min(clip.duration, duracion_objetivo)
        clip_cortado = clip.subclip(0, duracion)
        nombre_base = os.path.splitext(os.path.basename(video_path))[0]
        nuevo_path = os.path.join(os.path.dirname(video_path), f"{nombre_base}_cortado.mp4")
        clip_cortado.write_videofile(
            nuevo_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None
        )
        clip.close()
        clip_cortado.close()
        return nuevo_path
    except Exception as e:
        logger.error(f"Error al cortar video {video_path}: {e}")
        return None

def limpiar_archivos():
    """Elimina archivos temporales .txt y maneja archivos .mp4."""
    try:
        # Eliminar archivos .txt
        for archivo in ['tema.txt', 'temporal.txt', 'video_url.txt']:
            if os.path.exists(archivo):
                os.remove(archivo)
                logger.info(f"Archivo {archivo} eliminado")
                print(f"Archivo {archivo} eliminado", flush=True)

        # Manejar archivos .mp4
        videos_intermedios = ['downloaded_video.mp4', 'video_intermedio.mp4']
        os.makedirs(PRUEBA_DIR, exist_ok=True)

        tema = "video_final"  # Default si tema.txt no existe
        if os.path.exists('tema.txt'):
            with open('tema.txt', 'r', encoding='utf-8') as f:
                tema = sanitizar_nombre(f.read().strip())

        video_final = f"{tema}.mp4"

        for video in videos_intermedios:
            if os.path.exists(video) and video != video_final:
                # Cortar video
                video_cortado = cortar_video(video)
                if video_cortado:
                    # Mover a PRUEBA_DIR
                    destino = os.path.join(PRUEBA_DIR, os.path.basename(video_cortado))
                    shutil.move(video_cortado, destino)
                    logger.info(f"Video {video} cortado y movido a {destino}")
                    print(f"Video {video} cortado y movido a {destino}", flush=True)
                    # Eliminar original
                    os.remove(video)
                    logger.info(f"Video original {video} eliminado")
                    print(f"Video original {video} eliminado", flush=True)

    except Exception as e:
        logger.error(f"Error al limpiar archivos: {e}\n{traceback.format_exc()}")
        print(f"Error al limpiar archivos: {e}", flush=True)

def main():
    logger.info("Iniciando adición de GIFs...")
    try:
        # Validar video intermedio
        video_intermedio = os.path.join(DESTINO, "video_intermedio.mp4")
        if not os.path.exists(video_intermedio):
            logger.error("No se encontró video_intermedio.mp4")
            print("No se encontró video_intermedio.mp4", flush=True)
            return False

        # Cargar video intermedio
        video_clip = None
        try:
            video_clip = VideoFileClip(video_intermedio)
            duracion = video_clip.duration
            logger.info(f"Duración del video intermedio: {duracion} segundos")
            if duracion < 1:
                logger.error("El video intermedio es demasiado corto o inválido")
                print("El video intermedio es demasiado corto o inválido", flush=True)
                return False
        except Exception as e:
            logger.error(f"Error al cargar video intermedio: {e}\n{traceback.format_exc()}")
            print(f"Error al cargar el video intermedio: {e}", flush=True)
            return False

        # Validar GIFs
        diverza_gif = os.path.join(DESTINO, "diverza.gif")
        reportera_gif = os.path.join(DESTINO, "reportera.gif")
        if not os.path.exists(diverza_gif):
            logger.error("No se encontró diverza.gif")
            print("No se encontró diverza.gif", flush=True)
            return False

        # Cargar GIFs
        diverza_clip = None
        reportera_clip = None
        try:
            # Cargar diverza.gif con transparencia y animación
            diverza_clip = VideoFileClip(diverza_gif, has_mask=True)
            diverza_clip = loop(diverza_clip)  # Bucle infinito

            if os.path.exists(reportera_gif):
                # Cargar reportera.gif
                reportera_clip = VideoFileClip(reportera_gif, has_mask=True)
                reportera_clip = loop(reportera_clip)  # Bucle infinito
            else:
                logger.warning("reportera.gif no encontrado, usando solo diverza.gif")
        except Exception as e:
            logger.error(f"Error al cargar GIFs: {e}\n{traceback.format_exc()}")
            print(f"Error al cargar GIFs: {e}", flush=True)
            return False

        # Redimensionar GIFs
        ancho_video, alto_video = video_clip.size
        escala = 0.2
        try:
            diverza_clip = diverza_clip.resize(width=int(ancho_video * escala))
            if reportera_clip:
                reportera_clip = reportera_clip.resize(width=int(ancho_video * escala))
        except Exception as e:
            logger.error(f"Error al redimensionar GIFs: {e}\n{traceback.format_exc()}")
            print(f"Error al redimensionar GIFs: {e}", flush=True)
            return False

        # Posicionar GIFs
        try:
            # diverza.gif: abajo izquierda, todo el video
            diverza_clip = diverza_clip.set_position((10, alto_video - diverza_clip.h - 10))

            if reportera_clip:
                # reportera.gif: abajo derecha, todo el video
                reportera_clip = reportera_clip.set_position((ancho_video - reportera_clip.w - 10, alto_video - reportera_clip.h - 10))
        except Exception as e:
            logger.error(f"Error al posicionar GIFs: {e}\n{traceback.format_exc()}")
            print(f"Error al posicionar GIFs: {e}", flush=True)
            return False

        # Componer video final
        clips = [video_clip]
        if diverza_clip:
            clips.append(diverza_clip)
        if reportera_clip:
            clips.append(reportera_clip)

        final_clip = None
        try:
            final_clip = CompositeVideoClip(clips).set_duration(video_clip.duration)
        except Exception as e:
            logger.error(f"Error al componer video final: {e}\n{traceback.format_exc()}")
            print(f"Error al componer video final: {e}", flush=True)
            return False

        # Guardar video final
        tema = "video_final"
        if os.path.exists(os.path.join(DESTINO, "tema.txt")):
            with open(os.path.join(DESTINO, "tema.txt"), 'r', encoding='utf-8') as f:
                tema = sanitizar_nombre(f.read().strip())

        output_file = os.path.join(DESTINO, f"{tema}.mp4")
        try:
            final_clip.write_videofile(
                output_file,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                threads=4,
                preset='medium',
                bitrate='5000k',
                fps=24,
                logger=None
            )
            logger.info(f"Video final guardado como {output_file}")
            print(f"Video final guardado como {output_file}", flush=True)
        except Exception as e:
            logger.error(f"Error al guardar video final: {e}\n{traceback.format_exc()}")
            print(f"Error al guardar video final: {e}", flush=True)
            return False
        finally:
            if video_clip:
                video_clip.close()
            if diverza_clip:
                diverza_clip.close()
            if reportera_clip:
                reportera_clip.close()
            if final_clip:
                final_clip.close()

        # Limpiar archivos temporales
        try:
            limpiar_archivos()
            logger.info("Limpieza de archivos completada")
            print("Limpieza de archivos completada", flush=True)
        except Exception as e:
            logger.error(f"Error durante la limpieza: {e}\n{traceback.format_exc()}")
            print(f"Error durante la limpieza: {e}", flush=True)
            return False

        return True

    except Exception as e:
        logger.error(f"Error general: {e}\n{traceback.format_exc()}")
        print(f"Error general: {e}", flush=True)
        return False

if __name__ == "__main__":
    success = main()
    print(f"anadir_gifs.py finalizado con éxito: {success}", flush=True)
    sys.exit(0 if success else 1)