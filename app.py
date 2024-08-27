from urllib import request

from flask import Flask, json

from models import Funcionario, db_session

app = Flask(__name__)


@app.route('/login')
def hello_world():  # put application's code here socorro meu deus alguem me ajuda
    return 'Hello World!'


@app.route('/funcionario/add', methods=['POST'])
def add_funcionario():
    """Pagina para adicionar Funcionarios
    Para adiciona-la o adin deve listar o nome da pessoa junto com o email dela e o CPF e sua senha pessoal
    """
    pessoa = Pessoa(nome=request.form['nome'],
                    cpf=request.form['cpf'],
                    email=request.form['email'],
                    senha=request.form['senha'])

    db.session.add(pessoa)
    pessoa.save()
    final = {
        'status': 'ok',
        'nome': pessoa.nome,
        'cpf': pessoa.cpf,
        'email': pessoa.email,
        'senha': pessoa.senha
    }
    return app.response_class()

@app.route ('/funcionarioUpdate/<int:id>', methods=['PUT'])
def update_funcionario(id):
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario.__table__.delete())
        funcionario.nome = request.form['nome']
        funcionario.cpf = request.form['cpf']
        funcionario.email = request.form['email']
        db_session.commit()
        final = {
            'status': 'ok',
            'id': funcionario.id ,
            'nome': funcionario.nome,
            'cpf': funcionario.cpf,
            'email': funcionario.email,
        }
        return app.response_class(

        )

@app.route (

if __name__ == '__main__':
    app.run()
