from flask import Flask, request
from mysql.connector import connect

app = Flask('app')

@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    # Obter os dados da requisição
    data = request.get_json()
    email = data['email']
    senha = data['senha']

    # Conectar ao banco de dados
    db = connect(
        host="localhost",
        user="seu_usuario",
        password="sua_senha",
        database="seu_banco_de_dados"
    )

    # Criar o cursor
    cursor = db.cursor()

    # Executar a query para buscar o usuário pelo email e senha
    query = "SELECT * FROM USUARIO WHERE EMAIL = %s"
    values = (email)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
