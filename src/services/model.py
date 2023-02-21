from PIL import Image
import io
from werkzeug.exceptions import BadRequest

def get_prediction(img_bytes,model):
    img = Image.open(io.BytesIO(img_bytes))
    imgs = [img]  # batched list of images
    # inference
    results = model(imgs, size=640)  
    return results

def extract_img(request):
    # checking if image uploaded is valid
    if 'file' not in request.files:
        raise BadRequest("Missing file parameter!")
    file = request.files['file']
    if file.filename == '':
        raise BadRequest("Given file is invalid")
    return file