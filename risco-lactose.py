import mysql.connector

def calcular_risco_lactose(id_usuario, tipo_alimento):
    # Conectar ao banco de dados
    conn = mysql.connector.connect(
        host="seu_host",
        user="seu_usuario",
        password="sua_senha",
        database="seu_banco_de_dados"
    )

    cursor = conn.cursor()

    # Encontrar o ID do tipo de alimento na tabela de tipos
    cursor.execute("SELECT id FROM tabela_tipos WHERE nome = ?", (tipo_alimento,))
    tipo_id = cursor.fetchone()

    if tipo_id is None:
        conn.close()
        return "Tipo de alimento não encontrado no banco de dados."

    tipo_id = tipo_id[0]

    # Buscar todos os alimentos que são do mesmo tipo
    cursor.execute("SELECT id, nome FROM tabela_alimentos WHERE tipo_id = ?", (tipo_id,))
    alimentos_similares = cursor.fetchall()

    if not alimentos_similares:
        conn.close()
        return "Não há alimentos do mesmo tipo no banco de dados."

    # Calcular a quantidade total de lactose dos alimentos similares
    total_lactose = 0.0
    num_alimentos = 0

    for alimento_id, nome_alimento in alimentos_similares:
        cursor.execute("SELECT lactose FROM tabela_nutricional WHERE alimento_id = ?", (alimento_id,))
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
    risco_lactose = (media_lactose / 100) * 100  # Supondo que a quantidade máxima recomendada seja 100mg

    # Inserir os dados na tabela "historico"
    sql = "INSERT INTO historico (id_usuario, tipo_alimento, risco) VALUES (%s, %s, %s)"
    values = (id_usuario, tipo_alimento, risco_lactose)
    cursor.execute(sql, values)

    # Fazer o commit para salvar as alterações no banco de dados
    conn.commit()

    # Fechar a conexão com o banco de dados
    cursor.close()
    return risco_lactose