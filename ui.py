import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from tkcalendar import DateEntry
from database import Database, COLORS, ACCOUNT_TYPES
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from collections import defaultdict
from contas import mostrar_contas
from dashboard import mostrar_dashboard


CONFIG_FILE = "config.json"

BANKS = [
    "Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau",
    "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank"
]

class MainApplication:
    def __init__(self, master, database):
        self.master = master
        self.master.title("Mobills Offline")

        try:
            self.master.state('zoomed')
        except:
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            self.master.geometry(f"{screen_width}x{screen_height}+0+0")

        self.database = database

        self.sidebar_visible = True
        self.sidebar_frame = None
        self.icon_bar = None

        self.toggle_btn = None

        self.load_config()

        self.create_sidebar()
        self.create_main_content()

        self.show_dashboard()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.sidebar_visible = config.get("sidebar_visible", True)
            except Exception as e:
                print("Erro ao carregar config:", e)
                self.sidebar_visible = True

    def save_config(self):
        config = {
            "sidebar_visible": self.sidebar_visible
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print("Erro ao salvar config:", e)

    def create_sidebar(self):
        if self.sidebar_frame:
            self.sidebar_frame.destroy()
            self.sidebar_frame = None

        if self.icon_bar:
            self.icon_bar.destroy()
            self.icon_bar = None

        if self.toggle_btn:
            self.toggle_btn.destroy()
            self.toggle_btn = None

        if self.sidebar_visible:
            self.sidebar_frame = tk.Frame(self.master, bg="#f4f4f4", width=260)
            self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

            toggle_frame = tk.Frame(self.sidebar_frame, bg="#f4f4f4")
            toggle_frame.pack(fill=tk.X, anchor="ne")

            self.toggle_btn = tk.Button(toggle_frame, text="←", command=self.toggle_sidebar, width=2)
            self.toggle_btn.pack(anchor="ne", padx=5, pady=5)

            tk.Label(self.sidebar_frame, text="Menu", bg="#f4f4f4", font=("Arial", 16, "bold")).pack(pady=10)

            options = [
                ("🏠 Dashboard", self.show_dashboard),
                ("💰 Contas", self.show_accounts),
                ("📑 Transações", self.show_transactions),
                ("💳 Cartões de Crédito", self.show_credit_cards),
                ("⚙️ Configurações", self.show_settings)
            ]

            for label, command in options:
                btn = tk.Button(self.sidebar_frame, text=label, command=command,
                                width=20, height=1, bg="#ffffff", relief=tk.GROOVE, anchor="w",
                                font=("Arial", 10))
                btn.pack(pady=3, padx=10)

        else:
            self.icon_bar = tk.Frame(self.master, bg="#e0e0e0", width=60)
            self.icon_bar.pack(side=tk.LEFT, fill=tk.Y)

            self.toggle_btn = tk.Button(self.icon_bar, text="→", command=self.toggle_sidebar, width=2)
            self.toggle_btn.pack(anchor="ne", padx=5, pady=5)

            options = [
                ("🏠", self.show_dashboard, "Dashboard"),
                ("💰", self.show_accounts, "Contas"),
                ("📑", self.show_transactions, "Transações"),
                ("💳", self.show_credit_cards, "Cartões de Crédito"),
                ("⚙️", self.show_settings, "Configurações")
            ]

            for icon, command, tooltip in options:
                btn = tk.Button(self.icon_bar, text=icon, command=command, width=4, height=2, bg="#ffffff", font=("Arial", 16))
                btn.pack(pady=6)
                self.create_tooltip(btn, tooltip)

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        self.create_sidebar()
        self.save_config()

    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.withdraw()
        label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 30
            y += widget.winfo_rooty() + 20
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def create_main_content(self):
        self.main_content = tk.Frame(self.master, bg="#ffffff")
        self.main_content.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def clear_main_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Dashboard", font=("Arial", 24), bg="#ffffff").pack(pady=20)

    def show_transactions(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Transações", font=("Arial", 24), bg="#ffffff").pack(pady=20)

    def show_credit_cards(self):
        self.clear_main_content()
        tk.Label(self.main_content, text="Cartões de Crédito", font=("Arial", 24), bg="#ffffff").pack(pady=20)

    def show_settings(self):
        self.clear_main_content()

        tk.Label(self.main_content, text="Configurações", font=("Arial", 24), bg="#ffffff").pack(pady=20)

        filtro_frame = tk.Frame(self.main_content)
        filtro_frame.pack(pady=10)

        tk.Label(filtro_frame, text="Data Início").pack()
        self.filtro_data_inicio = DateEntry(filtro_frame, date_pattern="dd/mm/yyyy")
        self.filtro_data_inicio.pack()

        tk.Label(filtro_frame, text="Data Fim").pack()
        self.filtro_data_fim = DateEntry(filtro_frame, date_pattern="dd/mm/yyyy")
        self.filtro_data_fim.pack()

        tk.Label(filtro_frame, text="Tag").pack()
        self.filtro_tag = tk.Entry(filtro_frame)
        self.filtro_tag.pack()

        tk.Label(filtro_frame, text="Banco").pack()
        self.filtro_banco = tk.Entry(filtro_frame)
        self.filtro_banco.pack()

        tk.Label(filtro_frame, text="Buscar por descrição").pack()
        self.filtro_descricao = tk.Entry(filtro_frame)
        self.filtro_descricao.pack()

        self.sort_by = tk.StringVar(value="data")

        self.tree = tk.Listbox(self.main_content, width=120)
        self.tree.pack(pady=10)

        self.total_label = tk.Label(self.main_content, text="Total: R$ 0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=5)

        tk.Button(self.main_content, text="Salvar Configuração", command=self.save_settings).pack(pady=10)

        botoes_frame = tk.Frame(self.main_content)
        botoes_frame.pack(pady=10)

        tk.Button(botoes_frame, text="Adicionar Despesa", command=self.open_add_expense_window).pack(side=tk.LEFT, padx=10)
        tk.Button(botoes_frame, text="Editar Despesa", command=self.open_edit_expense_window).pack(side=tk.LEFT, padx=10)
        tk.Button(botoes_frame, text="Remover Despesa", command=self.remover_despesa).pack(side=tk.LEFT, padx=10)
        tk.Button(botoes_frame, text="Exportar CSV", command=self.exportar_csv).pack(side=tk.LEFT, padx=10)
        tk.Button(botoes_frame, text="Resumo", command=self.mostrar_resumo).pack(side=tk.LEFT, padx=10)

        self.refresh_expenses()

    def save_settings(self):
        messagebox.showinfo("Configurações", "Funcionalidade de salvar configurações ainda não implementada.")





    def refresh_expenses(self):
        self.tree.delete(0, tk.END)
        self.despesas_filtradas = self.database.listar_despesas(
            data_inicio=self.filtro_data_inicio.get(),
            data_fim=self.filtro_data_fim.get(),
            tag=self.filtro_tag.get(),
            banco=self.filtro_banco.get(),
            busca_descricao=self.filtro_descricao.get(),
            ordenar_por=self.sort_by.get()
        )
        total = 0.0
        for i, despesa in enumerate(self.despesas_filtradas):
            self.tree.insert(
                tk.END, f"{i+1}. {despesa['descricao']} | R${despesa['valor']:.2f} | {despesa['data']} | {despesa['tag']} | {despesa['banco']}")
            total += despesa['valor']

        self.total_label.config(text=f"Total: R${total:.2f}")

    def mostrar_resumo(self):
        if not hasattr(self, 'despesas_filtradas'):
            return

        total = sum(d['valor'] for d in self.despesas_filtradas)
        por_tag = defaultdict(float)
        por_banco = defaultdict(float)

        for d in self.despesas_filtradas:
            por_tag[d['tag']] += d['valor']
            por_banco[d['banco']] += d['valor']

        janela = tk.Toplevel(self.master)
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

    def open_add_expense_window(self):
        janela = tk.Toplevel(self.master)
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
                    self.database.adicionar_despesa(**dados)
                    self.refresh_expenses()
                    janela.destroy()
                except ValueError:
                    messagebox.showerror("Erro", "O valor deve ser numérico.")
            else:
                messagebox.showwarning("Campos incompletos", "Por favor, preencha todos os campos corretamente.")

        tk.Button(janela, text="Salvar", command=salvar).grid(row=len(campos), column=0, columnspan=2, pady=10)

    def open_edit_expense_window(self):
        selected_index = self.tree.curselection()
        if not selected_index:
            messagebox.showwarning("Nenhuma seleção", "Selecione uma despesa para editar.")
            return

        index = selected_index[0]
        despesa = self.despesas_filtradas[index]

        janela = tk.Toplevel(self.master)
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
                    self.database.editar_despesa(index, **novos_dados)
                    self.refresh_expenses()
                    janela.destroy()
                except ValueError:
                    messagebox.showerror("Erro", "O valor deve ser numérico.")
            else:
                messagebox.showwarning("Campos incompletos", "Por favor, preencha todos os campos corretamente.")

        tk.Button(janela, text="Salvar Alterações", command=salvar).grid(row=len(campos), column=0, columnspan=2, pady=10)

    def remover_despesa(self):
        selected_index = self.tree.curselection()
        if not selected_index:
            messagebox.showwarning("Nenhuma seleção", "Selecione uma despesa para remover.")
            return

        index = selected_index[0]
        confirm = messagebox.askyesno("Confirmar", "Tem certeza que deseja remover esta despesa?")
        if confirm:
            self.database.remover_despesa(index)
            self.refresh_expenses()

    def exportar_csv(self):
        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if caminho:
            sucesso = self.database.exportar_para_csv(
                caminho,
                data_inicio=self.filtro_data_inicio.get(),
                data_fim=self.filtro_data_fim.get(),
                tag=self.filtro_tag.get(),
                banco=self.filtro_banco.get(),
                busca_descricao=self.filtro_descricao.get(),
                ordenar_por=self.sort_by.get()
        )
        if sucesso:
            messagebox.showinfo("Exportado", "Despesas exportadas com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha ao exportar despesas.")


    def show_accounts(self):
        self.clear_main_content()

        tk.Label(self.main_content, text="Contas Bancárias", font=("Arial", 24), bg="#ffffff").pack(pady=20)

        add_icon = tk.PhotoImage(file="icons/plus.png")
        add_btn = tk.Button(
            self.main_content,
            text=" Adicionar Conta",
            image=add_icon,
            compound="left",
            command=self.open_account_window,
            bg="#4CAF50", fg="white", font=("Arial", 11), width=180, height=35
        )
        add_btn.image = add_icon
        add_btn.pack(pady=10)

        self.account_list_frame = tk.Frame(self.main_content, bg="#ffffff")
        self.account_list_frame.pack(pady=10)

        self.update_account_list()

    def open_account_window(self):
        form_window = tk.Toplevel(self.master)
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

            self.database.adicionar_conta(
                nome=nome_banco,
                saldo_inicial=saldo_inicial,
                descricao=descricao,
                tipo=tipo,
                cor=cor
)

            
            form_window.destroy()
            self.update_account_list()


        tk.Button(form_window, text="Salvar Conta", command=submit, bg="#2196F3", fg="white").pack(pady=10)

    def update_account_list(self):
        for widget in self.account_list_frame.winfo_children():
            widget.destroy()

        contas = self.database.listar_contas()

        if not contas:
            tk.Label(self.account_list_frame, text="Nenhuma conta cadastrada.", bg="#ffffff").pack()
        else:
            for conta in contas:
                nome = conta.get("nome", "Desconhecido")
                saldo = conta.get("saldo", 0)
                cor = conta.get("cor", "#ffffff")

                conta_btn = tk.Button(
                    self.account_list_frame,
                    text=f"{nome} - Saldo: R$ {saldo:.2f}",
                    bg=cor,
                    font=("Arial", 12),
                    fg="white",
                    width=40,
                    anchor="w",
                    command=lambda c=conta: self.mostrar_detalhes_conta(c)
                )
                conta_btn.pack(anchor="w", padx=10, pady=2)

    def mostrar_detalhes_conta(self, conta):
        detalhes = tk.Toplevel(self.master)
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
        ttk.Button(cor_frame, text="Selecionar Cor", command=lambda: self.selecionar_cor(cor_var)).pack(side=tk.LEFT)

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

            self.database.salvar_dados()
            self.update_account_list()
            detalhes.destroy()

        def excluir_conta():
            confirm = messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir a conta '{conta['nome']}'?")
            if confirm:
                self.database.remover_conta(conta['nome'])
                self.update_account_list()
                detalhes.destroy()

        ttk.Button(botoes_frame, text="Salvar Alterações", command=salvar_alteracoes).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Conta", command=excluir_conta).pack(side=tk.LEFT, padx=5)

    def selecionar_cor(self, cor_var):
        cor = colorchooser.askcolor(title="Escolher Cor")[1]
        if cor:
            cor_var.set(cor)