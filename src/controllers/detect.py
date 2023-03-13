from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from flask import Blueprint, request, jsonify, make_response
from firebase_admin import storage
from src.services.model import extract_img, get_prediction
import cv2
import torch
import base64
import tempfile
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()       
gauth.LocalWebserverAuth()    
drive = GoogleDrive(gauth)  

detect = Blueprint("detect", __name__, url_prefix="/api/v1/detect")

# # Download data.yaml file
# url = "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/coco.yaml"
# filename, _ = urllib.request.urlretrieve(url, filename="./data.yaml")

modelSystem = torch.hub.load('ultralytics/yolov5', 'custom', path='src\models\system\yolov5s.pt', verbose=False)
modelSystem.eval()

folderImageId='1AzA8Df1M0t0zMizdOwnS_Q-_Vs74OQ_4'
folderLabelId='1GIWPAAyZ3dQ9OoJI6KwmTXhdJUgqu3G9'

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
    image = request.files['image']
    label = request.files['label']
    # Upload file image
    file_name_image = image.filename
    gfile = drive.CreateFile({'parents': [{'id': folderImageId, 'title': file_name_image}]})
    # Save file to temporary directory
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        image.save(tmp.name)
        file_path_image = tmp.name
    
    # Set content of file
    gfile.SetContentFile(file_path_image)
    gfile.Upload() # Upload the file.
    gfile['title'] = file_name_image
    gfile.Upload()

    # Upload file label
    file_name_label = label.filename
    gfile = drive.CreateFile({'parents': [{'id': folderLabelId, 'title': file_name_label}]})
    with tempfile.NamedTemporaryFile(delete=False) as tmp1:
        label.save(tmp1.name)
        file_path_label = tmp1.name
    
    # Set content of file
    gfile.SetContentFile(file_path_label)
    gfile.Upload() # Upload the file.
    gfile['title'] = file_name_label
    gfile.Upload()

    return jsonify({
        'status': 'ok'
    })
    
@detect.post("/train-model")
def trainModelUser():
    userId = request.form['userId']
    
    return jsonify({
            "status": 'ok',
        }), HTTP_200_OK
