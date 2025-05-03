import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from ttkthemes import ThemedStyle
from tkcalendar import DateEntry
import locale

class TransacoesModernUI(ttk.Frame):
    def __init__(self, parent, database=None):
        super().__init__(parent)
        
        
        # Se database for uma string, considere como o caminho do arquivo
        if isinstance(database, str):
            self.json_file = database
            self.database = None
            print(f"Usando arquivo JSON: {self.json_file}")
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
        self.despesas = []
        self.edit_mode = False
        self.current_edit_index = None
        
        # Configurar a interface
        self.setup_ui()
        
        # Garantir que os dados sejam carregados após a interface estar pronta
        self.after(100, self.load_transactions)
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        
        # Configurar o estilo
        style = ThemedStyle(self)
        style.set_theme("arc")  # Tema moderno
        
        # Configurar o locale para formato brasileiro
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
                print("Locale configurado para Portuguese_Brazil.1252")
            except:
                print("Não foi possível configurar o locale para português")
                pass  # Se não conseguir definir o locale, usa o padrão
        
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para o formulário
        form_frame = ttk.LabelFrame(main_frame, text="Nova Transação")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tipo de transação (Despesa/Receita)
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(type_frame, text="Tipo:").pack(side=tk.LEFT, padx=5)
        self.transaction_type_var = tk.StringVar(value="Despesa")
        ttk.Radiobutton(type_frame, text="Despesa", variable=self.transaction_type_var, value="Despesa").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Receita", variable=self.transaction_type_var, value="Receita").pack(side=tk.LEFT, padx=5)
        
        # Data
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(date_frame, text="Data:").pack(side=tk.LEFT, padx=5)
        self.date_form_entry = DateEntry(date_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_form_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Descrição
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(desc_frame, text="Descrição:").pack(side=tk.LEFT, padx=5)
        self.descricao_form_entry = ttk.Entry(desc_frame)
        self.descricao_form_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Valor
        valor_frame = ttk.Frame(form_frame)
        valor_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(valor_frame, text="Valor (R$):").pack(side=tk.LEFT, padx=5)
        self.valor_form_entry = ttk.Entry(valor_frame)
        self.valor_form_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Banco/Cartão
        banco_frame = ttk.Frame(form_frame)
        banco_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(banco_frame, text="Banco/Cartão:").pack(side=tk.LEFT, padx=5)
        self.banco_form_entry = ttk.Entry(banco_frame)
        self.banco_form_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Tag/Categoria
        tag_frame = ttk.Frame(form_frame)
        tag_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(tag_frame, text="Categoria:").pack(side=tk.LEFT, padx=5)
        self.tag_form_entry = ttk.Entry(tag_frame)
        self.tag_form_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Botões
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_button = ttk.Button(buttons_frame, text="Adicionar", command=self.add_transaction)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(buttons_frame, text="Cancelar", command=self.cancel_edit)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        self.cancel_button.pack_forget()  # Esconde o botão inicialmente
        
        # Frame para pesquisa
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.search_transactions)
        
        # Frame para a lista de transações
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para mostrar as transações
        columns = ("data", "tipo", "descricao", "valor", "banco", "categoria")
        self.transaction_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Definir cabeçalhos
        self.transaction_tree.heading("data", text="Data")
        self.transaction_tree.heading("tipo", text="Tipo")
        self.transaction_tree.heading("descricao", text="Descrição")
        self.transaction_tree.heading("valor", text="Valor (R$)")
        self.transaction_tree.heading("banco", text="Banco/Cartão")
        self.transaction_tree.heading("categoria", text="Categoria")
        
        # Definir larguras das colunas
        self.transaction_tree.column("data", width=100)
        self.transaction_tree.column("tipo", width=80)
        self.transaction_tree.column("descricao", width=200)
        self.transaction_tree.column("valor", width=100)
        self.transaction_tree.column("banco", width=120)
        self.transaction_tree.column("categoria", width=120)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transaction_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Adicionar menu de contexto
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.edit_selected)
        self.context_menu.add_command(label="Excluir", command=self.delete_selected)
        
        # Binding para o menu de contexto
        self.transaction_tree.bind("<Button-3>", self.show_context_menu)
        self.transaction_tree.bind("<Double-1>", lambda event: self.edit_selected())
        
        
        
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
                        print("Usando método get_data()")
                        data = self.database.get_data()
                        print(f"Dados lidos do método get_data: {data}")
                        return data
                    elif hasattr(self.database, 'load_data'):
                        print("Usando método load_data()")
                        data = self.database.load_data()
                        print(f"Dados lidos do método load_data: {data}")
                        return data
                    elif hasattr(self.database, 'read'):
                        print("Usando método read()")
                        data = self.database.read()
                        print(f"Dados lidos do método read: {data}")
                        return data
                    else:
                        
                        # Se nenhum método conhecido estiver disponível, tente acessar o arquivo diretamente
                        with open(self.json_file, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            
                            return data
                except Exception as e:
                    print(f"Erro ao ler dados do banco de dados: {e}")
                    messagebox.showerror("Erro", f"Erro ao ler dados do banco de dados: {e}")
                    return {"despesas": [], "contas": [], "cartoes_de_credito": []}
            
            print(f"Tentando ler arquivo JSON: {self.json_file}")
            if os.path.exists(self.json_file):
                print(f"Arquivo encontrado: {self.json_file}")
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    print(f"Dados lidos do arquivo: {data}")
                    return data
            else:
                print(f"Arquivo não encontrado: {self.json_file}")
                # Se o arquivo não existir, cria um novo com estrutura vazia
                empty_data = {
                    "despesas": [],
                    "contas": [],
                    "cartoes_de_credito": []
                }
                with open(self.json_file, 'w', encoding='utf-8') as file:
                    json.dump(empty_data, file, indent=4, ensure_ascii=False)
                    print(f"Novo arquivo criado: {self.json_file}")
                return empty_data
        except Exception as e:
            print(f"Erro ao ler dados: {e}")
            messagebox.showerror("Erro", f"Erro ao ler o arquivo JSON: {e}")
            return {
                "despesas": [],
                "contas": [],
                "cartoes_de_credito": []
            }
    
    def write_json_data(self, data):
        """Escreve os dados no arquivo JSON ou no banco de dados"""
        print(f"Salvando dados: {data}")
        if self.database:
            try:
                print("Tentando salvar no objeto database...")
                if hasattr(self.database, 'save_data'):
                    print("Usando método save_data()")
                    self.database.save_data(data)
                elif hasattr(self.database, 'write_data'):
                    print("Usando método write_data()")
                    self.database.write_data(data)
                elif hasattr(self.database, 'write'):
                    print("Usando método write()")
                    self.database.write(data)
                elif hasattr(self.database, 'update'):
                    print("Usando método update()")
                    self.database.update(data)
                else:
                    print("Nenhum método conhecido encontrado, salvando diretamente no arquivo")
                    # Se nenhum método conhecido estiver disponível, tente salvar diretamente no arquivo
                    with open(self.json_file, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=4, ensure_ascii=False)
                print("Dados salvos com sucesso no database")
                return
            except Exception as e:
                print(f"Erro ao salvar no banco de dados: {e}")
                messagebox.showerror("Erro", f"Erro ao salvar no banco de dados: {e}")
        
        try:
            print(f"Salvando no arquivo JSON: {self.json_file}")
            with open(self.json_file, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print("Dados salvos com sucesso no arquivo")
        except Exception as e:
            print(f"Erro ao salvar no arquivo JSON: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar no arquivo JSON: {e}")
    
    def load_transactions(self):
        """Carrega as transações do arquivo JSON ou do banco de dados e exibe na treeview"""
        try:
            
            data = self.read_json_data()
            
            
            # Verificar se 'despesas' existe no dicionário
            if "despesas" in data:
                self.despesas = data["despesas"]
                
            else:
                print("Chave 'despesas' não encontrada nos dados")
                self.despesas = []
                
                # Tenta criar a estrutura se ela não existir
                data["despesas"] = []
                self.write_json_data(data)
            
            self.display_transactions(self.despesas)
        except Exception as e:
            print(f"Erro ao carregar transações: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar transações: {e}")
    
    def display_transactions(self, transactions):
        """Exibe as transações na treeview"""
        # Limpar a treeview
    
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        # Adicionar as transações
        for i, transaction in enumerate(transactions):
            data = transaction.get("data", "")
            tipo = transaction.get("tipo", "Despesa")
            descricao = transaction.get("descricao", "")
            valor = transaction.get("valor", 0)
            banco = transaction.get("banco", "")
            categoria = transaction.get("categoria", "")
            
            # Formatar o valor
            valor_formatado = f"{float(valor):.2f}".replace(".", ",")
            if tipo == "Despesa":
                valor_formatado = f"-{valor_formatado}"
            
            
            self.transaction_tree.insert("", tk.END, values=(data, tipo, descricao, valor_formatado, banco, categoria), tags=(str(i),))
            
            # Colorir as linhas baseado no tipo
            if tipo == "Despesa":
                self.transaction_tree.tag_configure(str(i), background="#ffcccc")
            else:
                self.transaction_tree.tag_configure(str(i), background="#ccffcc")
    
    def add_transaction(self):
        """Adiciona ou atualiza uma transação"""
        try:
            # Obter os valores do formulário
            data = self.date_form_entry.get()
            tipo = self.transaction_type_var.get()
            descricao = self.descricao_form_entry.get()
            valor_str = self.valor_form_entry.get().replace(",", ".")
            banco = self.banco_form_entry.get()
            categoria = self.tag_form_entry.get()
            
            print(f"Dados do formulário: {data}, {tipo}, {descricao}, {valor_str}, {banco}, {categoria}")
            
            # Validar os campos
            if not descricao:
                messagebox.showerror("Erro", "Por favor, preencha a descrição.")
                return
            
            try:
                valor = float(valor_str)
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido. Use apenas números e ponto ou vírgula.")
                return
            
            # Criar a transação
            transaction = {
                "data": data,
                "tipo": tipo,
                "descricao": descricao,
                "valor": valor,
                "banco": banco,
                "categoria": categoria
            }
            
            print(f"Transação criada: {transaction}")
            
            # Ler os dados atuais
            data_json = self.read_json_data()
            
            # Adicionar ou atualizar a transação
            if self.edit_mode and self.current_edit_index is not None:
                print(f"Atualizando transação no índice {self.current_edit_index}")
                data_json["despesas"][self.current_edit_index] = transaction
                messagebox.showinfo("Sucesso", "Transação atualizada com sucesso!")
                self.edit_mode = False
                self.current_edit_index = None
                self.add_button.config(text="Adicionar")
                self.cancel_button.pack_forget()
            else:
                print("Adicionando nova transação")
                data_json["despesas"].append(transaction)
                messagebox.showinfo("Sucesso", "Transação adicionada com sucesso!")
            
            # Salvar os dados
            self.write_json_data(data_json)
            
            # Recarregar as transações
            self.load_transactions()
            
            # Limpar o formulário
            self.clear_form()
            
        except Exception as e:
            print(f"Erro ao adicionar transação: {e}")
            messagebox.showerror("Erro", f"Erro ao adicionar transação: {e}")
    
    def clear_form(self):
        """Limpa o formulário"""
        print("Limpando formulário")
        self.date_form_entry.set_date(datetime.now())
        self.transaction_type_var.set("Despesa")
        self.descricao_form_entry.delete(0, tk.END)
        self.valor_form_entry.delete(0, tk.END)
        self.banco_form_entry.delete(0, tk.END)
        self.tag_form_entry.delete(0, tk.END)
    
    def edit_selected(self):
        """Edita a transação selecionada"""
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Nenhuma transação selecionada.")
            return
        
        # Obter o índice da transação
        item_id = selected[0]
        item_index = int(self.transaction_tree.item(item_id, "tags")[0])
        
        print(f"Editando transação no índice {item_index}")
        
        # Verificar se o índice é válido
        if item_index < 0 or item_index >= len(self.despesas):
            messagebox.showerror("Erro", "Índice de transação inválido.")
            return
        
        # Obter a transação
        transaction = self.despesas[item_index]
        print(f"Transação selecionada: {transaction}")
        
        # Preencher o formulário com os dados da transação
        self.transaction_type_var.set(transaction.get("tipo", "Despesa"))
        
        # Converter a data para o formato correto
        date_str = transaction.get("data", "")
        try:
            date_parts = date_str.split("/")
            if len(date_parts) == 3:
                day, month, year = map(int, date_parts)
                self.date_form_entry.set_date(datetime(year, month, day))
        except Exception as e:
            print(f"Erro ao converter data: {e}")
            self.date_form_entry.set_date(datetime.now())
        
        self.descricao_form_entry.delete(0, tk.END)
        self.descricao_form_entry.insert(0, transaction.get("descricao", ""))
        
        self.valor_form_entry.delete(0, tk.END)
        self.valor_form_entry.insert(0, str(transaction.get("valor", "")).replace(".", ","))
        
        self.banco_form_entry.delete(0, tk.END)
        self.banco_form_entry.insert(0, transaction.get("banco", ""))
        
        self.tag_form_entry.delete(0, tk.END)
        self.tag_form_entry.insert(0, transaction.get("categoria", ""))
        
        # Ativar o modo de edição
        self.edit_mode = True
        self.current_edit_index = item_index
        self.add_button.config(text="Atualizar")
        self.cancel_button.pack(side=tk.LEFT, padx=5)
    
    def cancel_edit(self):
        """Cancela a edição"""
        print("Cancelando edição")
        self.edit_mode = False
        self.current_edit_index = None
        self.add_button.config(text="Adicionar")
        self.cancel_button.pack_forget()
        self.clear_form()
    
    def delete_selected(self):
        """Exclui a transação selecionada"""
        selected = self.transaction_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Nenhuma transação selecionada.")
            return
        
        # Confirmar a exclusão
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta transação?"):
            return
        
        # Obter o índice da transação
        item_id = selected[0]
        item_index = int(self.transaction_tree.item(item_id, "tags")[0])
        
        print(f"Excluindo transação no índice {item_index}")
        
        # Verificar se o índice é válido
        if item_index < 0 or item_index >= len(self.despesas):
            messagebox.showerror("Erro", "Índice de transação inválido.")
            return
        
        # Ler os dados atuais
        data_json = self.read_json_data()
        
        # Remover a transação
        data_json["despesas"].pop(item_index)
        
        # Salvar os dados
        self.write_json_data(data_json)
        
        # Recarregar as transações
        self.load_transactions()
        
        messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
    
    def search_transactions(self, event=None):
        """Pesquisa transações"""
        search_term = self.search_entry.get().lower()
        
        print(f"Pesquisando por: '{search_term}'")
        
        if not search_term:
            # Se o termo de pesquisa estiver vazio, mostrar todas as transações
            print("Termo vazio, mostrando todas as transações")
            self.display_transactions(self.despesas)
            return
        
        # Filtrar as transações
        filtered_transactions = []
        for transaction in self.despesas:
            # Verificar se o termo de pesquisa está em qualquer campo
            if (search_term in transaction.get("descricao", "").lower() or
                search_term in transaction.get("banco", "").lower() or
                search_term in transaction.get("categoria", "").lower() or
                search_term in transaction.get("data", "").lower() or
                search_term in str(transaction.get("valor", "")).lower()):
                filtered_transactions.append(transaction)
        
        print(f"Encontradas {len(filtered_transactions)} transações")
        # Exibir as transações filtradas
        self.display_transactions(filtered_transactions)

# Para testes independentes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gerenciador de Transações")
    root.geometry("800x600")
    
    app = TransacoesModernUI(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
