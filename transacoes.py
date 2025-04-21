import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
import threading
from datetime import datetime

class Transacao:
    """Classe de domínio que representa uma transação financeira"""
    def __init__(self, descricao, valor, data, tag, banco):
        self.descricao = descricao
        self.valor = valor
        self.data = data
        self.tag = tag
        self.banco = banco
        self.timestamp = datetime.now()
    
    def validar(self):
        """Valida se todos os campos da transação estão preenchidos corretamente"""
        if not self.descricao or not self.data or not self.tag or not self.banco:
            return False
        try:
            float(self.valor)
            return True
        except ValueError:
            return False
    
    def to_dict(self):
        """Converte a transação para um dicionário"""
        return {
            "descricao": self.descricao,
            "valor": float(self.valor),
            "data": self.data,
            "tag": self.tag,
            "banco": self.banco
        }


class TransactionUnitOfWork:
    """Implementa o padrão Unit of Work para gerenciar transações com o banco de dados"""
    def __init__(self, database):
        self.database = database
        self.transaction = None
    
    def __enter__(self):
        # Iniciar transação (simulado, já que o database atual não suporta transações)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Se ocorrer uma exceção, faz rollback (simulado)
        if exc_type is not None:
            return False
        # Caso contrário, salva os dados
        self.database.salvar_dados()
        return True


class TransacoesController:
    """Controlador que gerencia a lógica de negócios das transações"""
    def __init__(self, database):
        self.database = database
    
    def listar_transacoes(self, filtros=None):
        """Lista transações com filtros opcionais"""
        if filtros is None:
            filtros = {}
        
        return self.database.listar_despesas(
            data_inicio=filtros.get('data_inicio', None),
            data_fim=filtros.get('data_fim', None),
            tag=filtros.get('tag', None),
            banco=filtros.get('banco', None),
            busca_descricao=filtros.get('busca_descricao', None),
            ordenar_por=filtros.get('ordenar_por', 'data')
        )
    
    def adicionar_transacao(self, transacao):
        """Adiciona uma nova transação"""
        if not transacao.validar():
            return False
        
        with TransactionUnitOfWork(self.database):
            return self.database.adicionar_despesa(**transacao.to_dict())
    
    def editar_transacao(self, indice, transacao):
        """Edita uma transação existente"""
        if not transacao.validar():
            return False
        
        with TransactionUnitOfWork(self.database):
            return self.database.editar_despesa(indice, **transacao.to_dict())
    
    def remover_transacao(self, indice):
        """Remove uma transação"""
        with TransactionUnitOfWork(self.database):
            return self.database.remover_despesa(indice)
    
    def exportar_para_csv(self, caminho, filtros=None):
        """Exporta transações para CSV"""
        if filtros is None:
            filtros = {}
        
        return self.database.exportar_para_csv(
            caminho,
            data_inicio=filtros.get('data_inicio', None),
            data_fim=filtros.get('data_fim', None),
            tag=filtros.get('tag', None),
            banco=filtros.get('banco', None),
            busca_descricao=filtros.get('busca_descricao', None),
            ordenar_por=filtros.get('ordenar_por', 'data')
        )
    
    def obter_resumo(self, filtros=None):
        """Obtém um resumo das transações agrupadas por tag e banco"""
        transacoes = self.listar_transacoes(filtros)
        
        total = sum(t['valor'] for t in transacoes)
        por_tag = defaultdict(float)
        por_banco = defaultdict(float)
        
        for t in transacoes:
            por_tag[t['tag']] += t['valor']
            por_banco[t['banco']] += t['valor']
        
        return {
            'total': total,
            'por_tag': dict(por_tag),
            'por_banco': dict(por_banco),
            'transacoes': transacoes
        }


class TransacoesUI:
    """Classe responsável pela interface do usuário para transações"""
    def __init__(self, main_content, controller):
        self.main_content = main_content
        self.controller = controller
        self.filtro_frame = None
        self.tree = None
        self.total_label = None
        self.despesas_filtradas = []
        
        # Opções para tags e ordenação
        self.opcoes_tag = ["Alimentação", "Lazer", "Assinatura", "Casa", "Compras", 
                           "Educação", "Saúde", "Pix", "Transporte", "Viagem"]
    
    def mostrar(self):
        """Método principal que exibe a interface de transações"""
        self._limpar_conteudo()
        self._criar_cabecalho()
        self._criar_filtros()
        self._criar_listagem()
        self._criar_botoes_acao()
        self._carregar_transacoes()
    
    def _limpar_conteudo(self):
        """Limpa o conteúdo atual da tela"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def _criar_cabecalho(self):
        """Cria o cabeçalho da página de transações"""
        tk.Label(self.main_content, text="Transações", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    def _criar_filtros(self):
        """Cria a seção de filtros"""
        self.filtro_frame = tk.Frame(self.main_content, bg="#ffffff")
        self.filtro_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Usar grid para melhor organização
        # Linha 1: Data Início e Data Fim
        tk.Label(self.filtro_frame, text="Data Início:", bg="#ffffff").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filtro_data_inicio = DateEntry(self.filtro_frame, date_pattern="dd/mm/yyyy", width=15)
        self.filtro_data_inicio.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(self.filtro_frame, text="Data Fim:", bg="#ffffff").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filtro_data_fim = DateEntry(self.filtro_frame, date_pattern="dd/mm/yyyy", width=15)
        self.filtro_data_fim.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Linha 2: Tag e Banco
        tk.Label(self.filtro_frame, text="Tag:", bg="#ffffff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.filtro_tag = ttk.Combobox(self.filtro_frame, values=self.opcoes_tag, width=15)
        self.filtro_tag.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(self.filtro_frame, text="Banco:", bg="#ffffff").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.filtro_banco = tk.Entry(self.filtro_frame, width=17)
        self.filtro_banco.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # Linha 3: Descrição e Botão de Busca
        tk.Label(self.filtro_frame, text="Descrição:", bg="#ffffff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.filtro_descricao = tk.Entry(self.filtro_frame, width=17)
        self.filtro_descricao.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Ordenação
        self.sort_by = tk.StringVar(value="data")
        ordenacao_frame = tk.Frame(self.filtro_frame, bg="#ffffff")
        ordenacao_frame.grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="w")
        
        tk.Label(ordenacao_frame, text="Ordenar por:", bg="#ffffff").pack(side=tk.LEFT)
        tk.Radiobutton(ordenacao_frame, text="Data", variable=self.sort_by, value="data", bg="#ffffff").pack(side=tk.LEFT)
        tk.Radiobutton(ordenacao_frame, text="Valor", variable=self.sort_by, value="valor", bg="#ffffff").pack(side=tk.LEFT)
        
        # Botão de busca
        tk.Button(self.filtro_frame, text="Buscar", command=self._carregar_transacoes, 
                  bg="#4CAF50", fg="white").grid(row=3, column=3, padx=5, pady=10, sticky="e")
        
        # Botão para limpar filtros
        tk.Button(self.filtro_frame, text="Limpar Filtros", command=self._limpar_filtros, 
                  bg="#f0f0f0").grid(row=3, column=2, padx=5, pady=10, sticky="e")
    
    def _criar_listagem(self):
        """Cria a listagem de transações"""
        # Frame para a listagem
        list_frame = tk.Frame(self.main_content, bg="#ffffff")
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        # Cabeçalho da listagem
        header_frame = tk.Frame(list_frame, bg="#f0f0f0")
        header_frame.pack(fill=tk.X)
        
        headers = ["Descrição", "Valor", "Data", "Tag", "Banco"]
        widths = [3, 1, 1, 1, 1]  # Proporções relativas
        
        for i, header in enumerate(headers):
            tk.Label(header_frame, text=header, font=("Arial", 10, "bold"), 
                     bg="#f0f0f0", width=15*widths[i]).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Listagem com scrollbar
        tree_frame = tk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = tk.Listbox(tree_frame, font=("Arial", 10), height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Label para mostrar o total
        self.total_label = tk.Label(self.main_content, text="Total: R$ 0,00", 
                                    font=("Arial", 12, "bold"), bg="#ffffff")
        self.total_label.pack(pady=10)
    
    def _criar_botoes_acao(self):
        """Cria os botões de ação"""
        botoes_frame = tk.Frame(self.main_content, bg="#ffffff")
        botoes_frame.pack(pady=15, padx=20)
        
        botoes = [
            ("Adicionar", self._abrir_janela_adicionar, "#4CAF50"),
            ("Editar", self._abrir_janela_editar, "#2196F3"),
            ("Remover", self._remover_transacao, "#F44336"),
            ("Exportar CSV", self._exportar_csv, "#FF9800"),
            ("Resumo", self._mostrar_resumo, "#9C27B0")
        ]
        
        for texto, comando, cor in botoes:
            tk.Button(botoes_frame, text=texto, command=comando, 
                      bg=cor, fg="white", width=12, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def _carregar_transacoes(self):
        """Carrega as transações com base nos filtros"""
        # Limpar listagem atual
        self.tree.delete(0, tk.END)
        
        # Obter filtros
        filtros = {
            'data_inicio': self.filtro_data_inicio.get(),
            'data_fim': self.filtro_data_fim.get(),
            'tag': self.filtro_tag.get(),
            'banco': self.filtro_banco.get(),
            'busca_descricao': self.filtro_descricao.get(),
            'ordenar_por': self.sort_by.get()
        }
        
        # Buscar transações
        self.despesas_filtradas = self.controller.listar_transacoes(filtros)
        
        # Preencher listagem
        total = 0.0
        for i, despesa in enumerate(self.despesas_filtradas):
            # Formatar valores para exibição
            valor_formatado = f"R$ {despesa['valor']:.2f}"
            
            # Definir cor com base no tipo (despesa ou receita)
            cor = "#ffcccc" if despesa['valor'] < 0 else "#ccffcc"
            
            # Inserir na listagem
            self.tree.insert(
                tk.END, 
                f"{despesa['descricao']:<30} {valor_formatado:>12} {despesa['data']:>12} {despesa['tag']:>15} {despesa['banco']:>15}"
            )
            
            # Alternar cores das linhas para melhor legibilidade
            if i % 2 == 0:
                self.tree.itemconfig(i, {'bg': '#f5f5f5'})
            
            # Somar ao total
            total += despesa['valor']
        
        # Atualizar label de total
        self.total_label.config(text=f"Total: R$ {total:.2f}")
    
    def _limpar_filtros(self):
        """Limpa todos os filtros"""
        self.filtro_tag.set("")
        self.filtro_banco.delete(0, tk.END)
        self.filtro_descricao.delete(0, tk.END)
        self.filtro_data_inicio.set_date(None)
        self.filtro_data_fim.set_date(None)
        self.sort_by.set("data")
        
        # Recarregar transações
        self._carregar_transacoes()
    
    def _abrir_janela_adicionar(self):
        """Abre janela para adicionar nova transação"""
        janela = tk.Toplevel(self.main_content)
        janela.title("Adicionar Transação")
        janela.geometry("400x350")
        janela.resizable(False, False)
        
        # Centralizar na tela
        janela.update_idletasks()
        width = janela.winfo_width()
        height = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (width // 2)
        y = (janela.winfo_screenheight() // 2) - (height // 2)
        janela.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Criar formulário
        form_frame = tk.Frame(janela)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campos do formulário
        campos = [
            ("Descrição:", "descricao", None),
            ("Valor:", "valor", None),
            ("Data:", "data", None),
            ("Tag:", "tag", self.opcoes_tag),
            ("Banco:", "banco", None)
        ]
        
        entradas = {}
        
        for i, (label_text, key, options) in enumerate(campos):
            tk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=8)
            
            if key == "data":
                entrada = DateEntry(form_frame, date_pattern="dd/mm/yyyy", width=20)
            elif options:
                entrada = ttk.Combobox(form_frame, values=options, width=20)
                entrada.current(0)
            else:
                entrada = tk.Entry(form_frame, width=22)
            
            entrada.grid(row=i, column=1, sticky="w", padx=10, pady=8)
            entradas[key] = entrada
        
        # Botões
        botoes_frame = tk.Frame(janela)
        botoes_frame.pack(pady=15)
        
        tk.Button(botoes_frame, text="Cancelar", command=janela.destroy, 
                  width=10).pack(side=tk.LEFT, padx=10)
        
        def salvar():
            # Obter dados do formulário
            dados = {
                'descricao': entradas['descricao'].get(),
                'valor': entradas['valor'].get().replace(',', '.'),
                'data': entradas['data'].get(),
                'tag': entradas['tag'].get(),
                'banco': entradas['banco'].get()
            }
            
            # Criar e validar transação
            transacao = Transacao(**dados)
            if not transacao.validar():
                messagebox.showwarning("Campos inválidos", 
                                      "Por favor, preencha todos os campos corretamente.")
                return
            
            # Adicionar transação
            try:
                self.controller.adicionar_transacao(transacao)
                messagebox.showinfo("Sucesso", "Transação adicionada com sucesso!")
                janela.destroy()
                self._carregar_transacoes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar transação: {str(e)}")
        
        tk.Button(botoes_frame, text="Salvar", command=salvar, 
                  bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=10)
    
    def _abrir_janela_editar(self):
        """Abre janela para editar transação selecionada"""
        # Verificar se há uma seleção
        selected_index = self.tree.curselection()
        if not selected_index:
            messagebox.showwarning("Nenhuma seleção", "Selecione uma transação para editar.")
            return
        
        index = selected_index[0]
        despesa = self.despesas_filtradas[index]
        
        # Criar janela
        janela = tk.Toplevel(self.main_content)
        janela.title("Editar Transação")
        janela.geometry("400x350")
        janela.resizable(False, False)
        
        # Centralizar na tela
        janela.update_idletasks()
        width = janela.winfo_width()
        height = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (width // 2)
        y = (janela.winfo_screenheight() // 2) - (height // 2)
        janela.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Criar formulário
        form_frame = tk.Frame(janela)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Campos do formulário
        campos = [
            ("Descrição:", "descricao", None, despesa['descricao']),
            ("Valor:", "valor", None, str(despesa['valor'])),
            ("Data:", "data", None, despesa['data']),
            ("Tag:", "tag", self.opcoes_tag, despesa['tag']),
            ("Banco:", "banco", None, despesa['banco'])
        ]
        
        entradas = {}
        
        for i, (label_text, key, options, valor) in enumerate(campos):
            tk.Label(form_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=8)
            
            if key == "data":
                entrada = DateEntry(form_frame, date_pattern="dd/mm/yyyy", width=20)
                entrada.set_date(valor)
            elif options:
                entrada = ttk.Combobox(form_frame, values=options, width=20)
                if valor in options:
                    entrada.set(valor)
                else:
                    entrada.current(0)
            else:
                entrada = tk.Entry(form_frame, width=22)
                entrada.insert(0, valor)
            
            entrada.grid(row=i, column=1, sticky="w", padx=10, pady=8)
            entradas[key] = entrada
        
        # Botões
        botoes_frame = tk.Frame(janela)
        botoes_frame.pack(pady=15)
        
        tk.Button(botoes_frame, text="Cancelar", command=janela.destroy, 
                  width=10).pack(side=tk.LEFT, padx=10)
        
        def salvar():
            # Obter dados do formulário
            dados = {
                'descricao': entradas['descricao'].get(),
                'valor': entradas['valor'].get().replace(',', '.'),
                'data': entradas['data'].get(),
                'tag': entradas['tag'].get(),
                'banco': entradas['banco'].get()
            }
            
            # Criar e validar transação
            transacao = Transacao(**dados)
            if not transacao.validar():
                messagebox.showwarning("Campos inválidos", 
                                      "Por favor, preencha todos os campos corretamente.")
                return
            
            # Editar transação
            try:
                self.controller.editar_transacao(index, transacao)
                messagebox.showinfo("Sucesso", "Transação atualizada com sucesso!")
                janela.destroy()
                self._carregar_transacoes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar transação: {str(e)}")
        
        tk.Button(botoes_frame, text="Salvar", command=salvar, 
                  bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=10)
    
    def _remover_transacao(self):
        """Remove a transação selecionada"""
        # Verificar se há uma seleção
        selected_index = self.tree.curselection()
        if not selected_index:
            messagebox.showwarning("Nenhuma seleção", "Selecione uma transação para remover.")
            return
        
        index = selected_index[0]
        
        # Confirmar remoção
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja remover esta transação?")
        if not confirm:
            return
        
        # Remover transação
        try:
            self.controller.remover_transacao(index)
            messagebox.showinfo("Sucesso", "Transação removida com sucesso!")
            self._carregar_transacoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover transação: {str(e)}")
    
    def _exportar_csv(self):
        """Exporta as transações para um arquivo CSV"""
        # Obter caminho do arquivo
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not caminho:
            return
        
        # Obter filtros atuais
        filtros = {
            'data_inicio': self.filtro_data_inicio.get(),
            'data_fim': self.filtro_data_fim.get(),
            'tag': self.filtro_tag.get(),
            'banco': self.filtro_banco.get(),
            'busca_descricao': self.filtro_descricao.get(),
            'ordenar_por': self.sort_by.get()
        }
        
        # Mostrar indicador de progresso
        progresso = tk.Toplevel(self.main_content)
        progresso.title("Exportando...")
        progresso.geometry("300x100")
        progresso.resizable(False, False)
        
        # Centralizar na tela
        progresso.update_idletasks()
        width = progresso.winfo_width()
        height = progresso.winfo_height()
        x = (progresso.winfo_screenwidth() // 2) - (width // 2)
        y = (progresso.winfo_screenheight() // 2) - (height // 2)
        progresso.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        tk.Label(progresso, text="Exportando dados, aguarde...", 
                 font=("Arial", 12)).pack(pady=20)
        
        # Função para executar em thread separada
        def executar_exportacao():
            try:
                sucesso = self.controller.exportar_para_csv(caminho, filtros)
                # Atualizar UI na thread principal
                self.main_content.after(0, lambda: self._finalizar_exportacao(progresso, sucesso))
            except Exception as e:
                self.main_content.after(0, lambda: self._finalizar_exportacao(
                    progresso, False, str(e)))
        
        # Iniciar thread
        thread = threading.Thread(target=executar_exportacao)
        thread.daemon = True
        thread.start()
    
    def _finalizar_exportacao(self, janela_progresso, sucesso, erro=None):
        """Finaliza o processo de exportação"""
        janela_progresso.destroy()
        
        if sucesso:
            messagebox.showinfo("Exportado", "Transações exportadas com sucesso!")
        else:
            mensagem = "Falha ao exportar transações."
            if erro:
                mensagem += f"\nErro: {erro}"
            messagebox.showerror("Erro", mensagem)
    
    def _mostrar_resumo(self):
        """Mostra um resumo gráfico das transações"""
        # Obter filtros atuais
        filtros = {
            'data_inicio': self.filtro_data_inicio.get(),
            'data_fim': self.filtro_data_fim.get(),
            'tag': self.filtro_tag.get(),
            'banco': self.filtro_banco.get(),
            'busca_descricao': self.filtro_descricao.get(),
            'ordenar_por': self.sort_by.get()
        }
        
        # Obter resumo
        resumo = self.controller.obter_resumo(filtros)
        
        if not resumo['transacoes']:
            messagebox.showinfo("Sem dados", "Não há transações para mostrar no resumo.")
            return
        
        # Criar janela
        janela = tk.Toplevel(self.main_content)
        janela.title("Resumo Financeiro")
        janela.geometry("800x600")
        
        # Cabeçalho
        tk.Label(janela, text="Resumo Financeiro", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(janela, text=f"Total: R$ {resumo['total']:.2f}", 
                 font=("Arial", 14)).pack(pady=5)
        
        # Criar gráficos
        fig = plt.figure(figsize=(10, 8))
        
        # Gráfico de pizza por tag
        ax1 = fig.add_subplot(221)
        if resumo['por_tag']:
            labels = list(resumo['por_tag'].keys())
            sizes = list(resumo['por_tag'].values())
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            ax1.set_title('Distribuição por Tag')
        
        # Gráfico de pizza por banco
        ax2 = fig.add_subplot(222)
        if resumo['por_banco']:
            labels = list(resumo['por_banco'].keys())
            sizes = list(resumo['por_banco'].values())
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            ax2.set_title('Distribuição por Banco')
        
        # Adicionar canvas para exibir os gráficos
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Botão para fechar
        tk.Button(janela, text="Fechar", command=janela.destroy, 
                  width=10).pack(pady=10)


def mostrar_transacoes(main_content, database):
    """Função principal para mostrar a aba de transações"""
    controller = TransacoesController(database)
    ui = TransacoesUI(main_content, controller)
    ui.mostrar()