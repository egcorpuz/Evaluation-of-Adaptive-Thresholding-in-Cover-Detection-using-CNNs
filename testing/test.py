# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 20:14:44 2021

@author: Craig
"""

# References:
# General Testing: https://machinelearningmastery.com/how-to-make-classification-and-regression-predictions-for-deep-learning-models-in-keras/
# Sorting matrix: https://www.kite.com/python/answers/how-to-sort-the-rows-of-a-numpy-array-by-a-column-in-python
# For Loading Dataset: https://towardsdatascience.com/loading-custom-image-dataset-for-deep-learning-models-part-1-d64fa7aaeca6
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential,load_model
from tensorflow.keras.layers import Dense
from keras.backend.tensorflow_backend import set_session
import numpy as np
import statistics
import cv2

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
tf.keras.backend.set_session(tf.Session(config=config))
maindir = os.getcwd()
test_path='/data1'
test_path= maindir + test_path

MNIT10_array = [] # Store number of correctly identified top 10 covers in each title
MR1_array = [] # Store the first rank 1 that appears in a matrix
MAP_array = [] # Store average precision for each query
MNIT102_array = []

def create_dataset(img_folder, query): # Modified from Loading Dataset Reference to add title array
   
    img_data_array=[]
    class_name=[]
    titles = []
    count = 0
    covers = 0
    noncovers = 0
    for dir1 in os.listdir(img_folder):
        for file in os.listdir(os.path.join(img_folder, dir1)):
            query_check = (ord(file[6]) - 48) * 10 +  ord(file[7]) - 48
            ref_check = (ord(file[18]) - 48) * 10 +  ord(file[19]) - 48
            if query_check == query:
                titles.append(file)
                image_path= os.path.join(img_folder, dir1,  file)
                image= cv2.imread(image_path)
                image=np.array(image)
                image = image.astype('float32')
                image /= 255
                img_data_array.append(image)
                class_name.append(dir1)
    return img_data_array, class_name, titles, count
query = 1
for x in range(30):

    test_set, targets_string, test_set_title, song_count = create_dataset(test_path,query)
    test_set_title = np.char.asarray(test_set_title)
    test_set = np.array(test_set)

    saved_model = load_model("Adaptive_Trained_Model_2k.h5")
    # make a prediction
    probability = saved_model.predict(test_set)
    probability = probability.transpose()
    test_matrix = np.vstack((test_set_title, probability[0])).T # Append probability that the test files are covers based on the trained model
    test_matrix = test_matrix[np.argsort(test_matrix[:, 1])]
    test_matrix = np.flipud(test_matrix)

    

    test_matrix_arranged = []
    iscover = []
    row_count = 0
    for rows in test_matrix:
        query_check = (ord(rows[0][6]) - 48) * 10 +  ord(rows[0][7]) - 48
        ref_check = (ord(rows[0][18]) - 48) * 10 +  ord(rows[0][19]) - 48
        test_matrix_arranged.append(rows)
        if query_check == ref_check:
            iscover.append(1)
        else:
            iscover.append(0)
        row_count += 1

    test_matrix_arranged = np.hstack((test_matrix_arranged, np.atleast_2d(iscover).T))
    row_count = 0
    correct_MNIT10 = 0 # Number of correctly identified covers in a title
    total = 0
    for rows in test_matrix_arranged:
        if test_matrix_arranged[row_count][2] == '1' and float(test_matrix_arranged[row_count][1]) >= 0.50: # True Positive:
            correct_MNIT10 += 1
        if test_matrix_arranged[row_count][2] == '1':
            total +=1
        row_count +=1

    # MR1
    row_count = 0
    MR1_temp = 0
    for i in range(total):
        if float(test_matrix_arranged[row_count][2]) == 1:
            MR1_temp +=1
        row_count += 1
    MR1_a = 1/(MR1_temp/total)
    MR1_array.append(MR1_a)

    # MNIT10
    row_count = 0
    correct_MNIT10 = 0 # Number of correctly identified covers in a title
    total = 0
    for rows in test_matrix_arranged:
        if test_matrix_arranged[row_count][2] == '1' and float(test_matrix_arranged[row_count][1]) >= 0.50: # True Positive:
            correct_MNIT10 += 1
        if test_matrix_arranged[row_count][2] == '1':
            total +=1
        row_count +=1
    MNIT10_array.append(correct_MNIT10/total*10)    



MR1 = statistics.mean(MR1_array)
MNIT10 = statistics.mean(MNIT10_array)    
print("MNIT10 = ", MNIT10, "\nMR1 = ", MR1)