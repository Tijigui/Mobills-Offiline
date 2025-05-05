import json
import os
import csv
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, MetaData, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('FinancasApp')

# Carregar variáveis de ambiente
load_dotenv()

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

EXPENSE_CATEGORIES = [
    "Alimentação",
    "Transporte",
    "Moradia",
    "Saúde",
    "Lazer",
    "Educação",
    "Outros"
]

class Database:
    def __init__(self, arquivo_dados="dados.json"):
        self.arquivo_dados = arquivo_dados
        self.use_postgres = os.getenv('USE_POSTGRES', 'False').lower() == 'true'
        self.engine = None
        self.metadata = None
        self.contas_table = None
        self.despesas_table = None
        self.cartoes_table = None
        
        # Configuração do PostgreSQL
        if self.use_postgres:
            self.db_host = os.getenv('DB_HOST', 'localhost')
            self.db_port = os.getenv('DB_PORT', '5432')
            self.db_name = os.getenv('DB_NAME', 'financas')
            self.db_user = os.getenv('DB_USER', 'postgres')
            self.db_password = os.getenv('DB_PASSWORD', '')
            
            # Configurar SQLAlchemy
            if not self.setup_postgres():
                logger.warning("Falha na configuração do PostgreSQL. Usando JSON como fallback.")
                self.use_postgres = False
        
        # Carregar dados do JSON ou PostgreSQL
        self.dados = self.carregar_dados()
        
        # Garantir que todas as estruturas existam
        if 'contas' not in self.dados:
            self.dados['contas'] = []
        if 'despesas' not in self.dados:
            self.dados['despesas'] = []
        if 'cartoes' not in self.dados:
            self.dados['cartoes'] = []
    
    def setup_postgres(self):
        """Configura a conexão com PostgreSQL e cria tabelas se necessário"""
        try:
            # String de conexão
            self.db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
            self.engine = create_engine(self.db_url)
            self.Base = declarative_base()
            self.Session = sessionmaker(bind=self.engine)
            
            # Definir metadados
            self.metadata = MetaData()
            
            # Definir tabelas
            self.contas_table = Table(
                'contas', self.metadata,
                Column('id', Integer, primary_key=True),
                Column('nome', String(255), unique=True, nullable=False),
                Column('saldo', Float, nullable=False),
                Column('saldo_inicial', Float, nullable=False),
                Column('descricao', Text),
                Column('tipo', String(100)),
                Column('cor', String(50)),
                Column('data_criacao', String(20))
            )
            
            self.despesas_table = Table(
                'despesas', self.metadata,
                Column('id', Integer, primary_key=True),
                Column('descricao', String(255), nullable=False),
                Column('valor', Float, nullable=False),
                Column('data', String(20)),
                Column('tag', String(100)),
                Column('banco', String(100)),
                Column('categoria', String(100))
            )
            
            self.cartoes_table = Table(
                'cartoes', self.metadata,
                Column('id', Integer, primary_key=True),
                Column('nome', String(255), unique=True, nullable=False),
                Column('limite', Float),
                Column('fechamento', Integer),
                Column('vencimento', Integer),
                Column('cor', String(50)),
                Column('dados_adicionais', JSON)
            )
            
            # Criar tabelas se não existirem
            self.metadata.create_all(self.engine)
            
            logger.info("Conexão com PostgreSQL estabelecida com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao configurar PostgreSQL: {e}")
            self.use_postgres = False
            return False
    
    def carregar_dados(self):
        """Carrega os dados do arquivo JSON ou do PostgreSQL"""
        if self.use_postgres:
            try:
                dados = {'contas': [], 'despesas': [], 'cartoes': []}
                
                # Carregar contas
                with self.engine.connect() as conn:
                    result = conn.execute(self.contas_table.select())
                    for row in result:
                        dados['contas'].append({
                            'nome': row.nome,
                            'saldo': float(row.saldo),
                            'saldo_inicial': float(row.saldo_inicial),
                            'descricao': row.descricao,
                            'tipo': row.tipo,
                            'cor': row.cor,
                            'data_criacao': row.data_criacao
                        })
                
                # Carregar despesas
                with self.engine.connect() as conn:
                    result = conn.execute(self.despesas_table.select())
                    for row in result:
                        dados['despesas'].append({
                            'id': row.id,
                            'descricao': row.descricao,
                            'valor': float(row.valor),
                            'data': row.data,
                            'tag': row.tag,
                            'banco': row.banco,
                            'categoria': row.categoria
                        })
                
                # Carregar cartões
                with self.engine.connect() as conn:
                    result = conn.execute(self.cartoes_table.select())
                    for row in result:
                        cartao = {
                            'id': row.id,
                            'nome': row.nome,
                            'limite': float(row.limite) if row.limite else 0,
                            'fechamento': row.fechamento,
                            'vencimento': row.vencimento,
                            'cor': row.cor
                        }
                        if row.dados_adicionais:
                            cartao.update(row.dados_adicionais)
                        dados['cartoes'].append(cartao)
                
                return dados
            except Exception as e:
                logger.error(f"Erro ao carregar dados do PostgreSQL: {e}")
                # Fallback para JSON se houver erro
                self.use_postgres = False
        
        # Carregar do JSON se não estiver usando PostgreSQL ou se houve erro
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar dados do JSON: {e}")
                return {}
        return {}
    
    def salvar_dados(self):
        """Salva os dados no arquivo JSON ou no PostgreSQL"""
        if self.use_postgres:
            try:
                # Salvar contas
                with self.engine.connect() as conn:
                    # Limpar tabela
                    conn.execute(self.contas_table.delete())
                    
                    # Inserir dados atualizados
                    for conta in self.dados['contas']:
                        conn.execute(self.contas_table.insert().values(
                            nome=conta['nome'],
                            saldo=conta['saldo'],
                            saldo_inicial=conta['saldo_inicial'],
                            descricao=conta.get('descricao', ''),
                            tipo=conta.get('tipo', ''),
                            cor=conta.get('cor', ''),
                            data_criacao=conta.get('data_criacao', datetime.now().strftime("%d/%m/%Y"))
                        ))
                
                # Salvar despesas
                with self.engine.connect() as conn:
                    # Limpar tabela
                    conn.execute(self.despesas_table.delete())
                    
                    # Inserir dados atualizados
                    for i, despesa in enumerate(self.dados['despesas']):
                        conn.execute(self.despesas_table.insert().values(
                            id=i+1,
                            descricao=despesa['descricao'],
                            valor=despesa['valor'],
                            data=despesa['data'],
                            tag=despesa.get('tag', ''),
                            banco=despesa.get('banco', ''),
                            categoria=despesa.get('categoria', '')
                        ))
                
                # Salvar cartões
                with self.engine.connect() as conn:
                    # Limpar tabela
                    conn.execute(self.cartoes_table.delete())
                    
                    # Inserir dados atualizados
                    for cartao in self.dados['cartoes']:
                        # Separar dados básicos dos adicionais
                        dados_basicos = {
                            'id': cartao.get('id', 0),
                            'nome': cartao['nome'],
                            'limite': cartao.get('limite', 0),
                            'fechamento': cartao.get('fechamento', 1),
                            'vencimento': cartao.get('vencimento', 10),
                            'cor': cartao.get('cor', '#757575')
                        }
                        
                        # Dados adicionais (qualquer outro campo)
                        dados_adicionais = {k: v for k, v in cartao.items() 
                                           if k not in ['id', 'nome', 'limite', 'fechamento', 'vencimento', 'cor']}
                        
                        conn.execute(self.cartoes_table.insert().values(
                            id=dados_basicos['id'],
                            nome=dados_basicos['nome'],
                            limite=dados_basicos['limite'],
                            fechamento=dados_basicos['fechamento'],
                            vencimento=dados_basicos['vencimento'],
                            cor=dados_basicos['cor'],
                            dados_adicionais=dados_adicionais
                        ))
                
                return True
            except Exception as e:
                logger.error(f"Erro ao salvar dados no PostgreSQL: {e}")
                # Fallback para JSON se houver erro
                if not self.salvar_dados_json():
                    return False
        else:
            # Salvar no JSON se não estiver usando PostgreSQL
            return self.salvar_dados_json()
        
        return True
    
    def salvar_dados_json(self):
        """Salva os dados no arquivo JSON"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(os.path.abspath(self.arquivo_dados)), exist_ok=True)
            
            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados no JSON: {e}")
            return False
    
    # Métodos para contas
    def adicionar_conta(self, nome, saldo_inicial, descricao, tipo, cor):
        """Adiciona uma nova conta bancária"""
        # Validação de entrada
        if not nome or nome.strip() == "":
            return False
        
        try:
            saldo_inicial = float(saldo_inicial)
        except (ValueError, TypeError):
            return False
            
        nova_conta = {
            "nome": nome,
            "saldo": saldo_inicial,
            "saldo_inicial": saldo_inicial,
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
        # Validação de entrada
        if not nome or nome.strip() == "":
            return False
        
        try:
            saldo = float(saldo)
        except (ValueError, TypeError):
            return False
            
        # Verificar se o novo nome já existe em outra conta
        if nome != nome_original:
            for conta in self.dados['contas']:
                if conta['nome'] == nome:
                    return False
        
        for i, conta in enumerate(self.dados['contas']):
            if conta['nome'] == nome_original:
                self.dados['contas'][i] = {
                    "nome": nome,
                    "saldo": saldo,
                    "saldo_inicial": conta.get('saldo_inicial', saldo),
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
    
    def calcular_saldo_total(self):
        """Calcula o saldo total de todas as contas"""
        saldo_total = 0
        for conta in self.dados['contas']:
            saldo_total += conta['saldo']
        return saldo_total
    
    # Métodos para despesas
    def adicionar_despesa(self, descricao, valor, data, tag, banco, categoria):
        """Adiciona uma nova despesa"""
        # Validação de entrada
        if not descricao or descricao.strip() == "":
            return False
        
        try:
            valor = float(valor)
        except (ValueError, TypeError):
            return False
            
        try:
            # Validar formato da data
            datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            return False
            
        nova_despesa = {
            "descricao": descricao,
            "valor": valor,
            "data": data,
            "tag": tag,
            "banco": banco,
            "categoria": categoria
        }
        
        if 'despesas' not in self.dados:
            self.dados['despesas'] = []
        
        self.dados['despesas'].append(nova_despesa)
        
        # Atualizar saldo da conta se banco for especificado
        if banco:
            for i, conta in enumerate(self.dados['contas']):
                if conta['nome'] == banco:
                    self.dados['contas'][i]['saldo'] -= valor
                    break
                    
        self.salvar_dados()
        return True
    
    def listar_despesas(self, data_inicio=None, data_fim=None, tag=None, banco=None, busca_descricao=None, categoria=None, ordenar_por="data"):
        """Lista despesas com filtros opcionais"""
        if 'despesas' not in self.dados:
            return []
        
        despesas_filtradas = self.dados['despesas']
        
        # Aplicar filtros
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
                despesas_filtradas = [d for d in despesas_filtradas if datetime.strptime(d['data'], "%d/%m/%Y") >= data_inicio_obj]
            except ValueError:
                logger.warning(f"Formato de data inválido para data_inicio: {data_inicio}")
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y")
                despesas_filtradas = [d for d in despesas_filtradas if datetime.strptime(d['data'], "%d/%m/%Y") <= data_fim_obj]
            except ValueError:
                logger.warning(f"Formato de data inválido para data_fim: {data_fim}")
        
        if tag and tag.strip():
            despesas_filtradas = [d for d in despesas_filtradas if 'tag' in d and tag.lower() in d['tag'].lower()]
        
        if banco and banco.strip():
            despesas_filtradas = [d for d in despesas_filtradas if 'banco' in d and banco.lower() in d['banco'].lower()]
        
        if busca_descricao and busca_descricao.strip():
            despesas_filtradas = [d for d in despesas_filtradas if busca_descricao.lower() in d['descricao'].lower()]
        
        if categoria and categoria.strip():
            despesas_filtradas = [d for d in despesas_filtradas if 'categoria' in d and categoria.lower() in d['categoria'].lower()]
        
        # Ordenar resultados
        if ordenar_por == "data":
            despesas_filtradas.sort(key=lambda x: datetime.strptime(x['data'], "%d/%m/%Y"), reverse=True)
        elif ordenar_por == "valor":
            despesas_filtradas.sort(key=lambda x: x['valor'], reverse=True)
        elif ordenar_por == "descricao":
            despesas_filtradas.sort(key=lambda x: x['descricao'].lower())
        
        return despesas_filtradas
    
    def editar_despesa(self, indice, descricao, valor, data, tag, banco, categoria):
        """Edita uma despesa existente pelo índice"""
        if 'despesas' not in self.dados or indice < 0 or indice >= len(self.dados['despesas']):
            return False
        
        # Validação de entrada
        if not descricao or descricao.strip() == "":
            return False
        
        try:
            valor = float(valor)
        except (ValueError, TypeError):
            return False
            
        try:
            # Validar formato da data
            datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            return False
        
        # Armazenar valores antigos para ajustar saldo
        despesa_antiga = self.dados['despesas'][indice]
        banco_antigo = despesa_antiga.get('banco', '')
        valor_antigo = despesa_antiga.get('valor', 0)
        
        self.dados['despesas'][indice] = {
            "descricao": descricao,
            "valor": valor,
            "data": data,
            "tag": tag,
            "banco": banco,
            "categoria": categoria
        }
        
        # Ajustar saldos das contas se necessário
        if banco_antigo:
            for i, conta in enumerate(self.dados['contas']):
                if conta['nome'] == banco_antigo:
                    self.dados['contas'][i]['saldo'] += valor_antigo
                    break
                    
        if banco:
            for i, conta in enumerate(self.dados['contas']):
                if conta['nome'] == banco:
                    self.dados['contas'][i]['saldo'] -= valor
                    break
        
        self.salvar_dados()
        return True
    
    def remover_despesa(self, indice):
        """Remove uma despesa pelo índice"""
        if 'despesas' not in self.dados or indice < 0 or indice >= len(self.dados['despesas']):
            return False
        
        # Ajustar saldo da conta se a despesa estava associada a uma
        despesa = self.dados['despesas'][indice]
        if 'banco' in despesa and despesa['banco']:
            for i, conta in enumerate(self.dados['contas']):
                if conta['nome'] == despesa['banco']:
                    self.dados['contas'][i]['saldo'] += despesa['valor']
                    break
        
        del self.dados['despesas'][indice]
        self.salvar_dados()
        return True
    
    def exportar_para_csv(self, caminho, data_inicio=None, data_fim=None, tag=None, banco=None, busca_descricao=None, categoria=None, ordenar_por="data"):
        """Exporta despesas para CSV com filtros opcionais"""
        despesas = self.listar_despesas(data_inicio, data_fim, tag, banco, busca_descricao, categoria, ordenar_por)
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
            
            with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
                writer = csv.writer(arquivo)
                writer.writerow(['Descrição', 'Valor', 'Data', 'Tag', 'Banco', 'Categoria'])
                
                for despesa in despesas:
                    writer.writerow([
                        despesa['descricao'],
                        despesa['valor'],
                        despesa['data'],
                        despesa.get('tag', ''),
                        despesa.get('banco', ''),
                        despesa.get('categoria', '')
                    ])
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {e}")
            return False
    
    # Métodos para cartões de crédito
    def listar_cartoes(self):
        """Retorna a lista de cartões de crédito cadastrados"""
        if 'cartoes' not in self.dados:
            self.dados['cartoes'] = []
        return self.dados['cartoes']
    
    def adicionar_cartao(self, cartao):
        """Adiciona um novo cartão de crédito"""
        # Validação básica
        if not cartao.get('nome') or cartao['nome'].strip() == "":
            return False
            
        try:
            if 'limite' in cartao:
                cartao['limite'] = float(cartao['limite'])
        except (ValueError, TypeError):
            cartao['limite'] = 0
            
        if 'cartoes' not in self.dados:
            self.dados['cartoes'] = []
        
        # Verificar se já existe um cartão com o mesmo nome
        for c in self.dados['cartoes']:
            if c['nome'] == cartao['nome']:
                return False
        
        # Gerar ID único se não for fornecido
        if 'id' not in cartao:
            ids = [c.get('id', 0) for c in self.dados['cartoes']]
            cartao['id'] = max(ids + [0]) + 1
        
        self.dados['cartoes'].append(cartao)
        self.salvar_dados()
        return True
    
    def atualizar_cartao(self, cartao):
        """Atualiza um cartão existente"""
        # Validação básica
        if not cartao.get('nome') or cartao['nome'].strip() == "":
            return False
            
        try:
            if 'limite' in cartao:
                cartao['limite'] = float(cartao['limite'])
        except (ValueError, TypeError):
            cartao['limite'] = 0
            
        if 'cartoes' not in self.dados:
            return False
        
        # Verificar se o nome já existe em outro cartão
        for c in self.dados['cartoes']:
            if c['nome'] == cartao['nome'] and c.get('id') != cartao.get('id'):
                return False
        
        for i, c in enumerate(self.dados['cartoes']):
            if c.get('id') == cartao.get('id') or c.get('nome') == cartao.get('nome'):
                self.dados['cartoes'][i] = cartao
                self.salvar_dados()
                return True
        return False
    
    def remover_cartao(self, cartao_id):
        """Remove um cartão de crédito pelo ID ou nome"""
        if 'cartoes' not in self.dados:
            return False
        
        for i, c in enumerate(self.dados['cartoes']):
            if c.get('id') == cartao_id or c.get('nome') == cartao_id:
                del self.dados['cartoes'][i]
                self.salvar_dados()
                return True
        return False
    
    def testar_conexao_postgres(self):
        """Testa a conexão com o PostgreSQL"""
        if not self.use_postgres:
            return False, "PostgreSQL não está configurado para uso"
        
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            conn.close()
            return True, "Conexão com PostgreSQL bem-sucedida!"
        except Exception as e:
            return False, f"Erro ao conectar ao PostgreSQL: {str(e)}"
