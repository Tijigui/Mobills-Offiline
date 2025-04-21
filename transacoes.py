import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def mostrar_transacoes(app):
    """
    Exibe a tela de listagem e gerenciamento de transações financeiras.
    
    Args:
        app: Instância da aplicação principal
    """
    tk.Label(app.main_content, text="Transações", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Frame para filtros
    filtro_frame = tk.Frame(app.main_content, bg="#ffffff")
    filtro_frame.pack(pady=10)

    tk.Label(filtro_frame, text="Data Início").grid(row=0, column=0, padx=5)
    app.filtro_data_inicio = DateEntry(filtro_frame, date_pattern="dd/mm/yyyy")
    app.filtro_data_inicio.grid(row=0, column=1, padx=5)

    tk.Label(filtro_frame, text="Data Fim").grid(row=0, column=2, padx=5)
    app.filtro_data_fim = DateEntry(filtro_frame, date_pattern="dd/mm/yyyy")
    app.filtro_data_fim.grid(row=0, column=3, padx=5)

    tk.Label(filtro_frame, text="Tag").grid(row=1, column=0, padx=5)
    app.filtro_tag = tk.Entry(filtro_frame)
    app.filtro_tag.grid(row=1, column=1, padx=5)

    tk.Label(filtro_frame, text="Banco").grid(row=1, column=2, padx=5)
    app.filtro_banco = tk.Entry(filtro_frame)
    app.filtro_banco.grid(row=1, column=3, padx=5)

    tk.Label(filtro_frame, text="Buscar por descrição").grid(row=2, column=0, padx=5)
    app.filtro_descricao = tk.Entry(filtro_frame)
    app.filtro_descricao.grid(row=2, column=1, padx=5)

    app.sort_by = tk.StringVar(value="data")
    
    tk.Button(filtro_frame, text="Filtrar", command=lambda: refresh_expenses(app)).grid(row=2, column=3, padx=5)

    # Frame para lista de transações
    app.tree = tk.Listbox(app.main_content, width=120, height=15)
    app.tree.pack(pady=10)

    app.total_label = tk.Label(app.main_content, text="Total: R$ 0.00", font=("Arial", 12, "bold"))
    app.total_label.pack(pady=5)

    # Frame para botões de ação
    botoes_frame = tk.Frame(app.main_content, bg="#ffffff")
    botoes_frame.pack(pady=10)

    tk.Button(botoes_frame, text="Adicionar Despesa", command=lambda: open_add_expense_window(app)).pack(side=tk.LEFT, padx=10)
    tk.Button(botoes_frame, text="Editar Despesa", command=lambda: open_edit_expense_window(app)).pack(side=tk.LEFT, padx=10)
    tk.Button(botoes_frame, text="Remover Despesa", command=lambda: remover_despesa(app)).pack(side=tk.LEFT, padx=10)
    tk.Button(botoes_frame, text="Exportar CSV", command=lambda: exportar_csv(app)).pack(side=tk.LEFT, padx=10)
    tk.Button(botoes_frame, text="Resumo", command=lambda: mostrar_resumo(app)).pack(side=tk.LEFT, padx=10)

    refresh_expenses(app)

def refresh_expenses(app):
    """
    Atualiza a lista de despesas de acordo com os filtros aplicados.
    
    Args:
        app: Instância da aplicação principal
    """
    app.tree.delete(0, tk.END)
    app.despesas_filtradas = app.database.listar_despesas(
        data_inicio=app.filtro_data_inicio.get(),
        data_fim=app.filtro_data_fim.get(),
        tag=app.filtro_tag.get(),
        banco=app.filtro_banco.get(),
        busca_descricao=app.filtro_descricao.get(),
        ordenar_por=app.sort_by.get()
    )
    total = 0.0
    for i, despesa in enumerate(app.despesas_filtradas):
        app.tree.insert(
            tk.END, f"{i+1}. {despesa['descricao']} | R${despesa['valor']:.2f} | {despesa['data']} | {despesa['tag']} | {despesa['banco']}")
        total += despesa['valor']

    app.total_label.config(text=f"Total: R${total:.2f}")

def mostrar_resumo(app):
    """
    Exibe um resumo visual das despesas com gráficos.
    
    Args:
        app: Instância da aplicação principal
    """
    if not hasattr(app, 'despesas_filtradas'):
        return

    total = sum(d['valor'] for d in app.despesas_filtradas)
    por_tag = defaultdict(float)
    por_banco = defaultdict(float)

    for d in app.despesas_filtradas:
        por_tag[d['tag']] += d['valor']
        por_banco[d['banco']] += d['valor']

    janela = tk.Toplevel(app.master)
    janela.title("Resumo Financeiro")

    tk.Label(janela, text=f"Total Geral: R$ {total:.2f}", font=("Arial", 12, "bold")).pack(pady=5)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.tight_layout(pad=4.0)

    if por_tag:
        ax1.pie(por_tag.values(), labels=por_tag.keys(), autopct='%1.1f%%')
        ax1.set_title('Por Tag')

    if por_banco:
        ax2.pie(por_banco.values(), labels=por_banco.keys(), autopct='%1.1f%%')
        ax2.set_title('Por Banco')

    canvas = FigureCanvasTkAgg(fig, master=janela)
    canvas.draw()
    canvas.get_tk_widget().pack()

def open_add_expense_window(app):
    """
    Abre a janela para adicionar uma nova despesa.
    
    Args:
        app: Instância da aplicação principal
    """
    janela = tk.Toplevel(app.master)
    janela.title("Adicionar Despesa")

    campos = [("Descrição", "descricao"), ("Valor", "valor"), ("Data", "data"), ("Tag", "tag"), ("Banco", "banco")]
    entradas = {}

    opcoes_tag = ["Alimentação", "Lazer", "Assinatura", "Casa", "Compras", "Educação", "Saúde", "Pix", "Transporte", "Viagem"]

    for i, (label, key) in enumerate(campos):
        tk.Label(janela, text=f"{label}:").grid(row=i, column=0, sticky="e")
        if key == "data":
            entrada = DateEntry(janela, date_pattern="dd/mm/yyyy")
        elif key == "tag":
            entrada = ttk.Combobox(janela, values=opcoes_tag, state="readonly")
            entrada.set("Selecione uma Tag")
        else:
            entrada = tk.Entry(janela)
        entrada.grid(row=i, column=1)
        entradas[key] = entrada

    def salvar():
        dados = {key: entrada.get() for key, entrada in entradas.items()}
        if all(dados.values()) and dados['tag'] != "Selecione uma Tag":
            try:
                dados['valor'] = float(dados['valor'].replace(",", "."))
                app.database.adicionar_despesa(**dados)
                refresh_expenses(app)
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "O valor deve ser numérico.")
        else:
            messagebox.showwarning("Campos incompletos", "Por favor, preencha todos os campos corretamente.")

    tk.Button(janela, text="Salvar", command=salvar).grid(row=len(campos), column=0, columnspan=2, pady=10)

def open_edit_expense_window(app):
    """
    Abre a janela para editar uma despesa existente.
    
    Args:
        app: Instância da aplicação principal
    """
    selected_index = app.tree.curselection()
    if not selected_index:
        messagebox.showwarning("Nenhuma seleção", "Selecione uma despesa para editar.")
        return

    index = selected_index[0]
    despesa = app.despesas_filtradas[index]

    janela = tk.Toplevel(app.master)
    janela.title("Editar Despesa")

    campos = [("Descrição", "descricao"), ("Valor", "valor"), ("Data", "data"), ("Tag", "tag"), ("Banco", "banco")]
    entradas = {}

    opcoes_tag = ["Alimentação", "Lazer", "Assinatura", "Casa", "Compras", "Educação", "Saúde", "Pix", "Transporte", "Viagem"]

    for i, (label, key) in enumerate(campos):
        tk.Label(janela, text=f"{label}:").grid(row=i, column=0, sticky="e")
        if key == "data":
            entrada = DateEntry(janela, date_pattern="dd/mm/yyyy")
            entrada.set_date(despesa[key])
        elif key == "tag":
            entrada = ttk.Combobox(janela, values=opcoes_tag, state="readonly")
            entrada.set(despesa[key])
        else:
            entrada = tk.Entry(janela)
            entrada.insert(0, despesa[key])
        entrada.grid(row=i, column=1)
        entradas[key] = entrada

    def salvar():
        novos_dados = {key: entrada.get() for key, entrada in entradas.items()}
        if all(novos_dados.values()) and novos_dados['tag'] != "Selecione uma Tag":
            try:
                novos_dados['valor'] = float(novos_dados['valor'].replace(",", "."))
                app.database.editar_despesa(index, **novos_dados)
                refresh_expenses(app)
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "O valor deve ser numérico.")
        else:
            messagebox.showwarning("Campos incompletos", "Por favor, preencha todos os campos corretamente.")

    tk.Button(janela, text="Salvar Alterações", command=salvar).grid(row=len(campos), column=0, columnspan=2, pady=10)

def remover_despesa(app):
    """
    Remove a despesa selecionada.
    
    Args:
        app: Instância da aplicação principal
    """
    selected_index = app.tree.curselection()
    if not selected_index:
        messagebox.showwarning("Nenhuma seleção", "Selecione uma despesa para remover.")
        return

    index = selected_index[0]
    confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja remover esta despesa?")
    if confirm:
        app.database.remover_despesa(index)
        refresh_expenses(app)

def exportar_csv(app):
    """
    Exporta as despesas filtradas para um arquivo CSV.
    
    Args:
        app: Instância da aplicação principal
    """
    caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if caminho:
        sucesso = app.database.exportar_para_csv(
            caminho,
            data_inicio=app.filtro_data_inicio.get(),
            data_fim=app.filtro_data_fim.get(),
            tag=app.filtro_tag.get(),
            banco=app.filtro_banco.get(),
            busca_descricao=app.filtro_descricao.get(),
            ordenar_por=app.sort_by.get()
        )
        if sucesso:
            messagebox.showinfo("Exportado", "Despesas exportadas com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao exportar despesas.")