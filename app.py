from flask import Flask

app = Flask(__name__)


@app.route('/login')
def hello_world():  # put application's code here
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



if __name__ == '__main__':
    app.run()
