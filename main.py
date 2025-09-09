import tkinter as tk
from ui import MainApplication
from database import Database

# Instancia o banco de dados e testa a conexão com o PostgreSQL.
# Se a conexão falhar, a classe Database usa o JSON como fallback.
db = Database()
success, message = db.testar_conexao_postgres()
print(message)


if __name__ == "__main__":
    # Cria a janela principal do Tkinter
    root = tk.Tk()
    # Instancia a aplicação principal, passando a janela e o banco de dados
    app = MainApplication(root, db)
    # Inicia o loop principal da aplicação Tkinter
    root.mainloop()