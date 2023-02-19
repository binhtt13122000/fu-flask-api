from src.constants.http_status_codes import HTTP_200_OK
from flask import Blueprint, request, jsonify
# from src.services.model import model, IMG_SIZE
from firebase_admin import storage
import numpy as np
import cv2
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from random import shuffle
from firebase_admin import storage
from io import BytesIO
import gcsfs
from tensorflow.python.framework import ops


detect = Blueprint("detect", __name__, url_prefix="/api/v1/detect")


@detect.post("/system-model")
def detectSystemModel():
    file = request.files['file']
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
    # bucket = client.get_bucket('your-bucket-name')

    # # Lấy đối tượng blob (tức là tệp tin) và đọc nội dung của nó
    # blob = bucket.blob('path/to/your/model.json')
    # model_json = blob.download_as_string()

    # # Tạo lại mô hình từ nội dung của tệp tin
    # model = tflearn.models.from_json(model_json)
    
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

    convnet = fully_connected(convnet, 2, activation ='softmax')
    convnet = regression(convnet, optimizer ='adam', learning_rate = LR,
        loss ='categorical_crossentropy', name ='targets')

    model = tflearn.DNN(convnet, tensorboard_dir ='log')
    # bucket = storage.bucket('fu-pet-ai.appspot.com')

    # # Lấy đối tượng blob của file TFL được lưu trữ trong bucket
    # blob = bucket.blob('system-model/model.tfl')

    # Tải nội dung của tệp TFL từ cloud xuống bộ nhớ
    # tfl_content = blob.download_as_string()

    # Đọc nội dung của tệp TFL vào bộ nhớ đệm sử dụng BytesIO
    # tfl_buffer = BytesIO(tfl_content)

    # Tải mô hình từ tệp TFL trong bộ nhớ đệm
    # model = tflearn.DNN.load(tfl_buffer)
    # bucket = storage.bucket()
    # blob_index = bucket.blob('system-model/model.tfl.index')
    # blob_meta = bucket.blob('system-model/model.tfl.meta')
    # blob_data = bucket.blob('system-model/model.tfl.data-00000-of-00001')
    # tfl_index = blob_index.download_as_string()
    # tfl_meta = blob_meta.download_as_string()
    # tfl_data = blob_data.download_as_string()
    # model.load(self=None, model_file='model.tfl', weights_bytes=tfl_data, meta_file_bytes=tfl_meta, checkpoint_path_bytes=tfl_index)
    # bytes_index = blob_index.download_as_bytes()
    # bytes_meta = blob_meta.download_as_bytes()
    # bytes_data = blob_data.download_as_bytes()

    # Tạo file-like object từ các bytes
    # index_file = BytesIO(bytes_index)
    # meta_file = BytesIO(bytes_meta)
    # data_file = BytesIO(bytes_data)
    # model.load('https://firebasestorage.googleapis.com/v0/b/fu-pet-ai.appspot.com/o/system-model%2Fmodel.tfl.index?alt=media&token=7fa82b16-16fa-400e-9c4a-e1cdd22b627b')
    # # Load model bằng tflearn
    # model = tflearn.DNN(convnet, tensorboard_verbose=0)
    # model.load({'checkpoint_path_bytes': index_file, 'meta_file_bytes': meta_file, 'weights_bytes': data_file})
    # model_path = 'fu-pet-ai.appspot.com/system-model/'
    # fs = gcsfs.GCSFileSystem(project='fu-pet-ai', token='firebase_admin_sdk.json')
    # print('DANH', fs.glob(model_path))
    # with fs.open(model_path, 'r') as f:
    #     print(f)
    #     model = tflearn.DNN(convnet, tensorboard_dir ='log')
    #     model.load(f)
    # model.load('model.tfl')
    #read image file string data
    filestr = file.read()
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
    if result == 1: str_label ='Dog'
    else: str_label ='Cat'

    return jsonify({
            "detect": str_label,
        }), HTTP_200_OK
