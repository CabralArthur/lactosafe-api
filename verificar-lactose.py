from flask import Flask, request
from mysql.connector import connect

app = Flask('app')

@app.route('/verificar-lactose', methods=['POST'])
def verificar_lactose():
    # Obter os dados da requisição
    data = request.get_json()
    alimento = data['alimento']

    # Conectar ao banco de dados
    db = connect(
        host="localhost",
        user="seu_usuario",
        password="sua_senha",
        database="seu_banco_de_dados"
    )

    # Criar o cursor
    cursor = db.cursor()

    # Executar a query para buscar a presença de lactose no alimento 
    query = "SELECT lactose FROM TABELA_NUTRICIONAL WHERE id_alimento = (SELECT id FROM ALIMENTO WHERE nome = %s)"
    values = (alimento,)
    cursor.execute(query, values)

    # Verificar a presença de lactose no alimento
    resultado = cursor.fetchone()
    if resultado:
        lactose = resultado[0]
        if lactose == 1:
            mensagem = {'message': 'O alimento contém lactose'}
        else:
            mensagem = {'message': 'O alimento não contém lactose'}
    else:
        mensagem = {'message': 'Alimento não encontrado'}

    # Fechar a conexão com o banco de dados
    cursor.close()
    db.close()

    # Retornar a resposta
    return mensagem

if __name__ == '__main__':
    app.run()
