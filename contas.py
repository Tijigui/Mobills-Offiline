import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from database import COLORS, ACCOUNT_TYPES

def mostrar_contas(main_content, database):
    """Função principal para mostrar a aba de contas"""
    for widget in main_content.winfo_children():
        widget.destroy()
        
    tk.Label(main_content, text="Contas Bancárias", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Frame para botão de adicionar
    btn_frame = tk.Frame(main_content, bg="#ffffff")
    btn_frame.pack(pady=10)
    
    # Botão para adicionar conta
    add_btn = tk.Button(
        btn_frame,
        text="Adicionar Conta",
        command=lambda: open_account_window(main_content, database),
        bg="#4CAF50", fg="white", font=("Arial", 11), width=15, height=2
    )
    add_btn.pack()
    
    # Frame para listagem de contas
    account_list_frame = tk.Frame(main_content, bg="#ffffff")
    account_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
    # Atualizar lista de contas
    update_account_list(account_list_frame, database, main_content)
    
    # Frame para resumo
    resumo_frame = tk.Frame(main_content, bg="#ffffff", relief=tk.RIDGE, bd=1)
    resumo_frame.pack(pady=10, padx=20, fill=tk.X)
    
    # Calcular saldo total
    contas = database.listar_contas()
    saldo_total = sum(conta.get('saldo', 0) for conta in contas)
    
    tk.Label(resumo_frame, text="Resumo de Contas", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=5)
    tk.Label(resumo_frame, text=f"Total de Contas: {len(contas)}", font=("Arial", 12), bg="#ffffff").pack(pady=2)
    tk.Label(resumo_frame, text=f"Saldo Total: R$ {saldo_total:.2f}", font=("Arial", 12, "bold"), bg="#ffffff", fg="#4CAF50").pack(pady=2)

def update_account_list(account_list_frame, database, main_content):
    """Atualiza a lista de contas na interface"""
    for widget in account_list_frame.winfo_children():
        widget.destroy()
    
    contas = database.listar_contas()
    
    if not contas:
        tk.Label(account_list_frame, text="Nenhuma conta cadastrada.", bg="#ffffff", font=("Arial", 12, "italic")).pack(pady=20)
    else:
        # Criar um canvas com scrollbar para muitas contas
        canvas = tk.Canvas(account_list_frame, bg="#ffffff")
        scrollbar = ttk.Scrollbar(account_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Adicionar cada conta à lista
        for conta in contas:
            nome = conta.get("nome", "Desconhecido")
            saldo = conta.get("saldo", 0)
            cor = conta.get("cor", "#ffffff")
            tipo = conta.get("tipo", "")
            
            # Criar frame para cada conta
            conta_frame = tk.Frame(scrollable_frame, bg="#f9f9f9", relief=tk.RAISED, bd=1)
            conta_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Indicador de cor
            cor_indicator = tk.Frame(conta_frame, bg=cor, width=10, height=50)
            cor_indicator.pack(side=tk.LEFT, padx=0, fill=tk.Y)
            
            # Informações da conta
            info_frame = tk.Frame(conta_frame, bg="#f9f9f9")
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            tk.Label(info_frame, text=nome, font=("Arial", 12, "bold"), bg="#f9f9f9").pack(anchor="w")
            tk.Label(info_frame, text=f"Tipo: {tipo}", font=("Arial", 10), bg="#f9f9f9").pack(anchor="w")
            tk.Label(info_frame, text=f"Saldo: R$ {saldo:.2f}", font=("Arial", 11), bg="#f9f9f9").pack(anchor="w")
            
            # Botões de ação
            btn_frame = tk.Frame(conta_frame, bg="#f9f9f9")
            btn_frame.pack(side=tk.RIGHT, padx=10, pady=5)
            
            tk.Button(
                btn_frame, text="Editar",
                command=lambda c=conta: mostrar_detalhes_conta(main_content, database, c, account_list_frame),
                bg="#2196F3", fg="white", width=8
            ).pack(side=tk.TOP, pady=2)
            
            tk.Button(
                btn_frame, text="Excluir",
                command=lambda c=conta: excluir_conta(database, c, account_list_frame, main_content),
                bg="#E53935", fg="white", width=8
            ).pack(side=tk.TOP, pady=2)

def open_account_window(main_content, database):
    """Abre janela para adicionar nova conta"""
    form_window = tk.Toplevel(main_content)
    form_window.title("Nova Conta")
    form_window.geometry("350x400")
    form_window.resizable(False, False)
    
    # Nome do Banco
    tk.Label(form_window, text="Nome do Banco:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    banco_var = tk.StringVar()
    banco_entry = ttk.Combobox(form_window, textvariable=banco_var, values=[
        "Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau",
        "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank"
    ], state="readonly", width=30)
    banco_entry.pack(pady=5)
    
    # Saldo Inicial
    tk.Label(form_window, text="Saldo Inicial:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    saldo_var = tk.StringVar()
    saldo_entry = tk.Entry(form_window, textvariable=saldo_var, width=30)
    saldo_entry.pack(pady=5)
    
    # Descrição
    tk.Label(form_window, text="Descrição:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    descricao_var = tk.StringVar()
    descricao_entry = tk.Entry(form_window, textvariable=descricao_var, width=30)
    descricao_entry.pack(pady=5)
    
    # Tipo de Conta
    tk.Label(form_window, text="Tipo de Conta:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    tipo_var = tk.StringVar()
    tipo_entry = ttk.Combobox(form_window, textvariable=tipo_var, values=ACCOUNT_TYPES, state="readonly", width=30)
    tipo_entry.pack(pady=5)
    
    # Cor
    tk.Label(form_window, text="Cor:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
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
        
        success = database.adicionar_conta(
            nome=nome_banco,
            saldo_inicial=saldo_inicial,
            descricao=descricao,
            tipo=tipo,
            cor=cor
        )
        
        if success:
            messagebox.showinfo("Sucesso", "Conta adicionada com sucesso!")
            form_window.destroy()
            # Atualizar a lista de contas
            for widget in main_content.winfo_children():
                if isinstance(widget, tk.Frame) and widget != form_window:
                    update_account_list(widget, database, main_content)
            # Recarregar a tela de contas
            mostrar_contas(main_content, database)
        else:
            messagebox.showerror("Erro", "Já existe uma conta com este nome.")
    
    tk.Button(form_window, text="Salvar Conta", command=submit, bg="#4CAF50", fg="white", font=("Arial", 11)).pack(pady=20)

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
            update_account_list(account_list_frame, database, main_content)
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
            update_account_list(account_list_frame, database, main_content)
            mostrar_contas(main_content, database)
        else:
            messagebox.showerror("Erro", "Não foi possível remover a conta.")