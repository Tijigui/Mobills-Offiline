import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from database import COLORS, ACCOUNT_TYPES
import locale
from datetime import datetime

# Configurar locale para formatação de moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass

def formatar_moeda(valor):
    """Formata um valor como moeda brasileira"""
    try:
        return locale.currency(float(valor), grouping=True)
    except:
        return f"R$ {valor:.2f}"

def mostrar_contas(main_content, database):
    """Função principal para mostrar a aba de contas"""
    for widget in main_content.winfo_children():
        widget.destroy()
    
    # Container principal com padding
    container = tk.Frame(main_content, bg="#f5f5f5", padx=20, pady=20)
    container.pack(fill=tk.BOTH, expand=True)
    
    # Cabeçalho com título e botão
    header_frame = tk.Frame(container, bg="#f5f5f5")
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    tk.Label(
        header_frame, 
        text="Contas Bancárias", 
        font=("Helvetica", 24, "bold"), 
        bg="#f5f5f5", 
        fg="#333333"
    ).pack(side=tk.LEFT)
    
    # Botão para adicionar conta
    add_btn = tk.Button(
        header_frame,
        text="+ Nova Conta",
        command=lambda: open_account_window(main_content, database),
        bg="#4CAF50", fg="white", 
        font=("Helvetica", 12),
        padx=15, pady=8,
        relief=tk.FLAT,
        cursor="hand2"
    )
    add_btn.pack(side=tk.RIGHT)
    
    # Frame para resumo financeiro
    resumo_frame = tk.Frame(container, bg="white", relief=tk.RIDGE, bd=1)
    resumo_frame.pack(pady=(0, 20), fill=tk.X)
    
    # Calcular saldo total e outros indicadores
    contas = database.listar_contas()
    saldo_total = sum(conta.get('saldo', 0) for conta in contas)
    
    # Adicionar previsão de saldo (simulação)
    saldo_previsto = saldo_total
    despesas_pendentes = 0
    receitas_pendentes = 0
    
    try:
        # Tenta obter transações futuras
        hoje = datetime.now().date()
        transacoes = database.listar_despesas()
        
        for transacao in transacoes:
            data_str = transacao.get('data', '')
            try:
                data = datetime.strptime(data_str, "%d/%m/%Y").date()
                if data > hoje:
                    if transacao.get('tipo') == 'receita':
                        receitas_pendentes += float(transacao.get('valor', 0))
                    else:
                        despesas_pendentes += float(transacao.get('valor', 0))
            except:
                pass
        
        saldo_previsto = saldo_total + receitas_pendentes - despesas_pendentes
    except:
        # Se não conseguir calcular, usa o saldo atual
        pass
    
    # Layout do resumo em grid
    resumo_inner = tk.Frame(resumo_frame, bg="white", padx=20, pady=15)
    resumo_inner.pack(fill=tk.X)
    
    # Título do resumo
    tk.Label(
        resumo_inner, 
        text="Resumo Financeiro", 
        font=("Helvetica", 16, "bold"), 
        bg="white", 
        fg="#333333"
    ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
    
    # Indicadores financeiros
    indicadores = [
        ("Total de Contas:", f"{len(contas)}", 0, 1),
        ("Saldo Total:", formatar_moeda(saldo_total), 0, 2),
        ("Despesas Pendentes:", formatar_moeda(despesas_pendentes), 1, 1),
        ("Receitas Pendentes:", formatar_moeda(receitas_pendentes), 1, 2),
        ("Saldo Previsto:", formatar_moeda(saldo_previsto), 2, 1)
    ]
    
    for label, valor, row, col in indicadores:
        tk.Label(
            resumo_inner, 
            text=label, 
            font=("Helvetica", 11), 
            bg="white", 
            fg="#555555"
        ).grid(row=row+1, column=col*2-2, sticky="w", pady=5, padx=(0, 10))
        
        cor_valor = "#4CAF50" if "Saldo" in label and float(valor.replace("R$", "").replace(".", "").replace(",", ".").strip()) > 0 else "#E53935" if "Saldo" in label else "#333333"
        
        tk.Label(
            resumo_inner, 
            text=valor, 
            font=("Helvetica", 11, "bold"), 
            bg="white", 
            fg=cor_valor
        ).grid(row=row+1, column=col*2-1, sticky="w", pady=5)
    
    # Frame para listagem de contas
    account_list_frame = tk.Frame(container, bg="#f5f5f5")
    account_list_frame.pack(fill=tk.BOTH, expand=True)
    
    # Atualizar lista de contas
    update_account_list(account_list_frame, database, main_content)

def update_account_list(account_list_frame, database, main_content):
    """Atualiza a lista de contas na interface com cards maiores"""
    for widget in account_list_frame.winfo_children():
        widget.destroy()
    
    contas = database.listar_contas()
    
    if not contas:
        empty_frame = tk.Frame(account_list_frame, bg="white", padx=30, pady=30)
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            empty_frame, 
            text="Nenhuma conta cadastrada", 
            font=("Helvetica", 14), 
            bg="white", 
            fg="#757575"
        ).pack(pady=20)
        
        tk.Label(
            empty_frame, 
            text="Clique em '+ Nova Conta' para adicionar sua primeira conta bancária", 
            font=("Helvetica", 12), 
            bg="white", 
            fg="#757575"
        ).pack()
    else:
        # Criar um canvas com scrollbar para muitas contas
        canvas_frame = tk.Frame(account_list_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg="#f5f5f5")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar grid de contas (2 por linha em telas grandes)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar o evento de rolagem do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Criar grid para os cards
        row, col = 0, 0
        max_cols = 2  # 2 cards por linha
        
        for i, conta in enumerate(contas):
            if col >= max_cols:
                col = 0
                row += 1
            
            # Criar card para cada conta
            criar_card_conta(scrollable_frame, conta, database, main_content, row, col)
            col += 1

def criar_card_conta(parent, conta, database, main_content, row, col):
    """Cria um card visualmente atraente para cada conta"""
    nome = conta.get("nome", "Desconhecido")
    saldo = conta.get("saldo", 0)
    cor = conta.get("cor", "#ffffff")
    tipo = conta.get("tipo", "")
    descricao = conta.get("descricao", "")
    
    # Calcular saldo previsto (simulação)
    saldo_previsto = saldo
    try:
        hoje = datetime.now().date()
        transacoes = database.listar_despesas()
        
        for transacao in transacoes:
            if transacao.get('conta') == nome:
                data_str = transacao.get('data', '')
                try:
                    data = datetime.strptime(data_str, "%d/%m/%Y").date()
                    if data > hoje:
                        if transacao.get('tipo') == 'receita':
                            saldo_previsto += float(transacao.get('valor', 0))
                        else:
                            saldo_previsto -= float(transacao.get('valor', 0))
                except:
                    pass
    except:
        pass
    
    # Frame principal do card
    card_frame = tk.Frame(
        parent, 
        bg="white", 
        relief=tk.RAISED,
        bd=1,
        padx=0,
        pady=0
    )
    card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    # Barra colorida superior
    color_bar = tk.Frame(card_frame, bg=cor, height=8)
    color_bar.pack(fill=tk.X)
    
    # Conteúdo do card
    content_frame = tk.Frame(card_frame, bg="white", padx=15, pady=15)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # Cabeçalho com nome do banco e tipo
    header_frame = tk.Frame(content_frame, bg="white")
    header_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Nome do banco com ícone de cor
    banco_frame = tk.Frame(header_frame, bg="white")
    banco_frame.pack(side=tk.LEFT)
    
    cor_indicator = tk.Frame(banco_frame, bg=cor, width=12, height=12)
    cor_indicator.pack(side=tk.LEFT, padx=(0, 8))
    
    tk.Label(
        banco_frame, 
        text=nome, 
        font=("Helvetica", 14, "bold"), 
        bg="white", 
        fg="#333333"
    ).pack(side=tk.LEFT)
    
    # Tipo de conta
    tk.Label(
        header_frame, 
        text=tipo, 
        font=("Helvetica", 10), 
        bg="#f0f0f0", 
        fg="#555555",
        padx=8,
        pady=2
    ).pack(side=tk.RIGHT)
    
    # Linha separadora
    separator = tk.Frame(content_frame, height=1, bg="#eeeeee")
    separator.pack(fill=tk.X, pady=8)
    
    # Descrição
    if descricao:
        desc_frame = tk.Frame(content_frame, bg="white")
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            desc_frame, 
            text="Descrição:", 
            font=("Helvetica", 10), 
            bg="white", 
            fg="#777777"
        ).pack(anchor="w")
        
        tk.Label(
            desc_frame, 
            text=descricao, 
            font=("Helvetica", 11), 
            bg="white", 
            fg="#333333",
            wraplength=250
        ).pack(anchor="w", pady=(2, 0))
    
    # Saldos
    saldos_frame = tk.Frame(content_frame, bg="white")
    saldos_frame.pack(fill=tk.X, pady=5)
    
    # Saldo atual
    saldo_atual_frame = tk.Frame(saldos_frame, bg="white")
    saldo_atual_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
    
    tk.Label(
        saldo_atual_frame, 
        text="Saldo Atual", 
        font=("Helvetica", 10), 
        bg="white", 
        fg="#777777"
    ).pack(anchor="w")
    
    cor_saldo = "#4CAF50" if saldo >= 0 else "#E53935"
    tk.Label(
        saldo_atual_frame, 
        text=formatar_moeda(saldo), 
        font=("Helvetica", 14, "bold"), 
        bg="white", 
        fg=cor_saldo
    ).pack(anchor="w")
    
    # Saldo previsto
    saldo_previsto_frame = tk.Frame(saldos_frame, bg="white")
    saldo_previsto_frame.pack(side=tk.LEFT, fill=tk.Y)
    
    tk.Label(
        saldo_previsto_frame, 
        text="Saldo Previsto", 
        font=("Helvetica", 10), 
        bg="white", 
        fg="#777777"
    ).pack(anchor="w")
    
    cor_previsto = "#4CAF50" if saldo_previsto >= 0 else "#E53935"
    tk.Label(
        saldo_previsto_frame, 
        text=formatar_moeda(saldo_previsto), 
        font=("Helvetica", 14, "bold"), 
        bg="white", 
        fg=cor_previsto
    ).pack(anchor="w")
    
    # Botões de ação
    actions_frame = tk.Frame(content_frame, bg="white")
    actions_frame.pack(fill=tk.X, pady=(15, 0))
    
    # Botão de editar
    edit_btn = tk.Button(
        actions_frame,
        text="Editar",
        command=lambda: mostrar_detalhes_conta(main_content, database, conta, parent),
        bg="#2196F3",
        fg="white",
        font=("Helvetica", 10),
        padx=15,
        pady=6,
        relief=tk.FLAT,
        cursor="hand2"
    )
    edit_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Botão de excluir
    delete_btn = tk.Button(
        actions_frame,
        text="Excluir",
        command=lambda: excluir_conta(database, conta, parent, main_content),
        bg="#E53935",
        fg="white",
        font=("Helvetica", 10),
        padx=15,
        pady=6,
        relief=tk.FLAT,
        cursor="hand2"
    )
    delete_btn.pack(side=tk.LEFT)
    
    # Configurar expansão do grid
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)

# Restante do código permanece o mesmo (open_account_window, mostrar_detalhes_conta, excluir_conta)
def open_account_window(main_content, database):
    """Abre janela para adicionar nova conta"""
    # Criar nova janela
    form_window = tk.Toplevel(main_content)
    form_window.title("Nova Conta")
    form_window.geometry("350x500")  # Tamanho maior para garantir espaço
    
    # Frame principal com scrollbar para garantir que todos elementos sejam visíveis
    canvas = tk.Canvas(form_window)
    scrollbar = tk.Scrollbar(form_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Adicionar padding ao frame principal
    main_frame = tk.Frame(scrollable_frame, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)
    
    # Título
    tk.Label(main_frame, text="Adicionar Nova Conta", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Nome do Banco - APENAS SELEÇÃO (não permite digitação)
    tk.Label(main_frame, text="Nome do Banco:").pack(anchor="w")
    banco_var = tk.StringVar()
    banco_entry = ttk.Combobox(main_frame, textvariable=banco_var, values=[
        "Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau",
        "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank"
    ], state="readonly")  # state="readonly" impede digitação
    banco_entry.pack(fill="x", pady=(0, 10))
    
    # Saldo Inicial
    tk.Label(main_frame, text="Saldo Inicial:").pack(anchor="w")
    saldo_var = tk.StringVar()
    saldo_entry = tk.Entry(main_frame, textvariable=saldo_var)
    saldo_entry.pack(fill="x", pady=(0, 10))
    
    # Descrição
    tk.Label(main_frame, text="Descrição:").pack(anchor="w")
    descricao_var = tk.StringVar()
    descricao_entry = tk.Entry(main_frame, textvariable=descricao_var)
    descricao_entry.pack(fill="x", pady=(0, 10))
    
    # Tipo de Conta - APENAS SELEÇÃO - COM OPÇÕES CORRIGIDAS
    tk.Label(main_frame, text="Tipo de Conta:").pack(anchor="w")
    tipo_var = tk.StringVar()
    tipo_entry = ttk.Combobox(main_frame, textvariable=tipo_var, values=[
        "Conta Corrente", "Conta Poupanca", "Investimento", "VR/VA", "Carteira", "Outros"
    ], state="readonly")  # state="readonly" impede digitação
    tipo_entry.pack(fill="x", pady=(0, 10))
    
    # Cor (com seleção de cores)
    tk.Label(main_frame, text="Cor:").pack(anchor="w")
    cor_var = tk.StringVar(value="#2196F3")
    
    # Frame para as cores predefinidas
    cores_frame = tk.Frame(main_frame)
    cores_frame.pack(fill="x", pady=(5, 10))
    
    # Cores predefinidas
    cores = {
        "Azul": "#2196F3",
        "Verde": "#4CAF50",
        "Vermelho": "#F44336",
        "Roxo": "#9C27B0",
        "Laranja": "#FF9800",
        "Cinza": "#9E9E9E",
        "Preto": "#000000",
        "Amarelo": "#FFEB3B"
    }
    
    # Criar botões de cores em duas linhas
    cores_lista = list(cores.items())
    for i, (nome_cor, hex_cor) in enumerate(cores_lista[:4]):
        rb = tk.Radiobutton(
            cores_frame, text=nome_cor, variable=cor_var, value=hex_cor,
            bg=hex_cor, fg="white" if nome_cor not in ["Amarelo"] else "black",
            indicatoron=0, width=8, height=2
        )
        rb.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
    
    for i, (nome_cor, hex_cor) in enumerate(cores_lista[4:]):
        rb = tk.Radiobutton(
            cores_frame, text=nome_cor, variable=cor_var, value=hex_cor,
            bg=hex_cor, fg="white" if nome_cor not in ["Amarelo"] else "black",
            indicatoron=0, width=8, height=2
        )
        rb.grid(row=1, column=i, padx=2, pady=2, sticky="ew")
    
    # Configurar o grid para distribuir espaço igualmente
    for i in range(4):
        cores_frame.columnconfigure(i, weight=1)
    
    # Função para salvar a conta
    def salvar_conta():
        try:
            nome = banco_var.get()
            saldo_texto = saldo_var.get().replace(',', '.')
            descricao = descricao_var.get()
            tipo = tipo_var.get()
            cor = cor_var.get()
            
            # Verificar campos obrigatórios
            if not nome:
                tk.messagebox.showwarning("Campo obrigatório", 
                                         "Selecione o nome do banco.")
                return
                
            if not tipo:
                tk.messagebox.showwarning("Campo obrigatório", 
                                         "Selecione o tipo de conta.")
                return
            
            # Verificar se o saldo é válido
            if not saldo_texto:
                tk.messagebox.showwarning("Campo obrigatório", 
                                         "Informe o saldo inicial.")
                return
                
            try:
                saldo = float(saldo_texto)
            except ValueError:
                tk.messagebox.showerror("Formato inválido", 
                                       "Saldo deve ser um número válido.")
                return
                
            # Adicionar conta ao banco de dados
            success = database.adicionar_conta(
                nome=nome,
                saldo_inicial=saldo,
                descricao=descricao,
                tipo=tipo,
                cor=cor
            )
            
            if success:
                tk.messagebox.showinfo("Sucesso", "Conta adicionada com sucesso!")
                form_window.destroy()
                # Atualizar a visualização
                mostrar_contas(main_content, database)
            else:
                tk.messagebox.showerror("Erro", "Não foi possível adicionar a conta.")
                
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    # BOTÃO DE SALVAR - Destacado e garantidamente visível
    botao_frame = tk.Frame(main_frame)
    botao_frame.pack(fill="x", pady=20)
    
    salvar_btn = tk.Button(
        botao_frame,
        text="SALVAR CONTA",
        command=salvar_conta,
        bg="#4CAF50",  # Verde
        fg="white",
        font=("Arial", 12, "bold"),
        relief="raised",
        bd=2,
        height=2
    )
    salvar_btn.pack(fill="x")
    
    # Botão cancelar
    cancelar_btn = tk.Button(
        botao_frame,
        text="Cancelar",
        command=form_window.destroy,
        bg="#f5f5f5",
        fg="#333333",
        pady=5
    )
    cancelar_btn.pack(fill="x", pady=(10, 0))
    
    # Centralizar a janela
    form_window.update_idletasks()
    width = form_window.winfo_width()
    height = form_window.winfo_height()
    x = (form_window.winfo_screenwidth() // 2) - (width // 2)
    y = (form_window.winfo_screenheight() // 2) - (height // 2)
    form_window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Tornar modal
    form_window.transient(main_content)
    form_window.grab_set()
    form_window.focus_set()

def mostrar_detalhes_conta(main_content, database, conta, account_list_frame):
    """Abre janela para editar conta existente"""
    detalhes = tk.Toplevel(main_content)
    detalhes.title(f"Detalhes da Conta: {conta['nome']}")
    detalhes.geometry("400x420")
    detalhes.resizable(False, False)
    
    nome_var = tk.StringVar(value=conta['nome'])
    saldo_var = tk.StringVar(value=str(conta['saldo']))
    descricao_var = tk.StringVar(value=conta['descricao'])
    tipo_var = tk.StringVar(value=conta['tipo'])
    cor_var = tk.StringVar(value=conta['cor'])
    
    # Nome
    tk.Label(detalhes, text="Nome:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    tk.Entry(detalhes, textvariable=nome_var, width=30).pack()
    
    # Saldo
    tk.Label(detalhes, text="Saldo:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    tk.Entry(detalhes, textvariable=saldo_var, width=30).pack()
    
    # Descrição
    tk.Label(detalhes, text="Descrição:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    tk.Entry(detalhes, textvariable=descricao_var, width=30).pack()
    
    # Tipo de Conta
    tk.Label(detalhes, text="Tipo de Conta:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    ttk.Combobox(detalhes, textvariable=tipo_var, values=ACCOUNT_TYPES, state="readonly", width=30).pack()
    
    # Cor
    tk.Label(detalhes, text="Cor:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    cor_frame = tk.Frame(detalhes)
    cor_frame.pack(pady=5)
    
    for nome_cor, hex_cor in COLORS.items():
        tk.Radiobutton(
            cor_frame, text=nome_cor, variable=cor_var, value=hex_cor,
            bg=hex_cor, fg="white", indicatoron=0, width=10
        ).pack(side=tk.LEFT, padx=2)
    
    def escolher_outra_cor():
        cor = colorchooser.askcolor(title="Escolher cor personalizada")
        if cor and cor[1]:
            cor_var.set(cor[1])
    
    tk.Button(detalhes, text="Outros", command=escolher_outra_cor).pack(pady=5)
    
    botoes_frame = tk.Frame(detalhes)
    botoes_frame.pack(pady=20)
    
    def salvar_alteracoes():
        try:
            novo_saldo = float(saldo_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Saldo inválido.")
            return
        
        if not nome_var.get().strip():
            messagebox.showerror("Erro", "Nome da conta não pode ser vazio.")
            return
        
        success = database.atualizar_conta(
            nome_original=conta['nome'],
            nome=nome_var.get().strip(),
            saldo=novo_saldo,
            descricao=descricao_var.get().strip(),
            tipo=tipo_var.get().strip(),
            cor=cor_var.get().strip()
        )
        
        if success:
            messagebox.showinfo("Sucesso", "Conta atualizada com sucesso!")
            detalhes.destroy()
            mostrar_contas(main_content, database)
        else:
            messagebox.showerror("Erro", "Não foi possível atualizar a conta.")
    
    def excluir_conta_detalhes():
        excluir_conta(database, conta, account_list_frame, main_content)
        detalhes.destroy()
    
    tk.Button(botoes_frame, text="Salvar Alterações", command=salvar_alteracoes, bg="#2196F3", fg="white", width=15).pack(side=tk.LEFT, padx=5)
    tk.Button(botoes_frame, text="Excluir Conta", command=excluir_conta_detalhes, bg="#E53935", fg="white", width=15).pack(side=tk.LEFT, padx=5)

def excluir_conta(database, conta, account_list_frame, main_content):
    """Exclui uma conta após confirmação"""
    confirm = messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir a conta '{conta['nome']}'?")
    if confirm:
        success = database.remover_conta(conta['nome'])
        if success:
            messagebox.showinfo("Sucesso", "Conta removida com sucesso!")
            mostrar_contas(main_content, database)
        else:
            messagebox.showerror("Erro", "Não foi possível remover a conta.")
