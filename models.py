from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, declarative_base


import os

import configparser


url_ =os.environ.get('DATABASE.URL')

print(f'modo1:{url_}')



config = configparser.ConfigParser()

config.read('config.ini')

database_url = config['DATABASE']['URL']

print(f'modo2:{database_url}')

engine = create_engine('sqlite:///TechManagers.db')
#engine = create_engine(database_url)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Funcionario(Base):
    __tablename__ = 'funcionario'
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    email = Column(String(40), nullable=False, index=True)
    cpf = Column(String(11), nullable=False, index=True, unique=True)
    senha = Column(String(11), nullable=False, index=True)
    admin = Column(String(11), nullable=False, index=True)

    def __repr__(self):
        return '<Funcionario: {}>'.format(self.nome, self.email, self.cpf, self.senha, self.admin)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_funcionario(self):
        dados_funcionario = {
            'funcionario_id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cpf': self.cpf,
            'senha': self.senha,
            'admin': self.admin

        }
        return dados_funcionario


class ITEM(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, index=True)
    nome = Column(String(40), nullable=False, index=True)
    tipo = Column(String(40), nullable=False, index=True)
    Quantidade = Column(Integer, nullable=False, index=True)

    def __repr__(self):
        return '<EPI: {}>'.format(self.nome, self.tipo, self.Quantidade)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_epi(self):
        dados_epi = {
            'EPI_id': self.id,
            'nome': self.nome,
            'validade': self.tipo,
            'Descricao': self.Quantidade
        }
        return dados_epi


class MOVIMENTACAO(Base):
    __tablename__ = 'movimentacao'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, index=True)
    movimentacao_item = Column(String(40), nullable=False)
    item_id = Column(Integer, ForeignKey('estoque.id'), nullable=False)
    item = relationship('ESTOQUE', backref='estoques')
    funcionario_id = Column(Integer, ForeignKey('funcionario.id'), nullable=False)
    funcionario = relationship('FUNCIONARIO', backref='funcionarios')
    data_estoque = Column(String(255), nullable=False, index=True)
    estoque_quantidade = Column(Integer, ForeignKey('epi.id'))

    def __repr__(self):
        return '<Entrega: {}>'.format(self.movimentacao_item, self.item_id, self.funcionario_id, self.data_estoque, self.estoque_quantidade)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_entrega(self):
        dados_entrega = {
            'estoque_id': self.id,
            'estoque_quantidade': self.estoque_quantidade,
            'item_id': self.item_id,
            'funcionario_id': self.funcionario_id,
            'movimentação_item': self.movimentacao_item,
            'data_estoque': self.data_estoque
        }
        return dados_entrega



def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()