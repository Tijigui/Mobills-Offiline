import tkinter as tk
from tkinter import messagebox, filedialog, ttk, colorchooser
from tkcalendar import DateEntry
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
from datetime import datetime
import csv

CONFIG_FILE = "config.json"

BANKS = [
    "Santander", "Nubank", "Banco do Brasil", "Caixa", "Itau",
    "Bradesco", "Pic Pay", "Banco Inter", "C6 Bank"
]

ACCOUNT_TYPES = [
    "Conta Corrente", "Dinheiro", "Poupança", "Investimento", "VR/VA", "Outros"
]

COLORS = {
    "Azul": "#2196F3",
    "Roxo": "#9C27B0",
    "Vermelho": "#F44336",
    "Laranja": "#FF9800"
}

class Database:
    def __init__(self, arquivo_dados="dados.json"):
        self.arquivo_dados = arquivo_dados
        self.dados = {
            "despesas": [],
            "contas": []
        }
        self.carregar_dados()

    def carregar_dados(self):
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, "r", encoding="utf-8") as f:
                    self.dados = json.load(f)
                for despesa in self.dados.get("despesas", []):
                    try:
                        despesa["valor"] = float(despesa["valor"])
                    except (ValueError, TypeError):
                        despesa["valor"] = 0.0
            except json.JSONDecodeError:
                print("Erro ao carregar o arquivo de dados. Usando estrutura vazia.")
                self.dados = {"despesas": [], "contas": []}

    def salvar_dados(self):
        with open(self.arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

    def adicionar_conta(self, nome, saldo_inicial, descricao, tipo, cor):
        if any(c['nome'].lower() == nome.lower() for c in self.dados["contas"]):
            print(f"Conta com nome '{nome}' já existe.")
            return False
        nova_conta = {
            "nome": nome.strip(),
            "saldo": float(saldo_inicial),
            "descricao": descricao.strip(),
            "tipo": tipo.strip(),
            "cor": cor.strip()
        }
        self.dados["contas"].append(nova_conta)
        self.salvar_dados()
        return True

    def remover_conta(self, nome):
        original = len(self.dados["contas"])
        self.dados["contas"] = [c for c in self.dados["contas"] if c['nome'].lower() != nome.lower()]
        self.salvar_dados()
        return len(self.dados["contas"]) < original

    def atualizar_saldo(self, nome, novo_saldo):
        for conta in self.dados["contas"]:
            if conta['nome'].lower() == nome.lower():
                conta['saldo'] = float(novo_saldo)
                self.salvar_dados()
                return True
        return False

    def listar_contas(self):
        return self.dados.get("contas", [])

    def adicionar_despesa(self, descricao, valor, data, tag, banco, observacoes=""):
        try:
            valor = float(str(valor).replace(",", "."))
            if not self._validar_data(data):
                print(f"Data inválida: {data}.")
                return False
            despesa = {
                "descricao": descricao.strip(),
                "valor": valor,
                "data": data,
                "tag": tag.strip(),
                "banco": banco.strip(),
                "observacoes": observacoes.strip()
            }
            self.dados["despesas"].append(despesa)
            self.salvar_dados()
            return True
        except Exception as e:
            print(f"Erro ao adicionar despesa: {e}")
            return False

    def listar_despesas(self, data_inicio=None, data_fim=None, tag=None, banco=None, busca_descricao=None, ordenar_por=None):
        despesas = self.dados.get("despesas", []).copy()

        if data_inicio:
            data_inicio_obj = self._normalizar_data(data_inicio)
            despesas = [d for d in despesas if self._normalizar_data(d["data"]) >= data_inicio_obj]

        if data_fim:
            data_fim_obj = self._normalizar_data(data_fim)
            despesas = [d for d in despesas if self._normalizar_data(d["data"]) <= data_fim_obj]

        if tag:
            despesas = [d for d in despesas if tag.lower() in d.get("tag", "").lower()]

        if banco:
            despesas = [d for d in despesas if banco.lower() in d.get("banco", "").lower()]

        if busca_descricao:
            despesas = [d for d in despesas if busca_descricao.lower() in d.get("descricao", "").lower()]

        if ordenar_por == "Data":
            despesas.sort(key=lambda d: self._normalizar_data(d["data"]) or datetime.min)
        elif ordenar_por == "Valor":
            despesas.sort(key=lambda d: d.get("valor", 0))
        elif ordenar_por == "Descrição":
            despesas.sort(key=lambda d: d.get("descricao", "").lower())

        return despesas

    def remover_despesa(self, index):
        try:
            if 0 <= index < len(self.dados["despesas"]):
                del self.dados["despesas"][index]
                self.salvar_dados()
                return True
            return False
        except Exception as e:
            print(f"Erro ao remover despesa: {e}")
            return False

    def editar_despesa(self, index, descricao, valor, data, tag, banco, observacoes=""):
        try:
            if 0 <= index < len(self.dados["despesas"]):
                valor = float(valor)
                if not self._validar_data(data):
                    print(f"Data inválida: {data}.")
                    return False
                self.dados["despesas"][index] = {
                    "descricao": descricao.strip(),
                    "valor": valor,
                    "data": data,
                    "tag": tag.strip(),
                    "banco": banco.strip(),
                    "observacoes": observacoes.strip()
                }
                self.salvar_dados()
                return True
            return False
        except Exception as e:
            print(f"Erro ao editar despesa: {e}")
            return False

    def exportar_para_csv(self, caminho):
        try:
            with open(caminho, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["descricao", "valor", "data", "tag", "banco", "observacoes"])
                writer.writeheader()
                for despesa in self.dados.get("despesas", []):
                    writer.writerow(despesa)
            return True
        except Exception as e:
            print(f"Erro ao exportar para CSV: {e}")
            return False

    def obter_resumo_financeiro(self):
        resumo = defaultdict(float)
        for despesa in self.dados.get("despesas", []):
            tag = despesa.get("tag", "Outros")
            resumo[tag] += despesa.get("valor", 0.0)
        return dict(resumo)

    def _validar_data(self, data_str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                datetime.strptime(data_str, fmt)
                return True
            except ValueError:
                continue
        return False

    def _normalizar_data(self, data_str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(data_str, fmt)
            except ValueError:
                continue
        return None
