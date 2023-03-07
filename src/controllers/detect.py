from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from flask import Blueprint, request, jsonify
import numpy as np
from PIL import Image
from firebase_admin import storage
from src.services.model import extract_img
from yolov5 import detect as detectYolo
import io
import base64
import cv2
import torch
import urllib.request

detect = Blueprint("detect", __name__, url_prefix="/api/v1/detect")

# # Download data.yaml file
# url = "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/coco.yaml"
# filename, _ = urllib.request.urlretrieve(url, filename="./data.yaml")

modelSystem = torch.hub.load('ultralytics/yolov5', 'custom', path='src\models\system\yolov5s.pt', verbose=False)
modelSystem.eval()

@detect.post("/system-model")
def detectSystemModel():
    file = extract_img(request)
    # Load the image
    img = Image.open(file).convert('RGB')

    # Convert the image to a numpy array
    img_array = np.array(img)

    # Use YOLOv5 to detect objects in the image
    results = modelSystem(img_array)

    # Extract the bounding boxes, class labels, and confidence scores from the results
    boxes = results.xyxy[0].numpy().tolist()
    class_ids = results.pred[0].numpy()[:, 5].tolist() # extract class ids
    labels = [results.names[int(class_id)] for class_id in class_ids] # convert class ids to labels
    scores = results.pred[0].numpy()[:, 4].tolist() # extract confidence scores

    # Loop over the bounding boxes and draw them on the image
    detections = []
    for i, box in enumerate(boxes):
        x1, y1, x2, y2, score, class_id = box
        label = results.names[int(class_id)]
        conf = f"{score:.2f}"
        cropped_img = img.crop((x1, y1, x2, y2))
        # Convert the image to a base64-encoded string
        output = io.BytesIO()
        cropped_img.save(output, format='JPEG')
        output.seek(0)
        result_bytes_crop = output.getvalue()
        result_str_crop = base64.b64encode(result_bytes_crop).decode('utf-8')
        # cropped_img_base64 = base64.b64encode(cropped_img.tobytes()).decode('utf-8')
        detections.append({'label': label, 'confidence': conf, 'image': result_str_crop})
    results.render()
    # encoding the resulting image and return it
    for img in results.ims:
        RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_arr = cv2.imencode('.jpg', RGB_img)[1]
        result_bytes = im_arr.tobytes()
        # response = make_response(im_arr.tobytes())
    
    # Encode the bytes using base64
    result_str = base64.b64encode(result_bytes).decode('utf-8')

    return jsonify({'result': result_str, 'detections': detections})

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
    # model = load('yolov5s.pt')
    # # set model parameters
    # model.conf = 0.25  # NMS confidence threshold
    # model.iou = 0.45  # NMS IoU threshold
    # model.agnostic = False  # NMS class-agnostic
    # model.multi_label = False  # NMS multiple labels per box
    # model.max_det = 1000  # maximum number of detections per image
    # # image
    # img = 'https://github.com/ultralytics/yolov5/raw/master/data/images/zidane.jpg'
    # # inference
    # results = model(img)
    # # inference with larger input size
    # results = model(img, size=1280)
    # # inference with test time augmentation
    # results = model(img, augment=True)
    # # parse results
    # predictions = results.pred[0]
    # boxes = predictions[:, :4] # x1, x2, y1, y2
    # scores = predictions[:, 4]
    # categories = predictions[:, 5]
    # show results
    # results.show()
    # dict_file = [{'sports' : ['soccer', 'football', 'basketball', 'cricket', 'hockey', 'table tennis']}]
    # with open(r'C:\Users\SE141208\Desktop\fu-flask-api\src\models\users\1\data.yaml', 'w') as file:
    #     yaml.dump(dict_file, file)
    # modelSystem.to_empty(device = 'cpu')
    # modelSystem.train()
    # train.run(imgsz=416, data='data.yaml', weights='yolov5s.pt',epochs=12,batch=32, workers = 2)
    img_path = 'C:/Users/SE141208/Desktop/fu-flask-api/test/images/flickr_wild_002929_jpg.rf.0718cb9abe616d9398d5ad571c75cac4.jpg'
    img = cv2.imread(img_path)
    results = detectYolo(img, imgsz=416, weights='runs/train/exp2/weights/best.pt', view_img=True)
    for result in results:
        print(result['label'], result['confidence'], result['bbox'])
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
