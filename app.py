import email
from lib2to3.pgen2 import driver

from flask import Flask, request, Response, render_template, redirect, session, flash, url_for
import json
import sqlalchemy
from sqlalchemy import select, true, false
from models import Funcionario, db_session, ITEM, MOVIMENTACAO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'TECHMANAGERS'


@app.route('/')
def home():
    return redirect("/login")


@app.route('/teste')
def inicial():
    return render_template("teste.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    admin_email = 'admin@gmail.com'
    admin_senha = '123*'

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if email == admin_email and senha == admin_senha:
            # Se o email e senha do admin forem válidos, redireciona para a tela privada do admin
            session['admin'] = True
            return redirect("/TelaAI")
        elif email == admin_email and senha != admin_senha:
            flash('senha do admin incorreta')
            return redirect("/login")
        else:
            # Se o email e senha do admin forem inválidos, redireciona para a tela de login novamente
            session['admin'] = False
            return redirect("/login")
    else:
        return render_template('login.html')

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        if email == "" and senha == "":
            # Se o email e senha do admin forem válidos, redireciona para a tela privada do admin
            return redirect("/TelaFI")
        elif email == admin_email and senha != admin_senha:
            flash('senha do admin incorreta')
            return redirect("/login")
        else:
            # Se o email e senha do admin forem inválidos, redireciona para a tela de login novamente
            return redirect("/login")
    else:
        return render_template('login.html')




@app.route('/base')
def base():
    return render_template("base.html")

@app.route('/TelaGraficos')
def TelaGraficos():
    return render_template("TeladeGraficos.html")

@app.route('/TelaFI')
def TelaFI():
    return render_template("TelaFItem.html")


@app.route('/TelaFM')
def TelaFM():
    return render_template("TelaFItemMateriaPrima.html")


@app.route('/TelaFR')
def TelaFR():
    return render_template("TelaFItemRoupas.html")


@app.route('/TelaFF')
def TelaFF():
    return render_template("TelaFItemFerramentas.html")


@app.route('/TelaCF', methods=['GET', 'POST'])
def TelaCF():
    if request.method == 'POST':
        try:
            funcionario = Funcionario(
                nome=request.form['nome'],
                email=request.form['email'],
                cpf=request.form['cpf'],
                senha=request.form['senha'],
                admin= True)

            db_session.add(funcionario)

            funcionario.save()
            return redirect(url_for('telafuncionarios'))

        except ValueError:
            flash('não foi possivel adicionar um funcionario no database', 'error')
        except sqlalchemy.exc.IntegrityError:
            flash('cpf ja cadastrado', 'error')


    return render_template("TelaCadastroFuncionario.html")


@app.route('/TelaCI')
def TelaCItem():
    return render_template("TelaCadastroItem.html")


@app.route('/TelaDF/<int:id>', methods=['GET'])
def TelaDF(id):
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        return render_template('TelaDetalhesFuncionario.html', funcionario=funcionario)
    except AttributeError:
        flash(message="Erro ao carregar detalhes do funcionário", category='error')
        return redirect(url_for('telafuncionarios'))


@app.route('/TelaDI')
def TelaDItem():
    return render_template("TelaDetalhesItem.html")


@app.route('/TelaEF/<int:id>', methods=['GET', 'POST'])
def TelaEF(id):
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        if request.method == 'POST':
            funcionario.nome = request.form['nome']
            funcionario.email = request.form['email']
            funcionario.cpf = request.form['cpf']
            funcionario.senha = request.form['senha']
            db_session.commit()
            return redirect(url_for('telafuncionarios'))
        return render_template('TelaEdicaoFuncionario.html', funcionario=funcionario)
    except AttributeError:
        flash(message="Erro ao editar funcionário", category='error')
        return render_template("TelaEdicaoFuncionario.html")



@app.route('/TelaEI')
def TelaEItem():
    return render_template("TelaEdicaoItem.html")


@app.route('/TelaRF')
def TelaRF():
    return render_template("RelatorioFuncionarios.html")


@app.route('/TelaAFe')
def telaferramentas():
    return render_template("TelaAFerramentas.html")


@app.route('/TelaAR')
def telaroupas():
    return render_template("TelaARoupas.html")

@app.route('/TelaAM')
def telamateriaprima():
    return render_template("TelaAMateriaPrima.html")


@app.route('/TelaAF')
def telafuncionarios():
    # pega todos os funcionarios
    funcionarios = Funcionario.query.all()

    return render_template("TelaAFuncionarios.html", funcionarios=funcionarios)


@app.route('/TelaAI')
def telaitens():
    return render_template("TelaAItens.html")


# ___________________________FUNCIONARIO____________________________

@app.route('/update_funcionario/<int:id>', methods=['PUT'])
def updatee(id):
    '''Esta rota é responsável por modificar informações de um funcionario no database
    #para que esta rota funcione é necessario que os valores nome ou email sejam alterados
    #utilizamos o try para modificar se ouver algum erro durante o processo de atualização'''
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        funcionario.nome = request.form['nome']
        funcionario.email = request.form['email']
        funcionario.cpf = request.form['cpf']
        funcionario.senha = request.form['senha']
        funcionario.admin = request.form['admin']
        db_session.commit()
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel atualizar verifique se o id é compativel no database'
        }
        return app.response_class(response=json.dumps(final), status=404, mimetype='application/json')
    except sqlalchemy.exc.IntegrityError:
        final = {
            'status': 'erro',
            'mensagem': 'cpf'
        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


@app.route('/get_funcionarios', methods=['GET'])
def cunsultar_usuarios():
    '''Esta rota é responsável por selecionar um usuario do database
    #Ao utilizar esta rota, a partir da informação do id do funcionario é possivel exibir as informações do mesmo'''
    try:
        funcionario = select(Funcionario).select_from(Funcionario)
        funcionario = db_session.execute(funcionario).scalars()
        result = []
        for consulta in funcionario:
            result.append(consulta.serialize_funcionario())
            final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except sqlalchemy.exc.OperationalError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel atualizar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')
    except UnboundLocalError:
        final = {
            'status': 'erro',
            'mensagem': 'Nenhum funcionario cadastrado'
        }
        return app.response_class(response=json.dumps(final), status=200, mimetype='application/json')


@app.route('/get_funcionario/<int:id>', methods=['GET'])
def cunsultar_usuarioo(id):
    '''Esta rota é responsável por selecionar um usuario do database
    #Ao utilizar esta rota, a partir da informação do id do funcionario é possivel exibir as informações do mesmo'''
    try:
        funcionario = select(Funcionario).select_from(Funcionario)
        funcionario = db_session.execute(funcionario).scalars()
        result = []
        for consulta in funcionario:
            result.append(consulta.serialize_epi())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel consultar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')
    except sqlalchemy.exc.IntegrityError:
        final = {
            'status': 'erro',
            'mensagem': 'cpf'
        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


@app.route('/get_funcionario/<cpf>', methods=['GET'])
def cunsultar_usuariocpf(cpf):
    '''Esta rota é responsável por selecionar um usuario do database
    #Ao utilizar esta rota, a partir da informação do id do funcionario é possivel exibir as informações do mesmo'''
    try:
        funcionario = select(Funcionario).select_from(Funcionario)
        funcionario = db_session.execute(funcionario).scalars()
        result = []
        for consulta in funcionario:
            result.append(consulta.serialize_funcionario())
            final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel consultar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')
    except sqlalchemy.exc.IntegrityError:
        final = {
            'status': 'erro',
            'mensagem': 'cpf'
        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


@app.route('/delete_funcionario/<int:id>', methods=['GET', 'DELETE'])
def delete_funcionario(id):
    '''Esta rota é responsável por deleter um funcionario no database
    #Para deletar um funcionario no database é necessário informar o id do funcionario'''
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        db_session.delete(funcionario)
        db_session.commit()
        return redirect(url_for('telafuncionarios'))
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel deletar, verifique se o id é compatível no database'
        }


# ________________________________ITEM________________________________

@app.route('/add_item', methods=['POST'])
def add():
    '''Esta rota é responsável por adicionar um EPI ao database
    #adiciona uma EPI no banco, esta EPI deve conter: nome, data_fabricacao, validade e description'''
    try:
        item = ITEM(nome=request.form['nome'],
                    tipo=request.form['tipo'],
                    Quantidade=request.form['quantidade'],
                    )
        db_session.add(ITEM)
        item.save()
        final = {
            'status': 'ok',
            'nome': item.nome,
            'tipo': item.tipo,
            'Quantidade': item.Quantidade
        }
        return app.response_class(response=json.dumps(final),
                                  status=201,
                                  mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel adicionar um ITEM no database'
        }
        return app.response_class(response=json.dumps(final),
                                  status=500,
                                  mimetype='application/json')


@app.route('/update_item/<int:id>', methods=['PUT'])
def update(id):
    '''Esta rota é responsável por modificar as informações de um EPI no database
    #para que esta rota funcione deve-se auterar ou o nome, a validade ou description
    #utiliza-se try no update, para informar se ouver algum erro na hora de atualizar'''
    try:
        item = select(ITEM).where(ITEM.id == id)
        item = db_session.execute(item).scalar()
        item.nome = request.form['nome']
        item.Quantidade = request.form['Quantidade']
        item.tipo = request.form['tipo']
        db_session.commit()
        final = {
            'status': 'ok',
            'nome': item.nome,
            'Quantidade': item.Quantidade,
            'tipo': item.tipo,
        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')


    except ValueError:

        final = {

            'status': 'erro',

            'mensagem': 'não foi possivel atualizar verifique se os campos são diferentes'

        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')

    except AttributeError:

        final = {

            'status': 'erro',

            'mensagem': 'epi não cadastrado na base de dados'

        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')


@app.route('/delete_item/<int:id>', methods=['DELETE'])
def delete(id):
    '''Esta rota é responsável por deletar um ITEM do database
    #Para deletar um ITEM voce deve informar o id do ITEM que deseja excluir'''
    try:
        item = select(ITEM).where(ITEM.id == id)
        item = db_session.execute(item).scalar()
        print(item)
        final = {
            'status': 'removido',
            'nome': item.nome,
            'Quantidade': item.Quantidade,
            'tipo': item.tipo}
        db_session.delete(item)
        db_session.commit()
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel atualizar, verifique se o id é compatível no database'
        }


@app.route('/get_itens', methods=['GET'])
def cunsultar_itens():
    '''Esta rota é responsável por consultar as informações de um livro no database
    #Ao colocar o id do ITEM ela requisita para o banco todas as informações do ITEM e exibi.'''
    try:
        item = ITEM.query.all()
        result = []
        for consulta in item:
            result.append(consulta.serialize_epi())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except sqlalchemy.exc.OperationalError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel atualizar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


@app.route('/get_item/<int:id>', methods=['GET'])
def cunsultar_item(id):
    '''Esta rota é responsável por consultar as informações de um livro no database
    #Ao colocar o id do ITEM ela requisita para o banco todas as informações do ITEM e exibi.'''
    try:
        item = ITEM.id.query.id()
        result = []
        for consulta in item:
            result.append(consulta.serialize_epi())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel consultar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


# ___________________________Movimentação____________________________

@app.route('/add_movimentacao', methods=['POST'])
def ad():
    '''Esta rota é responsável por adicionar um esprestimo no database
    #Adicionando os ids do funcionario e do EPI no database, assim como o tempo_de_entrega,
    é possivel cadastrar o entrega no banco'''
    try:
        movimentacao = MOVIMENTACAO(funcionario_id=int(request.form['funcionario_id']),
                                    item_id=int(request.form['item_id']),
                                    estoque_quantidade=request.form['estoque_quantidade'],
                                    movimentacao_item=request.form['movimentacao_item'],
                                    data_estoque=request.form['data_estoque'])
        db_session.add(movimentacao)
        movimentacao.save()
        final = {
            'status': 'ok',
            'funcionario_id': movimentacao.funcionario_id,
            'item_id': movimentacao.item_id,
            'estoque_quantidade': movimentacao.estoque_quantidade,
            'data_estoque': movimentacao.data_estoque,
            'movimentacao_item': movimentacao.movimentacao_item
        }
        return app.response_class(response=json.dumps(final),
                                  status=201,
                                  mimetype='application/json')
    except ValueError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel adicionar uma entrega no database'
        }
    except sqlalchemy.exc.IntegrityError:
        final = {
            'status': 'erro',
            'mensagem': 'entrega já cadastrada na base de dados'
        }


@app.route('/update_movimentacao/<int:id>', methods=['PUT'])
def update_movimentacao(id):
    '''Esta rota é responsável por modificar informações de um esprestimo no database
    #É possivel alterar os ids do funcionario e do EPI, assim como do tempo de emprestimo
    #Utilizando o try podemos notificar o usuario caso aja algum dado inválido'''
    try:
        movimentacao = select(MOVIMENTACAO).where(MOVIMENTACAO.id == id)
        movimentacao = db_session.execute(movimentacao).scalar()
        movimentacao.funcionario_id = request.form['funcionario_id']
        movimentacao.item_id = request.form['item_id']
        movimentacao.estoque_quantidade = request.form['estoque_quantidade']
        movimentacao.movimentacao_item = request.form['movimentacao_item']
        movimentacao.data_estoque = request.form['data_Estoque']
        db_session.commit()
        final = {
            'status': 'ok',
            'funcionario_id': movimentacao.funcionario_id,
            'item_id': movimentacao.item_id,
            'estoque_quantidade': movimentacao.estoque_quantidade,
            'movimentacao_item': movimentacao.movimentacao_item,
            'data_estoque': movimentacao.data_estoque
        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')


    except ValueError:

        final = {

            'status': 'erro',

            'mensagem': 'não foi possivel atualizar verifique se os campos são diferentes'

        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')

    except AttributeError:

        final = {

            'status': 'erro',

            'mensagem': 'Emprestiomo não cadastrado na base de dados'

        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')


@app.route('/delete_movimentacao/<int:id>', methods=['DELETE'])
def delete_movimentacao(id):
    '''Esta rota é responsável por deletar um esprestimo no database
    #Ao indicar um id, é possivel remover um esprestimo no banco'''
    try:
        movimentacao = select(MOVIMENTACAO).where(MOVIMENTACAO.id == id)
        movimentacao = db_session.execute(movimentacao).scalar()
        print(movimentacao)
        final = {
            'status': 'removido',
            'funcionario_id': movimentacao.funcionario_id,
            'item_id': movimentacao.item_id,
            'data_estoque': movimentacao.data_estoque,
            'movimetacao_item': movimentacao.movimentacao_item,
            'estoque_quantidade': movimentacao.estoque_quantidade}
        db_session.delete(movimentacao)
        db_session.commit()
        return Response(response=json.dumps(final),
                        status=201,
                        mimetype='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel atualizar, verifique se o id é compatível no database'
        }


@app.route('/get_movimentacao', methods=['GET'])
def cunsultar_movimentacao():
    '''Esta rota é responsável por mostar as informações de um esprestimo no database
    #Ao informar o id do esprestimo que deseja selecionar, o sistema faz um requerimento para o banco,
     de modo a pegar o esprestimo no banco'''
    try:
        movimentacao = MOVIMENTACAO.query.all()
        result = []
        for consulta in movimentacao:
            result.append(consulta.serialize_entrega())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except sqlalchemy.exc.OperationalError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel atualizar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')
    except sqlalchemy.exc.IntegrityError:
        final = {
            'status': 'erro',
            'mensagem': 'CA'
        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


@app.route('/get_movimentacao/<int:id>', methods=['GET'])
def cunsultar_movimentacaoid(id):
    '''Esta rota é responsável por mostar as informações de um esprestimo no database
    #Ao informar o id do esprestimo que deseja selecionar, o sistema faz um requerimento para o banco,
     de modo a pegar o esprestimo no banco'''
    try:
        movimentacao = MOVIMENTACAO.query.all()
        result = []
        for consulta in movimentacao:
            result.append(consulta.serialize_entrega())
        final = json.dumps(result)
        return Response(response=final,
                        status=201,
                        content_type='application/json')
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel consultar, verifique se o id é compatível no database'

        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')
    except sqlalchemy.exc.IntegrityError:
        final = {
            'status': 'erro',
            'mensagem': 'cpf'
        }
        return app.response_class(response=json.dumps(final), status=409, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
