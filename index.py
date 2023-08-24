from tensorflow.keras.models import load_model
from cv2 import imread, resize
from numpy import expand_dims, array, argmax
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np

app = Flask('app')
CORS(app)

# Carregar o modelo treinado
model = load_model('modelo2.h5')

# Fazer a previsão

# Imprimir as probabilidades de todas as classes
@app.route('/health', methods=['GET'])
def teste():
    return ('OK')

@app.route('/recognize-image', methods=['POST'])
def recognize_image():
    # Obtenha a imagem enviada na requisição
    image = request.files['image']
    image.save('temp_image.jpg')  # Salva a imagem em um arquivo temporário
    image = imread('temp_image.jpg')  # Lê a imagem do arquivo temporário
    image = resize(image, (150, 150))
    image = image.astype('float32') / 255.0
    image = expand_dims(image, axis=0)
    # Execute o algoritmo de reconhecimento de imagem na imagem recebida
    probabilities = model.predict(image)
    probabilities = probabilities[0]  # Extrair as probabilidades da matriz

    # Obter os índices dos 3 maiores valores de probabilidade
    top_3_indices = np.argsort(probabilities)[-3:][::-1]

    # Criar uma lista com as três maiores probabilidades e suas respectivas classes
    top_3_results = {'recognized_foods': []}
    for index in top_3_indices:
        class_label = ""
        if index == 0:
            class_label = 'Maca'
            image_url = 'https://i.imgur.com/IQapJAa.jpg'
        elif index == 1:
            class_label = 'Banana'
            image_url = 'https://i.imgur.com/dZ52849.jpg'
        elif index == 2:
            class_label = 'Pizza'
            image_url = 'https://i.imgur.com/vgSYyFu.jpg'
        
        probability = round(probabilities[index] * 100, 2)
        probability = float(probability)
        if probability > 0:
            top_3_results['recognized_foods'].append({'nome': class_label, 'porcentagem': probability, 'imageUrl': image_url})

    # Retorne os resultados em formato JSON
    return jsonify(top_3_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)