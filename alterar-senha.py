from flask import Flask, request
from mysql.connector import connect

app = Flask(__name__)

# Função para alterar a senha do usuário
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
        password="",
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
