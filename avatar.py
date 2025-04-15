import pygame
import librosa
import numpy as np
import time
import os
import glob

# Inicializar Pygame
pygame.init()
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Avatar 2D con Lip-Sync")

# Cargar imágenes del avatar
try:
    face_base = pygame.image.load("face_base.png")  # Cara sin boca
    mouth_closed = pygame.image.load("mouth_closed.png")
    mouth_open = pygame.image.load("mouth_open.png")
except FileNotFoundError:
    print("Error: No se encontraron las imágenes del avatar (face_base.png, mouth_closed.png, mouth_open.png)")
    pygame.quit()
    exit()

# Centrar la imagen de la cara
face_rect = face_base.get_rect()
face_rect.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)  # Centro de la ventana (400, 300)

# Ajustar la posición de la boca relativa a la cara
# Suponemos que la boca debe estar en la parte inferior de la cara
# Ajusta estos valores según el diseño de tu imagen (píxeles desde el centro de la cara)
MOUTH_OFFSET_X = 0  # Desplazamiento horizontal
MOUTH_OFFSET_Y = 50  # Desplazamiento vertical (boca más abajo)
mouth_pos = (face_rect.centerx + MOUTH_OFFSET_X, face_rect.centery + MOUTH_OFFSET_Y)

# Ruta de la carpeta
audio_folder = r"C:\Users\jeisson.rodriguez\Documents\Software-personal\project diverza curiosidad"

# Verificar si la carpeta existe
if not os.path.exists(audio_folder):
    print(f"Error: La carpeta no existe: {audio_folder}")
    pygame.quit()
    exit()

# Listar todos los archivos en la carpeta para depuración
print("Archivos en la carpeta:")
for file in os.listdir(audio_folder):
    print(f" - {file}")

# Buscar archivos MP3 (incluye .mp3 y .MP3)
mp3_files = glob.glob(os.path.join(audio_folder, "*.mp3")) + glob.glob(os.path.join(audio_folder, "*.MP3"))
if not mp3_files:
    print(f"Error: No se encontraron archivos MP3 en {audio_folder}")
    pygame.quit()
    exit()

# Usar el primer archivo MP3 encontrado
audio_path = mp3_files[0]
print(f"Usando archivo MP3: {audio_path}")

# Verificar que el archivo existe
if not os.path.exists(audio_path):
    print(f"Error: No se encuentra el archivo {audio_path}")
    pygame.quit()
    exit()

# Cargar audio MP3 con Librosa
try:
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
except Exception as e:
    print(f"Error al cargar el audio: {e}")
    pygame.quit()
    exit()

# Calcular amplitud del audio por frames
hop_length = 512
frame_rate = sr / hop_length  # Frames por segundo
amplitudes = np.abs(librosa.stft(y, hop_length=hop_length)).mean(axis=0)

# Normalizar amplitudes para mapear a movimiento de boca
amplitudes = amplitudes / np.max(amplitudes)

# Reproducir audio con Pygame
pygame.mixer.init()
pygame.mixer.music.load(audio_path)
pygame.mixer.music.play()

# Bucle principal
running = True
start_time = time.time()
frame_idx = 0

while running and (time.time() - start_time) < duration:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Obtener amplitud actual
    if frame_idx < len(amplitudes):
        amplitude = amplitudes[frame_idx]
    else:
        amplitude = 0

    # Dibujar avatar
    screen.fill((255, 255, 255))  # Fondo blanco
    screen.blit(face_base, face_rect.topleft)  # Dibujar cara centrada

    # Dibujar boca en posición relativa
    mouth_surface = mouth_open if amplitude > 0.5 else mouth_closed
    mouth_rect = mouth_surface.get_rect(center=mouth_pos)  # Centrar boca en la posición calculada
    screen.blit(mouth_surface, mouth_rect.topleft)

    pygame.display.flip()

    # Avanzar al siguiente frame
    frame_idx += 1
    time.sleep(1 / frame_rate)  # Sincronizar con frame rate

# Finalizar
pygame.quit()