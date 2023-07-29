from tensorflow.keras.models import load_model
from cv2 import imread, resize
from numpy import expand_dims, array, argmax
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask('app')
CORS(app)

# Carregar o modelo treinado
model = load_model('modelo1.h5')

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
    probabilities = array(probabilities)

    # Obtém o índice da maior probabilidade
    max_index = argmax(probabilities)

    # Recupera a classe correspondente ao índice
    class_label = f'Classe {max_index}'

    # Calcula a porcentagem da maior probabilidade
    percentage = round(max(probabilities[0]) * 100, 2)

    os.remove('temp_image.jpg')
    # Retorne os resultados em formato JSON
    if class_label == 'Classe 0':
        return jsonify({'nome': 'Maca', 'porcentagem': f'{percentage}%'})
   

    elif class_label == 'Classe 1':
        return jsonify({'nome': 'Banana', 'porcentagem': f'{percentage}%'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)