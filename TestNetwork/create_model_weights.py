import glob
import os
import math
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import pickle
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.applications.vgg16 import VGG16
#from cv2 import imshow

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import make_scorer
from sklearn.metrics import auc, roc_curve, roc_auc_score
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

from tensorflow import keras
from tensorflow.keras import Sequential, Model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.optimizers.legacy import Adam


# create model
def create_model(input_shape, optimizer='rmsprop', fine_tune=0):
  conv_base = VGG16(include_top=False, weights='imagenet', input_shape=input_shape)
  if fine_tune > 0:
      for layer in conv_base.layers[:-fine_tune]:
          layer.trainable = False
  else:
      for layer in conv_base.layers:
          layer.trainable = False

  top_model = conv_base.output

  top_model = Flatten(name="flatten")(top_model)
  top_model = Dense(4096, activation='relu')(top_model)
  top_model = Dense(1072, activation='relu')(top_model)
  top_model = Dropout(0.2)(top_model)
  output_layer = Dense(1, activation='sigmoid')(top_model)
  
  model = Model(inputs=conv_base.input, outputs=output_layer)

  model.compile(optimizer=optimizer, 
                loss='binary_crossentropy',
                metrics=['accuracy'])
  
  return model

def main():
  img_height = 256
  img_width = 256
  input_shape = (img_height, img_width, 3)
  optim_1 = Adam(learning_rate=0.001)
  model = create_model(input_shape, optim_1, fine_tune=0)
  # save initial model weights
  with open(sys.argv[1], 'wb') as file:
    pickle.dump(model.get_weights(), file)

if __name__ == "__main__":
  if len(sys.argv) < 2:
     print("Chua truyen tham so!")
  else:
    main()