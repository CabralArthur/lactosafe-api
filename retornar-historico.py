from flask import Flask, request, jsonify
import mysql.connector

app = Flask('app')

def obter_historico_usuario(id_usuario):
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="26112002",
        database="lactosafe_db"
    )

    cursor = conn.cursor()

    # Buscar o histórico de alimentos visualizados pelo usuário
    cursor.execute("SELECT ID_ALIMENTO, RISCO_FLOAT, RISCO_STR FROM historico WHERE ID_USUARIO = %s", (id_usuario,))
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

    conn.close()
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
