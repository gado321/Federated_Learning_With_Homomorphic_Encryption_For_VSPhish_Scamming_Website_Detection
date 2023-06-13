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

  root_dir = '/VisualPhish/'
  dataset_dir_benign = root_dir + 'benign_test'
  dataset_dir_phishing = root_dir + 'phishing'
  dataset_dir_trusted = root_dir + 'trusted_list'
  benign = list(glob.glob(dataset_dir_benign + '/*'))
  phishing = list(glob.glob(dataset_dir_phishing + '/**/*'))
  trusted_list = list(glob.glob(dataset_dir_trusted + '/**/*'))

  # remove files
  cnt = 0
  for f in benign:
    if f.upper().find(".PNG") == -1 and f.upper().find(".JPG") == -1:
      try:
        os.remove(f)
        cnt += 1
      except OSError as e:
        print(e)

  print("benign removed: " + str(cnt))
  cnt = 0

  for f in phishing:
    if f.upper().find(".PNG") == -1 and f.upper().find(".JPG") == -1:
      try:
        os.remove(f)
        cnt += 1
      except OSError as e:
        print(e)

  print("phishing removed: " + str(cnt))
  cnt = 0

  for f in trusted_list:
    if f.upper().find(".PNG") == -1 and f.upper().find(".JPG") == -1:
      try:
        os.remove(f)
        cnt += 1
      except OSError as e:
        print(e)

  # define 
  img_height = 256
  img_width = 256
  phishing_size = len(phishing)
  trusted_size = len(trusted_list)


  # Load dataset

  dataseta_train = tf.keras.preprocessing.image_dataset_from_directory(dataset_dir_phishing, validation_split=0.3, subset='training', seed=123, image_size=(img_height, img_width), batch_size=None, labels=[1 for i in range(phishing_size)], label_mode='int')
  datasetb_train = tf.keras.preprocessing.image_dataset_from_directory(dataset_dir_benign, validation_split=0.3, subset='training', seed=123, image_size=(img_height, img_width), batch_size=None, labels=None)
  datasetc_train = tf.keras.preprocessing.image_dataset_from_directory(dataset_dir_trusted, validation_split=0.3, subset='training', seed=123, image_size=(img_height, img_width), batch_size=None, labels=[1 for i in range(trusted_size)], label_mode='int')

  dataseta_train = dataseta_train.map(lambda x, y: (x, tf.cast(y, tf.float32)))
  datasetb_train = datasetb_train.map(lambda x: (x, tf.constant(0.0)))
  datasetc_train = datasetc_train.map(lambda x, y: (x, tf.cast(y, tf.float32)))

  dataseta_test = tf.keras.preprocessing.image_dataset_from_directory(dataset_dir_phishing, validation_split=0.3, subset='validation', seed=123, image_size=(img_height, img_width), batch_size=None, labels=[1 for i in range(phishing_size)], label_mode='int')
  datasetb_test = tf.keras.preprocessing.image_dataset_from_directory(dataset_dir_benign, validation_split=0.3, subset='validation', seed=123, image_size=(img_height, img_width), batch_size=None, labels=None)
  datasetc_test = tf.keras.preprocessing.image_dataset_from_directory(dataset_dir_trusted, validation_split=0.3, subset='validation', seed=123, image_size=(img_height, img_width), batch_size=None, labels=[1 for i in range(trusted_size)], label_mode='int')

  dataseta_test = dataseta_test.map(lambda x, y: (x, tf.cast(y, tf.float32)))
  datasetb_test = datasetb_test.map(lambda x: (x, tf.constant(0.0)))
  datasetc_test = datasetc_test.map(lambda x, y: (x, tf.cast(y, tf.float32)))

  train_ds = dataseta_train.concatenate(datasetb_train).concatenate(datasetc_train)
  test_ds = dataseta_test.concatenate(datasetb_test).concatenate(datasetc_test)

  # normalizatin
  normalization_layer = tf.keras.layers.Rescaling(1./255)

  train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
  test_ds = test_ds.map(lambda x, y: (normalization_layer(x), y))

  # reduce samples to test FL
  train_ds = train_ds.take(33)
  test_ds = test_ds.take(33)


  # define

  input_shape = (img_height, img_width, 3)
  optim_1 = Adam(learning_rate=0.001)
  n_epochs = 1
  batch_size = 32

  # batching
  local_train_ds = train_ds.batch(batch_size)
  local_test_ds = test_ds.batch(batch_size)

  # read received weights
  with open(sys.argv[1], "rb") as file:
    weights = pickle.load(file)

  # create model and train

  model = create_model(input_shape, optim_1, fine_tune=0)
  model.set_weights(weights)

  model.fit(local_train_ds, epochs=n_epochs, validation_data=local_test_ds, verbose=1)

  # now save model weights
  with open(sys.argv[2], "wb") as file:
    pickle.dump(model.get_weights(), file)

if __name__ == '__main__':
  if len(sys.argv) < 3:
    print("Chua truyen tham so!")
  else:
    main()