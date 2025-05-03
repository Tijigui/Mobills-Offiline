import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import base64
import io

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
        self.search_entry = None
        self.transaction_tree = None
        self.despesas = {"despesas": []}
        self.edit_mode = False
        self.current_edit_index = None
        self.filter_panel_visible = False
        self.filter_panel = None
        self.add_button = None
        self.cancel_button = None
        self.context_menu = None
        
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
        
        # Configurar a interface
        self.setup_ui()
        
        # Empacotar o frame principal para que seja exibido
        self.pack(fill=tk.BOTH, expand=True)
        
        # Garantir que os dados sejam carregados após a interface estar pronta
        self.after(100, self.load_transactions)

    def setup_ui(self):
        """Configura a interface do usuário para a tela de transações"""
        # Frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de cabeçalho
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Título como botão dropdown com estilo personalizado
        style = ttk.Style()
        style.configure("Title.TButton", font=("Arial", 16, "bold"))
        
        # Criar frame para o título com indicador dropdown
        self.title_label_frame = ttk.Frame(self.header_frame)
        self.title_label_frame.pack(side=tk.LEFT)
        
        self.title_button = ttk.Button(
            self.title_label_frame, 
            textvariable=self.transaction_type_menu,
            style="Title.TButton",
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

        # Botão de adicionar transação
        self.add_button = ttk.Button(self.header_frame, text="+ Nova Transação", 
                                    command=self.add_transaction)
        self.add_button.pack(side=tk.RIGHT, padx=5)

        # Botão de cancelar (inicialmente oculto)
        self.cancel_button = ttk.Button(self.header_frame, text="Cancelar", 
                                       command=self.cancel_edit)
        # Não empacotar ainda - será mostrado quando necessário

        # Botão de filtro no canto superior direito
        icon_path = "icons/filter_icon.png"  # Defina o caminho para seu ícone
        self.filter_icon = self.get_filter_icon(icon_path)

        if self.filter_icon:
            self.filter_button = ttk.Button(self.header_frame, image=self.filter_icon, 
                                        command=self.toggle_filter_panel)
        else:
            # Fallback para texto se o ícone não puder ser carregado
            self.filter_button = ttk.Button(self.header_frame, text="Filtro", 
                                        command=self.toggle_filter_panel)
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
        
        # Treeview para mostrar as transações
        columns = ("data", "tipo", "descricao", "valor", "banco", "categoria")
        self.transaction_tree = ttk.Treeview(self.transaction_frame, columns=columns, show="headings")
        
        # Definir cabeçalhos
        self.transaction_tree.heading("data", text="Data")
        self.transaction_tree.heading("tipo", text="Tipo")
        self.transaction_tree.heading("descricao", text="Descrição")
        self.transaction_tree.heading("valor", text="Valor")
        self.transaction_tree.heading("banco", text="Banco/Conta")
        self.transaction_tree.heading("categoria", text="Categoria")
        
        # Definir largura das colunas
        self.transaction_tree.column("data", width=80)
        self.transaction_tree.column("tipo", width=80)
        self.transaction_tree.column("descricao", width=200)
        self.transaction_tree.column("valor", width=80)
        self.transaction_tree.column("banco", width=100)
        self.transaction_tree.column("categoria", width=100)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(self.transaction_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscroll=scrollbar.set)
        
        # Empacotar a árvore e a scrollbar
        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Adicionar menu de contexto para a árvore
        self.context_menu = tk.Menu(self.transaction_tree, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.edit_selected)
        self.context_menu.add_command(label="Excluir", command=self.delete_selected)
        
        # Vincular o clique direito ao menu de contexto
        self.transaction_tree.bind("<Button-3>", self.show_context_menu)
        
        # Formulário para adicionar/editar transações
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Nova Transação")
        self.form_frame.pack(fill=tk.X, padx=10, pady=10)
        
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
        
        # Vincular a função ao evento de mudança do tipo de transação
        self.transaction_type_var.trace_add("write", self.on_transaction_type_changed)
        
        # Descrição
        ttk.Label(form_grid, text="Descrição:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.descricao_form_entry = ttk.Entry(form_grid, width=30)
        self.descricao_form_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Valor
        ttk.Label(form_grid, text="Valor (R$):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.valor_form_entry = ttk.Entry(form_grid, width=15)
        self.valor_form_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Banco/Conta
        ttk.Label(form_grid, text="Banco/Conta:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.banco_form_entry = ttk.Entry(form_grid, width=15)
        self.banco_form_entry.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        # Categoria
        ttk.Label(form_grid, text="Categoria:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.tag_form_entry = ttk.Combobox(form_grid, width=15)
        self.tag_form_entry['values'] = self.get_categories()[1:]  # Excluir "Todas"
        self.tag_form_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Botões
        button_frame = ttk.Frame(self.form_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.save_button = ttk.Button(button_frame, text="Adicionar", command=self.save_transaction)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_edit)
        # Não empacotar ainda - será mostrado quando necessário
    
    def on_transaction_type_changed(self, *args):
        """Ajusta o formulário com base no tipo de transação selecionado"""
        transaction_type = self.transaction_type_var.get()
        
        # Mostrar ou esconder campos específicos para transferências
        if transaction_type == "Transferência":
            if not hasattr(self, 'transfer_frame'):
                # Criar frame para campos de transferência
                self.transfer_frame = ttk.Frame(self.form_frame)
                self.transfer_frame.pack(fill=tk.X, padx=10, pady=5)
                
                ttk.Label(self.transfer_frame, text="De (conta origem):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
                self.from_account_entry = ttk.Entry(self.transfer_frame, width=15)
                self.from_account_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
                
                ttk.Label(self.transfer_frame, text="Para (conta destino):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
                self.to_account_entry = ttk.Entry(self.transfer_frame, width=15)
                self.to_account_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)
            else:
                self.transfer_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            # Esconder campos de transferência se existirem
            if hasattr(self, 'transfer_frame'):
                self.transfer_frame.pack_forget()

    def show_transaction_menu(self):
        """Exibe o menu dropdown quando o botão de título é clicado"""
        # Obter a posição do botão
        x = self.title_button.winfo_rootx()
        y = self.title_button.winfo_rooty() + self.title_button.winfo_height()
        
        # Exibir o menu na posição calculada
        self.transaction_menu.post(x, y)

    def filter_by_transaction_type(self, transaction_type):
        """Filtra as transações pelo tipo selecionado no menu dropdown"""
        # Atualizar o texto do botão
        if transaction_type == "Todas":
            self.transaction_type_menu.set("Transações")
        else:
            self.transaction_type_menu.set(transaction_type)
        
        # Filtrar as transações
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        
        if transaction_type == "Todas":
            # Mostrar todas as transações
            self.display_transactions(transactions)
        else:
            # Filtrar pelo tipo selecionado
            filtered_transactions = [t for t in transactions if t.get("tipo", "") == transaction_type]
            self.display_transactions(filtered_transactions)
    
    def get_filter_icon(self, icon_path=None):
        """
        Carrega um ícone de filtro a partir de um arquivo de imagem
        
        Args:
            icon_path (str, optional): Caminho para o arquivo de imagem do ícone.
                Se None, usa um caminho padrão.
        
        Returns:
            PhotoImage: Objeto de imagem para o ícone, ou None se não for possível carregar
        """
        try:
            # Usar o caminho fornecido ou um caminho padrão
            if icon_path is None:
                # Caminho padrão para o ícone (ajuste conforme necessário)
                icon_path = "icons/filter_button.png"
            
            # Verificar se o arquivo existe
            if not os.path.exists(icon_path):
                print(f"Arquivo de ícone não encontrado: {icon_path}")
                return None
                
            # Carregar e redimensionar o ícone
            icon = Image.open(icon_path)
            icon = icon.resize((20, 20), Image.LANCZOS)
            return ImageTk.PhotoImage(icon)
        except Exception as e:
            print(f"Erro ao carregar ícone de filtro: {e}")
            return None

    def get_categories(self):
        """Retorna uma lista de categorias disponíveis"""
        # Implementação básica - você pode expandir isso
        return ["Todas", "Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Outros"]

    def toggle_filter_panel(self):
        """Mostra ou esconde o painel de filtro"""
        if self.filter_panel_visible:
            self.filter_panel.pack_forget()
            self.filter_panel_visible = False
        else:
            self.filter_panel.pack(after=self.header_frame, fill=tk.X, padx=10, pady=5)
            self.filter_panel_visible = True
    
    def update_filter_options(self):
        """Atualiza as opções de filtro com base nos dados atuais"""
        # Obter categorias únicas
        categories = set()
        banks = set()
        
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        
        for transaction in transactions:
            if "categoria" in transaction and transaction["categoria"]:
                categories.add(transaction["categoria"])
            if "banco" in transaction and transaction["banco"]:
                banks.add(transaction["banco"])
        
        # Atualizar comboboxes
        self.filter_category['values'] = ["Todas"] + sorted(list(categories))
        self.filter_category.current(0)
        
        self.filter_bank['values'] = ["Todos"] + sorted(list(banks))
        self.filter_bank.current(0)
        
        # Atualizar também o combobox do formulário
        self.tag_form_entry['values'] = sorted(list(categories))
    
    def apply_filters(self):
        """Aplica os filtros selecionados"""
        search_term = self.search_entry.get().lower()
        
        try:
            date_from = self.date_from.get_date()
            date_to = self.date_to.get_date()
        except:
            messagebox.showwarning("Aviso", "Formato de data inválido.")
            return
        
        transaction_type = self.filter_type_var.get()
        category = self.filter_category.get()
        bank = self.filter_bank.get()
        
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        filtered_transactions = []
        
        for transaction in transactions:
            # Verificar se passa em todos os filtros
            include = True
            
            # Filtro de pesquisa
            if search_term:
                search_match = False
                for field in ["descricao", "banco", "categoria"]:
                    if field in transaction and search_term in str(transaction.get(field, "")).lower():
                        search_match = True
                        break
                if not search_match:
                    include = False
            
            # Filtro de data
            if include and "data" in transaction:
                try:
                    date_parts = transaction["data"].split("/")
                    if len(date_parts) == 3:
                        day, month, year = map(int, date_parts)
                        transaction_date = datetime(year, month, day).date()
                        if transaction_date < date_from.date() or transaction_date > date_to.date():
                            include = False
                except:
                    pass
            
            # Filtro de tipo
            if include and transaction_type != "Todos":
                if transaction.get("tipo", "") != transaction_type:
                    include = False
            
            # Filtro de categoria
            if include and category != "Todas":
                if transaction.get("categoria", "") != category:
                    include = False
            
            # Filtro de banco
            if include and bank != "Todos":
                if transaction.get("banco", "") != bank:
                    include = False
            
            if include:
                filtered_transactions.append(transaction)
        
        # Exibir as transações filtradas
        self.display_transactions(filtered_transactions)
    
    def clear_filters(self):
        """Limpa todos os filtros"""
        self.search_entry.delete(0, tk.END)
        self.date_from.set_date(datetime.now().replace(month=1, day=1))
        self.date_to.set_date(datetime.now())
        self.filter_type_var.set("Todos")
        self.filter_category.current(0)
        self.filter_bank.current(0)
        
        # Mostrar todas as transações
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        self.display_transactions(transactions)
    
    def show_context_menu(self, event):
        """Mostra o menu de contexto"""
        item = self.transaction_tree.identify_row(event.y)
        if item:
            self.transaction_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def read_json_data(self):
        """Lê os dados do arquivo JSON ou do banco de dados"""
        try:
            if self.database:
                try:
                    # Tente diferentes métodos possíveis
                    if hasattr(self.database, 'get_data'):
                        data = self.database.get_data()
                        return data
                    elif hasattr(self.database, 'load_data'):
                        data = self.database.load_data()
                        return data
                    elif hasattr(self.database, 'read'):
                        data = self.database.read()
                        return data
                    else:
                        # Se nenhum método conhecido estiver disponível, tente acessar o arquivo diretamente
                        with open(self.json_file, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            return data
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao ler dados do banco de dados: {e}")
                    return {"despesas": [], "contas": [], "cartoes_de_credito": []}
            
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    return data
            else:
                # Se o arquivo não existir, cria um novo com estrutura vazia
                empty_data = {
                    "despesas": [],
                    "contas": [],
                    "cartoes_de_credito": []
                }
                with open(self.json_file, 'w', encoding='utf-8') as file:
                    json.dump(empty_data, file, indent=4, ensure_ascii=False)
                return empty_data
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo JSON: {e}")
            return {
                "despesas": [],
                "contas": [],
                "cartoes_de_credito": []
            }
    
    def write_json_data(self, data):
        """Escreve os dados no arquivo JSON ou no banco de dados"""
        if self.database:
            try:
                if hasattr(self.database, 'save_data'):
                    self.database.save_data(data)
                elif hasattr(self.database, 'write_data'):
                    self.database.write_data(data)
                elif hasattr(self.database, 'write'):
                    self.database.write(data)
                elif hasattr(self.database, 'update'):
                    self.database.update(data)
                else:
                    # Se nenhum método conhecido estiver disponível, tente salvar diretamente no arquivo
                    with open(self.json_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                return
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar no banco de dados: {e}")
        
        try:
            with open(self.json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar no arquivo JSON: {e}")
    
    def load_transactions(self):
        """Carrega as transações do arquivo JSON ou do banco de dados"""
        try:
            data = None
            if self.database:
                # Se tiver uma instância de banco de dados, use-a
                try:
                    if hasattr(self.database, 'get_all_transactions'):
                        data = self.database.get_all_transactions()
                    elif hasattr(self.database, 'get_data'):
                        data = self.database.get_data()
                    else:
                        print("Método não encontrado no objeto de banco de dados")
                except Exception as e:
                    print(f"Erro ao acessar o banco de dados: {e}")
            else:
                # Caso contrário, tente carregar do arquivo JSON
                try:
                    with open(self.json_file, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                except FileNotFoundError:
                    print(f"Arquivo {self.json_file} não encontrado. Criando nova lista.")
                    data = {"despesas": []}
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar {self.json_file}. Criando nova lista.")
                    data = {"despesas": []}
            
            # Normalizar os dados
            if isinstance(data, dict) and "despesas" in data:
                self.despesas = data
            elif isinstance(data, list):
                self.despesas = {"despesas": data}
            else:
                self.despesas = {"despesas": []}
            
            # Atualizar a interface com as transações carregadas
            self.update_transaction_list()
        except Exception as e:
            print(f"Erro ao carregar transações: {e}")
            import traceback
            traceback.print_exc()
    
    def update_transaction_list(self):
        """Atualiza a lista de transações na interface"""
        # Verificar se os dados são um dicionário com a chave 'despesas'
        if isinstance(self.despesas, dict) and 'despesas' in self.despesas:
            self.display_transactions(self.despesas['despesas'])
        # Se for uma lista direta, exibir diretamente
        elif isinstance(self.despesas, list):
            self.display_transactions(self.despesas)
        else:
            print("Formato de dados inválido:", type(self.despesas))
            self.display_transactions([])  # Exibir lista vazia
        
        # Atualizar opções de filtro
        self.update_filter_options()
    
    def display_transactions(self, transactions):
        """
        Exibe as transações na treeview
        
        Args:
            transactions (list): Lista de transações para exibir
        """
        try:
            # Limpar a árvore atual
            for item in self.transaction_tree.get_children():
                self.transaction_tree.delete(item)
            
            # Adicionar as transações à árvore
            for i, transaction in enumerate(transactions):
                # Obter os valores para cada coluna
                data = transaction.get("data", "")
                tipo = transaction.get("tipo", "")
                descricao = transaction.get("descricao", "")
                valor = transaction.get("valor", 0)
                banco = transaction.get("banco", "")
                categoria = transaction.get("categoria", "")
                
                # Formatar o valor como moeda
                try:
                    valor_formatado = f"R$ {float(valor):.2f}"
                    # Adicionar sinal negativo para despesas
                    if tipo == "Despesa":
                        valor_formatado = f"-{valor_formatado}"
                except:
                    valor_formatado = f"R$ {valor}"
                
                # Inserir na árvore
                self.transaction_tree.insert("", tk.END, iid=str(i), values=(
                    data, tipo, descricao, valor_formatado, banco, categoria
                ), tags=(tipo.lower(),))
            
            # Configurar cores para diferentes tipos de transação
            self.transaction_tree.tag_configure("despesa", foreground="red")
            self.transaction_tree.tag_configure("receita", foreground="green")
            self.transaction_tree.tag_configure("transferência", foreground="blue")
        except Exception as e:
            print(f"Erro ao exibir transações: {e}")
    
    def add_transaction(self):
        """Prepara o formulário para adicionar uma nova transação"""
        # Limpar os campos do formulário
        self.date_form_entry.set_date(datetime.now())
        self.transaction_type_var.set("Despesa")
        self.descricao_form_entry.delete(0, tk.END)
        self.valor_form_entry.delete(0, tk.END)
        self.banco_form_entry.delete(0, tk.END)
        self.tag_form_entry.set("")
        
        # Atualizar o texto do botão e do formulário
        self.form_frame.config(text="Nova Transação")
        self.save_button.config(text="Adicionar")
        
        # Mostrar o botão de cancelar
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Desativar o modo de edição
        self.edit_mode = False
        self.current_edit_index = None
        
        # Esconder campos de transferência se existirem
        if hasattr(self, 'transfer_frame'):
            self.transfer_frame.pack_forget()
    
    def save_transaction(self):
        """Salva a transação atual (nova ou editada)"""
        # Obter os valores do formulário
        try:
            data = self.date_form_entry.get()
            tipo = self.transaction_type_var.get()
            descricao = self.descricao_form_entry.get()
            valor_str = self.valor_form_entry.get().replace(',', '.')
            
            # Validar o valor
            try:
                valor = float(valor_str)
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido. Use apenas números e ponto decimal.")
                return
            
            banco = self.banco_form_entry.get()
            categoria = self.tag_form_entry.get()
            
            # Validar campos obrigatórios
            if not descricao:
                messagebox.showerror("Erro", "Descrição é obrigatória.")
                return
            
            if not banco:
                messagebox.showerror("Erro", "Banco/Conta é obrigatório.")
                return
            
            # Criar o objeto de transação
            transaction = {
                "data": data,
                "tipo": tipo,
                "descricao": descricao,
                "valor": valor,
                "banco": banco,
                "categoria": categoria
            }
            
            # Se for uma transferência, adicionar contas de origem e destino
            if tipo == "Transferência" and hasattr(self, 'transfer_frame'):
                transaction["conta_origem"] = self.from_account_entry.get()
                transaction["conta_destino"] = self.to_account_entry.get()
                
                # Validar campos de transferência
                if not transaction["conta_origem"] or not transaction["conta_destino"]:
                    messagebox.showerror("Erro", "Contas de origem e destino são obrigatórias para transferências.")
                    return
            
            # Verificar se estamos editando ou adicionando
            if self.edit_mode and self.current_edit_index is not None:
                # Modo de edição - atualizar transação existente
                if isinstance(self.despesas, dict) and "despesas" in self.despesas:
                    self.despesas["despesas"][self.current_edit_index] = transaction
                elif isinstance(self.despesas, list):
                    self.despesas[self.current_edit_index] = transaction
            else:
                # Modo de adição - adicionar nova transação
                if isinstance(self.despesas, dict) and "despesas" in self.despesas:
                    self.despesas["despesas"].append(transaction)
                elif isinstance(self.despesas, list):
                    self.despesas.append(transaction)
                else:
                    # Se não houver estrutura de dados adequada, criar uma
                    self.despesas = {"despesas": [transaction]}
            
            # Salvar os dados
            self.write_json_data(self.despesas)
            
            # Atualizar a lista de transações
            self.update_transaction_list()
            
            # Limpar o formulário
            self.add_transaction()  # Reutilizar para limpar o formulário
            
            # Ocultar o botão de cancelar
            self.cancel_button.pack_forget()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar transação: {e}")
            import traceback
            traceback.print_exc()
    
    def cancel_edit(self):
        """Cancela a edição atual e limpa o formulário"""
        # Limpar o formulário
        self.add_transaction()
        
        # Ocultar o botão de cancelar
        self.cancel_button.pack_forget()
        
        # Desativar o modo de edição
        self.edit_mode = False
        self.current_edit_index = None
    
    def edit_selected(self):
        """Edita a transação selecionada"""
        selected_items = self.transaction_tree.selection()
        if not selected_items:
            messagebox.showinfo("Informação", "Selecione uma transação para editar.")
            return
        
        # Obter o índice da transação selecionada
        item_id = selected_items[0]
        index = int(item_id)
        
        # Obter a transação
        transaction = None
        if isinstance(self.despesas, dict) and "despesas" in self.despesas:
            if 0 <= index < len(self.despesas["despesas"]):
                transaction = self.despesas["despesas"][index]
        elif isinstance(self.despesas, list):
            if 0 <= index < len(self.despesas):
                transaction = self.despesas[index]
        
        if not transaction:
            messagebox.showerror("Erro", "Transação não encontrada.")
            return
        
        # Preencher o formulário com os dados da transação
        try:
            # Atualizar o tipo primeiro para garantir que os campos certos estejam visíveis
            self.transaction_type_var.set(transaction.get("tipo", "Despesa"))
            
            # Atualizar os campos do formulário
            data_str = transaction.get("data", "")
            if data_str:
                try:
                    # Tentar converter a string de data para objeto datetime
                    day, month, year = map(int, data_str.split("/"))
                    self.date_form_entry.set_date(datetime(year, month, day))
                except:
                    # Se falhar, usar a data atual
                    self.date_form_entry.set_date(datetime.now())
            else:
                self.date_form_entry.set_date(datetime.now())
            
            self.descricao_form_entry.delete(0, tk.END)
            self.descricao_form_entry.insert(0, transaction.get("descricao", ""))
            
            self.valor_form_entry.delete(0, tk.END)
            self.valor_form_entry.insert(0, str(transaction.get("valor", "")))
            
            self.banco_form_entry.delete(0, tk.END)
            self.banco_form_entry.insert(0, transaction.get("banco", ""))
            
            self.tag_form_entry.set(transaction.get("categoria", ""))
            
            # Se for transferência, preencher campos específicos
            if transaction.get("tipo") == "Transferência" and hasattr(self, 'transfer_frame'):
                self.from_account_entry.delete(0, tk.END)
                self.from_account_entry.insert(0, transaction.get("conta_origem", ""))
                
                self.to_account_entry.delete(0, tk.END)
                self.to_account_entry.insert(0, transaction.get("conta_destino", ""))
            
            # Atualizar o texto do botão e do formulário
            self.form_frame.config(text="Editar Transação")
            self.save_button.config(text="Salvar")
            
            # Mostrar o botão de cancelar
            self.cancel_button.pack(side=tk.LEFT, padx=5)
            
            # Ativar o modo de edição
            self.edit_mode = True
            self.current_edit_index = index
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados para edição: {e}")
            import traceback
            traceback.print_exc()
    
    def delete_selected(self):
        """Exclui a transação selecionada"""
        selected_items = self.transaction_tree.selection()
        if not selected_items:
            messagebox.showinfo("Informação", "Selecione uma transação para excluir.")
            return
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?"):
            return
        
        # Obter o índice da transação selecionada
        item_id = selected_items[0]
        index = int(item_id)
        
        # Excluir a transação
        try:
            if isinstance(self.despesas, dict) and "despesas" in self.despesas:
                if 0 <= index < len(self.despesas["despesas"]):
                    del self.despesas["despesas"][index]
            elif isinstance(self.despesas, list):
                if 0 <= index < len(self.despesas):
                    del self.despesas[index]
            
            # Salvar os dados
            self.write_json_data(self.despesas)
            
            # Atualizar a lista de transações
            self.update_transaction_list()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir transação: {e}")
    
    def search_transactions(self, event=None):
        """Pesquisa transações com base no texto inserido"""
        search_term = self.search_entry.get().lower()
        
        if not search_term:
            # Se o campo de pesquisa estiver vazio, mostrar todas as transações
            transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
            self.display_transactions(transactions)
            return
        
        # Filtrar transações com base no termo de pesquisa
        transactions = self.despesas.get("despesas", []) if isinstance(self.despesas, dict) else self.despesas
        filtered_transactions = []
        
        for transaction in transactions:
            # Verificar se o termo de pesquisa está em algum campo relevante
            for field in ["descricao", "banco", "categoria"]:
                if field in transaction and search_term in str(transaction.get(field, "")).lower():
                    filtered_transactions.append(transaction)
                    break
        
        # Exibir as transações filtradas
        self.display_transactions(filtered_transactions)
