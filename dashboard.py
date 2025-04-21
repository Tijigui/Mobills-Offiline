import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

def mostrar_dashboard(app):
    """
    Exibe o dashboard principal com gráficos e resumos financeiros.
    
    Args:
        app: Instância da aplicação principal
    """
    tk.Label(app.main_content, text="Dashboard", font=("Arial", 24), bg="#ffffff").pack(pady=20)
    
    # Aqui você pode adicionar gráficos e visualizações para o dashboard
    
    # Frame para resumo financeiro
    resumo_frame = tk.Frame(app.main_content, bg="#ffffff")
    resumo_frame.pack(pady=20, fill=tk.X, padx=20)
    
    # Exemplo de como mostrar um gráfico básico
    criar_grafico_resumo(app)

def criar_grafico_resumo(app):
    """
    Cria e exibe um gráfico de resumo financeiro no dashboard.
    
    Args:
        app: Instância da aplicação principal
    """
    # Obter dados do banco de dados
    try:
        # Aqui você pode implementar a lógica para obter os dados do seu banco de dados
        # Por exemplo, obter as despesas dos últimos meses
        
        # Exemplo simples para demonstração
        dados_despesas = defaultdict(float)
        dados_receitas = defaultdict(float)
        
        # Simular alguns dados para o gráfico
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        despesas = [1200, 1350, 1100, 1400, 1300, 1250]
        receitas = [2000, 2100, 2050, 2200, 2300, 2150]
        
        for i, mes in enumerate(meses):
            dados_despesas[mes] = despesas[i]
            dados_receitas[mes] = receitas[i]
        
        # Criar gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar([i-0.2 for i in range(len(meses))], despesas, width=0.4, label='Despesas', color='#f44336')
        ax.bar([i+0.2 for i in range(len(meses))], receitas, width=0.4, label='Receitas', color='#4CAF50')
        
        ax.set_xlabel('Mês')
        ax.set_ylabel('Valor (R$)')
        ax.set_title('Resumo Financeiro')
        ax.set_xticks(range(len(meses)))
        ax.set_xticklabels(meses)
        ax.legend()
        
        # Incorporar o gráfico na interface
        canvas = FigureCanvasTkAgg(fig, master=app.main_content)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
    except Exception as e:
        print(f"Erro ao criar gráfico: {e}")
        tk.Label(app.main_content, text="Não foi possível carregar o gráfico", 
                 font=("Arial", 12), bg="#ffffff", fg="red").pack(pady=10)