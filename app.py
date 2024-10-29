from Crypto.Util.Padding import unpad, pad
from flask import Flask, request, Response, render_template, redirect, session, flash, url_for
import json
import sqlalchemy
from sqlalchemy import select, func
from models import Funcionario, db_session, ITEM, MOVIMENTACAO
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'TECHMANAGERS'

# Chave e IV para criptografia AES (16 bytes cada para AES-128)
AES_KEY = b'teste_de_senha_de_32_bits_123456'  # Use uma chave de 32 bytes para segurança
AES_IV = get_random_bytes(16)  # Vetor de inicialização (IV)

# Função para criptografar senhas
# Função para criptografar senhas

def encrypt_password(password):
    iv = get_random_bytes(16)  # Gerar um novo IV para cada criptografia
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    password_padded = pad(password.encode(), AES.block_size)  # Preenche a senha para múltiplos de 16 bytes
    encrypted_password = cipher.encrypt(password_padded)
    return b64encode(iv + encrypted_password).decode('utf-8')  # Inclui o IV no resultado codificado

# Função para descriptografar senhas
def decrypt_password(encrypted_password):
    encrypted_data = b64decode(encrypted_password)
    iv = encrypted_data[:16]  # Extrai o IV dos primeiros 16 bytes
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_password = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size).decode('utf-8')  # Remove padding
    return decrypted_password


@app.route('/')
def home():
    return redirect("/login")

@app.route('/teste')
def inicial():
    return render_template("teste.html")

@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('funcionario', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    admin_email = 'admin@gmail.com'
    admin_senha = encrypt_password('123*')
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        # Verificar se o usuário é o administrador
        if email == admin_email and decrypt_password(admin_senha) == senha:
            session['admin'] = True
            session['nome_funcionario'] = 'Admin'
            print(session['nome_funcionario'])
            return redirect("/TelaAI")
        # Verificar se o usuário é um funcionário comum
        funcionario = Funcionario.query.filter_by(email=email).first()
        if funcionario and decrypt_password(funcionario.senha) == senha:
            session['funcionario'] = True
            session['nome_funcionario'] = funcionario.nome
            print(session['nome_funcionario'])
            return redirect("/TelaFI")
        # Se o usuário não for encontrado, exibir mensagem de erro
        flash('Usuario ou senha incorretos')
        return redirect("/login")
    return render_template('login.html')

def get_nome_funcionario():
    print(session['nome_funcionario'])
    return session.get('nome_funcionario')


@app.route('/base')
def base():
    nome_funcionario = get_nome_funcionario()
    return render_template("base.html", nome_funcionario=nome_funcionario)

@app.route('/TelaGraficos')
def TelaGraficos():
    return render_template("TeladeGraficos.html")

@app.route('/TelaRelatorio', methods=['GET'])
def TelaRelatorio():
    itens = ITEM.query.all()
    return render_template("RelatorioItens.html", itens=itens)

@app.route('/TelaF', methods=["GET"])
def TelaF():
    funcionarios = Funcionario.query.all()
    return render_template("TelaFuncionario.html", funcionarios=funcionarios)

@app.route('/TelaFI')
def TelaFI():
    itens = ITEM.query.all()
    return render_template("TelaFItem.html", itens=itens)

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
                senha=encrypt_password(request.form['senha']),
                admin=False)
            db_session.add(funcionario)

            funcionario.save()
            flash("Funcionario cadastrado com sucesso!")
            return redirect(url_for('telafuncionarios'))

        except ValueError:
            flash('não foi possivel adicionar um funcionario no database', 'error')
        except sqlalchemy.exc.IntegrityError:
            flash('cpf ja cadastrado', 'error')
            return redirect(url_for('TelaCF'))

    return render_template("TelaCadastroFuncionario.html")

@app.route('/TelaCI', methods=["GET", "POST"])
def TelaCItem():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']
        quantidade = int(request.form['quantidade'])

        # Verificar se o item já existe no banco de dados
        item = ITEM.query.filter_by(nome=nome, tipo=tipo).first()

        if item:
            # Se o item já existe, exibir mensagem de erro
            flash('Item já cadastrado!', 'error')
            return redirect(url_for('TelaCItem'))
        else:
            # Se o item não existe, criar um novo item
            item = ITEM(nome=nome, tipo=tipo, quantidade=quantidade)
            db_session.add(item)
            item.save()
            flash('Item cadastrado com sucesso!')
            return redirect(url_for('telaitens'))

    return render_template("TelaCadastroItem.html")

@app.route('/TelaDF/<int:id>', methods=['GET'])
def TelaDF(id):
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        if funcionario and funcionario.senha:
            funcionario.senha = decrypt_password(funcionario.senha)
        return render_template('TelaDetalhesFuncionario.html', funcionario=funcionario)
    except AttributeError:
        flash(message="Erro ao carregar detalhes do funcionário", category='error')
        return redirect(url_for('telafuncionarios'))

@app.route('/TelaDI/<int:id>', methods=['GET'])
def TelaDItem(id):
    item = select(ITEM).where(ITEM.id == id)
    item = db_session.execute(item).scalar()
    return render_template('TelaDetalhesItem.html', item=item)

@app.route('/TelaEF/<int:id>', methods=['GET', 'POST'])
def TelaEF(id):
    try:
        funcionario = select(Funcionario).where(Funcionario.id == id)
        funcionario = db_session.execute(funcionario).scalar()
        if funcionario and funcionario.senha:
            funcionario.senha = decrypt_password(funcionario.senha)
        if request.method == 'POST':
            funcionario.nome = request.form['nome']
            funcionario.email = request.form['email']
            funcionario.cpf = request.form['cpf']
            funcionario.senha = encrypt_password(request.form['senha'])
            db_session.commit()
            flash('Funcionario editado com sucesso!')
            return redirect(url_for('telafuncionarios'))
        return render_template('TelaEdicaoFuncionario.html', funcionario=funcionario)
    except AttributeError:
        flash(message="Erro ao editar funcionário", category='error')
        return render_template("TelaEdicaoFuncionario.html")

@app.route('/TelaEI/<int:id>', methods=['GET', 'POST'])
def TelaEItem(id):
    try:
        item = select(ITEM).where(ITEM.id == id)
        item = db_session.execute(item).scalar()
        if request.method == 'POST':
            item.nome = request.form['nome']
            item.tipo = request.form['tipo']
            item.quantidade = request.form['quantidade']
            db_session.commit()
            flash('Item editado com sucesso!')
            return redirect(url_for('telaitens'))
        return render_template('TelaEdicaoItem.html', item=item)
    except AttributeError:
        flash(message="Erro ao editar item", category='error')
        return render_template("TelaEdicaoItem.html")

@app.route('/TelaRF')
def TelaRF():
    return render_template("RelatorioFuncionarios.html")

@app.route('/TelaAM')
def tela_materia_prima():
    itens = ITEM.query.filter_by(tipo="Materia").all()
    return render_template("TelaAMateriaPrima.html", itens=itens)

@app.route('/TelaAR')
def tela_roupas():
    itens = ITEM.query.filter_by(tipo="Roupa").all()
    return render_template("TelaARoupas.html", itens=itens)

@app.route('/TelaAFe')
def tela_ferramentas():
    itens = ITEM.query.filter_by(tipo="Ferramenta").all()
    return render_template("TelaAFerramentas.html", itens=itens)

@app.route('/TelaAF')
def telafuncionarios():
    # pega todos os funcionarios
    funcionarios = Funcionario.query.all()
    return render_template("TelaAFuncionarios.html", funcionarios=funcionarios)

@app.route('/TelaAI')
def telaitens():
    itens = ITEM.query.all()
    total = db_session.query(func.sum(ITEM.quantidade)).scalar() or 0
    print(itens)
    print(total)

    return render_template("TelaAItens.html", itens=itens, total=total)



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
            result.append(consulta.serialize_item())
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

@app.route('/add_item', methods=['GET', 'POST'])
def add():
    '''Esta rota é responsável por adicionar um item ao database
    #adiciona uma item no banco, esta item deve conter: nome, data_fabricacao, validade e description'''
    if request.method == 'POST':
        add_item = ITEM(
            nome=request.form['nome'],
            tipo=request.form['tipo'],
            quantidade=int(request.form['quantidade'])
        )

        print(add_item)
        db_session.add(ITEM)

        add_item.save()

        return redirect(url_for('consultar_itens'))

    return render_template('TelaCadastroItem.html')


@app.route('/update_item/<int:id>', methods=['PUT'])
def update(id):
    '''Esta rota é responsável por modificar as informações de um item no database
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

            'mensagem': 'item não cadastrado na base de dados'

        }

        return app.response_class(response=json.dumps(final), status=201, mimetype='application/json')


@app.route('/delete_item/<int:id>', methods=['GET', 'DELETE'])
def delete(id):
    '''Esta rota é responsável por deletar um ITEM do database
    #Para deletar um ITEM voce deve informar o id do ITEM que deseja excluir'''
    try:
        item = select(ITEM).where(ITEM.id == id)
        item = db_session.execute(item).scalar()
        db_session.delete(item)
        db_session.commit()
        return redirect(url_for('telaitens'))
    except AttributeError:
        final = {
            'status': 'erro',
            'mensagem': 'não foi possivel deletar, verifique se o id é compatível no database'
        }


@app.route('/get_itens', methods=['GET'])
def cunsultar_itens():
    '''Esta rota é responsável por consultar as informações de um livro no database
    #Ao colocar o id do ITEM ela requisita para o banco todas as informações do ITEM e exibi.'''
    try:
        item = ITEM.query.all()
        result = []
        for consulta in item:
            result.append(consulta.serialize_item())
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
            result.append(consulta.serialize_item())
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
    #Adicionando os ids do funcionario e do item no database, assim como o tempo_de_entrega,
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
    #É possivel alterar os ids do funcionario e do item, assim como do tempo de emprestimo
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
