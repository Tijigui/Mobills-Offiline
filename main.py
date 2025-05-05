import tkinter as tk
from ui import MainApplication
from database import Database
from database import Database

db = Database()
success, message = db.testar_conexao_postgres()
print(message)


if __name__ == "__main__":
    root = tk.Tk()
    db = Database()  # Usa o arquivo despesas.json por padrão
    app = MainApplication(root, db)
    root.mainloop()
    