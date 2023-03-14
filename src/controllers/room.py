from os import access
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, app, request, jsonify
from firebase_admin import auth as authenticator
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.dtos.room import Room
from src.services.room import findById, create
import json
from bson.json_util import dumps
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from src.services.drive import drive


room = Blueprint("room", __name__, url_prefix="/api/v1/room")

parent_folder_id = '1jS_JMY6omPi0HDAZbgZO_5x8ep7IYPeG'
image_folder_name = 'images'
label_folder_name = 'labels'

@ room.post("/create-room")
def register():
    roomName = request.json["name"]
    root_folder = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()[0]
    existing_folders = drive.ListFile({'q': f"'{root_folder['id']}' in parents and trashed=false"}).GetList()
    print(existing_folders)
    folder_exists = any([folder['title'].lower() == roomName.lower() for folder in existing_folders])
    # Create folder room
    if not folder_exists:
        file_metadata_room = {
            'title': roomName,
            'parents': [{'id': parent_folder_id}], #parent folder
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folderRoom = drive.CreateFile(file_metadata_room)
        folderRoom.Upload()
        roomId = folderRoom['id']

        # Create folder image
        file_metadata_image = {
            'title': image_folder_name,
            'parents': [{'id': roomId}], #parent folder
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folderImage = drive.CreateFile(file_metadata_image)
        folderImage.Upload()
        imageId = folderImage['id']

        # Create folder label
        file_metadata_label = {
            'title': label_folder_name,
            'parents': [{'id': roomId}], #parent folder
            'mimeType': 'application/vnd.google-apps.folder'
        }

        folderLabel = drive.CreateFile(file_metadata_label)
        folderLabel.Upload()
        labelId = folderLabel['id']

        # Create dto room
        room = Room(
            name = roomName,
            roomId = roomId,
            imageId = imageId,
            labelId = labelId,
        )

        id = create(room.to_bson())
        return jsonify({
            'id': id,
            'name': room.name,
            'roomId': room.roomId,
            'imageId': room.imageId,
            'labelId': room.labelId,
        }), HTTP_201_CREATED
    else:
        return jsonify({
            'error': 'Room name have been existed!'
        }), HTTP_400_BAD_REQUEST


# @ auth.get("/profile")
# @jwt_required()
# def getProfile():
#     email = get_jwt_identity()
#     result = findByEmail(email)
#     if result is None:
#         return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
#     return jsonify(result), HTTP_200_OK

# @ auth.put("/")
# @jwt_required()
# def updateProfile():
#     email = get_jwt_identity()
#     isExist = findByEmail(email)
#     if isExist is None:
#         return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
#     req = request.get_json()
#     account = Account(**req)
#     account.email = email
#     result = update(email=email,document=account.to_bson())
#     print(result)
#     result["_id"] = None
#     return jsonify(result), HTTP_200_OK
