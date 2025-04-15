import time
import pyautogui
import pyperclip
from tkinter import Tk, Label, Entry, Button, Text, END
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
import threading
import os
import subprocess
import sys

# Función para hacer clic en una ubicación específica
def clic_repetido(x, y, veces=20):
    for _ in range(veces):
        pyautogui.click(x, y)
        time.sleep(0.5)

# Función para generar la respuesta
def generar_respuesta():
    tema = entry.get()
    output_text.delete(1.0, END)

    if not tema.strip():
        output_text.insert(END, "⚠️ Por favor ingresa un tema.\n")
        return

    prompt = f"Responde como un influencer llamado Diversa Curiosidad, eres gracioso, crítico y observador. Explica en español sin emojis y excelente ortografica el tema en menos de 1850 caracteres: {tema}"

    # Configuración del navegador Edge
    options = EdgeOptions()
    options.add_argument("--inprivate")
    options.add_argument("--start-maximized")
    driver = webdriver.Edge(options=options)
    driver.get("https://huggingface.co/spaces/yuntian-deng/ChatGPT")
    time.sleep(5)

    # Interacción con la página
    buscar_y_click("i_agree.png", "I Agree")
    time.sleep(2)
    buscar_y_click("permitir.png", "Permitir")
    time.sleep(3)
    
    # Buscar el área de texto AITEXT
    ubicacion = pyautogui.locateCenterOnScreen("aitext.png", confidence=0.8)
    if ubicacion:
        pyautogui.moveTo(ubicacion.x, ubicacion.y, duration=0.5)
        pyautogui.click()
        print(f"✅ Clic en Área de texto (AITEXT)")
        
        pyperclip.copy(prompt)
        pyautogui.hotkey('ctrl', 'v')
        print("✅ Texto pegado en el área de texto.")
        
        threading.Thread(target=clic_repetido, args=(ubicacion.x, ubicacion.y)).start()
        time.sleep(1)
        pyautogui.press('enter')
        print("✅ Enter presionado para enviar.")
    else:
        output_text.insert(END, "⚠️ No se encontró el área de texto (AITEXT).\n")
        driver.quit()
        return

    print("⏳ Esperando respuesta...")
    capturar_respuesta(driver, tema)
    
    # Guardar el tema en tema.txt
    with open("tema.txt", 'w', encoding='utf-8') as f:
        f.write(tema)
    
    # Cerrar Tkinter e iniciar controller.py
    root.destroy()
    subprocess.run([sys.executable, "controller.py"])

def capturar_respuesta(driver, tema):
    output_text.insert(END, "🔍 Capturando respuesta...\n")
    output_text.yview(END)
    
    temp_file_name = "temporal.txt"
    transcripcion_final = ""
    
    try:
        # Esperar 10 segundos después de Enter
        time.sleep(15)
        
        # Hacer clic en la mitad de la página
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(screen_width // 2, screen_height // 2)
        print("✅ Clic en la mitad de la página")
        
        # Seleccionar todo el texto con Ctrl + A
        pyautogui.hotkey('ctrl', 'a')
        print("✅ Seleccionado todo el texto con Ctrl + A")
        
        # Copiar el texto seleccionado con Ctrl + C
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)  # Breve pausa para asegurar que se copie
        print("✅ Texto copiado con Ctrl + C")
        
        # Obtener el texto del portapapeles
        texto_copiado = pyperclip.paste()
        
        # Filtrar el texto no deseado
        texto_no_deseado = [
            "GPT-4.1 mini: Research Preview (Short-Term Availability)",
            "This app provides you full access to GPT-4o mini (128K token limit). You don't need any OPENAI API key.",
            "Chatbot",
            "Type an input and press Enter",
            "Hi there!",
            "Run",
            "Status code from OpenAI server",
            "<Response [200]>",
            "Parameters",
            "Use via APIlogo",
            "logo",
            "Construido con Gradio"
        ]
        
        transcripcion_final = texto_copiado
        # Filtrar el prompt exacto y variaciones
        prompt_exacto = f"Responde como un influencer llamado Diversa Curiosidad, eres gracioso, crítico y observador. Explica en español sin emojis y excelente ortografica el tema en menos de 1850 caracteres: {tema}"
        transcripcion_final = transcripcion_final.replace(prompt_exacto, "").strip()
        # Filtrar variaciones del prompt
        transcripcion_final = transcripcion_final.replace(
            f"Responde como un influencer llamado Diversa Curiosidad, eres gracioso, crítico y observador. Explica en español sin emojis y excelente ortografica el tema en menos de 1850 caracteres: {tema}.", ""
        ).strip()
        transcripcion_final = transcripcion_final.replace(
            f"Toma el rol de un influencer gracioso, crítico, observador y habla sobre datos curiosos de {tema}. Utiliza no más de 2000 caracteres", ""
        ).strip()
        transcripcion_final = transcripcion_final.replace(
            f"Responde como un gracioso, crítico y observador. Explica en español el tema en menos de 2000 caracteres: {tema}", ""
        ).strip()
        
        # Filtrar el resto del texto no deseado
        for frase in texto_no_deseado:
            transcripcion_final = transcripcion_final.replace(frase, "").strip()
        
        # Limpiar líneas vacías y espacios múltiples
        transcripcion_final = "\n".join(line for line in transcripcion_final.splitlines() if line.strip())
        
        if not transcripcion_final:
            transcripcion_final = "⚠️ No se encontró texto válido después de filtrar."
        
        print(f"✅ Texto filtrado: {transcripcion_final[:50]}...")
        
    except Exception as e:
        transcripcion_final = f"⚠️ Error al capturar el texto: {str(e)[:100]}..."
        print(transcripcion_final)
    
    # Guardar la transcripción en temporal.txt sin "Transcripción completa:"
    with open(temp_file_name, 'w', encoding='utf-8') as f:
        f.write(transcripcion_final)
    
    # Mostrar en la interfaz
    output_text.delete(1.0, END)
    output_text.insert(END, f"📝 Respuesta:\n{transcripcion_final}\n")
    output_text.yview(END)
    
    driver.quit()

# Función para copiar el texto al portapapeles
def copiar_texto():
    texto = output_text.get(1.0, END).strip()
    if texto.startswith("📝 Respuesta:"):
        texto = "\n".join(line for line in texto.splitlines()[1:] if line.strip())
    
    pyperclip.copy(texto)
    print("✅ Texto copiado al portapapeles.")
    output_text.insert(END, "✅ Texto copiado al portapapeles.\n")
    output_text.yview(END)

# Función para buscar y hacer clic en la imagen
def buscar_y_click(imagen, descripcion):
    print(f"🔍 Buscando {descripcion}...")
    try:
        ubicacion = pyautogui.locateCenterOnScreen(imagen, confidence=0.8)
        if ubicacion:
            pyautogui.moveTo(ubicacion.x, ubicacion.y, duration=0.5)
            pyautogui.click()
            print(f"✅ Clic en {descripcion}")
        else:
            print(f"⚠️ No se encontró {descripcion}")
    except Exception as e:
        print(f"⚠️ Error al hacer clic en {descripcion}: {e}")

# Interfaz gráfica
root = Tk()
root.title("Chatbot Influencer - Español")
root.geometry("650x450")

Label(root, text="¿Sobre qué deseas hablar?").pack(pady=10)
entry = Entry(root, width=60)
entry.pack(pady=5)

Button(root, text="Generar Respuesta", command=generar_respuesta).pack(pady=10)

output_text = Text(root, height=15, wrap="word")
output_text.pack(padx=10, pady=10, fill="both", expand=True)

Button(root, text="Copiar Respuesta", command=copiar_texto).pack(pady=10)

root.mainloop()