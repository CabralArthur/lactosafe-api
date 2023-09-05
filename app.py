#imports
from flask import Flask, request, jsonify
from mysql.connector import connect
from flask_cors import CORS
import os
import numpy as np
from tensorflow.keras.models import load_model
from cv2 import imread, resize
from numpy import expand_dims, array, argmax

app = Flask('app')

#cadastro
@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    # Obter os dados da requisição
    data = request.get_json()
    email = data['email']
    senha = data['senha']

    # Conectar ao banco de dados
    db = connect(
        host="localhost",
        user="root",
        password="1234",
        database="lactosafe_db"
    )

    # Criar o cursor
    cursor = db.cursor()

    # Executar a query para buscar o usuário pelo email e senha
    
    query = "SELECT * FROM USUARIO WHERE EMAIL = %s"
    values = (email,)
    cursor.execute(query, values)

    # Verificar se o usuário existe no banco de dados
    usuario = cursor.fetchone()

    if usuario:
        # Usuário já existende no sistema, logo, as credenciais estão inválidas
        mensagem = {'message': 'Credenciais inválidas'}

        return mensagem
    
    # Executar a query para cadastrar o usuário
    query = "INSERT INTO USUARIO (EMAIL, SENHA) VALUES (%s, %s)"
    values = (email, senha)
    cursor.execute(query, values)

    # Fazer o commit das alterações
    db.commit()

    # Fechar a conexão com o banco de dados
    cursor.close()
    db.close()

    mensagem = {'message': 'Usuário cadastrado com sucesso'}

    # Retornar uma resposta de sucesso
    return mensagem

#login
@app.route('/login', methods=['POST'])
def fazer_login():
    # Obter os dados da requisição
    data = request.get_json()
    email = data['email']
    senha = data['senha']

    # Conectar ao banco de dados
    db = connect(
        host="localhost",
        user="root",
        password="1234",
        database="lactosafe_db"
    )

    # Criar o cursor
    cursor = db.cursor()

    # Executar a query para buscar o usuário pelo email e senha
    query = "SELECT * FROM USUARIO WHERE EMAIL = %s AND SENHA = %s LIMIT 1"
    values = (email, senha)
    cursor.execute(query, values)

    # Verificar se o usuário existe no banco de dados
    usuario = cursor.fetchone()

    if usuario:
        # Usuário autenticado, fazer algo aqui (exemplo: retornar uma mensagem de sucesso)
        mensagem = { 'userID': usuario[0], 'isLogged': True, 'message': 'Login realizado com sucesso'}

    else:
        # Usuário não encontrado, retornar uma mensagem de erro
        mensagem = { 'error': 'Email ou senha incorretos', 'isLogged': False }

    # Fechar o cursor e a conexão com o banco de dados
    cursor.close()
    db.close()

    # Retornar a mensagem
    return mensagem

#alterar-senha
@app.route('/alterar-senha', methods=['POST'])
def alterar_senha():
    # Obter os dados da requisição
    data = request.get_json()
    email = data['email']
    senha_atual = data['senha_atual']
    nova_senha = data['nova_senha']

    # Conectar ao banco de dados
    db = connect(
        host="localhost",
        user="root",
        password="1234",
        database="lactosafe_db"
    )

    # Criar o cursor
    cursor = db.cursor()

    # Verificar se o usuário existe no banco de dados com a senha atual
    query = "SELECT * FROM USUARIO WHERE EMAIL = %s AND SENHA = %s LIMIT 1"
    values = (email, senha_atual)
    cursor.execute(query, values)
    usuario = cursor.fetchone()

    if usuario:
        # Usuário autenticado, atualizar a senha no banco de dados
        query = "UPDATE USUARIO SET SENHA = %s WHERE EMAIL = %s"
        values = (nova_senha, email)
        cursor.execute(query, values)

        # Fazer o commit das alterações
        db.commit()

        mensagem = {'message': 'Senha alterada com sucesso'}
    else:
        # Usuário não encontrado ou senha atual incorreta, retornar mensagem de erro
        mensagem = {'error': 'Credenciais inválidas'}

    # Fechar o cursor e a conexão com o banco de dados
    cursor.close()
    db.close()

    # Retornar a mensagem
    return mensagem

#reconhecer
model = load_model('modelo2.h5')

# Imprimir as probabilidades de todas as classes
@app.route('/health', methods=['GET'])
def teste():
    return ('OK')

@app.route('/recognize-image', methods=['POST'])
def recognize_image():
    # Obtenha a imagem enviada na requisição
    image = request.files['image']
    image.save('temp_image.jpg')  # Salva a imagem em um arquivo temporário
    image = imread('temp_image.jpg')  # Lê a imagem do arquivo temporário
    image = resize(image, (150, 150))
    image = image.astype('float32') / 255.0
    image = expand_dims(image, axis=0)
    # Execute o algoritmo de reconhecimento de imagem na imagem recebida
    probabilities = model.predict(image)
    probabilities = probabilities[0]  # Extrair as probabilidades da matriz

    # Obter os índices dos 3 maiores valores de probabilidade
    top_3_indices = np.argsort(probabilities)[-3:][::-1]

    # Criar uma lista com as três maiores probabilidades e suas respectivas classes
    top_3_results = {'recognized_foods': []}
    for index in top_3_indices:
        class_label = ""
        if index == 0:
            class_label = 'Maca'
            image_url = 'https://i.imgur.com/IQapJAa.jpg'
        elif index == 1:
            class_label = 'Banana'
            image_url = 'https://i.imgur.com/W9h9tQt.jpg'
        elif index == 2:
            class_label = 'Pizza'
            image_url = 'https://i.imgur.com/vgSYyFu.jpg'
        
        probability = round(probabilities[index] * 100, 2)
        probability = float(probability)
        if probability > 0:
            top_3_results['recognized_foods'].append({'nome': class_label, 'porcentagem': probability, 'imageUrl': image_url})

    # Retorne os resultados em formato JSON
    return jsonify(top_3_results)

#risco-lactose
def calcular_risco_lactose(id_usuario, nome_alimento, imagem_id,id_al):
    # Conectar ao banco de dados
    db = connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="lactosafe_db"
    )

    cursor = db.cursor()

    # Encontrar o ID do tipo de alimento na tabela de tipos
    cursor.execute("SELECT TIPO_ALIMENTO_ID FROM ALIMENTO WHERE NOME = %s", (nome_alimento,))
    tipo_id = cursor.fetchone()

    if tipo_id is None:
        db.close()
        return "Tipo de alimento não encontrado no banco de dados."

    tipo_id = tipo_id[0]

    # Buscar todos os alimentos que são do mesmo tipo
    cursor.execute("SELECT id FROM ALIMENTO WHERE TIPO_ALIMENTO_ID = %s", (tipo_id,))
    alimentos_similares = cursor.fetchall()

    if not alimentos_similares:
        db.close()
        return "Não há alimentos do mesmo tipo no banco de dados."

    # Calcular a quantidade total de lactose dos alimentos similares
    total_lactose = 0.0
    num_alimentos = 0

    for alimento_id in alimentos_similares:
        alimento_id = alimento_id[0]
        cursor.execute("SELECT lactose FROM TABELA_NUTRICIONAL WHERE id = %s", (alimento_id,))
        lactose_alimento = cursor.fetchone()

        if lactose_alimento is not None and lactose_alimento[0] is not None:
            total_lactose += lactose_alimento[0]
            num_alimentos += 1

    # Calcular a média da quantidade de lactose entre os alimentos similares
    if num_alimentos > 0:
        media_lactose = total_lactose / num_alimentos
    else:
        db.close()
        return "Não foi encontrada informação nutricional para os alimentos similares."

    # Calcular o risco de lactose do alimento
    risco_lactose = (media_lactose / 12) * 100  # Supondo que a quantidade máxima recomendada seja 100mg
    risco_lactose = float(risco_lactose)
     # Definir a string de risco com base no valor do risco de lactose
    if risco_lactose == 0:
        risco_str = 'Inexistente'
    elif 1 <= risco_lactose <= 25:
        risco_str = 'Baixo'
    elif 25 < risco_lactose <= 50:
        risco_str = 'Medio'
    elif 50 < risco_lactose <= 75:
        risco_str = 'Alto'
    else:
        risco_str = 'Muito Alto'

    # Inserir os dados na tabela "historico"
    sql = "INSERT INTO historico (ID_USUARIO, ID_ALIMENTO, RISCO_FLOAT, RISCO_STR, ID_IMAGEM) VALUES (%s, %s, %s, %s, %s)"
    values = (id_usuario, id_al, risco_lactose, risco_str, imagem_id)
    cursor.execute(sql, values)

    # Fazer o commit para salvar as alterações no banco de dados
    db.commit()

    # Fechar a conexão com o banco de dados
    cursor.close()
    return risco_lactose

@app.route('/calcular_risco', methods=['POST'])
def calcular_risco():
    # Obtém os dados da requisição POST
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados não fornecidos'}), 400
        
    id_usuario = data.get('id_usuario')
    nome_alimento = data.get('nome_alimento')
        
    if id_usuario is None or nome_alimento is None:
        return jsonify({'error': 'Parâmetros incompletos'}), 400
        
    db = connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="lactosafe_db"
    )

    cursor = db.cursor()

    # Buscar o ID do alimento na tabela ALIMENTO
    cursor.execute("SELECT ID FROM ALIMENTO WHERE NOME = %s", (nome_alimento,))
    alimento_id = cursor.fetchone()[0]
    # Buscar o link da imagem na tabela IMAGEM usando o ID do alimento
    cursor.execute("SELECT IMAGEM FROM IMAGEM WHERE ALIMENTO_ID = %s", (alimento_id,))
    imagem_link = cursor.fetchone()[0]
    # Buscar o id da imagem na tabela IMAGEM usando o link
    cursor.execute("SELECT ID FROM IMAGEM WHERE IMAGEM = %s", (imagem_link,))
    imagem_id = cursor.fetchone()[0]
    # Buscar o texto_ajuda da alimento na tabela ALIMENTO usando o id
    cursor.execute("SELECT TEXTO_AJUDA FROM ALIMENTO WHERE ID = %s", (alimento_id,))
    texto_ajuda = cursor.fetchone()[0]
    db.close()   
    risco_lactose = calcular_risco_lactose(id_usuario, nome_alimento, imagem_id, alimento_id)
    
    if risco_lactose == 0:
        risco_str = 'Inexistente'
    elif 1 <= risco_lactose <= 25:
        risco_str = 'Baixo'
    elif 25 < risco_lactose <= 50:
        risco_str = 'Medio'
    elif 50 < risco_lactose <= 75:
        risco_str = 'Alto'
    else:
        risco_str = 'Muito alto'

    # Montar a resposta em JSON
    resposta = {
        'risco_lactose': risco_lactose,
        'risco_str': risco_str,
        'texto_ajuda' : texto_ajuda
    }

    return jsonify(resposta)

#historico
def obter_historico_usuario(id_usuario):
    db = connect(
        host="127.0.0.1",
        user="root",
        password="1234",
        database="lactosafe_db"
    )

    cursor = db.cursor()

    # Buscar o histórico de alimentos visualizados pelo usuário
    cursor.execute("SELECT ID_ALIMENTO, RISCO_FLOAT, RISCO_STR FROM historico WHERE ID_USUARIO = %s ORDER BY ID DESC", (id_usuario,))
    historico_alimentos = cursor.fetchall()

    alimentos_info = []

    for alimento_id, risco_float, risco_str in historico_alimentos:
        cursor.execute("SELECT NOME, TEXTO_AJUDA FROM ALIMENTO WHERE ID = %s", (alimento_id,))
        alimento_info = cursor.fetchone()

        cursor.execute("SELECT IMAGEM FROM IMAGEM WHERE ALIMENTO_ID = %s", (alimento_id,))
        imagem_link = cursor.fetchone()

        alimentos_info.append({
            'nome': alimento_info[0],
            'risco_float': risco_float,
            'risco_str': risco_str,
            'texto_ajuda': alimento_info[1],
            'imageUrl': imagem_link[0] if imagem_link else None
        })

    db.close()
    return alimentos_info

@app.route('/historico_alimentos', methods=['POST'])
def historico_alimentos():
    data = request.get_json()
    if not data or 'id_usuario' not in data:
        return jsonify({'error': 'ID do usuário não fornecido'}), 400

    id_usuario = data['id_usuario']

    historico = obter_historico_usuario(id_usuario)

    return jsonify({'historico_alimentos': historico})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)