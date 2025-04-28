import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import defaultdict
import calendar
from datetime import datetime, timedelta

# Definição de cores e estilos consistentes
PRIMARY_COLOR = "#3498db"
ACCENT_COLOR = "#2ecc71"
DANGER_COLOR = "#e74c3c"
BG_COLOR = "#f9f9f9"
CARD_BG = "#ffffff"
TEXT_COLOR = "#333333"
LIGHT_TEXT = "#7f8c8d"

def mostrar_dashboard(main_content, database):
    """Função principal para mostrar o dashboard"""
    for widget in main_content.winfo_children():
        widget.destroy()
    
    # Configurar o estilo geral
    main_content.configure(bg=BG_COLOR)
    
    # Cabeçalho com título e data
    header_frame = tk.Frame(main_content, bg=BG_COLOR)
    header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
    
    tk.Label(header_frame, text="Dashboard", font=("Helvetica", 26, "bold"), 
             bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
    
    hoje = datetime.now()
    data_str = hoje.strftime("%d de %B de %Y")
    tk.Label(header_frame, text=data_str, font=("Helvetica", 12), 
             bg=BG_COLOR, fg=LIGHT_TEXT).pack(side=tk.RIGHT, padx=10)
    
    # Criar frame principal com scroll se necessário
    canvas = tk.Canvas(main_content, bg=BG_COLOR)
    scrollbar = ttk.Scrollbar(main_content, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_COLOR)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    # Criar contêiner principal
    dashboard_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
    dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Adicionar cards de resumo no topo
    criar_cards_resumo(dashboard_frame, database)
    
    # Dividir em duas colunas
    columns_frame = tk.Frame(dashboard_frame, bg=BG_COLOR)
    columns_frame.pack(fill=tk.BOTH, expand=True, pady=15)
    
    left_frame = tk.Frame(columns_frame, bg=BG_COLOR)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
    
    right_frame = tk.Frame(columns_frame, bg=BG_COLOR)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
    
    # Configurar colunas para serem responsivas
    columns_frame.columnconfigure(0, weight=1)
    columns_frame.columnconfigure(1, weight=1)
    
    # Adicionar widgets ao dashboard
    criar_resumo_mensal(left_frame, database)
    criar_grafico_categorias(right_frame, database)
    criar_resumo_contas(left_frame, database)
    criar_ultimas_transacoes(right_frame, database)

def criar_cards_resumo(parent, database):
    """Cria cards com resumos rápidos de informações importantes"""
    cards_frame = tk.Frame(parent, bg=BG_COLOR)
    cards_frame.pack(fill=tk.X, pady=10)
    
    # Obter dados para os cards
    hoje = datetime.now()
    primeiro_dia_mes = hoje.replace(day=1).strftime("%d/%m/%Y")
    ultimo_dia_mes = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).strftime("%d/%m/%Y")
    
    # Despesas do mês
    despesas_mes = database.listar_despesas(data_inicio=primeiro_dia_mes, data_fim=ultimo_dia_mes)
    total_despesas_mes = sum(d['valor'] for d in despesas_mes)
    
    # Todas as despesas
    todas_despesas = database.listar_despesas()
    total_todas_despesas = sum(d['valor'] for d in todas_despesas)
    
    # Contas
    contas = database.listar_contas()
    saldo_total = sum(conta.get('saldo', 0) for conta in contas)
    
    # Criar os cards
    criar_card(cards_frame, "Despesas do Mês", f"R$ {total_despesas_mes:.2f}", DANGER_COLOR)
    criar_card(cards_frame, "Saldo Total", f"R$ {saldo_total:.2f}", ACCENT_COLOR)
    criar_card(cards_frame, "Total de Despesas", f"R$ {total_todas_despesas:.2f}", PRIMARY_COLOR)
    criar_card(cards_frame, "Transações", f"{len(todas_despesas)}", "#9b59b6")

def criar_card(parent, titulo, valor, cor):
    """Cria um card individual com informação resumida"""
    card = tk.Frame(parent, bg=CARD_BG, relief=tk.RAISED, bd=0)
    card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    # Adicionar borda superior colorida
    borda = tk.Frame(card, bg=cor, height=4)
    borda.pack(fill=tk.X)
    
    # Conteúdo do card
    conteudo = tk.Frame(card, bg=CARD_BG, padx=15, pady=15)
    conteudo.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(conteudo, text=titulo, font=("Helvetica", 12), 
             bg=CARD_BG, fg=LIGHT_TEXT).pack(anchor=tk.W)
    
    tk.Label(conteudo, text=valor, font=("Helvetica", 22, "bold"), 
             bg=CARD_BG, fg=TEXT_COLOR).pack(anchor=tk.W, pady=(5, 0))

def criar_resumo_mensal(parent, database):
    """Cria um resumo das despesas do mês atual"""
    frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief=tk.SOLID)
    frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    header = tk.Frame(frame, bg=PRIMARY_COLOR, padx=15, pady=10)
    header.pack(fill=tk.X)
    
    tk.Label(header, text="Evolução de Despesas", font=("Helvetica", 14, "bold"), 
             bg=PRIMARY_COLOR, fg="white").pack(anchor=tk.W)
    
    content = tk.Frame(frame, bg=CARD_BG, padx=15, pady=15)
    content.pack(fill=tk.BOTH, expand=True)
    
    # Obter mês atual
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1).strftime("%d/%m/%Y")
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).strftime("%d/%m/%Y")
    
    # Buscar despesas do mês
    despesas = database.listar_despesas(data_inicio=primeiro_dia, data_fim=ultimo_dia)
    total_despesas = sum(d['valor'] for d in despesas)
    
    # Mostrar total
    tk.Label(content, text=f"Total de despesas: R$ {total_despesas:.2f}", 
             font=("Helvetica", 12, "bold"), bg=CARD_BG, fg=DANGER_COLOR).pack(anchor=tk.W, pady=(0, 10))
    
    # Criar gráfico de evolução diária
    fig = Figure(figsize=(5, 3), dpi=100)
    ax = fig.add_subplot(111)
    
    # Agrupar por dia
    despesas_por_dia = defaultdict(float)
    for d in despesas:
        data = datetime.strptime(d['data'], "%d/%m/%Y")
        despesas_por_dia[data.day] += d['valor']
    
    # Criar dados para o gráfico
    dias = list(range(1, hoje.day + 1))
    valores = [despesas_por_dia.get(dia, 0) for dia in dias]
    
    # Plotar gráfico
    ax.plot(dias, valores, marker='o', color=PRIMARY_COLOR, linewidth=2)
    ax.fill_between(dias, valores, color=PRIMARY_COLOR, alpha=0.2)
    ax.set_title('Evolução de Despesas no Mês', fontsize=12)
    ax.set_xlabel('Dia')
    ax.set_ylabel('Valor (R$)')
    ax.grid(True, linestyle='--', alpha=0.7)
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

def criar_grafico_categorias(parent, database):
    """Cria um gráfico de pizza com as categorias de despesas"""
    frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief=tk.SOLID)
    frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    header = tk.Frame(frame, bg=ACCENT_COLOR, padx=15, pady=10)
    header.pack(fill=tk.X)
    
    tk.Label(header, text="Despesas por Categoria", font=("Helvetica", 14, "bold"), 
             bg=ACCENT_COLOR, fg="white").pack(anchor=tk.W)
    
    content = tk.Frame(frame, bg=CARD_BG, padx=15, pady=15)
    content.pack(fill=tk.BOTH, expand=True)
    
    # Obter mês atual
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1).strftime("%d/%m/%Y")
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).strftime("%d/%m/%Y")
    
    # Buscar despesas do mês
    despesas = database.listar_despesas(data_inicio=primeiro_dia, data_fim=ultimo_dia)
    
    # Agrupar por tag
    por_tag = defaultdict(float)
    for d in despesas:
        por_tag[d['tag']] += d['valor']
    
    if not por_tag:
        tk.Label(content, text="Sem dados para exibir", bg=CARD_BG, fg=LIGHT_TEXT,
                font=("Helvetica", 12)).pack(pady=50)
        return
    
    # Criar gráfico
    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    
    # Ordenar por valor para melhor visualização
    labels = []
    sizes = []
    for tag, valor in sorted(por_tag.items(), key=lambda x: x[1], reverse=True):
        labels.append(tag)
        sizes.append(valor)
    
    # Cores para o gráfico
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(labels)))
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=90,
        colors=colors,
        shadow=False,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )
    
    # Personalizar textos
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
    
    for text in texts:
        text.set_fontsize(9)
    
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=content)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

def criar_resumo_contas(parent, database):
    """Cria um resumo das contas bancárias"""
    frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief=tk.SOLID)
    frame.pack(fill=tk.BOTH, pady=10)
    
    header = tk.Frame(frame, bg="#9b59b6", padx=15, pady=10)
    header.pack(fill=tk.X)
    
    tk.Label(header, text="Resumo de Contas", font=("Helvetica", 14, "bold"), 
             bg="#9b59b6", fg="white").pack(anchor=tk.W)
    
    content = tk.Frame(frame, bg=CARD_BG, padx=15, pady=15)
    content.pack(fill=tk.BOTH, expand=True)
    
    contas = database.listar_contas()
    
    if not contas:
        tk.Label(content, text="Nenhuma conta cadastrada", bg=CARD_BG, fg=LIGHT_TEXT,
                font=("Helvetica", 12)).pack(pady=20)
        return
    
    # Calcular saldo total
    saldo_total = sum(conta.get('saldo', 0) for conta in contas)
    
    tk.Label(content, text=f"Saldo Total: R$ {saldo_total:.2f}", 
             font=("Helvetica", 14, "bold"), bg=CARD_BG, fg=ACCENT_COLOR).pack(anchor=tk.W, pady=(0, 15))
    
    # Criar cabeçalho da lista
    header_frame = tk.Frame(content, bg=CARD_BG)
    header_frame.pack(fill=tk.X, pady=(0, 5))
    
    tk.Label(header_frame, text="Conta", font=("Helvetica", 10, "bold"), 
             bg=CARD_BG, width=20, anchor="w").pack(side=tk.LEFT)
    
    tk.Label(header_frame, text="Saldo", font=("Helvetica", 10, "bold"), 
             bg=CARD_BG, width=15, anchor="e").pack(side=tk.RIGHT)
    
    # Separador
    separator = ttk.Separator(content, orient='horizontal')
    separator.pack(fill=tk.X, pady=5)
    
    # Listar contas
    for i, conta in enumerate(contas):
        conta_frame = tk.Frame(content, bg=CARD_BG)
        conta_frame.pack(fill=tk.X, pady=5)
        
        cor = conta.get('cor', PRIMARY_COLOR)
        nome = conta.get('nome', 'Desconhecido')
        saldo = conta.get('saldo', 0)
        
        # Indicador de cor
        cor_indicator = tk.Frame(conta_frame, bg=cor, width=5, height=20)
        cor_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # Nome da conta
        tk.Label(conta_frame, text=nome, bg=CARD_BG, width=20, anchor="w",
                font=("Helvetica", 10)).pack(side=tk.LEFT)
        
        # Saldo
        saldo_color = ACCENT_COLOR if saldo >= 0 else DANGER_COLOR
        tk.Label(conta_frame, text=f"R$ {saldo:.2f}", bg=CARD_BG, fg=saldo_color,
                font=("Helvetica", 10, "bold"), width=15, anchor="e").pack(side=tk.RIGHT)
        
        # Adicionar separador entre contas
        if i < len(contas) - 1:
            ttk.Separator(content, orient='horizontal').pack(fill=tk.X, pady=5)

def criar_ultimas_transacoes(parent, database):
    """Mostra as últimas transações"""
    frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief=tk.SOLID)
    frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    header = tk.Frame(frame, bg=PRIMARY_COLOR, padx=15, pady=10)
    header.pack(fill=tk.X)
    
    tk.Label(header, text="Últimas Transações", font=("Helvetica", 14, "bold"), 
             bg=PRIMARY_COLOR, fg="white").pack(anchor=tk.W)
    
    content = tk.Frame(frame, bg=CARD_BG, padx=15, pady=15)
    content.pack(fill=tk.BOTH, expand=True)
    
    # Buscar últimas 10 transações
    despesas = database.listar_despesas(ordenar_por="data")[-10:]
    
    if not despesas:
        tk.Label(content, text="Nenhuma transação encontrada", bg=CARD_BG, fg=LIGHT_TEXT,
                font=("Helvetica", 12)).pack(pady=50)
        return
    
    # Criar cabeçalho da tabela
    header_frame = tk.Frame(content, bg=CARD_BG)
    header_frame.pack(fill=tk.X, pady=(0, 5))
    
    tk.Label(header_frame, text="Data", font=("Helvetica", 10, "bold"), 
             bg=CARD_BG, width=10).pack(side=tk.LEFT, padx=5)
    
    tk.Label(header_frame, text="Descrição", font=("Helvetica", 10, "bold"), 
             bg=CARD_BG, width=25).pack(side=tk.LEFT, padx=5)
    
    tk.Label(header_frame, text="Valor", font=("Helvetica", 10, "bold"), 
             bg=CARD_BG, width=10).pack(side=tk.RIGHT, padx=5)
    
    # Separador
    separator = ttk.Separator(content, orient='horizontal')
    separator.pack(fill=tk.X, pady=5)
    
    # Criar tabela de transações
    table_frame = tk.Frame(content, bg=CARD_BG)
    table_frame.pack(fill=tk.BOTH, expand=True)
    
    # Adicionar transações à tabela
    for i, d in enumerate(reversed(despesas)):  # Mostrar as mais recentes primeiro
        row_bg = "#f5f5f5" if i % 2 == 0 else CARD_BG
        
        row = tk.Frame(table_frame, bg=row_bg)
        row.pack(fill=tk.X, pady=1)
        
        # Data
        tk.Label(row, text=d['data'], bg=row_bg, width=10,
                font=("Helvetica", 9)).pack(side=tk.LEFT, padx=5)
        
        # Descrição
        tk.Label(row, text=d['descricao'], bg=row_bg, width=25, anchor="w",
                font=("Helvetica", 9)).pack(side=tk.LEFT, padx=5)
        
        # Valor
        tk.Label(row, text=f"R$ {d['valor']:.2f}", bg=row_bg, width=10, fg=DANGER_COLOR,
                font=("Helvetica", 9, "bold")).pack(side=tk.RIGHT, padx=5)

# Adicionar esta função para compatibilidade com o código atualizado
import numpy as np
