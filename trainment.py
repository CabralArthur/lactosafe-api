# Importar as bibliotecas necessárias
import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import random

input_shape = (224, 224, 3)
num_classes = 5 
batch_size = 32
epochs = 25
learning_rate = 0.003

# Função para processar e substituir as imagens
def preprocess_and_replace_images(image_folder, target_size, normalization=True, crop=True, rotation_range=None):
    # Processar e substituir cada imagem
    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)
        
        # Carregar a imagem
        image = cv2.imread(image_path)
        
        # Redimensionar a imagem
        resized_image = cv2.resize(image, target_size)
        
       # Corte (cropping)
        if crop:
            crop_height, crop_width = target_size
            height, width, _ = resized_image.shape
            start_x = random.randint(0, width - crop_width)
            start_y = random.randint(0, height - crop_height)
            cropped_image = resized_image[start_y:start_y+crop_height, start_x:start_x+crop_width]
        else:
            cropped_image = resized_image

        # Rotação aleatória
        if rotation_range:
            angle = random.uniform(-rotation_range, rotation_range)
            rows, cols, _ = cropped_image.shape
            rotation_matrix = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
            rotated_image = cv2.warpAffine(cropped_image, rotation_matrix, (cols, rows))
        else:
            rotated_image = cropped_image
        
        # Substituir a imagem original pela imagem pré-processada
        cv2.imwrite(image_path, rotated_image)


# Exemplo de uso:
#image_folder = 'data/validacao/classe1'
#target_size = (224, 224)
#preprocess_and_replace_images(image_folder, target_size, normalization=True, crop=True, rotation_range=20)

train_data_dir = 'data/treino'
validation_data_dir = 'data/validacao'

# Criar o modelo
def create_model(input_shape, num_classes):
   # Carregar o modelo VGG16 pré-treinado (sem camada de saída)
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)

    # Congelar as camadas do modelo VGG16 para evitar que sejam treinadas novamente
    for layer in base_model.layers[:-4]:
        layer.trainable = False

    for layer in base_model.layers[-4:]:
        layer.trainable = True

    # Criar um novo modelo Sequential
    model = Sequential()

    # Adicionar as camadas do modelo VGG16 ao novo modelo
    model.add(base_model)

    # Adicionar camadas personalizadas para a tarefa de reconhecimento das três classes
    model.add(Conv2D(128, (2,2), activation='relu', kernel_regularizer=l2(0.03)))
    model.add(MaxPooling2D((2,2)))
    model.add(Flatten())
    model.add(Dropout(0.3))
    model.add(Dense(256, activation='relu', kernel_regularizer=l2(0.03)))    
    model.add(Dense(num_classes, activation='softmax'))

    return model

# Crie o otimizador Adam com a taxa de aprendizagem especificada
optimizer = Adam(learning_rate=learning_rate)

modelo = create_model(input_shape, num_classes)
modelo.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# Criar geradores de dados de treinamento e validação
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)
validation_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=input_shape[:2],
    batch_size=batch_size,
    color_mode = 'rgb',
    class_mode='categorical'
)

validation_generator = validation_datagen.flow_from_directory(
    validation_data_dir,
    target_size=input_shape[:2],
    batch_size=batch_size,
    color_mode = 'rgb',
    class_mode='categorical'
)

#earlystop
early_stopping = EarlyStopping(monitor='val_loss', patience = 3)

# Treinar o modelo
modelo.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size,
    callbacks = [early_stopping]
)

modelo.save('meu_modeloV2.h5')
print('sucesso')
