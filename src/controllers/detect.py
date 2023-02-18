from src.constants.http_status_codes import HTTP_200_OK
from flask import Blueprint, request, jsonify
# from src.services.model import model, IMG_SIZE
import numpy as np
import cv2
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from random import shuffle

from tensorflow.python.framework import ops


detect = Blueprint("detect", __name__, url_prefix="/api/v1/detect")


@detect.post("/system-model")
def detectSystemModel():
    f = request.files['file']
    IMG_SIZE = 50
    LR = 1e-3
    # bucket = storage.bucket('fu-pet-ai.appspot.com')
    # blobs = list(bucket.list_blobs())
    # blob = bucket.blob('system-model/model.tfl.data-00000-of-00001')
    # blob.download_to_filename('model.tfl.data-00000-of-00001')
    # blob = bucket.blob('system-model/model.tfl.index')
    # blob.download_to_filename('model.tfl.index')
    # blob = bucket.blob('system-model/model.tfl.meta')
    # blob.download_to_filename('model.tfl.meta')
    ops.reset_default_graph()
    convnet = input_data(shape =[None, IMG_SIZE, IMG_SIZE, 1], name ='input')

    convnet = conv_2d(convnet, 32, 5, activation ='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 64, 5, activation ='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 128, 5, activation ='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 64, 5, activation ='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = conv_2d(convnet, 32, 5, activation ='relu')
    convnet = max_pool_2d(convnet, 5)

    convnet = fully_connected(convnet, 1024, activation ='relu')
    convnet = dropout(convnet, 0.8)

    convnet = fully_connected(convnet, 8, activation ='softmax')
    convnet = regression(convnet, optimizer ='adam', learning_rate = LR,
        loss ='categorical_crossentropy', name ='targets')

    model = tflearn.DNN(convnet, tensorboard_dir ='log')
    model.load('model.tfl')
    #read image file string data
    filestr = f.read()
    #convert string data to numpy array
    file_bytes = np.fromstring(filestr, np.uint8)
    # convert numpy array to image
    img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    testing_data = []
    testing_data.append([np.array(img), 'cat'])
    shuffle(testing_data)
    model_out = model.predict([np.array(img).reshape(IMG_SIZE, IMG_SIZE, 1)])[0]
    result = np.argmax(model_out)
    if result==0: str_label ='Bird'
    elif result== 1: str_label ='Cat'
    elif result== 2: str_label ='Chair'
    elif result== 3: str_label ='Dog'
    elif result== 4: str_label ='Fish'
    elif result== 5: str_label ='Person'
    elif result== 6: str_label='Pig'
    elif result== 7: str_label='Table'

    return jsonify({
            "detect": str_label,
        }), HTTP_200_OK
