# -*- coding: utf-8 -*-

# References:
# For Loading Dataset: https://towardsdatascience.com/loading-custom-image-dataset-for-deep-learning-models-part-1-d64fa7aaeca6
# For K-fold Validation: https://androidkt.com/k-fold-cross-validation-with-tensorflow-keras/
# For General CNN Training using Tensorflow: https://deeplizard.com/learn/video/daovGOlMbT4
# For One-hot encoding the vector: https://www.educative.io/blog/one-hot-encoding


import numpy as np
import tensorflow as tf
import math
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Activation, Dense, Flatten, BatchNormalization, Conv2D, MaxPool2D, Input, InputLayer
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import sklearn.preprocessing as preprocessing
from tensorflow.keras.preprocessing import image
from keras.utils import to_categorical
from numpy import loadtxt
physical_devices = tf.config.experimental.list_physical_devices('GPU')
print("Num GPUs Available: ", len(physical_devices))
tf.config.experimental.set_memory_growth(physical_devices[0], True)
from sklearn.metrics import confusion_matrix
from sklearn.compose import ColumnTransformer
from tensorflow.keras import callbacks
tf.compat.v1.set_random_seed(69420)
import itertools
import os
import shutil
import cv2
import random
import glob
from  matplotlib import pyplot as plt
import matplotlib.image as mpimg
import warnings
import tqdm
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.model_selection import KFold
warnings.simplefilter(action='ignore', category=FutureWarning)



maindir = os.getcwd()

train_path='/data/train'
train_path= maindir + train_path
valid_path='/data/valid'
valid_path= maindir + valid_path


def create_dataset(img_folder):
   
	img_data_array=[]
	count=0
	class_name=[]
	for dir1 in os.listdir(img_folder):
		for file in os.listdir(os.path.join(img_folder, dir1)):    
			image_path= os.path.join(img_folder, dir1,  file)
			image= cv2.imread(image_path)
			image=np.array(image)
			image = image.astype('float32')
			image /= 255
			# image = image[:,:,0]
			img_data_array.append(image)
			class_name.append(dir1)
			# count += 1
			# if count >= 4700:
			# 	break
	return img_data_array, class_name
    





train_input, train_target = create_dataset(train_path)
targets_string = np.asarray(train_target)
targets_string = np.transpose(targets_string)
labelEnc = preprocessing.LabelEncoder()
new_target = labelEnc.fit_transform(targets_string)
onehotEnc = preprocessing.OneHotEncoder()
onehotEnc.fit(new_target.reshape(-1, 1))
train_target = onehotEnc.transform(new_target.reshape(-1, 1))
train_target = np.matrix(train_target.toarray())
i = range(4230)
train_input = np.take(train_input, i, axis=0)

test_input, test_target = create_dataset(valid_path)
targets_string = np.asarray(test_target)
targets_string = np.transpose(targets_string)
labelEnc = preprocessing.LabelEncoder()
new_target = labelEnc.fit_transform(targets_string)
onehotEnc = preprocessing.OneHotEncoder()
onehotEnc.fit(new_target.reshape(-1, 1))
test_target = onehotEnc.transform(new_target.reshape(-1, 1))
i = range(644)
test_input = np.take(test_input, i, axis=0)

print("Loading Dataset Completed." + '\n') 



  


#Model

model = tf.keras.models.Sequential([
    # Block 1
    tf.keras.layers.Conv2D(16,(3,3),activation = "relu", input_shape = (180,180,3), padding = "valid"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(16,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(2,2),

    
    # Block 2
    tf.keras.layers.Conv2D(32,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(32,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.Conv2D(32,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.BatchNormalization(),
    tf.keras.layers.MaxPooling2D(2,2),
    
    
    # Block 3
    tf.keras.layers.Conv2D(48,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.Conv2D(64,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.Conv2D(80,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.Conv2D(96,(3,3),activation = "relu", padding = "valid"),
    tf.keras.layers.MaxPooling2D(2,2),
    
    
    
    
    # Final Layers
    tf.keras.layers.Flatten(), 
    tf.keras.layers.Dense(1024,activation = "relu"),
    tf.keras.layers.Dropout(0.5,seed = 69420),
    tf.keras.layers.Dense(200,activation = "relu"),
    tf.keras.layers.Dropout(0.8,seed = 69420),
    tf.keras.layers.Dense(2,activation = "softmax"),
])


model.compile(optimizer=Adam(learning_rate=0.00001), loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()



# Fit data to model
earlystopping = callbacks.EarlyStopping(monitor ="val_acc", 
                                    mode ="max", patience = 10, 
                                    restore_best_weights = True)
history = model.fit(x=train_input, y=train_target, batch_size=10, validation_data = (test_input, test_target), epochs=100, verbose = 1,callbacks =[earlystopping]) # original: epochs = 15

# Generate generalization metrics
scores = model.evaluate(test_input, test_target, verbose=0)
print(f'{model.metrics_names[0]} of {scores[0]}; {model.metrics_names[1]} of {scores[1]*100}%')

model.save("Adaptive_Trained_Model_2_2k.h5")
print("Model Saved")
	
