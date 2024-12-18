from datetime import datetime, timedelta

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from flask import Flask, request, Response, render_template, redirect, session, flash, url_for
import json
import sqlalchemy
from sqlalchemy import select, func
from models import Funcionario, db_session, ITEM, MOVIMENTACAO
import os
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
    total_itens = db_session.query(func.sum(ITEM.quantidade)).scalar() or 0
    total_entrada = db_session.query(func.sum(MOVIMENTACAO.quantidade_final)).filter(MOVIMENTACAO.tipo_movimentacao == "Entrada").scalar() or 0
    total_saida = db_session.query(func.sum(MOVIMENTACAO.quantidade_final)).filter(MOVIMENTACAO.tipo_movimentacao == "Saida").scalar() or 0

    meses = ['Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro']
    total_por_mes = []
    for i in range(7, 12):  # Agora é de Julho a Novembro
        total_mes = db_session.query(func.sum(MOVIMENTACAO.quantidade_final)).filter(
            MOVIMENTACAO.data_movimentacao.like(f'2024-{i:02d}%')).scalar() or 0
        total_por_mes.append(total_mes)

    # Calcular os dias da semana (Segunda a Sexta)
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())  # Obter a segunda-feira da semana atual
    dias_da_semana = [(inicio_semana + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]  # Segunda a Sexta

    # Consultar entradas e saídas para cada dia
    entradas_diarias = []
    saidas_diarias = []
    for dia in dias_da_semana:
        entrada_dia = db_session.query(func.sum(MOVIMENTACAO.quantidade_final)).filter(
            MOVIMENTACAO.tipo_movimentacao == "Entrada",
            MOVIMENTACAO.data_movimentacao.like(f'{dia}%')
        ).scalar() or 0
        saida_dia = db_session.query(func.sum(MOVIMENTACAO.quantidade_final)).filter(
            MOVIMENTACAO.tipo_movimentacao == "Saida",
            MOVIMENTACAO.data_movimentacao.like(f'{dia}%')
        ).scalar() or 0
        entradas_diarias.append(entrada_dia)
        saidas_diarias.append(saida_dia)

        categorias = ['Matéria Prima', 'Roupas', 'Ferramentas']
        total_Materia = db_session.query(func.sum(ITEM.quantidade)).filter(ITEM.tipo == "Materia").scalar() or 0
        total_Roupa = db_session.query(func.sum(ITEM.quantidade)).filter(ITEM.tipo == "Roupa").scalar() or 0
        total_Ferramenta = db_session.query(func.sum(ITEM.quantidade)).filter(ITEM.tipo == "Ferramenta").scalar() or 0

    # Passar os dados ao template
    return render_template(
        "Teladegraficos.html",
        total_itens=total_itens,
        total_entrada=total_entrada,
        total_saida=total_saida,
        total_por_mes=total_por_mes,
        meses=meses,
        entradas_diarias=entradas_diarias,
        saidas_diarias=saidas_diarias,
        dias_da_semana=['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'],
        categorias=categorias,
        total_Materia=total_Materia,
        total_Roupa=total_Roupa,
        total_Ferramenta=total_Ferramenta
    )


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
    total = db_session.query(func.sum(ITEM.quantidade)).scalar() or 0
    return render_template("TelaFItem.html", itens=itens, total=total)

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
        quantidade = int(0)

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
    total = db_session.query(func.sum(ITEM.quantidade)).filter(ITEM.tipo == "Materia").scalar() or 0
    return render_template("TelaAMateriaPrima.html", itens=itens, total=total)

@app.route('/TelaAR')
def tela_roupas():
    itens = ITEM.query.filter_by(tipo="Roupa").all()
    total = db_session.query(func.sum(ITEM.quantidade)).filter(ITEM.tipo == "Roupa").scalar() or 0
    return render_template("TelaARoupas.html", itens=itens, total=total)

@app.route('/TelaAFe')
def tela_ferramentas():
    itens = ITEM.query.filter_by(tipo="Ferramenta").all()
    total = db_session.query(func.sum(ITEM.quantidade)).filter(ITEM.tipo == "Ferramenta").scalar() or 0
    return render_template("TelaAFerramentas.html", itens=itens, total=total)

@app.route('/TelaAF')
def telafuncionarios():
    # pega todos os funcionarios
    funcionarios = Funcionario.query.all()
    return render_template("TelaAFuncionarios.html", funcionarios=funcionarios)

@app.route('/TelaAI')
def telaitens():
    itens = ITEM.query.all()
    total = db_session.query(func.sum(ITEM.quantidade)).scalar() or 0


    return render_template("TelaAItens.html", itens=itens, total=total)


@app.route('/TelaMv', methods=['GET', 'POST'])
def tela_movimentacao():
    itens = ITEM.query.all()
    func = Funcionario.query.all()
    form_data = {}
    return render_template("TelaMovimentacao.html", itens=itens, func=func, form_data=form_data)

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
    Para deletar um ITEM você deve informar o id do ITEM que deseja excluir'''
    try:
        # Excluir todas as movimentações relacionadas ao item
        db_session.query(MOVIMENTACAO).filter(MOVIMENTACAO.item_id == id).delete()

        # Agora, excluir o item
        item = db_session.query(ITEM).filter_by(id=id).first()
        if item:
            db_session.delete(item)
            db_session.commit()
            flash('Item deletado com sucesso!', 'success')
        else:
            flash('Item não encontrado!', 'error')

        return redirect(url_for('telaitens'))
    except Exception as e:
        db_session.rollback()  # Rollback em caso de erro
        flash(f'Não foi possível deletar, erro: {str(e)}', 'error')
        return redirect(url_for('telaitens'))

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

@app.route('/ad', methods=['POST'])
def ad():
    # Get form data
    form_data = request.form
    item_id = request.form['id']
    funcionario_id = request.form['funcionario']
    data_movimentacao = request.form['data']
    quantidade = int(request.form['quantidade_final'])
    tipo_movimentacao = request.form['tipoM']  # "Entrada" or "Saida"

    # Retrieve the item
    item = db_session.query(ITEM).filter_by(id=item_id).first()
    funcionario = db_session.query(Funcionario).filter_by(id=funcionario_id).first()
    if tipo_movimentacao == "Entrada":
        item.quantidade = item.quantidade + quantidade
    else:
        if quantidade <= item.quantidade:
            item.quantidade = item.quantidade - quantidade
        else:
            flash('Estoque insuficiente!', 'error')
            return render_template('TelaMovimentacao.html', itens=ITEM.query.all(), func=Funcionario.query.all(), form_data=form_data)
    if not item:
        flash('Item não encontrado!', 'error')
        return render_template('TelaMovimentacao.html', itens=ITEM.query.all(), func=Funcionario.query.all(), form_data=form_data)

    # Save the item changes
    #db_session.commit()
    item.save()

    # Create a new MOVIMENTACAO entry
    movimentacao = MOVIMENTACAO(
        item_id=item.id,
        funcionario_id=funcionario_id,
        nome_item=item.nome,
        nome_funcionario=funcionario.nome,  # You might want to fetch the name based on ID
        data_movimentacao=data_movimentacao,
        tipo_movimentacao=tipo_movimentacao,
        quantidade_final=item.quantidade
    )
    movimentacao.save()
    flash('Movimentação registrada com sucesso!', 'success')
    return redirect(url_for('telaitens'))  # Adjust accordingly


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
