import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

CONFIG_FILE = "config.json"

def mostrar_configuracoes(main_content, database):
    """Função principal para mostrar a aba de configurações"""
    for widget in main_content.winfo_children():
        widget.destroy()
        
    tk.Label(main_content, text="Configurações", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Criar notebook para diferentes seções de configuração
    notebook = ttk.Notebook(main_content)
    notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Abas de configuração
    tab_geral = ttk.Frame(notebook)
    tab_filtros = ttk.Frame(notebook)
    tab_exportacao = ttk.Frame(notebook)
    tab_despesas = ttk.Frame(notebook)
    
    notebook.add(tab_geral, text="Geral")
    notebook.add(tab_filtros, text="Filtros")
    notebook.add(tab_exportacao, text="Exportação")
    notebook.add(tab_despesas, text="Despesas")
    
    # Configurações gerais
    criar_config_geral(tab_geral, database)
    
    # Configurações de filtros
    criar_config_filtros(tab_filtros, database, main_content)
    
    # Configurações de exportação
    criar_config_exportacao(tab_exportacao, database)
    
    # Gerenciamento de despesas
    criar_gerenciamento_despesas(tab_despesas, database, main_content)

def criar_config_geral(parent, database):
    """Cria a seção de configurações gerais"""
    frame = ttk.LabelFrame(parent, text="Configurações Gerais")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Tema da aplicação
    tema_frame = ttk.Frame(frame)
    tema_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(tema_frame, text="Tema da Aplicação:").pack(side=tk.LEFT, padx=5)
    tema_var = tk.StringVar(value="Claro")
    temas = ["Claro", "Escuro", "Sistema"]
    ttk.Combobox(tema_frame, textvariable=tema_var, values=temas, state="readonly", width=15).pack(side=tk.LEFT, padx=5)
    
    # Moeda padrão
    moeda_frame = ttk.Frame(frame)
    moeda_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(moeda_frame, text="Moeda Padrão:").pack(side=tk.LEFT, padx=5)
    moeda_var = tk.StringVar(value="R$")
    moedas = ["R$", "US$", "€", "£"]
    ttk.Combobox(moeda_frame, textvariable=moeda_var, values=moedas, state="readonly", width=15).pack(side=tk.LEFT, padx=5)
    
    # Formato de data
    data_frame = ttk.Frame(frame)
    data_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(data_frame, text="Formato de Data:").pack(side=tk.LEFT, padx=5)
    data_var = tk.StringVar(value="DD/MM/AAAA")
    formatos = ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"]
    ttk.Combobox(data_frame, textvariable=data_var, values=formatos, state="readonly", width=15).pack(side=tk.LEFT, padx=5)
    
    # Botão para salvar configurações
    ttk.Button(frame, text="Salvar Configurações", 
               command=lambda: salvar_config_geral(tema_var.get(), moeda_var.get(), data_var.get(), database)).pack(pady=20)

def salvar_config_geral(tema, moeda, formato_data, database):
    """Salva as configurações gerais"""
    config = {
        "tema": tema,
        "moeda": moeda,
        "formato_data": formato_data
    }
    
    try:
        with open(CONFIG_FILE, "r") as f:
            existing_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_config = {}
    
    existing_config.update(config)
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(existing_config, f, indent=4)
        messagebox.showinfo("Configurações", "Configurações gerais salvas com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")

def criar_config_filtros(parent, database, main_content):
    """Cria a seção de configurações de filtros"""
    frame = ttk.LabelFrame(parent, text="Configurações de Filtros")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Data Início
    data_inicio_frame = ttk.Frame(frame)
    data_inicio_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(data_inicio_frame, text="Data Início:").pack(side=tk.LEFT, padx=5)
    filtro_data_inicio = DateEntry(data_inicio_frame, date_pattern="dd/mm/yyyy", width=15)
    filtro_data_inicio.pack(side=tk.LEFT, padx=5)
    
    # Data Fim
    data_fim_frame = ttk.Frame(frame)
    data_fim_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(data_fim_frame, text="Data Fim:").pack(side=tk.LEFT, padx=5)
    filtro_data_fim = DateEntry(data_fim_frame, date_pattern="dd/mm/yyyy", width=15)
    filtro_data_fim.pack(side=tk.LEFT, padx=5)
    
    # Tag
    tag_frame = ttk.Frame(frame)
    tag_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(tag_frame, text="Tag:").pack(side=tk.LEFT, padx=5)
    filtro_tag = ttk.Entry(tag_frame, width=30)
    filtro_tag.pack(side=tk.LEFT, padx=5)
    
    # Banco
    banco_frame = ttk.Frame(frame)
    banco_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(banco_frame, text="Banco:").pack(side=tk.LEFT, padx=5)
    filtro_banco = ttk.Entry(banco_frame, width=30)
    filtro_banco.pack(side=tk.LEFT, padx=5)
    
    # Descrição
    descricao_frame = ttk.Frame(frame)
    descricao_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(descricao_frame, text="Buscar por descrição:").pack(side=tk.LEFT, padx=5)
    filtro_descricao = ttk.Entry(descricao_frame, width=30)
    filtro_descricao.pack(side=tk.LEFT, padx=5)
    
    # Ordenação
    ordenacao_frame = ttk.Frame(frame)
    ordenacao_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(ordenacao_frame, text="Ordenar por:").pack(side=tk.LEFT, padx=5)
    sort_by = tk.StringVar(value="data")
    opcoes_ordenacao = [("Data", "data"), ("Valor", "valor"), ("Descrição", "descricao")]
    
    for texto, valor in opcoes_ordenacao:
        ttk.Radiobutton(ordenacao_frame, text=texto, variable=sort_by, value=valor).pack(side=tk.LEFT, padx=5)
    
    # Botões
    botoes_frame = ttk.Frame(frame)
    botoes_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(botoes_frame, text="Aplicar Filtros", 
               command=lambda: aplicar_filtros(filtro_data_inicio, filtro_data_fim, filtro_tag, 
                                              filtro_banco, filtro_descricao, sort_by, 
                                              database, main_content)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(botoes_frame, text="Salvar como Padrão", 
               command=lambda: salvar_filtros_padrao(filtro_data_inicio, filtro_data_fim, filtro_tag, 
                                                   filtro_banco, filtro_descricao, sort_by)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(botoes_frame, text="Limpar Filtros", 
               command=lambda: limpar_filtros(filtro_data_inicio, filtro_data_fim, filtro_tag, 
                                            filtro_banco, filtro_descricao)).pack(side=tk.LEFT, padx=5)

def aplicar_filtros(data_inicio, data_fim, tag, banco, descricao, sort_by, database, main_content):
    """Aplica os filtros selecionados"""
    # Implementação futura para aplicar filtros
    messagebox.showinfo("Filtros", "Filtros aplicados com sucesso!")

def salvar_filtros_padrao(data_inicio, data_fim, tag, banco, descricao, sort_by):
    """Salva os filtros como padrão"""
    config = {
        "filtros": {
            "data_inicio": data_inicio.get(),
            "data_fim": data_fim.get(),
            "tag": tag.get(),
            "banco": banco.get(),
            "descricao": descricao.get(),
            "ordenar_por": sort_by.get()
        }
    }
    
    try:
        with open(CONFIG_FILE, "r") as f:
            existing_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_config = {}
    
    existing_config.update(config)
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(existing_config, f, indent=4)
        messagebox.showinfo("Configurações", "Filtros salvos como padrão!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar filtros: {str(e)}")

def limpar_filtros(data_inicio, data_fim, tag, banco, descricao):
    """Limpa todos os filtros"""
    # Limpar os campos
    tag.delete(0, tk.END)
    banco.delete(0, tk.END)
    descricao.delete(0, tk.END)
    
    # Resetar datas para hoje
    data_inicio.set_date(None)
    data_fim.set_date(None)
    
    messagebox.showinfo("Filtros", "Filtros limpos com sucesso!")

def criar_config_exportacao(parent, database):
    """Cria a seção de configurações de exportação"""
    frame = ttk.LabelFrame(parent, text="Configurações de Exportação")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Formato de exportação
    formato_frame = ttk.Frame(frame)
    formato_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(formato_frame, text="Formato de Exportação:").pack(side=tk.LEFT, padx=5)
    formato_var = tk.StringVar(value="CSV")
    formatos = ["CSV", "Excel", "PDF"]
    ttk.Combobox(formato_frame, textvariable=formato_var, values=formatos, state="readonly", width=15).pack(side=tk.LEFT, padx=5)
    
    # Separador CSV
    separador_frame = ttk.Frame(frame)
    separador_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(separador_frame, text="Separador CSV:").pack(side=tk.LEFT, padx=5)
    separador_var = tk.StringVar(value=",")
    separadores = [",", ";", "Tab", "|"]
    ttk.Combobox(separador_frame, textvariable=separador_var, values=separadores, state="readonly", width=15).pack(side=tk.LEFT, padx=5)
    
    # Incluir cabeçalho
    cabecalho_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(frame, text="Incluir cabeçalho", variable=cabecalho_var).pack(anchor="w", padx=5, pady=5)
    
    # Diretório padrão
    diretorio_frame = ttk.Frame(frame)
    diretorio_frame.pack(fill=tk.X, pady=10)
    
    ttk.Label(diretorio_frame, text="Diretório Padrão:").pack(side=tk.LEFT, padx=5)
    diretorio_var = tk.StringVar(value=os.path.expanduser("~"))
    diretorio_entry = ttk.Entry(diretorio_frame, textvariable=diretorio_var, width=30)
    diretorio_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Button(diretorio_frame, text="Procurar", 
               command=lambda: selecionar_diretorio(diretorio_var)).pack(side=tk.LEFT, padx=5)
    
    # Botão para salvar configurações
    ttk.Button(frame, text="Salvar Configurações", 
               command=lambda: salvar_config_exportacao(formato_var.get(), separador_var.get(), 
                                                      cabecalho_var.get(), diretorio_var.get())).pack(pady=20)

def selecionar_diretorio(diretorio_var):
    """Abre diálogo para selecionar diretório"""
    diretorio = filedialog.askdirectory(initialdir=diretorio_var.get())
    if diretorio:
        diretorio_var.set(diretorio)

def salvar_config_exportacao(formato, separador, cabecalho, diretorio):
    """Salva as configurações de exportação"""
    config = {
        "exportacao": {
            "formato": formato,
            "separador": separador,
            "cabecalho": cabecalho,
            "diretorio": diretorio
        }
    }
    
    try:
        with open(CONFIG_FILE, "r") as f:
            existing_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_config = {}
    
    existing_config.update(config)
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(existing_config, f, indent=4)
        messagebox.showinfo("Configurações", "Configurações de exportação salvas com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")

def criar_gerenciamento_despesas(parent, database, main_content):
    """Cria a seção de gerenciamento de despesas"""
    frame = ttk.LabelFrame(parent, text="Gerenciamento de Despesas")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Listagem de despesas
    tree_frame = ttk.Frame(frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    tree = tk.Listbox(tree_frame, width=80, height=15)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Total
    total_label = tk.Label(frame, text="Total: R$ 0.00", font=("Arial", 12, "bold"))
    total_label.pack(pady=5)
    
    # Botões de ação
    botoes_frame = ttk.Frame(frame)
    botoes_frame.pack(fill=tk.X, pady=10)
    
    ttk.Button(botoes_frame, text="Adicionar Despesa", 
               command=lambda: open_add_expense_window(parent, database, tree, total_label)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(botoes_frame, text="Editar Despesa", 
               command=lambda: open_edit_expense_window(parent, database, tree, total_label)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(botoes_frame, text="Remover Despesa", 
               command=lambda: remover_despesa(database, tree, total_label)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(botoes_frame, text="Exportar CSV", 
               command=lambda: exportar_csv(database)).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(botoes_frame, text="Resumo", 
               command=lambda: mostrar_resumo(parent, database)).pack(side=tk.LEFT, padx=5)
    
    # Carregar despesas iniciais
    refresh_expenses(database, tree, total_label)

def refresh_expenses(database, tree, total_label):
    """Atualiza a lista de despesas"""
    tree.delete(0, tk.END)
    
    despesas = database.listar_despesas()
    
    total = 0.0
    for i, despesa in enumerate(despesas):
        tree.insert(
            tk.END, f"{i+1}. {despesa['descricao']} | R${despesa['valor']:.2f} | {despesa['data']} | {despesa['tag']} | {despesa['banco']}")
        total += despesa['valor']
    
    total_label.config(text=f"Total: R${total:.2f}")
    
    # Armazenar para uso em outras funções
    tree.despesas = despesas

def open_add_expense_window(parent, database, tree, total_label):
    """Abre janela para adicionar nova despesa"""
    janela = tk.Toplevel(parent)
    janela.title("Adicionar Despesa")
    janela.geometry("350x300")
    
    campos = [("Descrição", "descricao"), ("Valor", "valor"), ("Data", "data"), ("Tag", "tag"), ("Banco", "banco")]
    entradas = {}
    
    opcoes_tag = ["Alimentação", "Lazer", "Assinatura", "Casa", "Compras", "Educação", "Saúde", "Pix", "Transporte", "Viagem"]
    
    for i, (label, key) in enumerate(campos):
        tk.Label(janela, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=10, pady=5)
        if key == "data":
            entrada = DateEntry(janela, date_pattern="dd/mm/yyyy")
        elif key == "tag":
            entrada = ttk.Combobox(janela, values=opcoes_tag, state="readonly")
            entrada.set("Selecione uma Tag")
        else:
            entrada = tk.Entry(janela)
        entrada.grid(row=i, column=1, padx=10, pady=5)
        entradas[key] = entrada
    
    def salvar():
        dados = {key: entrada.get() for key, entrada in entradas.items()}
        if all(dados.values()) and dados['tag'] != "Selecione uma Tag":
            try:
                dados['valor'] = float(dados['valor'].replace(",", "."))
                database.adicionar_despesa(**dados)
                refresh_expenses(database, tree, total_label)
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "O valor deve ser numérico.")
        else:
            messagebox.showwarning("Campos incompletos", "Por favor, preencha todos os campos corretamente.")
    
    tk.Button(janela, text="Salvar", command=salvar).grid(row=len(campos), column=0, columnspan=2, pady=10)

def open_edit_expense_window(parent, database, tree, total_label):
    """Abre janela para editar despesa selecionada"""
    selected_index = tree.curselection()
    if not selected_index:
        messagebox.showwarning("Nenhuma seleção", "Selecione uma despesa para editar.")
        return
    
    index = selected_index[0]
    despesa = tree.despesas[index]
    
    janela = tk.Toplevel(parent)
    janela.title("Editar Despesa")
    janela.geometry("350x300")
    
    campos = [("Descrição", "descricao"), ("Valor", "valor"), ("Data", "data"), ("Tag", "tag"), ("Banco", "banco")]
    entradas = {}
    
    opcoes_tag = ["Alimentação", "Lazer", "Assinatura", "Casa", "Compras", "Educação", "Saúde", "Pix", "Transporte", "Viagem"]
    
    for i, (label, key) in enumerate(campos):
        tk.Label(janela, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=10, pady=5)
        if key == "data":
            entrada = DateEntry(janela, date_pattern="dd/mm/yyyy")
            entrada.set_date(despesa[key])
        elif key == "tag":
            entrada = ttk.Combobox(janela, values=opcoes_tag, state="readonly")
            entrada.set(despesa[key])
        else:
            entrada = tk.Entry(janela)
            entrada.insert(0, despesa[key])
        entrada.grid(row=i, column=1, padx=10, pady=5)
        entradas[key] = entrada
    
    def salvar():
        novos_dados = {key: entrada.get() for key, entrada in entradas.items()}
        if all(novos_dados.values()) and novos_dados['tag'] != "Selecione uma Tag":
            try:
                novos_dados['valor'] = float(novos_dados['valor'].replace(",", "."))
                database.editar_despesa(index, **novos_dados)
                refresh_expenses(database, tree, total_label)
                janela.destroy()
            except ValueError:
                messagebox.showerror("Erro", "O valor deve ser numérico.")
        else:
            messagebox.showwarning("Campos incompletos", "Por favor, preencha todos os campos corretamente.")
    
    tk.Button(janela, text="Salvar Alterações", command=salvar).grid(row=len(campos), column=0, columnspan=2, pady=10)

def remover_despesa(database, tree, total_label):
    """Remove a despesa selecionada"""
    selected_index = tree.curselection()
    if not selected_index:
        messagebox.showwarning("Nenhuma seleção", "Selecione uma despesa para remover.")
        return
    
    index = selected_index[0]
    confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja remover esta despesa?")
    if confirm:
        database.remover_despesa(index)
        refresh_expenses(database, tree, total_label)

def exportar_csv(database):
    """Exporta as despesas para um arquivo CSV"""
    caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if caminho:
        sucesso = database.exportar_para_csv(caminho)
        if sucesso:
            messagebox.showinfo("Exportado", "Despesas exportadas com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao exportar despesas.")

def mostrar_resumo(parent, database):
    """Mostra um resumo gráfico das despesas"""
    despesas = database.listar_despesas()
    
    if not despesas:
        messagebox.showinfo("Sem dados", "Não há despesas para mostrar no resumo.")
        return
    
    total = sum(d['valor'] for d in despesas)
    por_tag = defaultdict(float)
    por_banco = defaultdict(float)
    
    for d in despesas:
        por_tag[d['tag']] += d['valor']
        por_banco[d['banco']] += d['valor']
    
    janela = tk.Toplevel(parent)
    janela.title("Resumo Financeiro")
    janela.geometry("800x500")
    
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
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def iniciar_modulo_cartoes(frame, database):
    """
    Inicializa o módulo de cartões na interface.
    
    Args:
        frame: O frame onde o módulo será exibido
        database: Objeto de banco de dados
    """
    import tkinter as tk
    from tkinter import ttk, simpledialog, messagebox
    import json
    import os
    
    # Função para salvar os dados dos cartões
    def salvar_cartoes(dados):
        cartoes_config_path = "data/cartoes.json"
        with open(cartoes_config_path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    
    # Função para adicionar um novo cartão
    def adicionar_cartao():
        # Criar uma nova janela para adicionar cartão
        add_window = tk.Toplevel()
        add_window.title("Adicionar Cartão")
        add_window.geometry("400x350")
        add_window.resizable(False, False)
        
        # Centralizar a janela
        add_window.update_idletasks()
        width = add_window.winfo_width()
        height = add_window.winfo_height()
        x = (add_window.winfo_screenwidth() // 2) - (width // 2)
        y = (add_window.winfo_screenheight() // 2) - (height // 2)
        add_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(add_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Campos do formulário
        ttk.Label(main_frame, text="Nome do Cartão:").grid(row=0, column=0, sticky="w", pady=5)
        nome_entry = ttk.Entry(main_frame, width=30)
        nome_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Bandeira:").grid(row=1, column=0, sticky="w", pady=5)
        bandeira_entry = ttk.Entry(main_frame, width=30)
        bandeira_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text="Limite (R$):").grid(row=2, column=0, sticky="w", pady=5)
        limite_entry = ttk.Entry(main_frame, width=30)
        limite_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(main_frame, text="Dia de Fechamento:").grid(row=3, column=0, sticky="w", pady=5)
        fechamento_entry = ttk.Spinbox(main_frame, from_=1, to=31, width=5)
        fechamento_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        ttk.Label(main_frame, text="Dia de Vencimento:").grid(row=4, column=0, sticky="w", pady=5)
        vencimento_entry = ttk.Spinbox(main_frame, from_=1, to=31, width=5)
        vencimento_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # Frame para botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Função para salvar o novo cartão
        def salvar():
            try:
                nome = nome_entry.get().strip()
                bandeira = bandeira_entry.get().strip()
                limite = float(limite_entry.get().replace(',', '.'))
                dia_fechamento = int(fechamento_entry.get())
                dia_vencimento = int(vencimento_entry.get())
                
                # Validações básicas
                if not nome:
                    messagebox.showerror("Erro", "O nome do cartão é obrigatório.")
                    return
                
                if not bandeira:
                    messagebox.showerror("Erro", "A bandeira do cartão é obrigatória.")
                    return
                
                if limite <= 0:
                    messagebox.showerror("Erro", "O limite deve ser maior que zero.")
                    return
                
                if not (1 <= dia_fechamento <= 31):
                    messagebox.showerror("Erro", "O dia de fechamento deve estar entre 1 e 31.")
                    return
                
                if not (1 <= dia_vencimento <= 31):
                    messagebox.showerror("Erro", "O dia de vencimento deve estar entre 1 e 31.")
                    return
                
                # Criar novo cartão
                novo_cartao = {
                    "nome": nome,
                    "bandeira": bandeira,
                    "limite": limite,
                    "dia_fechamento": dia_fechamento,
                    "dia_vencimento": dia_vencimento
                }
                
                # Adicionar à lista de cartões
                cartoes_data["cartoes"].append(novo_cartao)
                
                # Salvar no arquivo
                salvar_cartoes(cartoes_data)
                
                # Fechar janela e atualizar a interface
                add_window.destroy()
                iniciar_modulo_cartoes(frame, database)
                
            except ValueError as e:
                messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        
        # Botões
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=add_window.destroy).pack(side="left", padx=5)
    
    # Limpar o frame
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Carregar dados dos cartões
    cartoes_config_path = "data/cartoes.json"
    
    # Verificar se o diretório existe, se não, criar
    os.makedirs(os.path.dirname(cartoes_config_path), exist_ok=True)
    
    # Verificar se o arquivo de configuração existe
    if not os.path.exists(cartoes_config_path):
        # Criar arquivo de configuração padrão
        configuracao_padrao = {
            "cartoes": []
        }
        
        with open(cartoes_config_path, 'w', encoding='utf-8') as f:
            json.dump(configuracao_padrao, f, ensure_ascii=False, indent=4)
        
        cartoes_data = configuracao_padrao
    else:
        # Carregar configuração existente
        try:
            with open(cartoes_config_path, 'r', encoding='utf-8') as f:
                cartoes_data = json.load(f)
        except json.JSONDecodeError:
            # Se o arquivo estiver corrompido, criar um novo
            configuracao_padrao = {
                "cartoes": []
            }
            
            with open(cartoes_config_path, 'w', encoding='utf-8') as f:
                json.dump(configuracao_padrao, f, ensure_ascii=False, indent=4)
            
            cartoes_data = configuracao_padrao
    
    # Criar interface do módulo de cartões
    titulo = tk.Label(frame, text="Gerenciamento de Cartões de Crédito", font=("Arial", 16, "bold"))
    titulo.pack(pady=10)
    
    # Frame para lista de cartões
    cartoes_frame = tk.Frame(frame)
    cartoes_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Verificar se há cartões cadastrados
    if not cartoes_data["cartoes"]:
        msg = tk.Label(cartoes_frame, text="Nenhum cartão cadastrado. Clique em 'Adicionar Cartão' para começar.")
        msg.pack(pady=20)
    else:
        # Criar tabela de cartões
        colunas = ("Nome", "Bandeira", "Limite", "Fechamento", "Vencimento")
        
        tree = ttk.Treeview(cartoes_frame, columns=colunas, show="headings")
        
        # Configurar cabeçalhos
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Adicionar dados
        for cartao in cartoes_data["cartoes"]:
            tree.insert("", "end", values=(
                cartao["nome"],
                cartao["bandeira"],
                f"R$ {cartao['limite']:.2f}",
                f"Dia {cartao['dia_fechamento']}",
                f"Dia {cartao['dia_vencimento']}"
            ))
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(cartoes_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
    
    # Frame para botões
    botoes_frame = tk.Frame(frame)
    botoes_frame.pack(fill="x", padx=20, pady=10)
    
    # Botão para adicionar cartão
    btn_adicionar = ttk.Button(botoes_frame, text="Adicionar Cartão", command=adicionar_cartao)
    btn_adicionar.pack(side="left", padx=5)
    
    # Botão para editar cartão
    btn_editar = ttk.Button(botoes_frame, text="Editar Cartão")
    btn_editar.pack(side="left", padx=5)
    
    # Botão para remover cartão
    btn_remover = ttk.Button(botoes_frame, text="Remover Cartão")
    btn_remover.pack(side="left", padx=5)
    
    # Botão para gerenciar faturas
    btn_faturas = ttk.Button(botoes_frame, text="Gerenciar Faturas")
    btn_faturas.pack(side="left", padx=5)
    
    return cartoes_data