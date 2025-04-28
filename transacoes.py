import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import os
from PIL import Image, ImageTk
import io
import base64
import requests
from tkinter.font import Font

class TransacoesModernUI:
    """Classe responsável pela interface moderna do usuário para transações"""
    def __init__(self, root, database=None):
        self.root = root
        self.database = database
        
        # Verifica se root é uma janela (Tk ou Toplevel)
        self.is_window = hasattr(self.root, 'title')
        
        if self.is_window:
            self.root.title("")  # Título vazio
            # Configurações específicas para janela
            self.root.geometry("1200x700")
            self.root.minsize(800, 600)
        
        # Configuração da interface
        self.root.configure(bg="#1e1e1e")
        
        # Cores do tema escuro
        self.colors = {
            "bg_dark": "#1e1e1e",
            "bg_medium": "#2d2d2d",
            "bg_light": "#3d3d3d",
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "accent": "#8a56ff",
            "green": "#4CAF50",
            "red": "#F44336",
            "blue": "#2196F3",
            "teal": "#26a69a"
        }
        
        # Fontes personalizadas
        self.font_regular = Font(family="Segoe UI", size=10)
        self.font_bold = Font(family="Segoe UI", size=10, weight="bold")
        self.font_title = Font(family="Segoe UI", size=14, weight="bold")
        self.font_subtitle = Font(family="Segoe UI", size=12, weight="bold")
        
        # Configurar estilo para widgets
        self._configurar_estilo()
        
        # Criar layout principal
        self._criar_layout()
        
        # Carregar dados iniciais
        self._carregar_dados()
    
    def _configurar_estilo(self):
        """Configura o estilo dos widgets ttk"""
        style = ttk.Style()
        style.theme_use('default')
        
        # Configuração para Treeview (tabela)
        style.configure("Treeview", 
                        background=self.colors["bg_medium"],
                        foreground=self.colors["text"],
                        fieldbackground=self.colors["bg_medium"],
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        background=self.colors["bg_light"],
                        foreground=self.colors["text"],
                        relief="flat")
        
        style.map("Treeview.Heading",
                  background=[('active', self.colors["bg_light"])])
        
        style.map("Treeview",
                  background=[('selected', self.colors["accent"])],
                  foreground=[('selected', self.colors["text"])])
        
        # Configuração para botões
        style.configure("Accent.TButton", 
                        background=self.colors["accent"],
                        foreground=self.colors["text"])
        
        style.map("Accent.TButton",
                  background=[('active', self.colors["accent"])])
    
    def _criar_layout(self):
        """Cria o layout principal da aplicação"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg_dark"])
        self.main_frame.pack(fill="both", expand=True)
        
        # Container principal para conteúdo
        self.content_container = tk.Frame(self.main_frame, bg=self.colors["bg_dark"])
        self.content_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para área principal (esquerda) e área de resumo (direita)
        self.split_container = tk.Frame(self.content_container, bg=self.colors["bg_dark"])
        self.split_container.pack(fill="both", expand=True)
        
        # Área principal (esquerda)
        self.main_area = tk.Frame(self.split_container, bg=self.colors["bg_dark"])
        self.main_area.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Área de resumo (direita)
        self.summary_area = tk.Frame(self.split_container, bg=self.colors["bg_dark"], width=300)
        self.summary_area.pack(side="right", fill="y")
        self.summary_area.pack_propagate(False)  # Mantém a largura definida
        
        # Botão de Transações na parte superior da área principal
        self._criar_botao_transacoes()
        
        # Tabela de transações logo abaixo do botão
        self._criar_tabela_transacoes()
        
        # Área de resumo (lado direito)
        self._criar_area_resumo()
    
    def _criar_botao_transacoes(self):
        """Cria o botão de Transações na parte superior"""
        # Frame para o botão
        btn_frame = tk.Frame(self.main_area, bg=self.colors["bg_dark"])
        btn_frame.pack(fill="x", pady=(0, 10))
        
        # Botão de Transações (destacado)
        transacoes_btn = tk.Button(btn_frame, text="Transações",
                                  bg=self.colors["accent"],
                                  fg=self.colors["text"],
                                  font=self.font_regular,
                                  relief="flat",
                                  borderwidth=0,
                                  padx=15,
                                  pady=8,
                                  cursor="hand2")
        transacoes_btn.pack(side="left")
        
        # Arredondar os cantos do botão (simulação)
        self._arredondar_widget(transacoes_btn)
    
    def _criar_tabela_transacoes(self):
        """Cria a tabela de transações"""
        # Frame para a tabela com fundo diferente
        table_outer_frame = tk.Frame(self.main_area, bg=self.colors["bg_medium"])
        table_outer_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Arredondar os cantos do frame externo
        self._arredondar_widget(table_outer_frame)
        
        # Padding interno
        table_frame = tk.Frame(table_outer_frame, bg=self.colors["bg_medium"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Barra de navegação do mês
        self._criar_navegacao_mes(table_frame)
        
        # Cabeçalho da tabela
        headers = ["Situação", "Data", "Descrição", "Categoria", "Conta", "Valor", "Ações"]
        header_frame = tk.Frame(table_frame, bg=self.colors["bg_light"])
        header_frame.pack(fill="x", pady=(20, 0))
        
        # Larguras das colunas
        widths = [80, 100, 200, 150, 150, 100, 80]
        
        # Criar cabeçalhos
        for i, header in enumerate(headers):
            header_label = tk.Label(header_frame, text=header, 
                                   bg=self.colors["bg_light"],
                                   fg=self.colors["text_secondary"],
                                   font=self.font_bold,
                                   width=widths[i] // 10)  # Aproximação de pixels para caracteres
            header_label.grid(row=0, column=i, sticky="w", padx=5, pady=10)
        
        # Área de conteúdo da tabela
        table_content = tk.Frame(table_frame, bg=self.colors["bg_medium"])
        table_content.pack(fill="both", expand=True)
        
        # Mensagem de "Nenhum resultado" com ilustração
        empty_frame = tk.Frame(table_content, bg=self.colors["bg_medium"])
        empty_frame.pack(expand=True, fill="both")
        
        # Aqui seria ideal ter a imagem da ilustração
        # Como não temos a imagem exata, vamos usar um placeholder
        empty_label = tk.Label(empty_frame, text="📊", 
                              font=("Arial", 48),
                              bg=self.colors["bg_medium"],
                              fg=self.colors["accent"])
        empty_label.pack(pady=(50, 10))
        
        empty_text = tk.Label(empty_frame, text="Salve meu bom", 
                             font=self.font_subtitle,
                             bg=self.colors["bg_medium"],
                             fg=self.colors["text_secondary"])
        empty_text.pack()
    
    def _criar_navegacao_mes(self, parent_frame):
        """Cria a barra de navegação do mês"""
        nav_frame = tk.Frame(parent_frame, bg=self.colors["bg_medium"], height=50)
        nav_frame.pack(fill="x")
        
        # Botão anterior
        prev_btn = tk.Button(nav_frame, text="<", bg=self.colors["bg_medium"],
                            fg=self.colors["accent"], font=self.font_bold,
                            relief="flat", borderwidth=0, cursor="hand2")
        prev_btn.pack(side="left")
        
        # Mês atual (em destaque)
        month_frame = tk.Frame(nav_frame, bg=self.colors["accent"], padx=15, pady=5)
        month_frame.pack(side="left", expand=True)
        
        # Arredondar os cantos do frame do mês
        self._arredondar_widget(month_frame)
        
        month_label = tk.Label(month_frame, text="Abril 2025",
                              bg=self.colors["accent"], fg=self.colors["text"],
                              font=self.font_regular)
        month_label.pack()
        
        # Botão próximo
        next_btn = tk.Button(nav_frame, text=">", bg=self.colors["bg_medium"],
                            fg=self.colors["accent"], font=self.font_bold,
                            relief="flat", borderwidth=0, cursor="hand2")
        next_btn.pack(side="right")
    
    def _criar_area_resumo(self):
        """Cria a área de resumo financeiro (lado direito)"""
        # Cards de resumo
        self._criar_card_resumo("Saldo atual", "R$ -144,78", self.colors["blue"], "💰")
        self._criar_card_resumo("Receitas", "R$ 0,00", self.colors["green"], "⬆️")
        self._criar_card_resumo("Despesas", "R$ 0,00", self.colors["red"], "⬇️")
        self._criar_card_resumo("Balanço mensal", "R$ 0,00", self.colors["teal"], "⚖️")
    
    def _criar_card_resumo(self, titulo, valor, cor_icone, emoji):
        """Cria um card de resumo financeiro"""
        card_frame = tk.Frame(self.summary_area, bg=self.colors["bg_medium"], padx=15, pady=15)
        card_frame.pack(fill="x", pady=10, padx=10)
        
        # Arredondar os cantos do card
        self._arredondar_widget(card_frame)
        
        # Layout do card
        info_frame = tk.Frame(card_frame, bg=self.colors["bg_medium"])
        info_frame.pack(side="left", fill="both", expand=True)
        
        # Título do card
        title_label = tk.Label(info_frame, text=titulo, 
                              font=self.font_regular,
                              bg=self.colors["bg_medium"],
                              fg=self.colors["text_secondary"])
        title_label.pack(anchor="w")
        
        # Valor
        value_label = tk.Label(info_frame, text=valor, 
                              font=self.font_subtitle,
                              bg=self.colors["bg_medium"],
                              fg=self.colors["text"])
        value_label.pack(anchor="w", pady=(5, 0))
        
        # Ícone (círculo colorido com emoji)
        icon_frame = tk.Frame(card_frame, bg=self.colors["bg_medium"])
        icon_frame.pack(side="right", padx=(10, 0))
        
        icon_canvas = tk.Canvas(icon_frame, width=40, height=40, 
                               bg=self.colors["bg_medium"],
                               highlightthickness=0)
        icon_canvas.pack()
        
        # Círculo colorido
        icon_canvas.create_oval(5, 5, 35, 35, fill=cor_icone, outline="")
        
        # Emoji
        icon_canvas.create_text(20, 20, text=emoji, font=("Arial", 14))
    
    def _arredondar_widget(self, widget, radius=10):
        """Simula cantos arredondados em um widget"""
        # Nota: Esta é uma simulação visual. Em uma aplicação real,
        # seria melhor usar uma biblioteca como customtkinter ou
        # implementar uma solução mais robusta.
        widget.config(highlightbackground=widget["bg"], 
                     highlightcolor=widget["bg"],
                     highlightthickness=1,
                     bd=0)
    
    def _carregar_dados(self):
        """Carrega os dados iniciais"""
        # Aqui você conectaria com seu controller para buscar dados reais
        pass
