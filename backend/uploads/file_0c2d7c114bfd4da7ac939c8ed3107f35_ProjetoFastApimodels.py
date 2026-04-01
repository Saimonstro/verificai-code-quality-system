from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils import ChoiceType

# cria a conexão com o banco
db = create_engine("sqlite:///banco.db")

# cria a  base para o banco de dados
Base = declarative_base()

# cria as classes/tabelas
# Usuário
class Usuario(Base):
    __tablename__ = "usuarios"

    id  = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

# Pedido
class Pedido(Base):
    __tablename__ = "pedidos"
    '''
    STATUS_PEDIDOS = (
        ("PENDENTE", "PENDENTE"),
        ("CANCELADO", "CANCELADO"),
        ("FINALIZADO", "FINALIZADO")
    )
    '''
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    usuario = Column("usuario", ForeignKey("usuarios.id"))
    preco = Column("preco", Float)
    itens = relationship("ItemPedido", cascade="all, delete")
    
    
    def __init__(self, usuario, status="PENDENTE", preco=0):
        self.usuario = usuario
        self.preco = preco  
        self.status = status

    def calcular_preco(self):
        #percorrer itens
        #somar os preços
        #editar o preco do pedido
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)
    
# Itens do Pedido
class ItemPedido(Base):
    __tablename__ = "itens_pedidos" 

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    sabor = Column("sabor", String)
    tamanho = Column("tamanho", String)
    preco_unitario = Column("preco_unitario", Float)
    pedido = Column("pedido", ForeignKey("pedidos.id"))

    def __init__(self, quantidade, sabor, tamanho, preco_unitario, pedido):
        self.quantidade = quantidade
        self.sabor = sabor
        self.tamanho = tamanho
        self.preco_unitario = preco_unitario
        self.pedido = pedido

# -- MIGRAR O BANCO --

# criar a migração: alembic revision --autogenerate -m "MENSSAGEM DA MIGRAÇÃO"
# aplicar a migração: alembic upgrade head
# remover a migração: alembic downgrade -1  