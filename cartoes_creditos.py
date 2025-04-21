import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import calendar

def mostrar_cartoes_credito(main_content, database):
    """Função principal para mostrar a aba de cartões de crédito"""
    for widget in main_content.winfo_children():
        widget.destroy()
        
    tk.Label(main_content, text="Cartões de Crédito", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Frame principal
    main_frame = tk.Frame(main_content, bg="#ffffff")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Frame para botões de ação
    action_frame = tk.Frame(main_frame, bg="#ffffff")
    action_frame.pack(fill=tk.X, pady=10)
    
    # Botão para adicionar cartão
    tk.Button(action_frame, text="Adicionar Cartão", 
              command=lambda: abrir_janela_adicionar_cartao(main_content, database),
              bg="#4CAF50", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    
    # Listar cartões existentes
    listar_cartoes(main_frame, database, main_content)

def listar_cartoes(parent, database, main_content):
    """Lista os cartões de crédito cadastrados"""
    cartoes_frame = tk.Frame(parent, bg="#ffffff")
    cartoes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    cartoes = database.listar_cartoes()
    
    if not cartoes or len(cartoes) == 0:
        tk.Label(cartoes_frame, text="Nenhum cartão de crédito cadastrado", 
                 font=("Arial", 12), bg="#ffffff").pack(pady=20)
        return
    
    # Criar um canvas com scrollbar para muitos cartões
    canvas = tk.Canvas(cartoes_frame, bg="#ffffff")
    scrollbar = ttk.Scrollbar(cartoes_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#ffffff")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Criar um frame para cada cartão
    for cartao in cartoes:
        card_frame = tk.Frame(scrollable_frame, bg="#f0f0f0", relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Cabeçalho do cartão
        header_frame = tk.Frame(card_frame, bg=cartao.get('cor', '#1976D2'))
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, 
                 text=f"{cartao.get('banco', 'Desconhecido')} - {cartao.get('nome', 'Cartão')}",
                 font=("Arial", 12, "bold"), bg=cartao.get('cor', '#1976D2'), 
                 fg="white").pack(pady=5, padx=10, anchor="w")
        
        # Informações do cartão
        info_frame = tk.Frame(card_frame, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Limite
        limite_frame = tk.Frame(info_frame, bg="#f0f0f0")
        limite_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        tk.Label(limite_frame, text="Limite Total:", 
                 font=("Arial", 10), bg="#f0f0f0").pack(anchor="w")
        tk.Label(limite_frame, text=f"R$ {cartao.get('limite', 0):.2f}", 
                 font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w")
        
        # Fatura Atual
        fatura_frame = tk.Frame(info_frame, bg="#f0f0f0")
        fatura_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        tk.Label(fatura_frame, text="Fatura Atual:", 
                 font=("Arial", 10), bg="#f0f0f0").pack(anchor="w")
        tk.Label(fatura_frame, text=f"R$ {cartao.get('fatura_atual', 0):.2f}", 
                 font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w")
        
        # Vencimento
        vencimento_frame = tk.Frame(info_frame, bg="#f0f0f0")
        vencimento_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        tk.Label(vencimento_frame, text="Vencimento:", 
                 font=("Arial", 10), bg="#f0f0f0").pack(anchor="w")
        tk.Label(vencimento_frame, text=f"Dia {cartao.get('dia_vencimento', '-')}", 
                 font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor="w")
        
        # Botões de ação
        btn_frame = tk.Frame(info_frame, bg="#f0f0f0")
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(btn_frame, text="Editar", 
                  command=lambda c=cartao: abrir_janela_editar_cartao(main_content, database, c)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Excluir", 
                  command=lambda c=cartao: excluir_cartao(database, c, main_content)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Ver Faturas", 
                  command=lambda c=cartao: mostrar_faturas(main_content, database, c)).pack(side=tk.LEFT, padx=2)

def abrir_janela_adicionar_cartao(main_content, database):
    """Abre janela para adicionar novo cartão de crédito"""
    janela = tk.Toplevel(main_content)
    janela.title("Adicionar Cartão de Crédito")
    janela.geometry("400x450")
    janela.resizable(False, False)
    
    # Nome do cartão
    tk.Label(janela, text="Nome do Cartão:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    nome_var = tk.StringVar()
    tk.Entry(janela, textvariable=nome_var, width=30).pack(pady=(0, 10))
    
    # Banco
    tk.Label(janela, text="Banco:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    banco_var = tk.StringVar()
    bancos = ["Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau", 
              "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank", "Outro"]
    ttk.Combobox(janela, textvariable=banco_var, values=bancos, state="readonly", width=30).pack(pady=(0, 10))
    
    # Limite
    tk.Label(janela, text="Limite Total (R$):", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    limite_var = tk.StringVar()
    tk.Entry(janela, textvariable=limite_var, width=30).pack(pady=(0, 10))
    
    # Dia de fechamento
    tk.Label(janela, text="Dia de Fechamento:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    fechamento_var = tk.StringVar()
    dias = [str(i) for i in range(1, 32)]
    ttk.Combobox(janela, textvariable=fechamento_var, values=dias, state="readonly", width=30).pack(pady=(0, 10))
    
    # Dia de vencimento
    tk.Label(janela, text="Dia de Vencimento:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    vencimento_var = tk.StringVar()
    ttk.Combobox(janela, textvariable=vencimento_var, values=dias, state="readonly", width=30).pack(pady=(0, 10))
    
    # Cor
    tk.Label(janela, text="Cor:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    cor_var = tk.StringVar(value="#1976D2")
    cores = {
        "Azul": "#1976D2", "Vermelho": "#E53935", "Verde": "#43A047", 
        "Roxo": "#8E24AA", "Laranja": "#FB8C00", "Cinza": "#757575"
    }
    cor_frame = tk.Frame(janela)
    cor_frame.pack(pady=(0, 10))
    
    for nome_cor, hex_cor in cores.items():
        tk.Radiobutton(
            cor_frame, text=nome_cor, variable=cor_var, value=hex_cor,
            bg=hex_cor, fg="white", indicatoron=0, width=10
        ).pack(side=tk.LEFT, padx=2)
    
    def salvar_cartao():
        try:
            limite = float(limite_var.get().replace(",", "."))
            dia_fechamento = int(fechamento_var.get())
            dia_vencimento = int(vencimento_var.get())
            
            if not nome_var.get() or not banco_var.get():
                messagebox.showwarning("Campos obrigatórios", "Nome e Banco são campos obrigatórios.")
                return
                
            if dia_fechamento < 1 or dia_fechamento > 31 or dia_vencimento < 1 or dia_vencimento > 31:
                messagebox.showwarning("Dias inválidos", "Os dias devem estar entre 1 e 31.")
                return
                
            novo_cartao = {
                "nome": nome_var.get(),
                "banco": banco_var.get(),
                "limite": limite,
                "dia_fechamento": dia_fechamento,
                "dia_vencimento": dia_vencimento,
                "cor": cor_var.get(),
                "fatura_atual": 0.0
            }
            
            database.adicionar_cartao(novo_cartao)
            messagebox.showinfo("Sucesso", "Cartão adicionado com sucesso!")
            janela.destroy()
            mostrar_cartoes_credito(main_content, database)
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique se os valores numéricos estão corretos.")
    
    tk.Button(janela, text="Salvar Cartão", command=salvar_cartao, 
              bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=20)

def abrir_janela_editar_cartao(main_content, database, cartao):
    """Abre janela para editar cartão existente"""
    janela = tk.Toplevel(main_content)
    janela.title(f"Editar Cartão: {cartao['nome']}")
    janela.geometry("400x450")
    janela.resizable(False, False)
    
    # Nome do cartão
    tk.Label(janela, text="Nome do Cartão:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    nome_var = tk.StringVar(value=cartao.get('nome', ''))
    tk.Entry(janela, textvariable=nome_var, width=30).pack(pady=(0, 10))
    
    # Banco
    tk.Label(janela, text="Banco:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    banco_var = tk.StringVar(value=cartao.get('banco', ''))
    bancos = ["Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau", 
              "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank", "Outro"]
    ttk.Combobox(janela, textvariable=banco_var, values=bancos, state="readonly", width=30).pack(pady=(0, 10))
    
    # Limite
    tk.Label(janela, text="Limite Total (R$):", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    limite_var = tk.StringVar(value=str(cartao.get('limite', 0)))
    tk.Entry(janela, textvariable=limite_var, width=30).pack(pady=(0, 10))
    
    # Dia de fechamento
    tk.Label(janela, text="Dia de Fechamento:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    fechamento_var = tk.StringVar(value=str(cartao.get('dia_fechamento', 1)))
    dias = [str(i) for i in range(1, 32)]
    ttk.Combobox(janela, textvariable=fechamento_var, values=dias, state="readonly", width=30).pack(pady=(0, 10))
    
    # Dia de vencimento
    tk.Label(janela, text="Dia de Vencimento:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    vencimento_var = tk.StringVar(value=str(cartao.get('dia_vencimento', 1)))
    ttk.Combobox(janela, textvariable=vencimento_var, values=dias, state="readonly", width=30).pack(pady=(0, 10))
    
    # Cor
    tk.Label(janela, text="Cor:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    cor_var = tk.StringVar(value=cartao.get('cor', '#1976D2'))
    cores = {
        "Azul": "#1976D2", "Vermelho": "#E53935", "Verde": "#43A047", 
        "Roxo": "#8E24AA", "Laranja": "#FB8C00", "Cinza": "#757575"
    }
    cor_frame = tk.Frame(janela)
    cor_frame.pack(pady=(0, 10))
    
    for nome_cor, hex_cor in cores.items():
        tk.Radiobutton(
            cor_frame, text=nome_cor, variable=cor_var, value=hex_cor,
            bg=hex_cor, fg="white", indicatoron=0, width=10
        ).pack(side=tk.LEFT, padx=2)
    
    def salvar_alteracoes():
        try:
            limite = float(limite_var.get().replace(",", "."))
            dia_fechamento = int(fechamento_var.get())
            dia_vencimento = int(vencimento_var.get())
            
            if not nome_var.get() or not banco_var.get():
                messagebox.showwarning("Campos obrigatórios", "Nome e Banco são campos obrigatórios.")
                return
                
            if dia_fechamento < 1 or dia_fechamento > 31 or dia_vencimento < 1 or dia_vencimento > 31:
                messagebox.showwarning("Dias inválidos", "Os dias devem estar entre 1 e 31.")
                return
                
            cartao.update({
                "nome": nome_var.get(),
                "banco": banco_var.get(),
                "limite": limite,
                "dia_fechamento": dia_fechamento,
                "dia_vencimento": dia_vencimento,
                "cor": cor_var.get()
            })
            
            database.atualizar_cartao(cartao)
            messagebox.showinfo("Sucesso", "Cartão atualizado com sucesso!")
            janela.destroy()
            mostrar_cartoes_credito(main_content, database)
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique se os valores numéricos estão corretos.")
    
    tk.Button(janela, text="Salvar Alterações", command=salvar_alteracoes, 
              bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=20)

def excluir_cartao(database, cartao, main_content):
    """Exclui um cartão de crédito"""
    confirm = messagebox.askyesno("Confirmar Exclusão", 
                                  f"Tem certeza que deseja excluir o cartão {cartao['nome']}?")
    if confirm:
        database.remover_cartao(cartao)
        messagebox.showinfo("Sucesso", "Cartão removido com sucesso!")
        mostrar_cartoes_credito(main_content, database)

def mostrar_faturas(main_content, database, cartao):
    """Mostra as faturas do cartão selecionado"""
    janela = tk.Toplevel(main_content)
    janela.title(f"Faturas - {cartao['nome']}")
    janela.geometry("700x500")
    
    # Cabeçalho
    tk.Label(janela, text=f"Faturas do Cartão: {cartao['nome']}", 
             font=("Arial", 16, "bold")).pack(pady=10)
    
    # Frame para filtros
    filtro_frame = tk.Frame(janela)
    filtro_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Label(filtro_frame, text="Mês:").pack(side=tk.LEFT, padx=5)
    mes_var = tk.StringVar(value=str(datetime.now().month))
    meses = ["1 - Janeiro", "2 - Fevereiro", "3 - Março", "4 - Abril", 
             "5 - Maio", "6 - Junho", "7 - Julho", "8 - Agosto", 
             "9 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"]
    ttk.Combobox(filtro_frame, textvariable=mes_var, values=meses, state="readonly", width=15).pack(side=tk.LEFT, padx=5)
    
    tk.Label(filtro_frame, text="Ano:").pack(side=tk.LEFT, padx=5)
    ano_var = tk.StringVar(value=str(datetime.now().year))
    anos = [str(year) for year in range(datetime.now().year - 5, datetime.now().year + 2)]
    ttk.Combobox(filtro_frame, textvariable=ano_var, values=anos, state="readonly", width=10).pack(side=tk.LEFT, padx=5)
    
    tk.Button(filtro_frame, text="Buscar", command=lambda: buscar_faturas()).pack(side=tk.LEFT, padx=20)
    
    # Frame para listagem
    lista_frame = tk.Frame(janela)
    lista_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Treeview para mostrar as faturas
    colunas = ("data", "descricao", "valor", "categoria")
    tree = ttk.Treeview(lista_frame, columns=colunas, show="headings")
    
    tree.heading("data", text="Data")
    tree.heading("descricao", text="Descrição")
    tree.heading("valor", text="Valor")
    tree.heading("categoria", text="Categoria")
    
    tree.column("data", width=100)
    tree.column("descricao", width=250)
    tree.column("valor", width=100)
    tree.column("categoria", width=150)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Frame para total
    total_frame = tk.Frame(janela)
    total_frame.pack(fill=tk.X, padx=20, pady=10)
    
    total_label = tk.Label(total_frame, text="Total da Fatura: R$ 0,00", font=("Arial", 12, "bold"))
    total_label.pack(side=tk.RIGHT)
    
    # Frame para botões
    botoes_frame = tk.Frame(janela)
    botoes_frame.pack(fill=tk.X, padx=20, pady=10)
    
    tk.Button(botoes_frame, text="Adicionar Lançamento", 
              command=lambda: adicionar_lancamento()).pack(side=tk.LEFT, padx=5)
    tk.Button(botoes_frame, text="Editar Lançamento", 
              command=lambda: editar_lancamento()).pack(side=tk.LEFT, padx=5)
    tk.Button(botoes_frame, text="Remover Lançamento", 
              command=lambda: remover_lancamento()).pack(side=tk.LEFT, padx=5)
    tk.Button(botoes_frame, text="Exportar Fatura", 
              command=lambda: exportar_fatura()).pack(side=tk.LEFT, padx=5)
    
    def buscar_faturas():
        # Implementação futura para buscar faturas do banco de dados
        messagebox.showinfo("Informação", "Funcionalidade em desenvolvimento")
    
    def adicionar_lancamento():
        # Implementação futura para adicionar lançamento
        messagebox.showinfo("Informação", "Funcionalidade em desenvolvimento")
    
    def editar_lancamento():
        # Implementação futura para editar lançamento
        messagebox.showinfo("Informação", "Funcionalidade em desenvolvimento")
    
    def remover_lancamento():
        # Implementação futura para remover lançamento
        messagebox.showinfo("Informação", "Funcionalidade em desenvolvimento")
    
    def exportar_fatura():
        # Implementação futura para exportar fatura
        messagebox.showinfo("Informação", "Funcionalidade em desenvolvimento")
