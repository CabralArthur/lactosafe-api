from flask import Flask, request, jsonify
from mysql.connector import connect

app = Flask('app')

# Função para retornar o histórico de alimentos do usuário
@app.route('/historico-alimentos', methods=['POST'])
def historico_alimentos():
    # Obtém o ID do usuário da requisição
    user_id = request.args.get('user_id')

    # Conecta ao banco de dados
    db = connect(
        host="127.0.0.1",
        user="root",
        password="26112002",
        database="lactosafe_db"
    )

    # Cria o cursor
    cursor = db.cursor()

    # Executa a query para buscar o histórico de alimentos do usuário
    query = """
        SELECT a.NOME, h.RISCO_STR, i.URL_IMAGEM
        FROM HISTORICO h
        INNER JOIN ALIMENTO a ON h.ID_ALIMENTO = a.ID
        LEFT JOIN IMAGEM i ON h.ID_IMAGEM = i.ID
        WHERE h.ID_USUARIO = %s
    """
    values = (user_id,)
    cursor.execute(query, values)

    # Obtém os resultados da consulta
    historico = []
    for nome_alimento, risco_str, url_imagem in cursor.fetchall():
        historico.append({
            'nome_alimento': nome_alimento,
            'risco_str': risco_str,
            'url_imagem': url_imagem
        })

    # Fecha o cursor e a conexão com o banco de dados
    cursor.close()
    db.close()

    # Retorna o histórico como JSON
    return jsonify(historico)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
