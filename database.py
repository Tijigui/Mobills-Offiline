import json
import os
import csv
from datetime import datetime

# Constantes para uso em toda a aplicação
COLORS = {
    "Azul": "#2196F3",
    "Vermelho": "#E53935",
    "Verde": "#43A047",
    "Roxo": "#8E24AA",
    "Laranja": "#FB8C00",
    "Cinza": "#757575"
}

ACCOUNT_TYPES = [
    "Conta Corrente",
    "Conta Poupança",
    "Carteira",
    "Investimentos",
    "Outros"
]

class Database:
    def __init__(self, arquivo_dados="dados.json"):
        self.arquivo_dados = arquivo_dados
        self.dados = self.carregar_dados()
        
        # Garantir que todas as estruturas existam
        if 'contas' not in self.dados:
            self.dados['contas'] = []
        if 'despesas' not in self.dados:
            self.dados['despesas'] = []
        if 'cartoes' not in self.dados:
            self.dados['cartoes'] = []
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
                return {}
        return {}
    
    def salvar_dados(self):
        """Salva os dados no arquivo JSON"""
        try:
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
            return False
    
    # Métodos para contas
    def adicionar_conta(self, nome, saldo_inicial, descricao, tipo, cor):
        """Adiciona uma nova conta bancária"""
        nova_conta = {
            "nome": nome,
            "saldo": float(saldo_inicial),
            "saldo_inicial": float(saldo_inicial),
            "descricao": descricao,
            "tipo": tipo,
            "cor": cor,
            "data_criacao": datetime.now().strftime("%d/%m/%Y")
        }
        
        # Verificar se já existe uma conta com o mesmo nome
        for conta in self.dados['contas']:
            if conta['nome'] == nome:
                return False
        
        self.dados['contas'].append(nova_conta)
        self.salvar_dados()
        return True
    
    def listar_contas(self):
        """Retorna a lista de contas cadastradas"""
        return self.dados['contas']
    
    def obter_conta(self, nome):
        """Obtém uma conta pelo nome"""
        for conta in self.dados['contas']:
            if conta['nome'] == nome:
                return conta
        return None
    
    def atualizar_conta(self, nome_original, nome, saldo, descricao, tipo, cor):
        """Atualiza os dados de uma conta existente"""
        for i, conta in enumerate(self.dados['contas']):
            if conta['nome'] == nome_original:
                self.dados['contas'][i] = {
                    "nome": nome,
                    "saldo": float(saldo),
                    "saldo_inicial": conta.get('saldo_inicial', float(saldo)),
                    "descricao": descricao,
                    "tipo": tipo,
                    "cor": cor,
                    "data_criacao": conta.get('data_criacao', datetime.now().strftime("%d/%m/%Y"))
                }
                self.salvar_dados()
                return True
        return False
    
    def remover_conta(self, nome):
        """Remove uma conta pelo nome"""
        for i, conta in enumerate(self.dados['contas']):
            if conta['nome'] == nome:
                del self.dados['contas'][i]
                self.salvar_dados()
                return True
        return False
    
    # Métodos para despesas
    def adicionar_despesa(self, descricao, valor, data, tag, banco):
        """Adiciona uma nova despesa"""
        nova_despesa = {
            "descricao": descricao,
            "valor": float(valor),
            "data": data,
            "tag": tag,
            "banco": banco
        }
        
        if 'despesas' not in self.dados:
            self.dados['despesas'] = []
        
        self.dados['despesas'].append(nova_despesa)
        self.salvar_dados()
        return True
    
    def listar_despesas(self, data_inicio=None, data_fim=None, tag=None, banco=None, busca_descricao=None, ordenar_por="data"):
        """Lista despesas com filtros opcionais"""
        if 'despesas' not in self.dados:
            return []
        
        despesas_filtradas = self.dados['despesas']
        
        # Aplicar filtros
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
                despesas_filtradas = [d for d in despesas_filtradas if datetime.strptime(d['data'], "%d/%m/%Y") >= data_inicio_obj]
            except:
                pass
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y")
                despesas_filtradas = [d for d in despesas_filtradas if datetime.strptime(d['data'], "%d/%m/%Y") <= data_fim_obj]
            except:
                pass
        
        if tag and tag.strip():
            despesas_filtradas = [d for d in despesas_filtradas if tag.lower() in d['tag'].lower()]
        
        if banco and banco.strip():
            despesas_filtradas = [d for d in despesas_filtradas if banco.lower() in d['banco'].lower()]
        
        if busca_descricao and busca_descricao.strip():
            despesas_filtradas = [d for d in despesas_filtradas if busca_descricao.lower() in d['descricao'].lower()]
        
        # Ordenar resultados
        if ordenar_por == "data":
            despesas_filtradas.sort(key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y"), reverse=True)
        elif ordenar_por == "valor":
            despesas_filtradas.sort(key=lambda x: x['valor'], reverse=True)
        elif ordenar_por == "descricao":
            despesas_filtradas.sort(key=lambda x: x['descricao'].lower())
        
        return despesas_filtradas
    
    def editar_despesa(self, indice, descricao, valor, data, tag, banco):
        """Edita uma despesa existente pelo índice"""
        if 'despesas' not in self.dados or indice >= len(self.dados['despesas']):
            return False
        
        self.dados['despesas'][indice] = {
            "descricao": descricao,
            "valor": float(valor),
            "data": data,
            "tag": tag,
            "banco": banco
        }
        
        self.salvar_dados()
        return True
    
    def remover_despesa(self, indice):
        """Remove uma despesa pelo índice"""
        if 'despesas' not in self.dados or indice >= len(self.dados['despesas']):
            return False
        
        del self.dados['despesas'][indice]
        self.salvar_dados()
        return True
    
    def exportar_para_csv(self, caminho, data_inicio=None, data_fim=None, tag=None, banco=None, busca_descricao=None, ordenar_por="data"):
        """Exporta despesas para CSV com filtros opcionais"""
        despesas = self.listar_despesas(data_inicio, data_fim, tag, banco, busca_descricao, ordenar_por)
        
        try:
            with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
                writer = csv.writer(arquivo)
                writer.writerow(['Descrição', 'Valor', 'Data', 'Tag', 'Banco'])
                
                for despesa in despesas:
                    writer.writerow([
                        despesa['descricao'],
                        despesa['valor'],
                        despesa['data'],
                        despesa['tag'],
                        despesa['banco']
                    ])
            return True
        except Exception as e:
            print(f"Erro ao exportar para CSV: {e}")
            return False
    
    # Métodos para cartões de crédito
    def listar_cartoes(self):
        """Retorna a lista de cartões de crédito cadastrados"""
        if 'cartoes' not in self.dados:
            self.dados['cartoes'] = []
        return self.dados['cartoes']
    
    def adicionar_cartao(self, cartao):
        """Adiciona um novo cartão de crédito"""
        if 'cartoes' not in self.dados:
            self.dados['cartoes'] = []
        
        # Gerar ID único se não for fornecido
        if 'id' not in cartao:
            ids = [c.get('id', 0) for c in self.dados['cartoes']]
            cartao['id'] = max(ids + [0]) + 1
        
        self.dados['cartoes'].append(cartao)
        self.salvar_dados()
        return True
    
    def atualizar_cartao(self, cartao):
        """Atualiza um cartão existente"""
        if 'cartoes' not in self.dados:
            return False
        
        for i, c in enumerate(self.dados['cartoes']):
            if c.get('id') == cartao.get('id') or c.get('nome') == cartao.get('nome'):
                self.dados['cartoes'][i] = cartao
                self.salvar_dados()
                return True
        return False
    
    def remover_cartao(self, cartao):
        """Remove um cartão de crédito"""
        if 'cartoes' not in self.dados:
            return False
        
        for i, c in enumerate(self.dados['cartoes']):
            if c.get('id') == cartao.get('id') or c.get('nome') == cartao.get('nome'):
                del self.dados['cartoes'][i]
                self.salvar_dados()
                return True
        return False