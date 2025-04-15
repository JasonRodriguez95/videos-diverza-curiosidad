import tkinter as tk
from tkinter import scrolledtext
import subprocess
import sys
import logging
import os

# Forzar codificación UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processing Studio")
        self.root.geometry("900x650")
        self.root.configure(bg="#7B1FA2")
        self.root.resizable(False, False)

        # Estimaciones de tiempo por script (en segundos)
        self.time_estimates = {
            "descargarvoz.py": 30,
            "buscarurlvideos.py": 10,
            "descargarvideos.py": 60,
            "combinar_audios.py": 20,
            "resumen_video.py": 30,
            "anadir_gifs.py": 30
        }
        self.total_time = sum(self.time_estimates.values())
        self.remaining_time = 0
        self.running = False
        self.current_script = None
        self.countdown_active = False
        self.countdown_id = None
        self.flow_started = False

        # Lista ordenada de scripts para el flujo
        self.scripts = [
            ("descargarvoz.py", "descargarvoz"),
            ("buscarurlvideos.py", "buscarurlvideos"),
            ("descargarvideos.py", "descargarvideos"),
            ("combinar_audios.py", "combinar_audios"),
            ("resumen_video.py", "resumen_video"),
            ("anadir_gifs.py", "anadir_gifs")
        ]

        # Interfaz
        self.create_widgets()

        # Iniciar cuenta regresiva automática
        self.start_initial_countdown()

    def create_widgets(self):
        # Título
        title_label = tk.Label(
            self.root,
            text="Video Processing Studio",
            font=("Helvetica", 18, "bold"),
            bg="#7B1FA2",
            fg="#FFFFFF"
        )
        title_label.pack(pady=10)

        # Frame para botones
        button_frame = tk.Frame(self.root, bg="#7B1FA2")
        button_frame.pack(pady=10)

        # Botón para iniciar todo
        self.start_all_button = tk.Button(
            button_frame,
            text="Iniciar Todo",
            command=self.start_all,
            font=("Helvetica", 12),
            bg="#FBC02D",
            fg="#000000",
            activebackground="#F9A825",
            activeforeground="#000000",
            relief="flat",
            padx=10,
            pady=5
        )
        self.start_all_button.grid(row=0, column=0, padx=10, pady=5)

        # Botones individuales
        self.buttons = {
            "descargarvoz.py": tk.Button(
                button_frame,
                text="Descargar Voz",
                command=lambda: self.run_script("descargarvoz.py", "descargarvoz"),
                font=("Helvetica", 12),
                bg="#FBC02D",
                fg="#000000",
                activebackground="#F9A825",
                activeforeground="#000000",
                relief="flat",
                padx=10,
                pady=5
            ),
            "descargarvideos.py": tk.Button(
                button_frame,
                text="Descargar Video",
                command=self.run_download_video,
                font=("Helvetica", 12),
                bg="#FBC02D",
                fg="#000000",
                activebackground="#F9A825",
                activeforeground="#000000",
                relief="flat",
                padx=10,
                pady=5
            ),
            "combinar_audios.py": tk.Button(
                button_frame,
                text="Combinar Audios",
                command=lambda: self.run_script("combinar_audios.py", "combinar_audios"),
                font=("Helvetica", 12),
                bg="#FBC02D",
                fg="#000000",
                activebackground="#F9A825",
                activeforeground="#000000",
                relief="flat",
                padx=10,
                pady=5
            ),
            "resumen_video.py": tk.Button(
                button_frame,
                text="Resumen Video",
                command=lambda: self.run_script("resumen_video.py", "resumen_video"),
                font=("Helvetica", 12),
                bg="#FBC02D",
                fg="#000000",
                activebackground="#F9A825",
                activeforeground="#000000",
                relief="flat",
                padx=10,
                pady=5
            ),
            "anadir_gifs.py": tk.Button(
                button_frame,
                text="Añadir GIFs",
                command=lambda: self.run_script("anadir_gifs.py", "anadir_gifs"),
                font=("Helvetica", 12),
                bg="#FBC02D",
                fg="#000000",
                activebackground="#F9A825",
                activeforeground="#000000",
                relief="flat",
                padx=10,
                pady=5
            )
        }
        for i, button in enumerate(self.buttons.values(), 1):
            button.grid(row=0, column=i, padx=10, pady=5)

        # Label para cuenta regresiva
        self.countdown_label = tk.Label(
            self.root,
            text="Iniciando en: 5",
            font=("Helvetica", 14),
            bg="#7B1FA2",
            fg="#FFFFFF"
        )
        self.countdown_label.pack(pady=10)

        # Área de texto para logs
        log_frame = tk.Frame(self.root, bg="#FFFFFF")
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=100,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state='disabled',
            bg="#FFFFFF",
            fg="#000000",
            bd=2,
            relief="flat"
        )
        self.log_text.pack(fill="both", expand=True)

    def log(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        self.root.update_idletasks()

    def initial_countdown(self, count):
        if not self.countdown_active or self.flow_started:
            return
        if count >= 0:
            self.countdown_label.config(text=f"Iniciando en: {count}")
            self.log(f"[controller] Cuenta: {count}")
            self.root.update_idletasks()
            self.countdown_id = self.root.after(1000, self.initial_countdown, count - 1)
        else:
            self.countdown_active = False
            self.flow_started = True
            self.countdown_label.config(text="Tiempo restante: 00:00")
            self.log("[controller] Cuenta terminada")
            self.start_all()

    def start_initial_countdown(self):
        if not self.flow_started:
            self.countdown_active = True
            self.running = False
            self.log("[controller] Iniciando cuenta de 5 segundos")
            self.initial_countdown(5)

    def stop_countdown(self):
        if self.countdown_active:
            self.countdown_active = False
            if self.countdown_id is not None:
                self.root.after_cancel(self.countdown_id)
                self.countdown_id = None
            self.countdown_label.config(text="Tiempo restante: 00:00")
            self.log("[controller] Cuenta regresiva cancelada")

    def update_countdown(self):
        if not self.running or not self.current_script:
            self.countdown_label.config(text="Tiempo restante: 00:00")
            return
        self.remaining_time = max(0, self.remaining_time - 1)
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.countdown_label.config(text=f"Tiempo restante: {minutes:02d}:{seconds:02d}")
        self.root.after(1000, self.update_countdown)

    def run_script(self, script_name, prefix):
        if self.running:
            self.log(f"[controller] Ya hay un proceso en ejecución")
            return False
        self.running = True
        self.flow_started = True
        self.current_script = script_name
        self.remaining_time = self.time_estimates.get(script_name, 30)
        self.start_all_button.config(state='disabled')
        for button in self.buttons.values():
            button.config(state='disabled')
        self.update_countdown()

        success = False
        try:
            if not os.path.exists(script_name):
                self.log(f"[controller] Error: No se encontró {script_name}")
                logger.error(f"No se encontró {script_name}")
                return False
            self.log(f"[{prefix}] Iniciando {script_name}...")
            logger.info(f"Ejecutando {script_name}...")
            process = subprocess.run(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            if process.stdout:
                for line in process.stdout.splitlines():
                    self.log(f"[{prefix}] {line.strip()}")
            if process.stderr:
                for line in process.stderr.splitlines():
                    self.log(f"[{prefix}] ERROR: {line.strip()}")
            if process.returncode != 0:
                self.log(f"[{prefix}] Error: {script_name} falló")
                logger.error(f"{script_name} falló con código {process.returncode}")
                return False
            self.log(f"[{prefix}] Completado con éxito")
            logger.info(f"{script_name} completado con éxito")
            success = True
            return True
        except Exception as e:
            self.log(f"[{prefix}] Error al ejecutar {script_name}: {e}")
            logger.error(f"Error al ejecutar {script_name}: {e}")
            return False
        finally:
            self.running = False
            self.current_script = None
            self.start_all_button.config(state='normal')
            for button in self.buttons.values():
                button.config(state='normal')
            self.countdown_label.config(text="Tiempo restante: 00:00")
            if success:
                self.run_remaining_scripts(script_name)

    def run_remaining_scripts(self, current_script):
        if self.running:
            self.log(f"[controller] Ya hay un proceso en ejecución, no se puede continuar")
            return
        current_index = next((i for i, (script, _) in enumerate(self.scripts) if script == current_script), -1)
        if current_index == -1:
            self.log("[controller] Script no encontrado")
            return
        if current_index == len(self.scripts) - 1:
            self.log("[controller] Flujo completo")
            return

        self.log(f"[controller] Continuando flujo desde {current_script}...")
        self.remaining_time = sum(self.time_estimates.get(script, 30) for script, _ in self.scripts[current_index + 1:])
        self.update_countdown()

        for script_name, prefix in self.scripts[current_index + 1:]:
            self.log(f"[controller] Iniciando {script_name}...")
            success = self.run_script(script_name, prefix)
            self.remaining_time -= self.time_estimates.get(script_name, 30)
            if not success:
                self.log(f"[controller] Flujo detenido por error en {script_name}")
                break
        else:
            self.log("[controller] ¡Todos los procesos completados!")
            logger.info("Todos los procesos completados")

    def run_download_video(self):
        self.stop_countdown()
        if self.running:
            self.log(f"[controller] Ya hay un proceso en ejecución")
            return
        self.flow_started = True
        self.log("[controller] Iniciando flujo de descarga de video desde buscarurlvideos.py...")
        self.run_script("buscarurlvideos.py", "buscarurlvideos")

    def start_all(self):
        self.stop_countdown()
        self.flow_started = True
        self.log("[controller] Iniciando flujo completo")
        self.run_script(self.scripts[0][0], self.scripts[0][1])

if __name__ == "__main__":
    root = tk.Tk()
    app = ControllerApp(root)
    root.mainloop()