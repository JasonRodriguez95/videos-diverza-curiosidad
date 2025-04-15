import os
import logging
import sys
import traceback
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carpeta destino
DESTINO_MP3 = r"C:\Users\jeisson.rodriguez\Documents\Software-personal\project diverza curiosidad"

def crear_resumen_video(clip, duracion_real, duracion_objetivo):
    """Crea un resumen del video ajustado a la duración objetivo."""
    logger.info(f"Creando resumen: duracion_real={duracion_real}s, duracion_objetivo={duracion_objetivo}s")
    try:
        if duracion_real <= 0:
            raise ValueError("Duración del video original inválida")
        
        if duracion_real <= duracion_objetivo:
            logger.info("Video más corto, ajustando con loop...")
            return clip.set_duration(duracion_objetivo)
        
        logger.info("Video más largo, dividiendo en partes iguales...")
        num_segmentos = max(3, int(duracion_real / 10))
        segmento_duracion = duracion_objetivo / num_segmentos
        clips = []
        
        for i in range(num_segmentos):
            inicio = (i / num_segmentos) * duracion_real
            fin = min(inicio + segmento_duracion, duracion_real)
            if fin > inicio + 0.1:  # Asegurar segmento válido
                try:
                    subclip = clip.subclip(max(0, inicio), fin)
                    if subclip.duration > 0:
                        clips.append(subclip)
                    else:
                        logger.warning(f"Segmento {i+1} tiene duración cero, omitiendo")
                except Exception as e:
                    logger.warning(f"Error en segmento {i+1}: {e}")
                    continue
            else:
                logger.warning(f"Segmento {i+1} inválido (inicio={inicio}, fin={fin}), omitiendo")
        
        if not clips:
            logger.warning("No se generaron clips válidos, recortando video completo")
            return clip.subclip(0, min(duracion_real, duracion_objetivo))
        
        try:
            final_clip = concatenate_videoclips(clips, method="compose")
            return final_clip.set_duration(duracion_objetivo)
        except Exception as e:
            logger.error(f"Error al concatenar clips: {e}")
            logger.warning("Usando video original recortado como respaldo")
            return clip.subclip(0, min(duracion_real, duracion_objetivo))
    except Exception as e:
        logger.error(f"Error en crear_resumen_video: {e}\n{traceback.format_exc()}")
        return clip.subclip(0, min(duracion_real, duracion_objetivo))

def main():
    logger.info("Iniciando creación de video intermedio...")
    
    try:
        # Validar audio combinado
        logger.info("Validando audio_combinado.mp3...")
        mp3_combinado = os.path.join(DESTINO_MP3, "audio_combinado.mp3")
        if not os.path.exists(mp3_combinado):
            logger.error("No se encontró audio_combinado.mp3")
            print("No se encontró audio_combinado.mp3", flush=True)
            return False
        
        try:
            audio_clip = AudioFileClip(mp3_combinado)
            duracion_objetivo = audio_clip.duration
            audio_clip.close()
            logger.info(f"Duración del MP3 combinado: {duracion_objetivo} segundos")
            if duracion_objetivo <= 0:
                logger.error("La duración del MP3 combinado es inválida")
                print("La duración del MP3 combinado es inválida", flush=True)
                return False
        except Exception as e:
            logger.error(f"Error al obtener duración: {e}\n{traceback.format_exc()}")
            print(f"Error al leer la duración del MP3 combinado: {e}", flush=True)
            return False

        # Validar y cargar video descargado
        logger.info("Validando y cargar video descargado...")
        archivo_original = "downloaded_video.mp4"
        if not os.path.exists(archivo_original):
            logger.error("No se encontró downloaded_video.mp4")
            print("No se encontró downloaded_video.mp4", flush=True)
            return False
        
        clip = None
        try:
            clip = VideoFileClip(archivo_original)
            duracion_real = clip.duration
            logger.info(f"Duración del video: {duracion_real} segundos")
            if duracion_real < 1:
                logger.error("El video descargado es demasiado corto o inválido")
                print("El video descargado es demasiado corto o inválido", flush=True)
                return False
        except Exception as e:
            logger.error(f"Error al cargar video: {e}\n{traceback.format_exc()}")
            print(f"Error al cargar el video descargado: {e}", flush=True)
            return False
        finally:
            if clip:
                clip.close()

        # Procesar video
        logger.info("Procesando video...")
        clip = None
        final_clip = None
        audio_clip = None
        try:
            clip = VideoFileClip(archivo_original)
            final_clip = crear_resumen_video(clip, duracion_real, duracion_objetivo)
            if final_clip is None:
                logger.error("No se generó un clip válido en crear_resumen_video")
                print("No se generó un clip válido en crear_resumen_video", flush=True)
                return False
            
            logger.info("Montando audio combinado...")
            try:
                audio_clip = AudioFileClip(mp3_combinado)
                final_clip = final_clip.set_audio(audio_clip).set_duration(duracion_objetivo)
            except Exception as e:
                logger.error(f"Error al montar audio: {e}\n{traceback.format_exc()}")
                print(f"Error al montar el audio combinado: {e}", flush=True)
                return False
            
            # Guardar video intermedio
            logger.info("Guardando video intermedio...")
            output_file = os.path.join(DESTINO_MP3, "video_intermedio.mp4")
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
                logger.info(f"Video intermedio guardado como {output_file}")
                print(f"Video intermedio guardado como {output_file}", flush=True)
            except Exception as e:
                logger.error(f"Error al guardar video intermedio: {e}\n{traceback.format_exc()}")
                print(f"Error al guardar el video intermedio: {e}", flush=True)
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error al procesar video: {e}\n{traceback.format_exc()}")
            print(f"Error al procesar el video: {e}", flush=True)
            return False
        finally:
            if clip:
                clip.close()
            if final_clip:
                final_clip.close()
            if audio_clip:
                audio_clip.close()

    except Exception as e:
        logger.error(f"Error general: {e}\n{traceback.format_exc()}")
        print(f"Error general: {e}", flush=True)
        return False

if __name__ == "__main__":
    success = main()
    print(f"resumen_video.py finalizado con éxito: {success}", flush=True)
    sys.exit(0 if success else 1)