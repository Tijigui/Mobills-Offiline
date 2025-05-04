import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import base64
import io
import shutil

class TransacoesModernUI(ttk.Frame):
    def __init__(self, parent, database=None):
        """
        Inicializa a interface de transações
        
        Args:
            parent: Widget pai onde esta interface será exibida
            database: Instância do banco de dados ou caminho do arquivo JSON
        """
        super().__init__(parent)  # Importante: inicializar a classe pai
        
        # Armazenar o parent explicitamente
        self.parent = parent
        
        # Se database for uma string, considere como o caminho do arquivo
        if isinstance(database, str):
            self.json_file = database
            self.database = None
        else:
            self.database = database
            self.json_file = "despesas.json"  # Arquivo padrão como fallback
            
        # Inicializar todos os atributos importantes
        self.tag_form_entry = None
        self.banco_form_entry = None
        self.date_form_entry = None
        self.descricao_form_entry = None
        self.valor_form_entry = None
        self.transaction_type_var = None
        self.situacao_var = None
        self.search_entry = None
        self.transaction_tree = None
        self.despesas = {"despesas": []}
        self.edit_mode = False
        self.current_edit_index = None
        self.filter_panel_visible = False
        self.filter_panel = None
        self.cancel_button = None
        self.context_menu = None
        self.document_path_var = None
        self.from_account_entry = None
        self.to_account_entry = None
        
        # Inicializar atributos para o painel de filtro
        self.date_from = None
        self.date_to = None
        self.filter_category = None
        self.filter_bank = None
        self.filter_type_var = None
        self.filter_icon = None
        
        # Inicializar atributos para o menu dropdown
        self.transaction_type_menu = tk.StringVar(value="Transações")
        self.transaction_menu = None
        self.title_button = None
        
        # Inicializar atributos para o sidebar
        self.sidebar_frame = None
        self.start_date_entry = None
        self.end_date_entry = None
        self.category_var = None
        self.status_var = None
        
        # Configurar a interface
        self.setup_ui()
        
        # Configurar estilos específicos para a TreeView (após sua criação)
        self.setup_tree_styles()
        
        # Empacotar o frame principal para que seja exibido
        self.pack(fill=tk.BOTH, expand=True)
        
        # Garantir que os dados sejam carregados após a interface estar pronta
        self.after(100, self.load_transactions)

    def setup_tree_styles(self):
        """Configura os estilos específicos para a TreeView"""
        style = ttk.Style()
        
        # Configuração geral da TreeView
        style.configure("Treeview", 
                        font=("Segoe UI", 11),
                        rowheight=36)  # Aumenta a altura das linhas
        
        # Configuração para a coluna de ações
        style.configure("ActionColumn.Treeview.Cell", font=("Segoe UI", 14))
        
        # Estilo para o sidebar
        style.configure("Sidebar.TFrame", background="#f0f0f0")
        
        # Estilo para os botões do sidebar
        style.configure("Sidebar.TButton", font=("Helvetica", 10))
        
        # Estilo para os títulos do sidebar
        style.configure("SidebarTitle.TLabel", font=("Helvetica", 12, "bold"))
        
        # Estilo para o botão de título
        style.configure("Title.TButton", font=("Arial", 16, "bold"))
        
        # Configurar cores para os diferentes tipos de transação
        self.transaction_tree.tag_configure("tag_Despesa", foreground="red")
        self.transaction_tree.tag_configure("tag_Receita", foreground="green")
        self.transaction_tree.tag_configure("tag_Transferência", foreground="blue")

    def setup_ui(self):
        """Configura a interface do usuário para a tela de transações"""
        # Frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de cabeçalho
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Título como botão dropdown com estilo personalizado
        
        # Criar frame para o título com indicador dropdown
        self.title_label_frame = ttk.Frame(self.header_frame)
        self.title_label_frame.pack(side=tk.LEFT)
        
        self.title_button = ttk.Button(
            self.title_label_frame, 
            textvariable=self.transaction_type_menu,
            command=self.show_transaction_menu
        )
        self.title_button.pack(side=tk.LEFT)
        
        # Indicador de dropdown
        ttk.Label(self.title_label_frame, text="▼", font=("Arial", 12)).pack(side=tk.LEFT, padx=(2, 0))
        
        # Criar o menu dropdown para o botão de título
        self.transaction_menu = tk.Menu(self.header_frame, tearoff=0)
        self.transaction_menu.add_command(label="Todas", command=lambda: self.filter_by_transaction_type("Todas"))
        self.transaction_menu.add_command(label="Despesas", command=lambda: self.filter_by_transaction_type("Despesa"))
        self.transaction_menu.add_command(label="Receitas", command=lambda: self.filter_by_transaction_type("Receita"))
        self.transaction_menu.add_command(label="Transferências", command=lambda: self.filter_by_transaction_type("Transferência"))

        # Botão de filtro no canto superior direito
        self.filter_button = ttk.Button(self.header_frame, text="Filtros", 
                                    command=self.show_filter_sidebar)
        self.filter_button.pack(side=tk.RIGHT, padx=5)

        # Frame para o painel de filtros (inicialmente oculto)
        self.filter_panel = ttk.LabelFrame(self.main_frame, text="Filtros")
        
        # Elementos do painel de filtro
        filter_grid = ttk.Frame(self.filter_panel)
        filter_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Filtro por data
        ttk.Label(filter_grid, text="Data:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_from = DateEntry(filter_grid, width=10, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_from.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(filter_grid, text="até").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.date_to = DateEntry(filter_grid, width=10, background='darkblue',
                               foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_to.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Filtro por tipo
        ttk.Label(filter_grid, text="Tipo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.filter_type_var = tk.StringVar(value="Todos")
        self.type_combo = ttk.Combobox(filter_grid, textvariable=self.filter_type_var, width=15)
        self.type_combo['values'] = ["Todos", "Receita", "Despesa", "Transferência"]
        self.type_combo.current(0)
        self.type_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Filtro por categoria
        ttk.Label(filter_grid, text="Categoria:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_grid, width=15)
        self.filter_category['values'] = self.get_categories()
        self.filter_category.current(0)
        self.filter_category.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Filtro por banco
        ttk.Label(filter_grid, text="Banco:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.filter_bank = ttk.Combobox(filter_grid, width=15)
        self.filter_bank['values'] = ["Todos"]
        self.filter_bank.current(0)
        self.filter_bank.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Campo de pesquisa
        ttk.Label(filter_grid, text="Pesquisar:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.search_entry = ttk.Entry(filter_grid, width=15)
        self.search_entry.grid(row=2, column=3, sticky="ew", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_transactions)
        
        # Botões de filtro
        button_frame = ttk.Frame(self.filter_panel)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Aplicar", command=self.apply_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar", command=self.clear_filters).pack(side=tk.LEFT, padx=5)

        # Lista de transações
        self.transaction_frame = ttk.Frame(self.main_frame)
        self.transaction_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview para mostrar as transações com as colunas solicitadas
        columns = ("situacao", "data", "descricao", "categoria", "conta", "valor", "acoes")
        self.transaction_tree = ttk.Treeview(self.transaction_frame, columns=columns, show="headings")
        
        # Definir cabeçalhos
        self.transaction_tree.heading("situacao", text="Situação")
        self.transaction_tree.heading("data", text="Data")
        self.transaction_tree.heading("descricao", text="Descrição")
        self.transaction_tree.heading("categoria", text="Categoria")
        self.transaction_tree.heading("conta", text="Conta")
        self.transaction_tree.heading("valor", text="Valor")
        self.transaction_tree.heading("acoes", text="Ações")
        
        # Definir largura das colunas
        self.transaction_tree.column("situacao", width=80)
        self.transaction_tree.column("data", width=80)
        self.transaction_tree.column("descricao", width=200)
        self.transaction_tree.column("categoria", width=100)
        self.transaction_tree.column("conta", width=100)
        self.transaction_tree.column("valor", width=80)
        self.transaction_tree.column("acoes", width=150)  # Aumentada para 150
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(self.transaction_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscroll=scrollbar.set)
        
        # Empacotar a árvore e a scrollbar
        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Adicionar menu de contexto para a árvore
        self.context_menu = tk.Menu(self.transaction_tree, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.edit_selected)
        self.context_menu.add_command(label="Anexar documento", command=self.attach_document)
        self.context_menu.add_command(label="Ver documento", command=self.view_document)
        self.context_menu.add_command(label="Excluir", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Marcar como pago/recebido", command=lambda: self.change_transaction_status("Pago"))
        self.context_menu.add_command(label="Marcar como pendente", command=lambda: self.change_transaction_status("Pendente"))
        self.context_menu.add_command(label="Marcar como cancelado", command=lambda: self.change_transaction_status("Cancelado"))
        
        # Vincular o clique direito ao menu de contexto
        self.transaction_tree.bind("<Button-3>", self.show_context_menu)
        # Vincular duplo clique para editar
        self.transaction_tree.bind("<Double-1>", lambda e: self.edit_selected())
        # Vincular clique em botões na coluna de ações
        self.transaction_tree.bind("<Button-1>", self.handle_action_click)
        
        # Formulário para editar transações
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Editar Transação")
        
        # Grid para o formulário
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Data
        ttk.Label(form_grid, text="Data:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_form_entry = DateEntry(form_grid, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_form_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Tipo
        ttk.Label(form_grid, text="Tipo:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.transaction_type_var = tk.StringVar(value="Despesa")
        type_combo = ttk.Combobox(form_grid, textvariable=self.transaction_type_var, width=10, state="readonly")
        type_combo['values'] = ["Despesa", "Receita", "Transferência"]
        type_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Situação
        ttk.Label(form_grid, text="Situação:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.situacao_var = tk.StringVar(value="Pendente")
        situacao_combo = ttk.Combobox(form_grid, textvariable=self.situacao_var, width=10, state="readonly")
        situacao_combo['values'] = ["Pendente", "Pago", "Cancelado"]
        situacao_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Vincular a função ao evento de mudança do tipo de transação
        self.transaction_type_var.trace_add("write", self.on_transaction_type_changed)
        
        # Descrição
        ttk.Label(form_grid, text="Descrição:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.descricao_form_entry = ttk.Entry(form_grid, width=30)
        self.descricao_form_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Valor
        ttk.Label(form_grid, text="Valor (R$):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.valor_form_entry = ttk.Entry(form_grid, width=15)
        self.valor_form_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Banco/Conta
        ttk.Label(form_grid, text="Banco/Conta:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        self.banco_form_entry = ttk.Entry(form_grid, width=15)
        self.banco_form_entry.grid(row=3, column=3, sticky="w", padx=5, pady=5)
        
        # Categoria
        ttk.Label(form_grid, text="Categoria:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.tag_form_entry = ttk.Combobox(form_grid, width=15)
        self.tag_form_entry['values'] = self.get_categories()[1:]  # Excluir "Todas"
        self.tag_form_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Documento
        ttk.Label(form_grid, text="Documento:").grid(row=4, column=2, sticky="w", padx=5, pady=5)
        self.document_path_var = tk.StringVar()
        doc_frame = ttk.Frame(form_grid)
        doc_frame.grid(row=4, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(doc_frame, textvariable=self.document_path_var, width=10).pack(side=tk.LEFT)
        ttk.Button(doc_frame, text="...", width=3, command=self.browse_document).pack(side=tk.LEFT)
        
        # Frame para campos de transferência (inicialmente oculto)
        self.transfer_frame = ttk.Frame(self.form_frame)
        
        ttk.Label(self.transfer_frame, text="De (conta origem):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.from_account_entry = ttk.Entry(self.transfer_frame, width=15)
        self.from_account_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.transfer_frame, text="Para (conta destino):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.to_account_entry = ttk.Entry(self.transfer_frame, width=15)
        self.to_account_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Botões
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="Salvar", command=self.save_transaction)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_edit)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Inicialmente esconder o formulário de edição
        self.form_frame.pack_forget()

    def show_filter_sidebar(self):
        """Exibe o menu lateral de filtros"""
        # Verifica se o sidebar já existe e está visível
        if hasattr(self, 'sidebar_frame') and self.sidebar_frame is not None and self.sidebar_frame.winfo_ismapped():
            self.sidebar_frame.place_forget()  # Esconde o sidebar se já estiver visível
            return
        
        # Cria o frame do sidebar se não existir
        if not hasattr(self, 'sidebar_frame') or self.sidebar_frame is None:
            self.create_sidebar()
        
        # Exibe o sidebar
        self.sidebar_frame.place(relx=1.0, rely=0, anchor="ne", width=250, height=self.winfo_height())
        self.animate_sidebar(True)

    def create_sidebar(self):
        """Cria o menu lateral de filtros"""
        # Frame principal do sidebar
        self.sidebar_frame = ttk.Frame(self, style="Sidebar.TFrame", relief="raised", borderwidth=1)
        
        # Título do sidebar
        sidebar_title = ttk.Label(self.sidebar_frame, text="Filtros", font=("Helvetica", 12, "bold"))
        sidebar_title.pack(pady=10, padx=5)
        
        # Botão para fechar o sidebar
        close_button = ttk.Button(self.sidebar_frame, text="X", width=2, 
                                command=lambda: self.animate_sidebar(False))
        close_button.place(x=5, y=5)
        
        # Adicionar widgets de filtro
        # Filtro por data
        date_frame = ttk.LabelFrame(self.sidebar_frame, text="Período")
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Data inicial
        ttk.Label(date_frame, text="De:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = DateEntry(date_frame, width=10, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Data final
        ttk.Label(date_frame, text="Até:").grid(row=1, column=0, padx=5, pady=5)
        self.end_date_entry = DateEntry(date_frame, width=10, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Filtro por categoria
        category_frame = ttk.LabelFrame(self.sidebar_frame, text="Categorias")
        category_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Lista de categorias (exemplo)
        categories = self.get_categories()
        self.category_var = tk.StringVar(value="Todas")
        
        for i, category in enumerate(categories):
            rb = ttk.Radiobutton(category_frame, text=category, value=category, variable=self.category_var)
            rb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Filtro por status
        status_frame = ttk.LabelFrame(self.sidebar_frame, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        statuses = ["Todos", "Pago", "Pendente", "Cancelado"]
        self.status_var = tk.StringVar(value="Todos")
        
        for status in statuses:
            rb = ttk.Radiobutton(status_frame, text=status, value=status, variable=self.status_var)
            rb.pack(anchor=tk.W, padx=5, pady=2)
        
        # Botão para aplicar filtros
        apply_button = ttk.Button(self.sidebar_frame, text="Aplicar Filtros", 
                                command=self.apply_sidebar_filters)
        apply_button.pack(pady=10)
        
        # Botão para limpar filtros
        clear_button = ttk.Button(self.sidebar_frame, text="Limpar Filtros", 
                                command=self.clear_sidebar_filters)
        clear_button.pack(pady=5)

    def animate_sidebar(self, show=True):
        """Anima a abertura/fechamento do sidebar"""
        if not hasattr(self, 'sidebar_frame') or self.sidebar_frame is None:
            self.create_sidebar()
        
        width = 250  # Largura máxima do sidebar
        
        if show:
            # Mostrar o sidebar
            self.sidebar_frame.place(relx=1.0, rely=0, anchor="ne", height=self.winfo_height())
            
            # Animar a abertura
            for w in range(0, width + 1, 10):
                self.sidebar_frame.configure(width=w)
                self.update()
                time.sleep(0.01)
        else:
            # Animar o fechamento
            for w in range(width, -1, -10):
                self.sidebar_frame.configure(width=w)
                self.update()
                time.sleep(0.01)
            
            # Esconder o sidebar
            self.sidebar_frame.place_forget()

    def apply_sidebar_filters(self):
        """Aplica os filtros selecionados no sidebar"""
        # Implementar a lógica de filtro aqui
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        category = self.category_var.get()
        status = self.status_var.get()
        
        # Filtrar os dados com base nos critérios
        filtered_data = self.filter_sidebar_transactions(start_date, end_date, category, status)
        
        # Atualizar a exibição com os dados filtrados
        self.display_transactions(filtered_data)
        
        # Opcional: esconder o sidebar após aplicar
        self.animate_sidebar(False)

    def clear_sidebar_filters(self):
        """Limpa todos os filtros do sidebar"""
        today = datetime.now()
        self.start_date_entry.set_date(today.replace(day=1))  # Primeiro dia do mês atual
        self.end_date_entry.set_date(today)
        self.category_var.set("Todas")
        self.status_var.set("Todos")
        
        # Restaurar exibição original
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        self.display_transactions(transactions)

    def filter_sidebar_transactions(self, start_date=None, end_date=None, category=None, status=None):
        """Filtra as transações com base nos critérios fornecidos pelo sidebar"""
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        filtered = []
        
        for transaction in transactions:
            # Verificar se passa em todos os filtros
            include = True
            
            # Filtro de data
            if start_date and end_date and "data" in transaction:
                try:
                    date_parts = transaction["data"].split("/")
                    if len(date_parts) == 3:
                        day, month, year = map(int, date_parts)
                        transaction_date = datetime(year, month, day).date()
                        if transaction_date < start_date.date() or transaction_date > end_date.date():
                            include = False
                except Exception as e:
                    print(f"Erro ao processar data: {e}")
                    pass
            
            # Filtro de categoria
            if include and category != "Todas":
                if transaction.get("categoria", "") != category:
                    include = False
            
            # Filtro de status
            if include and status != "Todos":
                if transaction.get("situacao", "") != status:
                    include = False
            
            if include:
                filtered.append(transaction)
        
        return filtered

    def write_json_data(self, data):
        """Escreve os dados no arquivo JSON ou no banco de dados"""
        try:
            if self.database:
                try:
                    # Tente diferentes métodos possíveis para salvar dados
                    if hasattr(self.database, 'save_data'):
                        self.database.save_data(data)
                    elif hasattr(self.database, 'write'):
                        self.database.write(data)
                    elif hasattr(self.database, 'update'):
                        self.database.update(data)
                    else:
                        # Se nenhum método conhecido estiver disponível, salve diretamente no arquivo
                        with open(self.json_file, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=4, ensure_ascii=False)
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar dados no banco de dados: {e}")
            else:
                with open(self.json_file, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo JSON: {e}")

    def update_transaction_display(self, transactions):
        """Atualiza a exibição com as transações filtradas"""
        # Limpar a exibição atual
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Adicionar as transações filtradas
        for i, transaction in enumerate(transactions):
            # Formatar o valor
            valor = transaction.get("valor", 0)
            if isinstance(valor, str):
                try:
                    valor = float(valor.replace("R$", "").replace(".", "").replace(",", ".").strip())
                except:
                    valor = 0
            
            # Formatar o valor como moeda
            valor_formatado = f"R$ {valor:.2f}".replace(".", ",")
            
            # Determinar a cor com base no tipo de transação
            tipo = transaction.get("tipo", "Despesa")
            tag = f"tag_{tipo}"
            
            # Obter a situação
            situacao = transaction.get("situacao", "Pendente")
            
            # Criar os botões de ação como texto (serão tratados no evento de clique)
            acoes = "✏️ 🗑️ 📎"
            
            # Inserir na árvore
            self.transaction_tree.insert("", tk.END, values=(
                situacao,
                transaction.get("data", ""),
                transaction.get("descricao", ""),
                transaction.get("categoria", ""),
                transaction.get("banco", ""),
                valor_formatado,
                acoes
            ), tags=(tag, f"id_{i}"))

    def filter_by_transaction_type(self, tipo):
        """Filtra as transações por tipo (Despesa, Receita, Transferência)"""
        self.transaction_type_menu.set(tipo if tipo != "Todas" else "Transações")
        
        # Carregar todas as transações
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        
        # Filtrar por tipo se não for "Todas"
        if tipo != "Todas":
            transactions = [t for t in transactions if t.get("tipo", "Despesa") == tipo]
        
        # Atualizar a exibição
        self.display_transactions(transactions)

    def show_transaction_menu(self, event=None):
        """Exibe o menu dropdown de tipos de transação"""
        # Obter a posição do botão de título
        x = self.title_button.winfo_rootx()
        y = self.title_button.winfo_rooty() + self.title_button.winfo_height()
        
        # Exibir o menu na posição correta
        self.transaction_menu.post(x, y)

    def get_categories(self):
        """Retorna a lista de categorias únicas das transações"""
        categories = ["Todas"]  # Começar com "Todas" como opção padrão
        
        # Carregar transações
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        
        # Extrair categorias únicas
        for transaction in transactions:
            category = transaction.get("categoria", "")
            if category and category not in categories:
                categories.append(category)
        
        # Adicionar algumas categorias padrão se não houver muitas
        if len(categories) < 5:
            default_categories = ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação"]
            for cat in default_categories:
                if cat not in categories:
                    categories.append(cat)
        
        return categories

    def on_transaction_type_changed(self, *args):
        """Manipula a alteração do tipo de transação no formulário"""
        tipo = self.transaction_type_var.get()
        
        # Se for transferência, mostrar campos adicionais
        if tipo == "Transferência":
            self.transfer_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.transfer_frame.pack_forget()
        
        # Atualizar rótulos e comportamentos com base no tipo
        if tipo == "Receita":
            self.situacao_var.set("Pendente")  # Valor padrão para receitas
            # Atualizar outras configurações específicas para receitas
        elif tipo == "Despesa":
            self.situacao_var.set("Pendente")  # Valor padrão para despesas
            # Atualizar outras configurações específicas para despesas

    def load_transactions(self):
        """Carrega as transações do arquivo JSON ou do banco de dados"""
        try:
            if self.database:
                try:
                    # Tente diferentes métodos possíveis para carregar dados
                    if hasattr(self.database, 'get_data'):
                        self.despesas = self.database.get_data()
                    elif hasattr(self.database, 'read'):
                        self.despesas = self.database.read()
                    elif hasattr(self.database, 'load'):
                        self.despesas = self.database.load()
                    else:
                        # Se nenhum método conhecido estiver disponível, carregue diretamente do arquivo
                        if os.path.exists(self.json_file):
                            with open(self.json_file, 'r', encoding='utf-8') as file:
                                self.despesas = json.load(file)
                        else:
                            self.despesas = {"despesas": []}
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar dados do banco de dados: {e}")
                    self.despesas = {"despesas": []}
            elif os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    self.despesas = json.load(file)
            else:
                self.despesas = {"despesas": []}
                
            # Garantir que temos uma estrutura válida
            if not isinstance(self.despesas, dict) or "despesas" not in self.despesas:
                if isinstance(self.despesas, list):
                    self.despesas = {"despesas": self.despesas}
                else:
                    self.despesas = {"despesas": []}
            
            # Exibir as transações
            self.display_transactions(self.despesas["despesas"])
            
            # Atualizar os comboboxes de categoria e banco
            self.update_comboboxes()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar transações: {e}")
            self.despesas = {"despesas": []}

    def update_comboboxes(self):
        """Atualiza os comboboxes com os valores atuais do banco de dados"""
        # Atualizar categorias
        categories = self.get_categories()
        self.tag_form_entry['values'] = categories[1:]  # Excluir "Todas"
        self.filter_category['values'] = categories
        
        # Atualizar bancos
        banks = ["Todos"]
        transactions = self.despesas.get("despesas", [])
        
        for transaction in transactions:
            bank = transaction.get("banco", "")
            if bank and bank not in banks:
                banks.append(bank)
        
        self.filter_bank['values'] = banks

    def display_transactions(self, transactions):
        """Exibe as transações na TreeView"""
        # Limpar a exibição atual
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Adicionar as transações à TreeView
        for i, transaction in enumerate(transactions):
            # Formatar o valor
            valor = transaction.get("valor", 0)
            if isinstance(valor, str):
                try:
                    valor = float(valor.replace("R$", "").replace(".", "").replace(",", ".").strip())
                except:
                    valor = 0
            
            # Formatar o valor como moeda
            valor_formatado = f"R$ {valor:.2f}".replace(".", ",")
            
            # Determinar a conta/banco a exibir
            if transaction.get("tipo") == "Transferência":
                conta = f"{transaction.get('conta_origem', '')} → {transaction.get('conta_destino', '')}"
            else:
                conta = transaction.get("banco", "")
            
            # Criar os botões de ação como texto (serão tratados no evento de clique)
            acoes = "✏️ 🗑️ 📎"
            
            # Inserir na árvore com a tag apropriada para colorização
            tag = f"tag_{transaction.get('tipo', 'Despesa')}"
            
            self.transaction_tree.insert("", tk.END, values=(
                transaction.get("situacao", "Pendente"),
                transaction.get("data", ""),
                transaction.get("descricao", ""),
                transaction.get("categoria", ""),
                conta,
                valor_formatado,
                acoes
            ), tags=(tag, f"id_{i}"))

    def handle_action_click(self, event):
        """Trata os cliques nos botões de ação na coluna de ações"""
        # Identificar em qual região foi clicado
        region = self.transaction_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        # Obter o item e a coluna clicados
        item = self.transaction_tree.identify_row(event.y)
        column = self.transaction_tree.identify_column(event.x)
        
        # Se não for a coluna de ações, ignorar
        if column != "#7":  # A coluna de ações é a sétima (#7)
            return
        
        # Obter a posição do clique dentro da célula
        cell_box = self.transaction_tree.bbox(item, column)
        if not cell_box:
            return
        
        # Calcular em qual botão foi clicado (dividindo a largura da célula em 3 partes)
        cell_width = cell_box[2]
        relative_x = event.x - cell_box[0]
        
        # Obter o índice da transação a partir da tag
        tags = self.transaction_tree.item(item, "tags")
        id_tag = next((tag for tag in tags if tag.startswith("id_")), None)
        if not id_tag:
            return
        
        index = int(id_tag.split("_")[1])
        
        # Determinar qual botão foi clicado
        if relative_x < cell_width / 3:  # Editar (primeiro terço)
            self.edit_transaction(index)
        elif relative_x < 2 * cell_width / 3:  # Excluir (segundo terço)
            self.delete_transaction(index)
        else:  # Anexar documento (terceiro terço)
            self.attach_document(index)

    def edit_transaction(self, index):
        """Edita uma transação existente"""
        # Verificar se o índice é válido
        if not 0 <= index < len(self.despesas["despesas"]):
            messagebox.showerror("Erro", "Transação não encontrada.")
            return
        
        # Obter a transação a ser editada
        transaction = self.despesas["despesas"][index]
        
        # Preencher o formulário com os dados da transação
        self.fill_form(transaction)
        
        # Ativar o modo de edição
        self.edit_mode = True
        self.current_edit_index = index
        
        # Exibir o formulário
        self.form_frame.pack(fill=tk.X, padx=10, pady=5, after=self.transaction_frame)
        
        # Atualizar o texto do botão
        self.save_button.configure(text="Atualizar")

    def fill_form(self, transaction):
        """Preenche o formulário com os dados da transação"""
        # Definir a data
        if "data" in transaction:
            try:
                day, month, year = map(int, transaction["data"].split("/"))
                self.date_form_entry.set_date(datetime(year, month, day))
            except:
                # Em caso de erro, usar a data atual
                self.date_form_entry.set_date(datetime.now())
        else:
            self.date_form_entry.set_date(datetime.now())
        
        # Definir o tipo
        self.transaction_type_var.set(transaction.get("tipo", "Despesa"))
        
        # Definir a situação
        self.situacao_var.set(transaction.get("situacao", "Pendente"))
        
        # Definir a descrição
        self.descricao_form_entry.delete(0, tk.END)
        self.descricao_form_entry.insert(0, transaction.get("descricao", ""))
        
        # Definir o valor
        self.valor_form_entry.delete(0, tk.END)
        valor = transaction.get("valor", "")
        if isinstance(valor, (int, float)):
            valor = f"{valor:.2f}".replace(".", ",")
        self.valor_form_entry.insert(0, valor)
        
        # Definir o banco/conta
        self.banco_form_entry.delete(0, tk.END)
        self.banco_form_entry.insert(0, transaction.get("banco", ""))
        
        # Definir a categoria
        self.tag_form_entry.set(transaction.get("categoria", ""))
        
        # Definir o documento
        self.document_path_var.set(os.path.basename(transaction.get("documento", "")))
        
        # Se for transferência, preencher os campos adicionais
        if transaction.get("tipo") == "Transferência":
            self.from_account_entry.delete(0, tk.END)
            self.from_account_entry.insert(0, transaction.get("conta_origem", ""))
            
            self.to_account_entry.delete(0, tk.END)
            self.to_account_entry.insert(0, transaction.get("conta_destino", ""))
            
            # Exibir o frame de transferência
            self.transfer_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            # Esconder o frame de transferência
            self.transfer_frame.pack_forget()

    def delete_transaction(self, index):
        """Exclui uma transação"""
        # Confirmar a exclusão
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?"):
            return
        
        # Verificar se o índice é válido
        if not 0 <= index < len(self.despesas["despesas"]):
            messagebox.showerror("Erro", "Transação não encontrada.")
            return
        
        # Remover a transação
        del self.despesas["despesas"][index]
        
        # Salvar as alterações
        self.write_json_data(self.despesas)
        
        # Atualizar a exibição
        self.display_transactions(self.despesas["despesas"])
        
        # Feedback ao usuário
        messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")

    def attach_document(self, index=None):
        """Anexa um documento à transação selecionada"""
        # Se não foi fornecido um índice, usar o índice de edição atual
        if index is None:
            if self.edit_mode and self.current_edit_index is not None:
                index = self.current_edit_index
            else:
                # Obter o item selecionado na árvore
                selected = self.transaction_tree.selection()
                if not selected:
                    messagebox.showerror("Erro", "Selecione uma transação primeiro.")
                    return
                
                # Obter o índice a partir da tag
                tags = self.transaction_tree.item(selected[0], "tags")
                id_tag = next((tag for tag in tags if tag.startswith("id_")), None)
                if not id_tag:
                    messagebox.showerror("Erro", "Não foi possível identificar a transação.")
                    return
                
                index = int(id_tag.split("_")[1])
        
        # Verificar se o índice é válido
        if not 0 <= index < len(self.despesas["despesas"]):
            messagebox.showerror("Erro", "Transação não encontrada.")
            return
        
        # Abrir diálogo para selecionar o arquivo
        file_path = filedialog.askopenfilename(
            title="Selecionar Documento",
            filetypes=[
                ("Documentos", "*.pdf;*.doc;*.docx;*.jpg;*.jpeg;*.png"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Criar diretório para documentos se não existir
        doc_dir = os.path.join(os.path.dirname(self.json_file), "documentos")
        if not os.path.exists(doc_dir):
            os.makedirs(doc_dir)
        
        # Gerar nome único para o arquivo
        file_ext = os.path.splitext(file_path)[1]
        new_filename = f"doc_{int(time.time())}_{index}{file_ext}"
        new_file_path = os.path.join(doc_dir, new_filename)
        
        try:
            # Copiar o arquivo para o diretório de documentos
            shutil.copy2(file_path, new_file_path)
            
            # Atualizar o caminho do documento na transação
            self.despesas["despesas"][index]["documento"] = new_file_path
            
            # Se estiver no modo de edição, atualizar o campo do formulário
            if self.edit_mode and index == self.current_edit_index:
                self.document_path_var.set(os.path.basename(new_file_path))
            
            # Salvar as alterações
            self.write_json_data(self.despesas)
            
            # Feedback ao usuário
            messagebox.showinfo("Sucesso", "Documento anexado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao anexar documento: {e}")

    def browse_document(self):
        """Abre o diálogo para selecionar um documento no formulário"""
        file_path = filedialog.askopenfilename(
            title="Selecionar Documento",
            filetypes=[
                ("Documentos", "*.pdf;*.doc;*.docx;*.jpg;*.jpeg;*.png"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if file_path:
            self.document_path_var.set(os.path.basename(file_path))
            # Armazenar o caminho completo como um atributo temporário
            self.temp_document_path = file_path

    def view_document(self):
        """Visualiza o documento anexado à transação selecionada"""
        # Obter o item selecionado na árvore
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma transação primeiro.")
            return
        
        # Obter o índice a partir da tag
        tags = self.transaction_tree.item(selected[0], "tags")
        id_tag = next((tag for tag in tags if tag.startswith("id_")), None)
        if not id_tag:
            messagebox.showerror("Erro", "Não foi possível identificar a transação.")
            return
        
        index = int(id_tag.split("_")[1])
        
        # Verificar se o índice é válido
        if not 0 <= index < len(self.despesas["despesas"]):
            messagebox.showerror("Erro", "Transação não encontrada.")
            return
        
        # Verificar se há um documento anexado
        document_path = self.despesas["despesas"][index].get("documento", "")
        if not document_path or not os.path.exists(document_path):
            messagebox.showerror("Erro", "Não há documento anexado a esta transação.")
            return
        
        try:
            # Abrir o documento com o aplicativo padrão do sistema
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(document_path)
            elif system == "Darwin":  # macOS
                subprocess.call(["open", document_path])
            else:  # Linux e outros
                subprocess.call(["xdg-open", document_path])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir o documento: {e}")

    def save_transaction(self):
        """Salva ou atualiza uma transação"""
        try:
            # Obter os dados do formulário
            data = self.date_form_entry.get_date().strftime("%d/%m/%Y")
            tipo = self.transaction_type_var.get()
            situacao = self.situacao_var.get()
            descricao = self.descricao_form_entry.get()
            
            # Validar descrição
            if not descricao:
                messagebox.showerror("Erro", "A descrição é obrigatória.")
                return
            
            # Obter e validar o valor
            valor_str = self.valor_form_entry.get().replace(".", "").replace(",", ".")
            try:
                valor = float(valor_str)
            except:
                messagebox.showerror("Erro", "Valor inválido.")
                return
            
            banco = self.banco_form_entry.get()
            categoria = self.tag_form_entry.get()
            
            # Criar o dicionário da transação
            transaction = {
                "data": data,
                "tipo": tipo,
                "situacao": situacao,
                "descricao": descricao,
                "valor": valor,
                "banco": banco,
                "categoria": categoria
            }
            
            # Se for transferência, adicionar os campos específicos
            if tipo == "Transferência":
                conta_origem = self.from_account_entry.get()
                conta_destino = self.to_account_entry.get()
                
                if not conta_origem or not conta_destino:
                    messagebox.showerror("Erro", "Para transferências, as contas de origem e destino são obrigatórias.")
                    return
                
                transaction["conta_origem"] = conta_origem
                transaction["conta_destino"] = conta_destino
            
            # Se houver um documento selecionado, processá-lo
            if hasattr(self, 'temp_document_path') and self.temp_document_path:
                # Criar diretório para documentos se não existir
                doc_dir = os.path.join(os.path.dirname(self.json_file), "documentos")
                if not os.path.exists(doc_dir):
                    os.makedirs(doc_dir)
                
                # Gerar nome único para o arquivo
                file_ext = os.path.splitext(self.temp_document_path)[1]
                timestamp = int(time.time())
                index = self.current_edit_index if self.edit_mode else len(self.despesas["despesas"])
                new_filename = f"doc_{timestamp}_{index}{file_ext}"
                new_file_path = os.path.join(doc_dir, new_filename)
                
                # Copiar o arquivo para o diretório de documentos
                shutil.copy2(self.temp_document_path, new_file_path)
                
                # Adicionar o caminho do documento à transação
                transaction["documento"] = new_file_path
                
                # Limpar o caminho temporário
                self.temp_document_path = None
            
            # Se estiver no modo de edição, atualizar a transação existente
            if self.edit_mode:
                # Preservar o documento existente se não foi alterado
                if "documento" not in transaction and "documento" in self.despesas["despesas"][self.current_edit_index]:
                    transaction["documento"] = self.despesas["despesas"][self.current_edit_index]["documento"]
                
                self.despesas["despesas"][self.current_edit_index] = transaction
            else:
                # Adicionar nova transação
                self.despesas["despesas"].append(transaction)
            
            # Salvar as alterações
            self.write_json_data(self.despesas)
            
            # Atualizar a exibição
            self.display_transactions(self.despesas["despesas"])
            
            # Limpar o formulário e escondê-lo
            self.cancel_edit()
            
            # Feedback ao usuário
            action = "atualizada" if self.edit_mode else "adicionada"
            messagebox.showinfo("Sucesso", f"Transação {action} com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar a transação: {e}")

    def cancel_edit(self):
        """Cancela a edição e esconde o formulário"""
        self.form_frame.pack_forget()
        self.edit_mode = False
        self.current_edit_index = None
        
        # Limpar os campos do formulário
        self.date_form_entry.set_date(datetime.now())
        self.transaction_type_var.set("Despesa")
        self.situacao_var.set("Pendente")
        self.descricao_form_entry.delete(0, tk.END)
        self.valor_form_entry.delete(0, tk.END)
        self.banco_form_entry.delete(0, tk.END)
        self.tag_form_entry.set("")
        self.document_path_var.set("")
        
        # Limpar os campos de transferência
        self.from_account_entry.delete(0, tk.END)
        self.to_account_entry.delete(0, tk.END)
        
        # Esconder o frame de transferência
        self.transfer_frame.pack_forget()
        
        # Restaurar o texto do botão
        self.save_button.configure(text="Salvar")

    def edit_selected(self):
        """Edita a transação selecionada na TreeView"""
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma transação para editar.")
            return
        
        # Obter o índice a partir da tag
        tags = self.transaction_tree.item(selected[0], "tags")
        id_tag = next((tag for tag in tags if tag.startswith("id_")), None)
        if not id_tag:
            messagebox.showerror("Erro", "Não foi possível identificar a transação.")
            return
        
        index = int(id_tag.split("_")[1])
        self.edit_transaction(index)

    def delete_selected(self):
        """Exclui a transação selecionada na TreeView"""
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma transação para excluir.")
            return
        
        # Obter o índice a partir da tag
        tags = self.transaction_tree.item(selected[0], "tags")
        id_tag = next((tag for tag in tags if tag.startswith("id_")), None)
        if not id_tag:
            messagebox.showerror("Erro", "Não foi possível identificar a transação.")
            return
        
        index = int(id_tag.split("_")[1])
        self.delete_transaction(index)

    def change_transaction_status(self, status):
        """Altera o status da transação selecionada"""
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma transação primeiro.")
            return
        
        # Obter o índice a partir da tag
        tags = self.transaction_tree.item(selected[0], "tags")
        id_tag = next((tag for tag in tags if tag.startswith("id_")), None)
        if not id_tag:
            messagebox.showerror("Erro", "Não foi possível identificar a transação.")
            return
        
        index = int(id_tag.split("_")[1])
        
        # Verificar se o índice é válido
        if not 0 <= index < len(self.despesas["despesas"]):
            messagebox.showerror("Erro", "Transação não encontrada.")
            return
        
        # Atualizar o status
        self.despesas["despesas"][index]["situacao"] = status
        
        # Salvar as alterações
        self.write_json_data(self.despesas)
        
        # Atualizar a exibição
        self.display_transactions(self.despesas["despesas"])
        
        # Feedback ao usuário
        messagebox.showinfo("Sucesso", f"Status alterado para '{status}' com sucesso!")

    def show_context_menu(self, event):
        """Exibe o menu de contexto ao clicar com o botão direito na TreeView"""
        # Selecionar o item sob o cursor
        item = self.transaction_tree.identify_row(event.y)
        if item:
            # Selecionar o item
            self.transaction_tree.selection_set(item)
            
            # Exibir o menu de contexto
            self.context_menu.post(event.x_root, event.y_root)

    def search_transactions(self, event=None):
        """Pesquisa transações com base no texto inserido"""
        search_text = self.search_entry.get().lower()
        
        if not search_text:
            # Se o campo de pesquisa estiver vazio, mostrar todas as transações
            self.display_transactions(self.despesas["despesas"])
            return
        
        # Filtrar as transações que correspondem ao texto de pesquisa
        filtered = []
        for transaction in self.despesas["despesas"]:
            # Verificar em vários campos
            if (search_text in transaction.get("descricao", "").lower() or
                search_text in transaction.get("categoria", "").lower() or
                search_text in transaction.get("banco", "").lower() or
                search_text in str(transaction.get("valor", "")).lower()):
                filtered.append(transaction)
        
        # Atualizar a exibição com as transações filtradas
        self.display_transactions(filtered)

    def apply_filters(self):
        """Aplica os filtros selecionados no painel de filtros"""
        # Obter os valores dos filtros
        start_date = self.date_from.get_date()
        end_date = self.date_to.get_date()
        tipo = self.filter_type_var.get()
        categoria = self.filter_category.get()
        banco = self.filter_bank.get()
        search_text = self.search_entry.get().lower()
        
        # Filtrar as transações
        filtered = []
        
        # Este é um resumo do histórico de chat como um recapitulativo: 
        for transaction in self.despesas["despesas"]:
            # Converter a data da transação para um objeto datetime
            try:
                day, month, year = map(int, transaction.get("data", "01/01/2000").split("/"))
                transaction_date = datetime(year, month, day)
            except:
                # Se a data for inválida, usar uma data antiga para que não seja incluída no filtro
                transaction_date = datetime(1900, 1, 1)
            
            # Verificar se a data está no intervalo
            if not (start_date <= transaction_date <= end_date):
                continue
            
            # Verificar o tipo
            if tipo != "Todas" and transaction.get("tipo", "Despesa") != tipo:
                continue
            
            # Verificar a categoria
            if categoria != "Todas" and transaction.get("categoria", "") != categoria:
                continue
            
            # Verificar o banco
            if banco != "Todos" and transaction.get("banco", "") != banco:
                continue
            
            # Verificar o texto de pesquisa
            if search_text:
                if not (search_text in transaction.get("descricao", "").lower() or
                        search_text in transaction.get("categoria", "").lower() or
                        search_text in transaction.get("banco", "").lower() or
                        search_text in str(transaction.get("valor", "")).lower()):
                    continue
            
            # Se passou por todos os filtros, adicionar à lista filtrada
            filtered.append(transaction)
        
        # Atualizar a exibição com as transações filtradas
        self.display_transactions(filtered)

    def reset_filters(self):
            """Redefine todos os filtros para seus valores padrão"""
            # Redefinir datas
            self.date_from.set_date(datetime(datetime.now().year, datetime.now().month, 1))
            self.date_to.set_date(datetime.now())
            
            # Redefinir tipo
            self.filter_type_var.set("Todas")
            
            # Redefinir categoria
            self.filter_category.set("Todas")
            
            # Redefinir banco
            self.filter_bank.set("Todos")
            
            # Limpar pesquisa
            self.search_entry.delete(0, tk.END)
            
            # Exibir todas as transações
            self.display_transactions(self.despesas["despesas"])

    def toggle_filter_panel(self):
            """Alterna a visibilidade do painel de filtros"""
            if self.filter_frame.winfo_ismapped():
                self.filter_frame.pack_forget()
                self.filter_button.configure(text="Mostrar Filtros")
            else:
                self.filter_frame.pack(fill=tk.X, padx=10, pady=5, after=self.search_frame)
                self.filter_button.configure(text="Ocultar Filtros")

    def toggle_form(self):
            """Alterna a visibilidade do formulário de transação"""
            if self.form_frame.winfo_ismapped():
                self.form_frame.pack_forget()
                self.add_button.configure(text="Nova Transação")
            else:
                # Limpar os campos do formulário
                self.cancel_edit()
                
                # Exibir o formulário
                self.form_frame.pack(fill=tk.X, padx=10, pady=5, after=self.transaction_frame)
                self.add_button.configure(text="Cancelar")

    def export_to_csv(self):
            """Exporta as transações para um arquivo CSV"""
            # Abrir diálogo para selecionar o local de salvamento
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Exportar para CSV"
            )
            
            if not file_path:
                return
            
            try:
                # Obter as transações atualmente exibidas
                displayed_transactions = []
                for item in self.transaction_tree.get_children():
                    values = self.transaction_tree.item(item, "values")
                    tags = self.transaction_tree.item(item, "tags")
                    
                    # Obter o tipo a partir da tag
                    tipo = next((tag.split("_")[1] for tag in tags if tag.startswith("tag_")), "Despesa")
                    
                    # Obter o valor formatado e convertê-lo para float
                    valor_formatado = values[5]  # Índice 5 é o valor
                    valor = float(valor_formatado.replace("R$", "").replace(".", "").replace(",", ".").strip())
                    
                    transaction = {
                        "situacao": values[0],
                        "data": values[1],
                        "descricao": values[2],
                        "categoria": values[3],
                        "banco": values[4],
                        "valor": valor,
                        "tipo": tipo
                    }
                    displayed_transactions.append(transaction)
                
                # Escrever no arquivo CSV
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["data", "tipo", "situacao", "descricao", "categoria", "banco", "valor"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for transaction in displayed_transactions:
                        writer.writerow(transaction)
                
                messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para {file_path}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar para CSV: {e}")

    def import_from_csv(self):
            """Importa transações de um arquivo CSV"""
            # Abrir diálogo para selecionar o arquivo
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Importar de CSV"
            )
            
            if not file_path:
                return
            
            try:
                # Ler o arquivo CSV
                imported_transactions = []
                with open(file_path, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # Converter o valor para float
                        try:
                            valor = float(row.get("valor", "0").replace("R$", "").replace(".", "").replace(",", ".").strip())
                        except:
                            valor = 0
                        
                        # Criar a transação
                        transaction = {
                            "data": row.get("data", ""),
                            "tipo": row.get("tipo", "Despesa"),
                            "situacao": row.get("situacao", "Pendente"),
                            "descricao": row.get("descricao", ""),
                            "categoria": row.get("categoria", ""),
                            "banco": row.get("banco", ""),
                            "valor": valor
                        }
                        imported_transactions.append(transaction)
                
                # Perguntar se deve substituir ou adicionar
                if messagebox.askyesno("Importar", "Deseja substituir as transações existentes? Selecione 'Não' para adicionar às existentes."):
                    self.despesas["despesas"] = imported_transactions
                else:
                    self.despesas["despesas"].extend(imported_transactions)
                
                # Salvar as alterações
                self.write_json_data(self.despesas)
                
                # Atualizar a exibição
                self.display_transactions(self.despesas["despesas"])
                
                # Atualizar os comboboxes
                self.update_comboboxes()
                
                # Feedback ao usuário
                messagebox.showinfo("Sucesso", f"Importados {len(imported_transactions)} registros com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar do CSV: {e}")

    def write_json_data(self, data):
            """Escreve os dados no arquivo JSON ou no banco de dados"""
            try:
                if self.database:
                    try:
                        # Tente diferentes métodos possíveis para salvar dados
                        if hasattr(self.database, 'save_data'):
                            self.database.save_data(data)
                        elif hasattr(self.database, 'write'):
                            self.database.write(data)
                        elif hasattr(self.database, 'save'):
                            self.database.save(data)
                        else:
                            # Se nenhum método conhecido estiver disponível, salve diretamente no arquivo
                            with open(self.json_file, 'w', encoding='utf-8') as file:
                                json.dump(data, file, ensure_ascii=False, indent=4)
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao salvar dados no banco de dados: {e}")
                else:
                    with open(self.json_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar os dados: {e}")

    def calculate_summary(self):
            """Calcula o resumo financeiro das transações exibidas"""
            # Obter as transações atualmente exibidas
            displayed_transactions = []
            for item in self.transaction_tree.get_children():
                values = self.transaction_tree.item(item, "values")
                tags = self.transaction_tree.item(item, "tags")
                
                # Obter o tipo a partir da tag
                tipo = next((tag.split("_")[1] for tag in tags if tag.startswith("tag_")), "Despesa")
                
                # Obter o valor formatado e convertê-lo para float
                valor_formatado = values[5]  # Índice 5 é o valor
                valor = float(valor_formatado.replace("R$", "").replace(".", "").replace(",", ".").strip())
                
                transaction = {
                    "situacao": values[0],
                    "data": values[1],
                    "descricao": values[2],
                    "categoria": values[3],
                    "banco": values[4],
                    "valor": valor,
                    "tipo": tipo
                }
                displayed_transactions.append(transaction)
            
            # Calcular totais
            total_receitas = sum(t["valor"] for t in displayed_transactions if t["tipo"] == "Receita")
            total_despesas = sum(t["valor"] for t in displayed_transactions if t["tipo"] == "Despesa")
            saldo = total_receitas - total_despesas
            
            # Calcular totais por categoria
            categorias = {}
            for t in displayed_transactions:
                categoria = t["categoria"]
                if categoria not in categorias:
                    categorias[categoria] = {"Receita": 0, "Despesa": 0, "Transferência": 0}
                
                categorias[categoria][t["tipo"]] += t["valor"]
            
            # Calcular totais por banco
            bancos = {}
            for t in displayed_transactions:
                banco = t["banco"]
                if banco not in bancos:
                    bancos[banco] = {"Receita": 0, "Despesa": 0, "Transferência": 0}
                
                bancos[banco][t["tipo"]] += t["valor"]
            
            # Exibir o resumo em uma nova janela
            self.show_summary_window(total_receitas, total_despesas, saldo, categorias, bancos)

    def show_summary_window(self, total_receitas, total_despesas, saldo, categorias, bancos):
        """Exibe uma janela com o resumo financeiro"""
        # Criar uma nova janela
        summary_window = tk.Toplevel(self.master)
        summary_window.title("Resumo Financeiro")
        summary_window.geometry("700x550")
        summary_window.minsize(700, 550)
        
        # Adicionar um notebook (abas)
        notebook = ttk.Notebook(summary_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de resumo geral
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="Resumo Geral")
        
        # Exibir totais
        ttk.Label(general_tab, text="Resumo Financeiro", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Frame para os totais
        totals_frame = ttk.Frame(general_tab)
        totals_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Estilo para os valores
        style = ttk.Style()
        style.configure("Green.TLabel", foreground="green")
        style.configure("Red.TLabel", foreground="red")
        style.configure("Black.TLabel", foreground="black")
        style.configure("Bold.TLabel", font=("Helvetica", 12, "bold"))
        
        # Receitas
        ttk.Label(totals_frame, text="Total de Receitas:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(totals_frame, text=f"R$ {total_receitas:.2f}".replace(".", ","), 
                font=("Helvetica", 12, "bold"), style="Green.TLabel").grid(row=0, column=1, sticky="e", padx=10, pady=5)
        
        # Despesas
        ttk.Label(totals_frame, text="Total de Despesas:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(totals_frame, text=f"R$ {total_despesas:.2f}".replace(".", ","), 
                font=("Helvetica", 12, "bold"), style="Red.TLabel").grid(row=1, column=1, sticky="e", padx=10, pady=5)
        
        # Saldo
        ttk.Label(totals_frame, text="Saldo:", font=("Helvetica", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        saldo_style = "Green.TLabel" if saldo >= 0 else "Red.TLabel"
        ttk.Label(totals_frame, text=f"R$ {saldo:.2f}".replace(".", ","), 
                font=("Helvetica", 12, "bold"), style=saldo_style).grid(row=2, column=1, sticky="e", padx=10, pady=5)
        
        # Separador
        ttk.Separator(general_tab, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # Gráfico de pizza para a distribuição de despesas por categoria
        if matplotlib_available:
            try:
                # Preparar dados para o gráfico
                despesas_por_categoria = {cat: valores["Despesa"] for cat, valores in categorias.items() if valores["Despesa"] > 0}
                
                if despesas_por_categoria:
                    # Criar figura para o gráfico
                    fig = Figure(figsize=(6, 4), dpi=100)
                    ax = fig.add_subplot(111)
                    
                    # Criar gráfico de pizza
                    labels = list(despesas_por_categoria.keys())
                    values = list(despesas_por_categoria.values())
                    
                    # Ordenar por valor para melhor visualização
                    sorted_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
                    labels = [labels[i] for i in sorted_indices]
                    values = [values[i] for i in sorted_indices]
                    
                    # Limitar o número de categorias mostradas diretamente
                    max_categories = 7
                    if len(labels) > max_categories:
                        other_sum = sum(values[max_categories:])
                        labels = labels[:max_categories] + ["Outros"]
                        values = values[:max_categories] + [other_sum]
                    
                    # Criar o gráfico
                    wedges, texts, autotexts = ax.pie(
                        values, 
                        labels=None,  # Não mostrar labels diretamente no gráfico
                        autopct='%1.1f%%',
                        startangle=90,
                        shadow=False
                    )
                    
                    # Ajustar propriedades dos textos de porcentagem
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontsize(9)
                    
                    # Adicionar legenda
                    ax.legend(wedges, labels, title="Categorias", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
                    
                    ax.set_title("Distribuição de Despesas por Categoria")
                    ax.axis('equal')  # Para que o gráfico seja um círculo
                    
                    # Incorporar o gráfico no tkinter
                    canvas = FigureCanvasTkAgg(fig, master=general_tab)
                    canvas.draw()
                    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            except Exception as e:
                print(f"Erro ao criar gráfico: {e}")
        
        # Aba de categorias
        categories_tab = ttk.Frame(notebook)
        notebook.add(categories_tab, text="Por Categoria")
        
        # Frame para controles
        cat_control_frame = ttk.Frame(categories_tab)
        cat_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Opção para ordenar
        ttk.Label(cat_control_frame, text="Ordenar por:").pack(side=tk.LEFT, padx=5)
        cat_sort_var = tk.StringVar(value="Categoria")
        cat_sort_combo = ttk.Combobox(cat_control_frame, textvariable=cat_sort_var, 
                                    values=["Categoria", "Receitas", "Despesas", "Saldo"], 
                                    state="readonly", width=10)
        cat_sort_combo.pack(side=tk.LEFT, padx=5)
        
        # Direção da ordenação
        cat_sort_dir_var = tk.BooleanVar(value=True)  # True = ascendente
        cat_sort_dir_check = ttk.Checkbutton(cat_control_frame, text="Crescente", variable=cat_sort_dir_var)
        cat_sort_dir_check.pack(side=tk.LEFT, padx=5)
        
        # Criar TreeView para categorias
        cat_tree = ttk.Treeview(categories_tab, columns=("categoria", "receitas", "despesas", "saldo"), show="headings")
        cat_tree.heading("categoria", text="Categoria")
        cat_tree.heading("receitas", text="Receitas")
        cat_tree.heading("despesas", text="Despesas")
        cat_tree.heading("saldo", text="Saldo")
        
        cat_tree.column("categoria", width=200)
        cat_tree.column("receitas", width=120, anchor="e")
        cat_tree.column("despesas", width=120, anchor="e")
        cat_tree.column("saldo", width=120, anchor="e")
        
        cat_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Adicionar scrollbar
        cat_scrollbar = ttk.Scrollbar(categories_tab, orient="vertical", command=cat_tree.yview)
        cat_scrollbar.pack(side="right", fill="y")
        cat_tree.configure(yscrollcommand=cat_scrollbar.set)
        
        # Função para atualizar a TreeView de categorias com ordenação
        def update_cat_tree():
            # Limpar a TreeView
            for item in cat_tree.get_children():
                cat_tree.delete(item)
            
            # Preparar dados para ordenação
            cat_data = []
            for categoria, valores in categorias.items():
                receitas = valores["Receita"]
                despesas = valores["Despesa"]
                saldo_cat = receitas - despesas
                cat_data.append((categoria, receitas, despesas, saldo_cat))
            
            # Ordenar dados
            sort_column = cat_sort_var.get()
            reverse = not cat_sort_dir_var.get()  # True = descendente
            
            if sort_column == "Categoria":
                cat_data.sort(key=lambda x: x[0], reverse=reverse)
            elif sort_column == "Receitas":
                cat_data.sort(key=lambda x: x[1], reverse=reverse)
            elif sort_column == "Despesas":
                cat_data.sort(key=lambda x: x[2], reverse=reverse)
            elif sort_column == "Saldo":
                cat_data.sort(key=lambda x: x[3], reverse=reverse)
            
            # Preencher a TreeView
            for categoria, receitas, despesas, saldo_cat in cat_data:
                item_id = cat_tree.insert("", tk.END, values=(
                    categoria,
                    f"R$ {receitas:.2f}".replace(".", ","),
                    f"R$ {despesas:.2f}".replace(".", ","),
                    f"R$ {saldo_cat:.2f}".replace(".", ",")
                ))
                
                # Aplicar cor ao saldo
                if saldo_cat < 0:
                    cat_tree.tag_configure("negative", foreground="red")
                    cat_tree.item(item_id, tags=("negative",))
                elif saldo_cat > 0:
                    cat_tree.tag_configure("positive", foreground="green")
                    cat_tree.item(item_id, tags=("positive",))
        
        # Vincular a função de atualização aos controles
        cat_sort_combo.bind("<<ComboboxSelected>>", lambda e: update_cat_tree())
        cat_sort_dir_check.configure(command=update_cat_tree)
        
        # Preencher a TreeView inicialmente
        update_cat_tree()
        
        # Aba de bancos
        banks_tab = ttk.Frame(notebook)
        notebook.add(banks_tab, text="Por Banco")
        
        # Frame para controles
        bank_control_frame = ttk.Frame(banks_tab)
        bank_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Opção para ordenar
        ttk.Label(bank_control_frame, text="Ordenar por:").pack(side=tk.LEFT, padx=5)
        bank_sort_var = tk.StringVar(value="Banco")
        bank_sort_combo = ttk.Combobox(bank_control_frame, textvariable=bank_sort_var, 
                                    values=["Banco", "Receitas", "Despesas", "Saldo"], 
                                    state="readonly", width=10)
        bank_sort_combo.pack(side=tk.LEFT, padx=5)
        
        # Direção da ordenação
        bank_sort_dir_var = tk.BooleanVar(value=True)  # True = ascendente
        bank_sort_dir_check = ttk.Checkbutton(bank_control_frame, text="Crescente", variable=bank_sort_dir_var)
        bank_sort_dir_check.pack(side=tk.LEFT, padx=5)
        
        # Criar TreeView para bancos
        bank_tree = ttk.Treeview(banks_tab, columns=("banco", "receitas", "despesas", "saldo"), show="headings")
        bank_tree.heading("banco", text="Banco/Conta")
        bank_tree.heading("receitas", text="Receitas")
        bank_tree.heading("despesas", text="Despesas")
        bank_tree.heading("saldo", text="Saldo")
        
        bank_tree.column("banco", width=200)
        bank_tree.column("receitas", width=120, anchor="e")
        bank_tree.column("despesas", width=120, anchor="e")
        bank_tree.column("saldo", width=120, anchor="e")
        
        bank_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Adicionar scrollbar
        bank_scrollbar = ttk.Scrollbar(banks_tab, orient="vertical", command=bank_tree.yview)
        bank_scrollbar.pack(side="right", fill="y")
        bank_tree.configure(yscrollcommand=bank_scrollbar.set)
        
        # Função para atualizar a TreeView de bancos com ordenação
        def update_bank_tree():
            # Limpar a TreeView
            for item in bank_tree.get_children():
                bank_tree.delete(item)
            
            # Preparar dados para ordenação
            bank_data = []
            for banco, valores in bancos.items():
                receitas = valores["Receita"]
                despesas = valores["Despesa"]
                saldo_banco = receitas - despesas
                bank_data.append((banco, receitas, despesas, saldo_banco))
            
            # Ordenar dados
            sort_column = bank_sort_var.get()
            reverse = not bank_sort_dir_var.get()  # True = descendente
            
            if sort_column == "Banco":
                bank_data.sort(key=lambda x: x[0], reverse=reverse)
            elif sort_column == "Receitas":
                bank_data.sort(key=lambda x: x[1], reverse=reverse)
            elif sort_column == "Despesas":
                bank_data.sort(key=lambda x: x[2], reverse=reverse)
            elif sort_column == "Saldo":
                bank_data.sort(key=lambda x: x[3], reverse=reverse)
            
            # Preencher a TreeView
            for banco, receitas, despesas, saldo_banco in bank_data:
                item_id = bank_tree.insert("", tk.END, values=(
                    banco,
                    f"R$ {receitas:.2f}".replace(".", ","),
                    f"R$ {despesas:.2f}".replace(".", ","),
                    f"R$ {saldo_banco:.2f}".replace(".", ",")
                ))
                
                # Aplicar cor ao saldo
                if saldo_banco < 0:
                    bank_tree.tag_configure("negative", foreground="red")
                    bank_tree.item(item_id, tags=("negative",))
                elif saldo_banco > 0:
                    bank_tree.tag_configure("positive", foreground="green")
                    bank_tree.item(item_id, tags=("positive",))
        
        # Vincular a função de atualização aos controles
        bank_sort_combo.bind("<<ComboboxSelected>>", lambda e: update_bank_tree())
        bank_sort_dir_check.configure(command=update_bank_tree)
        
        # Preencher a TreeView inicialmente
        update_bank_tree()
        
        # Aba de gráficos
        if matplotlib_available:
            try:
                charts_tab = ttk.Frame(notebook)
                notebook.add(charts_tab, text="Gráficos")
                
                # Criar um notebook interno para diferentes gráficos
                charts_notebook = ttk.Notebook(charts_tab)
                charts_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Aba para gráfico de barras de receitas vs despesas por categoria
                bar_tab = ttk.Frame(charts_notebook)
                charts_notebook.add(bar_tab, text="Receitas vs Despesas")
                
                # Preparar dados para o gráfico
                cat_names = []
                cat_receitas = []
                cat_despesas = []
                
                # Pegar as top 10 categorias por volume total
                cat_volume = {cat: valores["Receita"] + valores["Despesa"] 
                            for cat, valores in categorias.items()}
                top_cats = sorted(cat_volume.items(), key=lambda x: x[1], reverse=True)[:10]
                top_cat_names = [cat for cat, _ in top_cats]
                
                for cat in top_cat_names:
                    if cat in categorias:
                        cat_names.append(cat)
                        cat_receitas.append(categorias[cat]["Receita"])
                        cat_despesas.append(categorias[cat]["Despesa"])
                
                # Criar figura para o gráfico de barras
                fig_bar = Figure(figsize=(8, 5), dpi=100)
                ax_bar = fig_bar.add_subplot(111)
                
                # Definir largura das barras e posições
                bar_width = 0.35
                x = range(len(cat_names))
                
                # Criar barras
                ax_bar.bar([i - bar_width/2 for i in x], cat_receitas, bar_width, label='Receitas', color='green', alpha=0.7)
                ax_bar.bar([i + bar_width/2 for i in x], cat_despesas, bar_width, label='Despesas', color='red', alpha=0.7)
                
                # Configurar eixos e legendas
                ax_bar.set_xlabel('Categoria')
                ax_bar.set_ylabel('Valor (R$)')
                ax_bar.set_title('Receitas vs Despesas por Categoria')
                ax_bar.set_xticks(x)
                ax_bar.set_xticklabels(cat_names, rotation=45, ha='right')
                ax_bar.legend()
                
                fig_bar.tight_layout()
                
                # Incorporar o gráfico no tkinter
                canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_tab)
                canvas_bar.draw()
                canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                # Aba para gráfico de pizza de bancos
                pie_bank_tab = ttk.Frame(charts_notebook)
                charts_notebook.add(pie_bank_tab, text="Distribuição por Banco")
                
                # Preparar dados para o gráfico
                bank_names = []
                bank_values = []
                
                for banco, valores in bancos.items():
                    bank_names.append(banco)
                    bank_values.append(valores["Receita"] - valores["Despesa"])  # Saldo
                
                # Criar figura para o gráfico de pizza
                fig_pie_bank = Figure(figsize=(6, 5), dpi=100)
                ax_pie_bank = fig_pie_bank.add_subplot(111)
                
                # Separar valores positivos e negativos
                pos_banks = [(name, val) for name, val in zip(bank_names, bank_values) if val > 0]
                neg_banks = [(name, abs(val)) for name, val in zip(bank_names, bank_values) if val < 0]
                
                pos_names = [b[0] for b in pos_banks]
                pos_values = [b[1] for b in pos_banks]
                neg_names = [b[0] for b in neg_banks]
                neg_values = [b[1] for b in neg_banks]
                
                # Criar dois gráficos de pizza lado a lado
                if pos_values:
                    ax_pie_bank.pie(
                        pos_values,
                        labels=pos_names,
                        autopct='%1.1f%%',
                        startangle=90,
                        shadow=False,
                        wedgeprops=dict(width=0.5),
                        textprops={'fontsize': 9},
                        colors=plt.cm.Greens(np.linspace(0.5, 0.8, len(pos_values)))
                    )
                
                ax_pie_bank.set_title("Distribuição de Saldo por Banco")
                ax_pie_bank.axis('equal')
                
                # Incorporar o gráfico no tkinter
                canvas_pie_bank = FigureCanvasTkAgg(fig_pie_bank, master=pie_bank_tab)
                canvas_pie_bank.draw()
                canvas_pie_bank.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                print(f"Erro ao criar gráficos: {e}")
        
        # Frame para botões na parte inferior
        button_frame = ttk.Frame(summary_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botão para exportar o resumo
        def export_summary():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Exportar Resumo"
            )
            
            if file_path:
                try:
                    # Criar um PDF com o resumo
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib import colors
                    
                    doc = SimpleDocTemplate(file_path, pagesize=letter)
                    styles = getSampleStyleSheet()
                    elements = []
                    
                    # Título
                    title_style = styles["Title"]
                    elements.append(Paragraph("Resumo Financeiro", title_style))
                    elements.append(Spacer(1, 12))
                    
                    # Resumo geral
                    elements.append(Paragraph("Resumo Geral", styles["Heading2"]))
                    elements.append(Spacer(1, 6))
                    
                    data = [
                        ["Total de Receitas:", f"R$ {total_receitas:.2f}".replace(".", ",")],
                        ["Total de Despesas:", f"R$ {total_despesas:.2f}".replace(".", ",")],
                        ["Saldo:", f"R$ {saldo:.2f}".replace(".", ",")]
                    ]
                    
                    t = Table(data, colWidths=[200, 100])
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(t)
                    elements.append(Spacer(1, 12))
                    
                    # Resumo por categoria
                    elements.append(Paragraph("Resumo por Categoria", styles["Heading2"]))
                    elements.append(Spacer(1, 6))
                    
                    # Cabeçalho da tabela
                    cat_data = [["Categoria", "Receitas", "Despesas", "Saldo"]]
                    
                    # Dados das categorias
                    for categoria, valores in categorias.items():
                        receitas = valores["Receita"]
                        despesas = valores["Despesa"]
                        saldo_cat = receitas - despesas
                        cat_data.append([
                            categoria,
                            f"R$ {receitas:.2f}".replace(".", ","),
                            f"R$ {despesas:.2f}".replace(".", ","),
                            f"R$ {saldo_cat:.2f}".replace(".", ",")
                        ])
                    
                    # Criar tabela
                    cat_table = Table(cat_data, colWidths=[200, 100, 100, 100])
                    cat_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(cat_table)
                    elements.append(Spacer(1, 12))
                    
                    # Resumo por banco
                    elements.append(Paragraph("Resumo por Banco", styles["Heading2"]))
                    elements.append(Spacer(1, 6))
                    
                    # Cabeçalho da tabela
                    bank_data = [["Banco/Conta", "Receitas", "Despesas", "Saldo"]]
                    
                    # Dados dos bancos
                    for banco, valores in bancos.items():
                        receitas = valores["Receita"]
                        despesas = valores["Despesa"]
                        saldo_banco = receitas - despesas
                        bank_data.append([
                            banco,
                            f"R$ {receitas:.2f}".replace(".", ","),
                            f"R$ {despesas:.2f}".replace(".", ","),
                            f"R$ {saldo_banco:.2f}".replace(".", ",")
                        ])
                    
                    # Criar tabela
                    bank_table = Table(bank_data, colWidths=[200, 100, 100, 100])
                    bank_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(bank_table)
                    
                    # Construir o documento
                    doc.build(elements)
                    
                    messagebox.showinfo("Sucesso", f"Resumo exportado com sucesso para {file_path}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao exportar o resumo: {e}")
        
        # Botão para exportar
        export_button = ttk.Button(button_frame, text="Exportar Resumo", command=export_summary)
        export_button.pack(side=tk.LEFT, padx=5)
        
        # Botão para fechar
        close_button = ttk.Button(button_frame, text="Fechar", command=summary_window.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Centralizar a janela
        summary_window.update_idletasks()
        width = summary_window.winfo_width()
        height = summary_window.winfo_height()
        x = (summary_window.winfo_screenwidth() // 2) - (width // 2)
        y = (summary_window.winfo_screenheight() // 2) - (height // 2)
        summary_window.geometry(f'{width}x{height}+{x}+{y}')

    def clear_filters(self):
        """Limpa todos os filtros aplicados"""
        # Redefinir datas
        self.date_from.set_date(datetime(datetime.now().year, datetime.now().month, 1))
        self.date_to.set_date(datetime.now())
        
        # Redefinir tipo
        self.filter_type_var.set("Todas")
        
        # Redefinir categoria
        self.filter_category.set("Todas")
        
        # Redefinir banco
        self.filter_bank.set("Todos")
        
        # Limpar pesquisa
        self.search_entry.delete(0, tk.END)
        
        # Exibir todas as transações
        self.display_transactions(self.despesas["despesas"])
