import os
import glob
import logging
import sys
import traceback
from moviepy.editor import AudioFileClip, CompositeAudioClip

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carpeta destino para el MP3
DESTINO_MP3 = r"C:\Users\jeisson.rodriguez\Documents\Software-personal\project diverza curiosidad"

def combinar_audios(mp3_principal, mp3_diverza, output_path):
    """Combina dos audios, asegurando sincronización sin artefactos."""
    logger.info(f"Combinando audios: {mp3_principal} y {mp3_diverza}")
    try:
        audio_principal = AudioFileClip(mp3_principal)
        audio_diverza = AudioFileClip(mp3_diverza)
        duracion_principal = audio_principal.duration
        
        # Validar duraciones
        logger.info(f"Duración principal: {duracion_principal}s, diverza: {audio_diverza.duration}s")
        if duracion_principal <= 0 or audio_diverza.duration <= 0:
            raise ValueError("Uno de los audios tiene duración inválida")
        
        # Ajustar duración de diverza
        if audio_diverza.duration > duracion_principal:
            logger.info(f"Recortando {mp3_diverza} a {duracion_principal}s")
            audio_diverza = audio_diverza.subclip(0, duracion_principal)
        elif audio_diverza.duration < duracion_principal:
            logger.info(f"Repitiendo {mp3_diverza} hasta {duracion_principal}s")
            audio_diverza = audio_diverza.loop(duration=duracion_principal)
        
        # Combinar audios
        logger.info("Superponiendo audios: principal al 100%, diverza al 30%...")
        audio_combinado = CompositeAudioClip([audio_principal.volumex(1.0), audio_diverza.volumex(0.3)])
        audio_combinado.fps = audio_principal.fps if audio_principal.fps else 44100
        
        # Exportar con alta calidad
        audio_combinado.write_audiofile(output_path, codec='mp3', bitrate='320k', fps=audio_combinado.fps, logger=None)
        logger.info(f"Audio combinado guardado en {output_path}")
        
        # Validar archivo generado
        try:
            test_audio = AudioFileClip(output_path)
            logger.info(f"Duración del audio combinado: {test_audio.duration}s")
            if abs(test_audio.duration - duracion_principal) > 0.1:
                logger.warning(f"Duración del audio combinado ({test_audio.duration}s) no coincide con la esperada ({duracion_principal}s)")
            test_audio.close()
        except Exception as e:
            logger.error(f"Error al validar audio combinado: {e}")
            raise
        
        audio_principal.close()
        audio_diverza.close()
        audio_combinado.close()
        return output_path
    except Exception as e:
        logger.error(f"Error al combinar audios: {e}\n{traceback.format_exc()}")
        raise

def main():
    logger.info("Iniciando combinación de audios...")
    
    try:
        # Buscar archivos MP3
        logger.info("Buscando archivos MP3...")
        mp3_files = glob.glob(os.path.join(DESTINO_MP3, "*.mp3"))
        logger.info(f"Archivos MP3 encontrados: {mp3_files}")
        
        diverza_mp3 = os.path.join(DESTINO_MP3, "diverza_curiosidad.mp3")
        otros_mp3 = [f for f in mp3_files if f != diverza_mp3]
        
        if not os.path.exists(diverza_mp3):
            logger.error("No se encontró diverza_curiosidad.mp3")
            print("No se encontró diverza_curiosidad.mp3", flush=True)
            return False
        
        if not otros_mp3:
            logger.error("No se encontró ningún otro archivo MP3")
            print("No se encontró otro archivo MP3 además de diverza_curiosidad.mp3", flush=True)
            return False
        
        mp3_principal = max(otros_mp3, key=os.path.getctime)
        logger.info(f"MP3 principal seleccionado: {mp3_principal}")
        
        # Combinar audios
        logger.info("Combinando audios...")
        mp3_combinado = os.path.join(DESTINO_MP3, "audio_combinado.mp3")
        combinar_audios(mp3_principal, diverza_mp3, mp3_combinado)
        return True
        
    except Exception as e:
        logger.error(f"Error general: {e}\n{traceback.format_exc()}")
        print(f"Error general: {e}", flush=True)
        return False

if __name__ == "__main__":
    success = main()
    print(f"combinar_audios.py finalizado con éxito: {success}", flush=True)
    sys.exit(0 if success else 1)