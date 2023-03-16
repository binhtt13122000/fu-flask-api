from os import access
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, app, request, jsonify
from firebase_admin import auth as authenticator
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.dtos.room import Room
from src.services.room import findById, create, getList,delete, update
import json
from bson.json_util import dumps
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from src.services.drive import drive


room = Blueprint("room", __name__, url_prefix="/api/v1/room")

parent_folder_id = '1jS_JMY6omPi0HDAZbgZO_5x8ep7IYPeG'
image_folder_name = 'images'
label_folder_name = 'labels'

@ room.post("/create-room")
def createRoom():
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

@room.get("/list-room")
def getRooms():
    result = getList()
    return json.loads(dumps(result))

@room.put('/update-room')
def updateRoom():
    try:
        data = request.get_json()
        id = data.get('id')
        newName = data.get('name')
        trainURL = data.get('trainURL')

        room = findById(id)
        if room is None:
            return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
        
        roomId = room['roomId']
        if newName is not None:
            # Get handle to the folder to be updated
            folder = drive.CreateFile({'id': roomId})
            folder.FetchMetadata()
            # Update the folder name
            folder['title'] = newName
            folder.Upload()

        print(room)
        room['name'] = newName
        room['trainURL'] = trainURL
        print(room)
        result = update(id=id,document=room)
        result['_id'] = str(result['_id'])
        return json.loads(dumps(result)), HTTP_200_OK
    except:
        return jsonify({'error': 'Failed to update room.'}), HTTP_500_INTERNAL_SERVER_ERROR


@room.delete('/delete-room')
def deleteRoom():
    id = request.json["id"]
    room = findById(id)
    if room is None:
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
    roomId = room['roomId']
    try:
        # Delete the document with the given ID
        result = delete(room['_id'])
        # Check if the deletion was successful
        if result.deleted_count == 1:
            # Retrieve folder with given ID
            folder = drive.CreateFile({'id': roomId})

            # Check if file is a folder
            if folder['mimeType'] == 'application/vnd.google-apps.folder':
                # Delete folder
                folder.Delete()
                return jsonify({'message': 'Room deleted successfully.'})
            else:
                return jsonify({'error': 'Failed to delete room.'}), HTTP_400_BAD_REQUEST
    except:
        return jsonify({'error': 'Failed to delete room.'}), HTTP_500_INTERNAL_SERVER_ERROR
