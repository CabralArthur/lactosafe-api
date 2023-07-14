from flask import Flask, request
import mysql.connector

app = Flask('app')

@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    # Obter os dados da requisição
    data = request.get_json()
    email = data['email']
    senha = data['senha']

    # Conectar ao banco de dados
    db = mysql.connector.connect(
        host="localhost",
        user="seu_usuario",
        password="sua_senha",
        database="seu_banco_de_dados"
    )

    # Criar o cursor
    cursor = db.cursor()

    # Executar a query para cadastrar o usuário
    query = "INSERT INTO USUARIO (EMAIL, SENHA) VALUES (%s, %s)"
    values = (email, senha)
    cursor.execute(query, values)

    # Fazer o commit das alterações
    db.commit()

    # Fechar a conexão com o banco de dados
    cursor.close()
    db.close()

    # Retornar uma resposta de sucesso
    return {'message': 'Usuário cadastrado com sucesso'}

if __name__ == '__main__':
    app.run()
