from tensorflow.keras.models import load_model
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask('app')
CORS(app)

# Carregar o modelo treinado
model = load_model('modelo1.h5')

# Fazer a previsão


# Imprimir as probabilidades de todas as classes
@app.route('/test', methods=['GET'])
def teste():
    return ('Sucesso')

@app.route('/recognize-image', methods=['POST'])
def recognize_image():
    # Obtenha a imagem enviada na requisição
    image = request.files['image']
    image.save('temp_image.jpg')  # Salva a imagem em um arquivo temporário
    image = cv2.imread('temp_image.jpg')  # Lê a imagem do arquivo temporário
    image = cv2.resize(image, (150, 150))
    image = image.astype('float32') / 255.0
    image = np.expand_dims(image, axis=0)
    # Execute o algoritmo de reconhecimento de imagem na imagem recebida
    probabilities = model.predict(image)
    probabilities = np.array(probabilities)

    # Obtém o índice da maior probabilidade
    max_index = np.argmax(probabilities)

    # Recupera a classe correspondente ao índice
    class_label = f'Classe {max_index}'

    # Calcula a porcentagem da maior probabilidade
    percentage = round(max(probabilities[0]) * 100, 2)

    os.remove('temp_image.jpg')
    # Retorne os resultados em formato JSON
    return jsonify(f'{class_label}: {percentage}%')

if __name__ == '__main__':
    app.run()