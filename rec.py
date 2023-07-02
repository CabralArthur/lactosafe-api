# Importar as bibliotecas necessárias
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Passo 1: Coletar e preparar os dados
# ...

# Passo 2: Dividir os dados em conjuntos de treinamento, validação e teste
# ...

# Passo 3: Pré-processar as imagens
# ...
img_heigth, img_width = 150, 150
batch_size = 4
num_classes = 2
epochs = 25

# Função para processar e substituir as imagens
def preprocess_and_replace_images(image_folder, target_size):
    # Processar e substituir cada imagem
    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)
        
        # Carregar a imagem
        image = cv2.imread(image_path)
        
        # Redimensionar a imagem
        resized_image = cv2.resize(image, target_size)
        
        # Substituir a imagem original pela redimensionada
        cv2.imwrite(image_path, resized_image)

# Definir o caminho da pasta das imagens
image_folder_train = 'data/treino/classe2'
image_folder_val = 'data/validacao/classe2'
# Definir o tamanho de destino para redimensionamento
target_size = (150,150)
# Chamar a função para processar e substituir as imagens






# Passo 4: Construir a arquitetura da CNN
# ...
# Definir a arquitetura da CNN

# Passo 5: Treinar a CNN
# ...
# Carregar e pré-processar os dados
train_data_dir = 'data/treino'
validation_data_dir = 'data/validacao'

# Definir o tamanho das imagens de entrada
input_shape = (img_heigth, img_width, 3)

# Criar o modelo
def create_model(input_shape, num_classes):
    modelo = Sequential()
    modelo.add(Conv2D(32, (3, 3), activation='relu', input_shape=(img_heigth, img_width, 3)))
    modelo.add(MaxPooling2D((2, 2)))
    modelo.add(Conv2D(128, (3, 3), activation='relu'))
    modelo.add(MaxPooling2D((2, 2)))
    modelo.add(Flatten())
    modelo.add(Dense(512, activation='relu'))
    modelo.add(Dropout(0.5))
    modelo.add(Dense(num_classes, activation='softmax'))
    return modelo

modelo = create_model(input_shape, num_classes)
modelo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'], run_eagerly=True)

# Criar geradores de dados de treinamento e validação
train_datagen = ImageDataGenerator(rescale=1.0/255)
validation_datagen = ImageDataGenerator(rescale=1.0/255)
train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=input_shape[:2],
    batch_size=batch_size,
    class_mode='categorical'
)

validation_generator = validation_datagen.flow_from_directory(
    validation_data_dir,
    target_size=input_shape[:2],
    batch_size=batch_size,
    class_mode='categorical'
)
# Treinar o modelo
modelo.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size
)

modelo.save('meu_modelo3.h5')
print('sucesso')
# Passo 6: Avaliar o desempenho do modelo
# ...

# Passo 7: Testar o modelo
# ...
