import time
import pyautogui
import os
import pytesseract
import random
import mss
import cv2
import numpy as np
from PIL import Image
import re
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import logging
import sys
import pyperclip  # Añadido para manejar el portapapeles

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Carpeta destino para el MP3
DESTINO_MP3 = r"C:\Users\jeisson.rodriguez\Documents\Software-personal\project diverza curiosidad"

# Configuración de PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Función para buscar y hacer clic en imagen
def buscar_y_click(imagen, descripcion, confidence=0.8):
    logger.info(f"Buscando {descripcion} ({imagen})...")
    try:
        ubicacion = pyautogui.locateCenterOnScreen(imagen, confidence=confidence)
        if ubicacion:
            pyautogui.moveTo(ubicacion.x, ubicacion.y, duration=0.5)
            pyautogui.click()
            logger.info(f"Clic en {descripcion}")
            return True
        else:
            logger.warning(f"No se encontró {descripcion}")
            return False
    except Exception as e:
        logger.error(f"Error al hacer clic en {descripcion}: {e}")
        return False

def descargar_voz():
    # Leer el texto de temporal.txt
    temp_file = "temporal.txt"
    if not os.path.exists(temp_file):
        logger.error("No se encontró temporal.txt")
        return False

    with open(temp_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Ignorar la primera línea si es "Transcripción completa:"
        texto = "".join(lines[1:]).strip() if lines and lines[0].startswith("Transcripción completa:") else "".join(lines).strip()

    if not texto:
        logger.error("El archivo temporal.txt está vacío")
        return False

    # Copiar el texto al portapapeles
    pyperclip.copy(texto)

    logger.info("Iniciando descarga de voz...")
    options = ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """
    })

    try:
        driver.get('https://speechma.com/#contact')
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(3)

        if not buscar_y_click('voz.png', 'voz'):
            raise Exception("voz.png no detectado")

        pyautogui.write("salom")
        logger.info("Escrito: salom")

        if not buscar_y_click('salome.png', 'salome'):
            raise Exception("salome.png no detectado")

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        if not buscar_y_click('text.png', 'texto'):
            raise Exception("text.png no detectado")

        time.sleep(5)
        pyautogui.hotkey('ctrl', 'v')
        logger.info(f"Pegado texto: {texto[:50]}...")

        for _ in range(5):
            pyautogui.hotkey('ctrl', '+')
            time.sleep(0.6)

        driver.execute_script("window.scrollTo(0, 200);")
        time.sleep(3)

        REGION = (0, 150, 960, 500)
        max_ciclos = 4
        max_intentos_por_ciclo = 2
        numeros = []

        with mss.mss() as sct:
            for ciclo in range(1, max_ciclos + 1):
                logger.info(f"Ciclo {ciclo}/{max_ciclos} de OCR...")
                for intento in range(1, max_intentos_por_ciclo + 1):
                    logger.info(f"Intento {intento}/{max_intentos_por_ciclo}: Captura con mss...")
                    screenshot = sct.grab(REGION)
                    img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)

                    img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    img_clahe = clahe.apply(img_gray)
                    _, img_bw = cv2.threshold(img_clahe, 150, 255, cv2.THRESH_BINARY)

                    texto_ocr = pytesseract.image_to_string(img_bw, config='--psm 6 -c tessedit_char_whitelist=0123456789')
                    logger.info(f"OCR detectado: {texto_ocr.strip()}")

                    numeros = re.findall(r"\b\d{5}\b", texto_ocr)
                    if numeros:
                        logger.info(f"Número encontrado: {numeros}")
                        break
                    time.sleep(2.5)

                if numeros:
                    break

                if buscar_y_click('reload.png', 'reload'):
                    x = random.randint(100, 300)
                    y = random.randint(100, 200)
                    pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.2))
                    time.sleep(4)

        if not numeros:
            raise Exception("No se encontró ningún número de 5 dígitos")

        pyautogui.hotkey('ctrl', '0')
        time.sleep(2)

        if not buscar_y_click('verificar.png', 'verificación'):
            raise Exception("verificar.png no detectado")

        for numero in numeros:
            logger.info(f"Probando número: {numero}")
            pyautogui.write(numero)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2.5)

            if not buscar_y_click('generar_audio.png', 'generar audio'):
                continue

            x = random.randint(100, 300)
            y = random.randint(100, 200)
            pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.2))
            logger.info("Esperando 40 segundos para la descarga del audio...")
            time.sleep(40)

            if not buscar_y_click('descarga.png', 'descarga'):
                continue

            time.sleep(5)
            downloads_folder = os.path.expanduser("~/Downloads")
            mp3_files = [f for f in os.listdir(downloads_folder) if f.endswith('.mp3')]
            if mp3_files:
                latest_mp3 = max(
                    [os.path.join(downloads_folder, f) for f in mp3_files],
                    key=os.path.getctime
                )
                destino = os.path.join(DESTINO_MP3, os.path.basename(latest_mp3))
                shutil.move(latest_mp3, destino)
                logger.info(f"MP3 movido a: {destino}")
                return True
            else:
                logger.warning("No se encontró archivo MP3 en descargas")
                return False

        return False
    except Exception as e:
        logger.error(f"Error en descargar_voz: {e}")
        return False
    finally:
        driver.quit()
        logger.info("Navegador Chrome cerrado")

if __name__ == "__main__":
    success = descargar_voz()
    sys.exit(0 if success else 1)