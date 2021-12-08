import h5py
import numpy as np
import matplotlib.pyplot as plt
import glob
import keras
from tensorflow.keras import backend as K 
import tensorflow as tf
from keras.optimizers import Adam
import os


def dice_coefficient(y_true, y_pred, axis=(0,1,2), epsilon=0.00001):
   
  dice_numerator = 2. * K.sum(y_true * y_pred, axis=axis) + epsilon
  dice_denominator = K.sum(y_true, axis=axis) + K.sum(y_pred, axis=axis) + epsilon
  dice_coefficient = K.mean((dice_numerator)/(dice_denominator))

  return dice_coefficient

def soft_dice_loss(y_true, y_pred, axis=(0,1,2), epsilon=0.00001):

  dice_numerator = 2. * K.sum(y_true * y_pred, axis=axis) + epsilon
  dice_denominator = K.sum(y_true**2, axis=axis) + K.sum(y_pred**2, axis=axis) + epsilon
  dice_loss = 1 - K.mean((dice_numerator)/(dice_denominator))

  return dice_loss

optimizer = Adam
model = tf.keras.models.load_model('/home/pi/brain_stroke/base_model.h5',compile= False)
model.compile(optimizer=optimizer(lr=5e-4), loss=soft_dice_loss, metrics=[dice_coefficient])
model.load_weights('/home/pi/brain_stroke/weight_4layerisensee_val_best.hdf5')

del optimizer

#model.summary()

file_n = glob.glob("/home/pi/brain_stroke/preprocess/*")[0]

with h5py.File(file_n,'r') as f:
    X_norm=np.moveaxis(np.array(f.get("X_train")),0,3)
    #y=np.array(f.get("Y"))
X_norm_with_batch_dimension = np.expand_dims(X_norm, axis=0)
del X_norm
print("Got the data for prediction")
print(X_norm_with_batch_dimension.shape)
pred = model.predict(X_norm_with_batch_dimension)
del model
print("Prediction complete")


def get_mask(img,thr=0.5):
    img[img > thr] = 1.0
    img[img <= thr] = 0.0
    return img
    

pred = get_mask(pred)

def create_results(filename,data,pred):
    file_folder = '/home/pi/brain_stroke/outputs/'+filename
    os.mkdir('/home/pi/brain_stroke/outputs/'+filename)
    for i in range(0,8):
        mask=pred[0,:,:,i,0]
        alphas=np.array(np.where(mask==1,1,0),dtype=np.int8)
        img = data[0,:,:,i,3]
        plt.imshow(img,cmap="Greys_r")
        plt.imshow(mask,alpha=alphas)
        plt.axis('off')
        filen = f'{file_folder}/{filename}_result_{i}.png'
        plt.savefig(filen)
        plt.close()

file_n = file_n.split('/')[-1]
create_results(file_n,X_norm_with_batch_dimension,pred)
