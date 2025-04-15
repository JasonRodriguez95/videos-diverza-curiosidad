import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
import logging

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def buscar_url_video():
    logger.info("Iniciando búsqueda de URL de video...")
    print("Iniciando búsqueda de URL de video...", flush=True)
    tema_file = "tema.txt"
    if not os.path.exists(tema_file):
        logger.error("No se encontró tema.txt")
        print("No se encontró tema.txt", flush=True)
        return False

    with open(tema_file, 'r', encoding='utf-8') as f:
        tema = f.read().strip()

    if not tema:
        logger.error("El tema está vacío")
        print("El tema está vacío", flush=True)
        return False

    video_query = f"compilacion o resumen de videos de {tema} en 5 minutos"

    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")  # Ejecutar en modo headless para estabilidad
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = None

    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.youtube.com/")
        time.sleep(2)

        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(video_query)
        search_box.send_keys(Keys.RETURN)
        logger.info(f"Buscando: {video_query}")
        print(f"Buscando: {video_query}", flush=True)

        time.sleep(3)

        video_element = driver.find_element(By.XPATH, '//*[@id="video-title"]')
        video_url = video_element.get_attribute("href")
        if not video_url or not video_url.startswith("https://www.youtube.com/"):
            logger.error("URL inválida obtenida")
            print("URL inválida obtenida", flush=True)
            return False

        logger.info(f"URL del video encontrado: {video_url}")
        print(f"URL del video encontrado: {video_url}", flush=True)

        with open("video_url.txt", 'w', encoding='utf-8') as f:
            f.write(video_url)

        logger.info("video_url.txt generado con éxito")
        print("video_url.txt generado con éxito", flush=True)
        return True

    except Exception as e:
        logger.error(f"Error al buscar URL de video: {e}")
        print(f"Error al buscar URL de video: {e}", flush=True)
        return False
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Navegador Chrome cerrado")
                print("Navegador Chrome cerrado", flush=True)
            except:
                pass

if __name__ == "__main__":
    success = buscar_url_video()
    print(f"buscarurlvideos.py finalizado con éxito: {success}", flush=True)
    sys.exit(0 if success else 1)