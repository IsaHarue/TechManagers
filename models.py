from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, declarative_base


import os

import configparser


url_ =os.environ.get('DATABASE.URL')

print(f'modo1:{url_}')



config = configparser.ConfigParser()

config.read('config.ini')

#database_url = config['database']['url']

#print(f'modo2:{database_url}')

engine = create_engine('sqlite:///TechManagers.db')
#engine = create_engine(database_url)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Funcionario(Base):
    __tablename__ = 'funcionario'
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    email = Column(String(40), nullable=False, index=True, unique=True)
    cpf = Column(String(11), nullable=False, index=True, unique=True)
    senha = Column(String(128), nullable=False, index=True)
    admin = Column(Boolean, default=False)

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
    quantidade = Column(Integer, nullable=False, index=True)

    def __repr__(self):
        return '<ITEM: {}>'.format(self.nome, self.tipo, self.quantidade)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_item(self):
        dados_item = {
            'item_id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'quantidade': self.quantidade
        }
        return dados_item


class MOVIMENTACAO(Base):
    __tablename__ = 'movimentacao'
    id = Column(Integer, primary_key=True, unique=True, nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    item = relationship('ITEM', backref='movimentacoes')
    funcionario_id = Column(Integer, ForeignKey('funcionario.id'), nullable=False)
    funcionario = relationship('Funcionario', backref='movimentacoes')
    movimentacao_item = Column(Integer, nullable=False)
    data_movimentacao = Column(String(255), nullable=False, index=True)
    tipo_movimentacao = Column(Integer, nullable=False, index=True)


    def __repr__(self):
        return '<Entrega: {}>'.format(self.item_id, self.funcionario_id, self.movimentacao_item, self.data_movimentacao, self.tipo_movimentacao)

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_entrega(self):
        dados_entrega = {
            'movimentacao_id': self.id,
            'item_id': self.item_id,
            'funcionario_id': self.funcionario_id,
            'movimentacao_item': self.movimentacao_item,
            'data_movimentacao': self.data_movimentacao,
            'tipo_movimetacao': self.tipo_movimentacao
        }
        return dados_entrega



def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()