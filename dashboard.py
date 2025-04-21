import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import calendar
from datetime import datetime, timedelta

def mostrar_dashboard(main_content, database):
    """Função principal para mostrar o dashboard"""
    for widget in main_content.winfo_children():
        widget.destroy()
    
    tk.Label(main_content, text="Dashboard", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Criar frame principal
    dashboard_frame = tk.Frame(main_content, bg="#ffffff")
    dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Dividir em duas colunas
    left_frame = tk.Frame(dashboard_frame, bg="#ffffff")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    right_frame = tk.Frame(dashboard_frame, bg="#ffffff")
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
    
    # Adicionar widgets ao dashboard
    criar_resumo_mensal(left_frame, database)
    criar_grafico_categorias(right_frame, database)
    criar_resumo_contas(left_frame, database)
    criar_ultimas_transacoes(right_frame, database)

def criar_resumo_mensal(parent, database):
    """Cria um resumo das despesas do mês atual"""
    frame = tk.LabelFrame(parent, text="Resumo do Mês", font=("Arial", 12, "bold"), bg="#ffffff")
    frame.pack(fill=tk.X, pady=10)
    
    # Obter mês atual
    hoje = datetime.now()
    primeiro_dia = hoje.replace(day=1).strftime("%d/%m/%Y")
    ultimo_dia = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1]).strftime("%d/%m/%Y")
    
    # Buscar despesas do mês
    despesas = database.listar_despesas(data_inicio=primeiro_dia, data_fim=ultimo_dia)
    total_despesas = sum(d['valor'] for d in despesas)
    
    # Mostrar total
    tk.Label(frame, text=f"Total de despesas: R$ {total_despesas:.2f}", 
             font=("Arial", 14), bg="#ffffff", fg="#E53935").pack(pady=10)
    
    # Criar gráfico de evolução diária
    fig, ax = plt.subplots(figsize=(5, 3))
    
    # Agrupar por dia
    despesas_por_dia = defaultdict(float)
    for d in despesas:
        data = datetime.strptime(d['data'], "%d/%m/%Y")
        despesas_por_dia[data.day] += d['valor']
    
    # Criar dados para o gráfico
    dias = list(range(1, hoje.day + 1))
    valores = [despesas_por_dia.get(dia, 0) for dia in dias]
    
    # Plotar gráfico
    ax.plot(dias, valores, marker='o')
    ax.set_title('Evolução de Despesas no Mês')
    ax.set_xlabel('Dia')
    ax.set_ylabel('Valor (R$)')
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

def criar_grafico_categorias(parent, database):
    """Cria um gráfico de pizza com as categorias de despesas"""
    frame = tk.LabelFrame(parent, text="Despesas por Categoria", font=("Arial", 12, "bold"), bg="#ffffff")
    frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
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
        tk.Label(frame, text="Sem dados para exibir", bg="#ffffff").pack(pady=20)
        return
    
    # Criar gráfico
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Ordenar por valor para melhor visualização
    labels = []
    sizes = []
    for tag, valor in sorted(por_tag.items(), key=lambda x: x[1], reverse=True):
        labels.append(tag)
        sizes.append(valor)
    
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

def criar_resumo_contas(parent, database):
    """Cria um resumo das contas bancárias"""
    frame = tk.LabelFrame(parent, text="Resumo de Contas", font=("Arial", 12, "bold"), bg="#ffffff")
    frame.pack(fill=tk.X, pady=10)
    
    contas = database.listar_contas()
    
    if not contas:
        tk.Label(frame, text="Nenhuma conta cadastrada", bg="#ffffff").pack(pady=10)
        return
    
    # Calcular saldo total
    saldo_total = sum(conta.get('saldo', 0) for conta in contas)
    
    tk.Label(frame, text=f"Saldo Total: R$ {saldo_total:.2f}", 
             font=("Arial", 14), bg="#ffffff", fg="#4CAF50").pack(pady=10)
    
    # Listar contas
    for conta in contas:
        conta_frame = tk.Frame(frame, bg="#ffffff")
        conta_frame.pack(fill=tk.X, pady=2)
        
        cor = conta.get('cor', '#2196F3')
        nome = conta.get('nome', 'Desconhecido')
        saldo = conta.get('saldo', 0)
        
        # Indicador de cor
        cor_indicator = tk.Frame(conta_frame, bg=cor, width=10, height=20)
        cor_indicator.pack(side=tk.LEFT, padx=5)
        
        # Nome da conta
        tk.Label(conta_frame, text=nome, bg="#ffffff", width=15, anchor="w").pack(side=tk.LEFT, padx=5)
        
        # Saldo
        tk.Label(conta_frame, text=f"R$ {saldo:.2f}", bg="#ffffff", anchor="e").pack(side=tk.RIGHT, padx=5)

def criar_ultimas_transacoes(parent, database):
    """Mostra as últimas transações"""
    frame = tk.LabelFrame(parent, text="Últimas Transações", font=("Arial", 12, "bold"), bg="#ffffff")
    frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Buscar últimas 10 transações
    despesas = database.listar_despesas(ordenar_por="data")[-10:]
    
    if not despesas:
        tk.Label(frame, text="Nenhuma transação encontrada", bg="#ffffff").pack(pady=10)
        return
    
    # Criar listbox para mostrar transações
    lista = tk.Listbox(frame, height=10, width=50)
    lista.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Adicionar transações à lista
    for i, d in enumerate(reversed(despesas)):  # Mostrar as mais recentes primeiro
        lista.insert(tk.END, f"{d['data']} | {d['descricao']} | R$ {d['valor']:.2f}")
        # Alternar cores para melhor legibilidade
        if i % 2 == 0:
            lista.itemconfig(i, {'bg': '#f0f0f0'})
