from urllib import request

from flask import Flask

from models import Funcionario, db_session

app = Flask(__name__)


@app.route('/login')
def hello_world():  # put application's code here socorro meu deus alguem me ajuda
    return 'Hello World!'

@app.route('/funcionario/add', methods=['POST'])
def add_funcionario():
    """Pagina para adicionar Funcionarios
    Para adiciona-la o admin deve listar o nome da pessoa junto com o email dela e o CPF e sua senha pessoal
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

@app.route('/item/add', methods=['POST'])
def add_item():
    item = Item(nome=request.form['nome'],
                tipo=request.form['tipo'],
                quantidade=request.form['quantidade'])
    db_session.add(item)
    item.save()
    final = {
        'status': 'success',
        'nome': item.nome,
        'tipo': item.tipo,
        'quantidade': item.quantidade}
    return app.response_class(response=json.dumps(final),
                              status=201,
                              mimetype='application/json')
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

@app.route('/item/update/<int:id>', methods=['PUT'])
def update_item(id):
        item = select(Item).where(Item.id == id)
        item = db_session.execute(item).scalar()
        item.nome = request.form['nome']
        item.tipo = request.form['tipo']
        item.quantidade = request.form['quantidade']
        db_session.commit()
        final = {
            'status': 'success',
            'nome': item.nome,
            'tipo': item.tipo,
            'quantidade': item.quantidade}

        return Response(response=json.dumps(final),

                        status=201,
                        mimetype='application/json')

@app.route('/item/delete/<int:id>', methods=['DELETE'])
def delete_item(id):
    item = select(Item).where(Item.id == id)
    item = db_session.execute(item).scalar()
    db.session.add(pessoa)
    pessoa.save()
    final = {
        'status': 'removido',
        'nome': item.nome,
        'tipo': item.tipo,
        'quantidade': item.quantidade}
    db_session.delete(item)
    db_session.commit()
    return Response(response=json.dumps(final),
                    status=201,
                    mimetype='application/json')

@app.route('/item/detalhes', methods=['GET'])
def detalhes_item():
    item = Item.query.all()
    result = []
    for consulta in item:
        result.append(consulta.serialize_item())
    final = json.dumps(result)
    return Response(response=final,
                    status=201,
                    content_type='application/json')

@app.route (

if __name__ == '__main__':
    app.run()
