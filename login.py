from flask import Flask, request
from mysql.connector import connect

app = Flask(__name__)

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
        password="",
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
        mensagem = {'message': 'Login realizado com sucesso'}

    else:
        # Usuário não encontrado, retornar uma mensagem de erro
        mensagem = {'error': 'Credenciais inválidas'}

    # Fechar o cursor e a conexão com o banco de dados
    cursor.close()
    db.close()

    # Retornar a mensagem
    return mensagem

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
