import tkinter as tk
from ui import MainApplication
from database import Database

if __name__ == "__main__":
    root = tk.Tk()
    db = Database()  # Usa o arquivo despesas.json por padrão
    app = MainApplication(root, db)
    root.mainloop()
