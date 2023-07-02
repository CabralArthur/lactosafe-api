from tensorflow.keras.models import load_model
import cv2
import numpy as np

# Carregar o modelo treinado
model = load_model('meu_modelo2.h5')

# Carregar a imagem de teste
image_path = 'maca1.jpg'
image = cv2.imread(image_path)

# Pré-processar a imagem
image = cv2.resize(image, (150, 150))
image = image.astype('float32') / 255.0
image = np.expand_dims(image, axis=0)

# Fazer a previsão
probabilities = model.predict(image)

# Imprimir as probabilidades de todas as classes
for i, probability in enumerate(probabilities[0]):
    class_label = f'Classe {i}'
    percentage = round(probability * 100, 2)
    print(f'{class_label}: {percentage}%')
