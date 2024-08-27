import json
from urllib import request

from flask import Flask
from sqlalchemy import select

app = Flask(__name__)


@app.route('/login')
def hello_world():  # put application's code here
    return 'Hello World!'


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



if __name__ == '__main__':
    app.run()
