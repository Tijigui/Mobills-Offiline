import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from database import ACCOUNT_TYPES, BANKS, COLORS

def mostrar_contas(app):
    """
    Exibe a tela de gerenciamento de contas bancárias.
    
    Args:
        app: Instância da aplicação principal
    """
    tk.Label(app.main_content, text="Contas Bancárias", font=("Arial", 24), bg="#ffffff").pack(pady=20)

    # Botão para adicionar nova conta
    try:
        add_icon = tk.PhotoImage(file="icons/plus.png")
        add_btn = tk.Button(
            app.main_content,
            text=" Adicionar Conta",
            image=add_icon,
            compound="left",
            command=lambda: open_account_window(app),
            bg="#4CAF50", fg="white", font=("Arial", 11), width=180, height=35
        )
        add_btn.image = add_icon  # Mantém uma referência para evitar garbage collection
    except Exception as e:
        print(f"Erro ao carregar ícone: {e}")
        add_btn = tk.Button(
            app.main_content,
            text="Adicionar Conta",
            command=lambda: open_account_window(app),
            bg="#4CAF50", fg="white", font=("Arial", 11), width=180, height=35
        )
    
    add_btn.pack(pady=10)

    # Frame para listar as contas
    app.account_list_frame = tk.Frame(app.main_content, bg="#ffffff")
    app.account_list_frame.pack(pady=10)

    update_account_list(app)

def update_account_list(app):
    """
    Atualiza a lista de contas exibida na interface.
    
    Args:
        app: Instância da aplicação principal
    """
    for widget in app.account_list_frame.winfo_children():
        widget.destroy()

    contas = app.database.listar_contas()

    if not contas:
        tk.Label(app.account_list_frame, text="Nenhuma conta cadastrada.", bg="#ffffff").pack()
    else:
        for conta in contas:
            nome = conta.get("nome", "Desconhecido")
            saldo = conta.get("saldo", 0)
            cor = conta.get("cor", "#ffffff")

            conta_btn = tk.Button(
                app.account_list_frame,
                text=f"{nome} - Saldo: R$ {saldo:.2f}",
                bg=cor,
                font=("Arial", 12),
                fg="white",
                width=40,
                anchor="w",
                command=lambda c=conta: mostrar_detalhes_conta(app, c)
            )
            conta_btn.pack(anchor="w", padx=10, pady=2)

def open_account_window(app):
    """
    Abre a janela para adicionar uma nova conta bancária.
    
    Args:
        app: Instância da aplicação principal
    """
    form_window = tk.Toplevel(app.master)
    form_window.title("Nova Conta")
    form_window.geometry("350x400")

    # Nome do Banco
    tk.Label(form_window, text="Nome do Banco:").pack(pady=5)
    banco_var = tk.StringVar()
    banco_entry = ttk.Combobox(form_window, textvariable=banco_var, values=BANKS, state="readonly")
    banco_entry.pack(pady=5)

    # Saldo Inicial
    tk.Label(form_window, text="Saldo Inicial:").pack(pady=5)
    saldo_var = tk.StringVar()
    saldo_entry = tk.Entry(form_window, textvariable=saldo_var)
    saldo_entry.pack(pady=5)

    # Descrição
    tk.Label(form_window, text="Descrição:").pack(pady=5)
    descricao_var = tk.StringVar()
    descricao_entry = tk.Entry(form_window, textvariable=descricao_var)
    descricao_entry.pack(pady=5)

    # Tipo de Conta
    tk.Label(form_window, text="Tipo de Conta:").pack(pady=5)
    tipo_var = tk.StringVar()
    tipo_entry = ttk.Combobox(form_window, textvariable=tipo_var, values=ACCOUNT_TYPES, state="readonly")
    tipo_entry.pack(pady=5)

    # Cor
    tk.Label(form_window, text="Cor:").pack(pady=5)
    cor_var = tk.StringVar(value="#2196F3")  # Valor padrão azul
    cor_frame = tk.Frame(form_window)
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

    tk.Button(form_window, text="Outros", command=escolher_outra_cor).pack(pady=5)

    def submit():
        nome_banco = banco_var.get()
        descricao = descricao_var.get()
        tipo = tipo_var.get()
        cor = cor_var.get()
        try:
            saldo_inicial = float(saldo_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Saldo inicial deve ser um número válido.")
            return

        if not nome_banco or not descricao or not tipo:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos obrigatórios.")
            return

        app.database.adicionar_conta(
            nome=nome_banco,
            saldo_inicial=saldo_inicial,
            descricao=descricao,
            tipo=tipo,
            cor=cor
        )
        
        form_window.destroy()
        update_account_list(app)

    tk.Button(form_window, text="Salvar Conta", command=submit, bg="#2196F3", fg="white").pack(pady=10)

def mostrar_detalhes_conta(app, conta):
    """
    Mostra os detalhes de uma conta bancária e permite edição.
    
    Args:
        app: Instância da aplicação principal
        conta: Dicionário com os dados da conta
    """
    detalhes = tk.Toplevel(app.master)
    detalhes.title(f"Detalhes da Conta: {conta['nome']}")
    detalhes.geometry("400x420")
    detalhes.resizable(False, False)

    nome_var = tk.StringVar(value=conta['nome'])
    saldo_var = tk.StringVar(value=str(conta['saldo']))
    descricao_var = tk.StringVar(value=conta['descricao'])
    tipo_var = tk.StringVar(value=conta['tipo'])
    cor_var = tk.StringVar(value=conta['cor'])

    ttk.Label(detalhes, text="Nome:").pack(pady=(10, 0))
    ttk.Entry(detalhes, textvariable=nome_var).pack()

    ttk.Label(detalhes, text="Saldo Inicial:").pack(pady=(10, 0))
    ttk.Entry(detalhes, textvariable=saldo_var).pack()

    ttk.Label(detalhes, text="Descrição:").pack(pady=(10, 0))
    ttk.Entry(detalhes, textvariable=descricao_var).pack()

    ttk.Label(detalhes, text="Tipo de Conta:").pack(pady=(10, 0))
    ttk.Combobox(detalhes, textvariable=tipo_var, values=ACCOUNT_TYPES, state="readonly").pack()

    ttk.Label(detalhes, text="Cor:").pack(pady=(10, 0))
    cor_frame = ttk.Frame(detalhes)
    cor_frame.pack(pady=(0, 10))
    ttk.Entry(cor_frame, textvariable=cor_var, width=10).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(cor_frame, text="Selecionar Cor", command=lambda: selecionar_cor(cor_var)).pack(side=tk.LEFT)

    botoes_frame = ttk.Frame(detalhes)
    botoes_frame.pack(pady=10)

    def salvar_alteracoes():
        try:
            novo_saldo = float(saldo_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Saldo inválido.")
            return

        if not nome_var.get().strip():
            messagebox.showerror("Erro", "Nome da conta não pode ser vazio.")
            return

        conta['nome'] = nome_var.get().strip()
        conta['saldo'] = novo_saldo
        conta['descricao'] = descricao_var.get().strip()
        conta['tipo'] = tipo_var.get().strip()
        conta['cor'] = cor_var.get().strip()

        app.database.salvar_dados()
        update_account_list(app)
        detalhes.destroy()

    def excluir_conta():
        confirm = messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir a conta '{conta['nome']}'?")
        if confirm:
            app.database.remover_conta(conta['nome'])
            update_account_list(app)
            detalhes.destroy()

    ttk.Button(botoes_frame, text="Salvar Alterações", command=salvar_alteracoes).pack(side=tk.LEFT, padx=5)
    ttk.Button(botoes_frame, text="Excluir Conta", command=excluir_conta).pack(side=tk.LEFT, padx=5)

def selecionar_cor(cor_var):
    """
    Abre o seletor de cores e atualiza a variável com a cor escolhida.
    
    Args:
        cor_var: Variável StringVar que armazena o valor da cor
    """
    cor = colorchooser.askcolor(title="Escolher Cor")[1]
    if cor:
        cor_var.set(cor)