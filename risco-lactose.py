from flask import Flask, request, jsonify
import mysql.connector

app = Flask('app')

def calcular_risco_lactose(id_usuario, nome_alimento, imagem_id):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="26112002",
        database="lactosafe_db"
    )

    cursor = conn.cursor()

    # Encontrar o ID do tipo de alimento na tabela de tipos
    cursor.execute("SELECT TIPO_ALIMENTO_ID FROM ALIMENTO WHERE NOME = %s", (nome_alimento,))
    tipo_id = cursor.fetchone()

    if tipo_id is None:
        conn.close()
        return "Tipo de alimento não encontrado no banco de dados."

    tipo_id = tipo_id[0]

    # Buscar todos os alimentos que são do mesmo tipo
    cursor.execute("SELECT id FROM ALIMENTO WHERE TIPO_ALIMENTO_ID = %s", (tipo_id,))
    alimentos_similares = cursor.fetchall()

    if not alimentos_similares:
        conn.close()
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
        conn.close()
        return "Não foi encontrada informação nutricional para os alimentos similares."

    # Calcular o risco de lactose do alimento
    risco_lactose = (media_lactose / 12) * 100  # Supondo que a quantidade máxima recomendada seja 100mg
    risco_lactose = float(risco_lactose)
     # Definir a string de risco com base no valor do risco de lactose
    if risco_lactose == 0:
        risco_str = 'inexistente'
    elif 1 <= risco_lactose <= 25:
        risco_str = 'baixo'
    elif 25 < risco_lactose <= 50:
        risco_str = 'medio'
    elif 50 < risco_lactose <= 75:
        risco_str = 'alto'
    else:
        risco_str = 'muito alto'

    # Inserir os dados na tabela "historico"
    sql = "INSERT INTO historico (ID_USUARIO, ID_ALIMENTO, RISCO_FLOAT, RISCO_STR, ID_IMAGEM) VALUES (%s, %s, %s, %s, %s)"
    values = (id_usuario, tipo_id, risco_lactose, risco_str, imagem_id)
    cursor.execute(sql, values)

    # Fazer o commit para salvar as alterações no banco de dados
    conn.commit()

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
        
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="26112002",
        database="lactosafe_db"
    )

    cursor = conn.cursor()

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
    conn.close()   
    risco_lactose = calcular_risco_lactose(id_usuario, nome_alimento, imagem_id)
    
    if risco_lactose == 0:
        risco_str = 'inexistente'
    elif 1 <= risco_lactose <= 25:
        risco_str = 'baixo'
    elif 25 < risco_lactose <= 50:
        risco_str = 'medio'
    elif 50 < risco_lactose <= 75:
        risco_str = 'alto'
    else:
        risco_str = 'muito alto'

    # Montar a resposta em JSON
    resposta = {
        'risco_lactose': risco_lactose,
        'risco_str': risco_str,
        'texto_ajuda' : texto_ajuda
    }

    return jsonify(resposta)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
