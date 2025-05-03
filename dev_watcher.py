import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, app_process):
        self.app_process = app_process
        self.last_modified = time.time()

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Evitar múltiplas recargas
                self.last_modified = current_time
                print(f"Arquivo modificado: {event.src_path}")
                # Reiniciar o processo
                if self.app_process.poll() is None:  # Se o processo estiver rodando
                    self.app_process.terminate()
                    time.sleep(0.5)
                self.app_process = subprocess.Popen([sys.executable, 'main.py'])

if __name__ == "__main__":
    # Substitua 'main.py' pelo nome do arquivo principal da sua aplicação
    main_file = 'main.py'  # Altere para o nome correto do seu arquivo principal
    
    app_process = subprocess.Popen([sys.executable, main_file])
    event_handler = CodeChangeHandler(app_process)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if app_process.poll() is None:
            app_process.terminate()
    observer.join()
