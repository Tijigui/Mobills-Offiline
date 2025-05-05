import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from tkcalendar import DateEntry
from database import Database, COLORS, ACCOUNT_TYPES
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from collections import defaultdict
from contas import mostrar_contas
from dashboard import mostrar_dashboard
from transacoes import TransacoesModernUI
from cartoes_creditos import mostrar_cartoes_credito
# Removida a importação do módulo configuracoes que não existe

CONFIG_FILE = "config.json"

BANKS = [
    "Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau",
    "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank"
]

class MainApplication:
    def __init__(self, master, database):
        self.master = master
        self.master.title("Mobills Offline")

        # Criar barra de menu
        menu_bar = tk.Menu(master)
        master.config(menu=menu_bar)
        
        # Criar menu Arquivo
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Sair", command=self.on_closing)

        # Tentar maximizar a janela
        try:
            self.master.state('zoomed')
        except:
            # Fallback para sistemas que não suportam 'zoomed'
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            self.master.geometry(f"{screen_width}x{screen_height}+0+0")

        self.database = database
        self.sidebar_visible = True
        self.sidebar_frame = None
        self.icon_bar = None
        self.toggle_btn = None
        self.transacoes_ui = None  # Referência para a interface de transações

        # Tratar evento de fechamento da janela
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.load_config()

        self.create_sidebar()
        self.create_main_content()

        self.show_dashboard()

    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.sidebar_visible = config.get("sidebar_visible", True)
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
                self.sidebar_visible = True
        else:
            # Arquivo de configuração não existe, usar valores padrão
            self.sidebar_visible = True

    def save_config(self):
        """Salva configurações no arquivo JSON"""
        config = {
            "sidebar_visible": self.sidebar_visible
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

    def create_sidebar(self):
        """Cria a barra lateral ou a barra de ícones, dependendo da configuração"""
        # Limpar componentes anteriores se existirem
        if self.sidebar_frame:
            self.sidebar_frame.destroy()
            self.sidebar_frame = None

        if self.icon_bar:
            self.icon_bar.destroy()
            self.icon_bar = None

        if self.toggle_btn:
            self.toggle_btn.destroy()
            self.toggle_btn = None

        if self.sidebar_visible:
            # Criar barra lateral completa
            self.sidebar_frame = tk.Frame(self.master, bg="#f4f4f4", width=260)
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
            self.sidebar_frame.pack_propagate(False)  # Manter largura fixa

            toggle_frame = tk.Frame(self.sidebar_frame, bg="#f4f4f4")
            toggle_frame.pack(fill=tk.X, anchor="ne")

            self.toggle_btn = tk.Button(toggle_frame, text="←", command=self.toggle_sidebar, 
                                       width=2, bg="#e0e0e0", relief=tk.GROOVE)
            self.toggle_btn.pack(anchor="ne", padx=5, pady=5)

            # Título do menu
            title_frame = tk.Frame(self.sidebar_frame, bg="#f4f4f4")
            title_frame.pack(fill=tk.X, pady=10)
            
            tk.Label(title_frame, text="Menu", bg="#f4f4f4", 
                    font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=10)

            # Opções do menu
            options = [
                ("🏠 Dashboard", self.show_dashboard),
                ("💰 Contas", self.show_accounts),
                ("📑 Transações", self.show_transactions),
                ("💳 Cartões de Crédito", self.show_credit_cards),
                ("⚙️ Configurações", self.show_settings),
                ("🚪 Sair", self.on_closing)
            ]

            # Frame para os botões do menu
            buttons_frame = tk.Frame(self.sidebar_frame, bg="#f4f4f4")
            buttons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            for label, command in options:
                btn = tk.Button(buttons_frame, text=label, command=command,
                               width=22, height=2, bg="#ffffff", relief=tk.GROOVE, 
                               anchor="w", font=("Arial", 10))
                btn.pack(pady=3, fill=tk.X)
                
                # Adicionar hover effect
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#f0f0f0"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#ffffff"))

        else:
            # Criar barra de ícones compacta
            self.icon_bar = tk.Frame(self.master, bg="#e0e0e0", width=60)
            self.icon_bar.pack(side=tk.LEFT, fill=tk.Y)
            self.icon_bar.pack_propagate(False)  # Manter largura fixa

            self.toggle_btn = tk.Button(self.icon_bar, text="→", command=self.toggle_sidebar, 
                                       width=2, bg="#d0d0d0", relief=tk.GROOVE)
            self.toggle_btn.pack(anchor="ne", padx=5, pady=5)

            options = [
                ("🏠", self.show_dashboard, "Dashboard"),
                ("💰", self.show_accounts, "Contas"),
                ("📑", self.show_transactions, "Transações"),
                ("💳", self.show_credit_cards, "Cartões de Crédito"),
                ("⚙️", self.show_settings, "Configurações"),
                ("🚪", self.on_closing, "Sair")
            ]

            for icon, command, tooltip in options:
                btn = tk.Button(self.icon_bar, text=icon, command=command, 
                               width=1, height=1, bg="#ffffff", font=("Arial", 16),
                               relief=tk.GROOVE)
                btn.pack(pady=6, padx=5, fill=tk.X)
                
                # Adicionar hover effect
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#f0f0f0"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#ffffff"))
                
                # Criar tooltip
                self.create_tooltip(btn, tooltip)

    def toggle_sidebar(self):
        """Alterna entre a barra lateral e a barra de ícones"""
        self.sidebar_visible = not self.sidebar_visible
        self.create_sidebar()
        self.save_config()

    def create_tooltip(self, widget, text):
        """Cria uma tooltip para um widget"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.withdraw()
        label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 30
            y += widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def create_main_content(self):
        """Cria o frame principal para exibir o conteúdo"""
        self.main_content = tk.Frame(self.master, bg="#ffffff")
        self.main_content.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def clear_main_content(self):
        """Limpa todos os widgets do frame principal"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Exibe o dashboard"""
        self.clear_main_content()
        mostrar_dashboard(self.main_content, self.database)

    def show_accounts(self):
        """Exibe a tela de contas"""
        self.clear_main_content()
        mostrar_contas(self.main_content, self.database)

    def show_transactions(self):
        """Exibe a tela de transações"""
        self.clear_main_content()
        
        try:
            # Criar a interface de transações diretamente no main_content
            self.transacoes_ui = TransacoesModernUI(self.main_content, self.database)
            
            # IMPORTANTE: Empacotar o frame TransacoesModernUI
            self.transacoes_ui.pack(fill=tk.BOTH, expand=True)
            
            print("Interface de transações carregada com sucesso")
        except Exception as e:
            # Exibir mensagem de erro no frame principal
            error_label = tk.Label(
                self.main_content, 
                text=f"Erro ao carregar transações: {str(e)}", 
                fg="red", 
                font=("Arial", 12)
            )
            error_label.pack(pady=20)
            print(f"Erro ao carregar transações: {e}")
            import traceback
            traceback.print_exc()


    def show_credit_cards(self):
        """Exibe a tela de cartões de crédito"""
        self.clear_main_content()
        mostrar_cartoes_credito(self.main_content, self.database)

    def show_settings(self):
        """Exibe uma mensagem temporária na tela de configurações"""
        self.clear_main_content()
        
        # Título da página
        tk.Label(self.main_content, text="Configurações", font=("Arial", 24), bg="#ffffff").pack(pady=20)
        
        # Mensagem temporária
        mensagem = "Módulo de configurações em desenvolvimento."
        tk.Label(self.main_content, text=mensagem, font=("Arial", 12), bg="#ffffff").pack(pady=40)

    def on_closing(self):
        """Trata evento de fechamento da janela"""
        try:
            # Parar quaisquer atualizações periódicas
            if hasattr(self, 'atualizacao_id'):
                self.master.after_cancel(self.atualizacao_id)
            
            # Salvar configurações
            self.save_config()
            
            # Salvar dados do banco de dados
            self.database.salvar_dados()
            
            # Perguntar ao usuário se realmente deseja sair
            if messagebox.askokcancel("Sair", "Deseja realmente sair do Mobills Offline?"):
                # Destruir a janela principal
                self.master.destroy()
        except Exception as e:
            print(f"Erro ao fechar aplicação: {e}")
            # Em caso de erro, tenta forçar o fechamento
            self.master.destroy()
