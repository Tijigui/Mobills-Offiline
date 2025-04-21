import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def mostrar_cartoes_credito(app):
    """
    Exibe a tela de gerenciamento de cartões de crédito.
    
    Args:
        app: Instância da aplicação principal
    """
    tk.Label(app.main_content, text="Cartões de Crédito", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Botões de ação
    botoes_frame = tk.Frame(app.main_content, bg="#ffffff")
    botoes_frame.pack(pady=10)
    
    tk.Button(
        botoes_frame,
        text="Adicionar Cartão",
        command=lambda: abrir_adicionar_cartao(app),
        bg="#4CAF50",
        fg="white",
        font=("Arial", 11)
    ).pack(side=tk.LEFT, padx=10)
    
    # Frame para lista de cartões
    app.cartoes_list_frame = tk.Frame(app.main_content, bg="#ffffff")
    app.cartoes_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
    # Atualiza a lista de cartões
    atualizar_lista_cartoes(app)
    
    # Frame para resumo e estatísticas
    resumo_frame = tk.Frame(app.main_content, bg="#ffffff")
    resumo_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(
        resumo_frame,
        text="Resumo dos Cartões",
        font=("Arial", 16, "bold"),
        bg="#ffffff"
    ).pack(pady=5)

def atualizar_lista_cartoes(app):
    """
    Atualiza a lista de cartões de crédito exibida na interface.
    
    Args:
        app: Instância da aplicação principal
    """
    for widget in app.cartoes_list_frame.winfo_children():
        widget.destroy()
    
    # Obter os cartões do banco de dados
    # Assumindo que existe um método para isso, similar ao listar_contas()
    try:
        cartoes = app.database.listar_cartoes_credito()
    except AttributeError:
        # Se o método não existir ainda
        cartoes = []
        tk.Label(
            app.cartoes_list_frame,
            text="Funcionalidade de cartões ainda não implementada no banco de dados.",
            bg="#ffffff",
            fg="red"
        ).pack(pady=10)
        return
    
    if not cartoes:
        tk.Label(
            app.cartoes_list_frame,
            text="Nenhum cartão de crédito cadastrado.",
            bg="#ffffff"
        ).pack(pady=10)
        return
    
    # Criar uma entrada para cada cartão
    for cartao in cartoes:
        cartao_frame = tk.Frame(app.cartoes_list_frame, bg="#f0f0f0", padx=10, pady=10)
        cartao_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Informações do cartão
        info_frame = tk.Frame(cartao_frame, bg="#f0f0f0")
        info_frame.pack(fill=tk.X)
        
        # Nome/bandeira do cartão
        tk.Label(
            info_frame,
            text=cartao.get("nome", "Cartão"),
            font=("Arial", 14, "bold"),
            bg="#f0f0f0"
        ).grid(row=0, column=0, sticky="w")
        
        # Limite disponível
        tk.Label(
            info_frame,
            text=f"Limite: R$ {cartao.get('limite', 0):.2f}",
            bg="#f0f0f0"
        ).grid(row=1, column=0, sticky="w")
        
        # Valor da fatura atual
        tk.Label(
            info_frame,
            text=f"Fatura Atual: R$ {cartao.get('fatura_atual', 0):.2f}",
            bg="#f0f0f0"
        ).grid(row=2, column=0, sticky="w")
        
        # Dia de fechamento
        tk.Label(
            info_frame,
            text=f"Fecha dia: {cartao.get('dia_fechamento', '-')}",
            bg="#f0f0f0"
        ).grid(row=1, column=1, sticky="w", padx=(20, 0))
        
        # Dia de vencimento
        tk.Label(
            info_frame,
            text=f"Vence dia: {cartao.get('dia_vencimento', '-')}",
            bg="#f0f0f0"
        ).grid(row=2, column=1, sticky="w", padx=(20, 0))
        
        # Botões de ação
        botoes_frame = tk.Frame(cartao_frame, bg="#f0f0f0")
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            botoes_frame,
            text="Editar",
            command=lambda c=cartao: abrir_editar_cartao(app, c)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="Ver Fatura",
            command=lambda c=cartao: mostrar_fatura(app, c)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="Adicionar Compra",
            command=lambda c=cartao: adicionar_compra_cartao(app, c)
        ).pack(side=tk.LEFT, padx=5)

def abrir_adicionar_cartao(app):
    """
    Abre a janela para adicionar um novo cartão de crédito.
    
    Args:
        app: Instância da aplicação principal
    """
    janela = tk.Toplevel(app.master)
    janela.title("Adicionar Cartão de Crédito")
    janela.geometry("400x500")
    
    # Formulário de cadastro
    tk.Label(janela, text="Nome/Bandeira do Cartão:").pack(pady=(10, 0))
    nome_var = tk.StringVar()
    tk.Entry(janela, textvariable=nome_var, width=30).pack(pady=(0, 10))
    
    tk.Label(janela, text="Limite Total (R$):").pack(pady=(10, 0))
    limite_var = tk.StringVar()
    tk.Entry(janela, textvariable=limite_var, width=30).pack(pady=(0, 10))
    
    tk.Label(janela, text="Dia de Fechamento:").pack(pady=(10, 0))
    dia_fechamento_var = tk.StringVar()
    tk.Spinbox(janela, from_=1, to=31, textvariable=dia_fechamento_var, width=5).pack(pady=(0, 10))
    
    tk.Label(janela, text="Dia de Vencimento:").pack(pady=(10, 0))
    dia_vencimento_var = tk.StringVar()
    tk.Spinbox(janela, from_=1, to=31, textvariable=dia_vencimento_var, width=5).pack(pady=(0, 10))
    
    tk.Label(janela, text="Banco/Instituição:").pack(pady=(10, 0))
    banco_var = tk.StringVar()
    tk.Entry(janela, textvariable=banco_var, width=30).pack(pady=(0, 10))
    
    tk.Label(janela, text="Cor:").pack(pady=(10, 0))
    cor_var = tk.StringVar(value="#2196F3")  # Azul padrão
    cor_frame = tk.Frame(janela)
    cor_frame.pack(pady=(0, 10))
    
    cor_label = tk.Label(cor_frame, bg=cor_var.get(), width=3, height=1)
    cor_label.pack(side=tk.LEFT, padx=(0, 5))
    
    def escolher_cor():
        cor = colorchooser.askcolor(title="Escolher Cor")[1]
        if cor:
            cor_var.set(cor)
            cor_label.config(bg=cor)
    
    tk.Button(cor_frame, text="Escolher Cor", command=escolher_cor).pack(side=tk.LEFT)
    
    # Botão para salvar
    def salvar_cartao():
        try:
            nome = nome_var.get().strip()
            limite = float(limite_var.get().replace(",", "."))
            dia_fechamento = int(dia_fechamento_var.get())
            dia_vencimento = int(dia_vencimento_var.get())
            banco = banco_var.get().strip()
            cor = cor_var.get()
            
            if not nome or not banco:
                messagebox.showwarning("Campos Incompletos", "Preencha todos os campos obrigatórios.")
                return
            
            if dia_fechamento < 1 or dia_fechamento > 31 or dia_vencimento < 1 or dia_vencimento > 31:
                messagebox.showwarning("Dados Inválidos", "Os dias de fechamento e vencimento devem estar entre 1 e 31.")
                return
            
            # Adicionar cartão ao banco de dados
            # Este método precisa ser implementado no database.py
            try:
                app.database.adicionar_cartao_credito(
                    nome=nome,
                    limite=limite,
                    dia_fechamento=dia_fechamento,
                    dia_vencimento=dia_vencimento,
                    banco=banco,
                    cor=cor,
                    fatura_atual=0.0
                )
                janela.destroy()
                atualizar_lista_cartoes(app)
            except AttributeError:
                messagebox.showerror(
                    "Funcionalidade Não Implementada",
                    "A função para adicionar cartões ainda não foi implementada no banco de dados."
                )
                
        except ValueError:
            messagebox.showerror("Erro", "Verifique se os valores numéricos estão corretos.")
    
    tk.Button(
        janela,
        text="Salvar Cartão",
        command=salvar_cartao,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12)
    ).pack(pady=20)

def abrir_editar_cartao(app, cartao):
    """
    Abre a janela para editar um cartão de crédito existente.
    
    Args:
        app: Instância da aplicação principal
        cartao: Dicionário com as informações do cartão
    """
    janela = tk.Toplevel(app.master)
    janela.title(f"Editar Cartão: {cartao['nome']}")
    janela.geometry("400x500")
    
    # Preencher o formulário com os dados existentes
    tk.Label(janela, text="Nome/Bandeira do Cartão:").pack(pady=(10, 0))
    nome_var = tk.StringVar(value=cartao.get('nome', ''))
    tk.Entry(janela, textvariable=nome_var, width=30).pack(pady=(0, 10))
    
    tk.Label(janela, text="Limite Total (R$):").pack(pady=(10, 0))
    limite_var = tk.StringVar(value=str(cartao.get('limite', 0)))
    tk.Entry(janela, textvariable=limite_var, width=30).pack(pady=(0, 10))
    
    tk.Label(janela, text="Dia de Fechamento:").pack(pady=(10, 0))
    dia_fechamento_var = tk.StringVar(value=str(cartao.get('dia_fechamento', 1)))
    tk.Spinbox(janela, from_=1, to=31, textvariable=dia_fechamento_var, width=5).pack(pady=(0, 10))
    
    tk.Label(janela, text="Dia de Vencimento:").pack(pady=(10, 0))
    dia_vencimento_var = tk.StringVar(value=str(cartao.get('dia_vencimento', 1)))
    tk.Spinbox(janela, from_=1, to=31, textvariable=dia_vencimento_var, width=5).pack(pady=(0, 10))
    
    tk.Label(janela, text="Banco/Instituição:").pack(pady=(10, 0))
    banco_var = tk.StringVar(value=cartao.get('banco', ''))
    tk.Entry(janela, textvariable=banco_var, width=30).pack(pady=(0, 10))
    
    tk.Label(janela, text="Cor:").pack(pady=(10, 0))
    cor_var = tk.StringVar(value=cartao.get('cor', '#2196F3'))
    cor_frame = tk.Frame(janela)
    cor_frame.pack(pady=(0, 10))
    
    cor_label = tk.Label(cor_frame, bg=cor_var.get(), width=3, height=1)
    cor_label.pack(side=tk.LEFT, padx=(0, 5))
    
    def escolher_cor():
        cor = colorchooser.askcolor(title="Escolher Cor")[1]
        if cor:
            cor_var.set(cor)
            cor_label.config(bg=cor)
    
    tk.Button(cor_frame, text="Escolher Cor", command=escolher_cor).pack(side=tk.LEFT)
    
    # Botões de ação
    botoes_frame = tk.Frame(janela)
    botoes_frame.pack(pady=20)
    
    def salvar_alteracoes():
        try:
            nome = nome_var.get().strip()
            limite = float(limite_var.get().replace(",", "."))
            dia_fechamento = int(dia_fechamento_var.get())
            dia_vencimento = int(dia_vencimento_var.get())
            banco = banco_var.get().strip()
            cor = cor_var.get()
            
            if not nome or not banco:
                messagebox.showwarning("Campos Incompletos", "Preencha todos os campos obrigatórios.")
                return
            
            # Atualizar cartão no banco de dados
            try:
                app.database.atualizar_cartao_credito(
                    id_cartao=cartao.get('id'),  # Assumindo que existe um ID
                    nome=nome,
                    limite=limite,
                    dia_fechamento=dia_fechamento,
                    dia_vencimento=dia_vencimento,
                    banco=banco,
                    cor=cor
                )
                janela.destroy()
                atualizar_lista_cartoes(app)
            except AttributeError:
                messagebox.showerror(
                    "Funcionalidade Não Implementada",
                    "A função para editar cartões ainda não foi implementada no banco de dados."
                )
                
        except ValueError:
            messagebox.showerror("Erro", "Verifique se os valores numéricos estão corretos.")
    
    def excluir_cartao():
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o cartão {cartao['nome']}?\nEsta ação não pode ser desfeita."
        )
        if confirmar:
            try:
                app.database.remover_cartao_credito(cartao.get('id'))
                janela.destroy()
                atualizar_lista_cartoes(app)
            except AttributeError:
                messagebox.showerror(
                    "Funcionalidade Não Implementada",
                    "A função para remover cartões ainda não foi implementada no banco de dados."
                )
    
    tk.Button(
        botoes_frame,
        text="Salvar Alterações",
        command=salvar_alteracoes,
        bg="#2196F3",
        fg="white"
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        botoes_frame,
        text="Excluir Cartão",
        command=excluir_cartao,
        bg="#f44336",
        fg="white"
    ).pack(side=tk.LEFT, padx=5)

def mostrar_fatura(app, cartao):
    """
    Exibe os detalhes da fatura atual do cartão de crédito.
    
    Args:
        app: Instância da aplicação principal
        cartao: Dicionário com as informações do cartão
    """
    janela = tk.Toplevel(app.master)
    janela.title(f"Fatura do Cartão: {cartao['nome']}")
    janela.geometry("600x500")
    
    # Informações da fatura
    tk.Label(
        janela,
        text=f"Fatura do Cartão {cartao['nome']}",
        font=("Arial", 16, "bold")
    ).pack(pady=10)
    
    tk.Label(
        janela,
        text=f"Valor Total: R$ {cartao.get('fatura_atual', 0):.2f}",
        font=("Arial", 14)
    ).pack(pady=5)
    
    # Obter