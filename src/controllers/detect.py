from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from flask import Flask, Blueprint, request, jsonify, make_response
# from src.services.model import model, IMG_SIZE
import numpy as np
import cv2
from random import shuffle
import sys
import io
from PIL import Image
import torch
from src.services.model import extract_img, get_prediction
import os

detect = Blueprint("detect", __name__, url_prefix="/api/v1/detect")

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.eval()

@detect.post("/system-model")
def detectSystemModel():
    file = extract_img(request)
    img_bytes = file.read()
    # choice of the model
    results = get_prediction(img_bytes,model)
    # updates results.imgs with boxes and labels
    results.render()
    # encoding the resulting image and return it
    for img in results.ims:
        RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_arr = cv2.imencode('.jpg', RGB_img)[1]
        response = make_response(im_arr.tobytes())
        response.headers['Content-Type'] = 'image/jpeg'
    return response

@detect.post("/train-model")
def trainModelUser():
    userId = request.form['userId']
    return jsonify({
            "status": 'ok',
        }), HTTP_200_OK
