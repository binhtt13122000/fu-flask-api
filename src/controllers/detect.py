from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from flask import Blueprint, request, jsonify, make_response
import numpy as np
from random import shuffle
from PIL import Image
from src.services.model import extract_img, get_prediction
from yolov5 import train
import os
detect = Blueprint("detect", __name__, url_prefix="/api/v1/detect")

modelSystem = torch.hub.load('ultralytics/yolov5', 'custom', path='src\models\system\yolov5s.pt', verbose=False)
modelSystem.eval()

@detect.post("/system-model")
def detectSystemModel():
    file = extract_img(request)
    img_bytes = file.read()
    # choice of the modelcd Des
    results = get_prediction(img_bytes,modelSystem)
    # updates results.imgs with boxes and labels
    results.render()
    # encoding the resulting image and return it
    for img in results.ims:
        RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_arr = cv2.imencode('.jpg', RGB_img)[1]
        response = make_response(im_arr.tobytes())
        response.headers['Content-Type'] = 'image/jpeg'
    return response

@detect.post("/upload-data")
def uploadDataSet():
    if 'image' not in request.files:
        return jsonify({
            'message': "Missing file parameter!",
            'status': HTTP_400_BAD_REQUEST
        })
    if 'label' not in request.files:
        return jsonify({
            'message': "Missing file parameter!",
            'status': HTTP_400_BAD_REQUEST
        })
    if 'className' not in request.form:
        return jsonify({
            'message': "Missing class name parameter!",
            'status': HTTP_400_BAD_REQUEST
        })
    if 'userId' not in request.form:
        return jsonify({
            'message': "Missing userId parameter!",
            'status': HTTP_400_BAD_REQUEST
        })
    image = request.files['image']
    label = request.files['label']
    className = request.form['className']
    userId = request.form['userId']

    bucket = storage.bucket()
    # Upload file image to data set image with specific class
    blobImage = bucket.blob('user-model/' + className + '/train/images/' + str(userId) + '-' + image.filename)
    blobImage.upload_from_file(image)
    # Upload file label to data set label with specific class
    blobLabel = bucket.blob('user-model/' + className + '/train/labels/' + str(userId) + '-' + label.filename)
    blobLabel.upload_from_file(label)
    return jsonify({
        'status': 'ok'
    })
    
@detect.post("/train-model")
def trainModelUser():
    userId = request.form['userId']
    # dict_file = [{'sports' : ['soccer', 'football', 'basketball', 'cricket', 'hockey', 'table tennis']}]
    # with open(r'C:\Users\SE141208\Desktop\fu-flask-api\src\models\users\1\data.yaml', 'w') as file:
    #     yaml.dump(dict_file, file)
    modelSystem.to_empty(device = 'cpu')
    modelSystem.train()
    train.run(imgsz=300, data='data.yaml', weights='yolov5s.pt',epochs=100,batch=32, workers = 2, nosave=True)
    # Đọc file byte của ảnh và nhãn 
    # print(os.path.curdir)
    # for filename in os.listdir("C:/Users/SE141208/Desktop/fu-flask-api/src/models_train/train/labels"):
    #         print(filename)
    #     img_bytes = filename.read()
    #     img = cv2.imread(os.path.join(folder,filename))
    #     if img is not None:
    #         images.append(img)
    # return images
    return jsonify({
            "status": 'ok',
        }), HTTP_200_OK
