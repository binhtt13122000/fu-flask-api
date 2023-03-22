from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask import Blueprint, request, jsonify
from src.dtos.room import Room
from src.services.room import findById, create, getList,delete, update, findByName
import json
from bson.json_util import dumps
from src.services.account import findByEmail
from pydrive.auth import GoogleAuth
from oauth2client.client import GoogleCredentials
from pydrive.drive import GoogleDrive
from flask_cors import cross_origin


room = Blueprint("room", __name__, url_prefix="/api/v1/room")

image_folder_name = 'images'
label_folder_name = 'labels'

def getGoogleDrive(credentialsJs):
    gauth = GoogleAuth()
    print(credentialsJs);
    credentials = GoogleCredentials.from_json(json.dumps(credentialsJs))
    gauth.credentials = credentials
    drive = GoogleDrive(gauth) 
    return drive

@ room.post("/create-room")
@cross_origin()
def createRoom():
    email = request.json["email"]
    if email is None:
        return jsonify({
            'error': 'Required email parameter!'
        }), HTTP_400_BAD_REQUEST
    userAdmin = findByEmail(email=email)
    if userAdmin is None:
        return jsonify({
            'error': 'User is not found!'
        }), HTTP_404_NOT_FOUND
    
    credentialsJs = userAdmin['credentials']
    print(credentialsJs);
    if credentialsJs is None:
        return jsonify({
            'error': 'Created User doesnt connect drive!'
        }), HTTP_400_BAD_REQUEST
    print("1");
    folderParentId = userAdmin['folderParentId']
    print("2");
    drive = getGoogleDrive(credentialsJs=credentialsJs)
    print("3");
    roomName = request.json["name"]
    root_folder = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()[0]
    print("4");
    existing_folders = drive.ListFile({'q': f"'{root_folder['id']}' in parents and trashed=false"}).GetList()
    print("5");
    folder_exists = any([folder['title'].lower() == roomName.lower() for folder in existing_folders])
    print("6");
    # Create folder room
    if not folder_exists:
        # Check room name have been existed in database
        room_existed_db = findByName(roomName)
        if room_existed_db is not None:
            return jsonify({
                'error': 'Room name have been existed!'
            }), HTTP_400_BAD_REQUEST
        file_metadata_room = {
            'title': roomName,
            'parents': [{'id': folderParentId}], #parent folder
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
            email= userAdmin['email']
        )

        id = create(room.to_bson())
        return jsonify({
            'id': id,
            'name': room.name,
            'roomId': room.roomId,
            'imageId': room.imageId,
            'labelId': room.labelId,
            'email': room.email
        }), HTTP_201_CREATED
    else:
        return jsonify({
            'error': 'Room name have been existed!'
        }), HTTP_400_BAD_REQUEST

@room.get("/list-room")
@cross_origin()
def getRooms():
    email = request.args.get('email')
    if email is None:
        return jsonify({
            'error': 'Required email parameter!'
        }), HTTP_400_BAD_REQUEST
    userAdmin = findByEmail(email=email)
    if userAdmin is None:
        return jsonify({
            'error': 'User is not found!'
        }), HTTP_404_NOT_FOUND
    credentialsJs = userAdmin['credentials']
    if credentialsJs is None:
        return jsonify({
            'error': 'Created User doesnt connect drive!'
        }), HTTP_400_BAD_REQUEST
    drive = getGoogleDrive(credentialsJs=credentialsJs)
    documents = []
    result = getList(email=email)
    for document in result:
        # Query for all the files in the folder
        query = f"'{document['labelId']}' in parents and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()

        # Count the number of files in the list
        num_files = len(file_list)
        document['total'] = num_files
        documents.append(document)
    return json.loads(dumps(documents)), HTTP_200_OK

@room.get("/list-room-mobile")
@cross_origin()
def getRoomsMobile():
    result = getList(email=None)
    return json.loads(dumps(result)), HTTP_200_OK

@room.get("/<string:room_id>")
@cross_origin()
def getRoomById(room_id):
    print(room_id)
    room = findById(room_id)
    if room is not None:
        room['_id'] = str(room['_id'])
        # Room found, return its details as a JSON object
        return json.loads(dumps(room)), HTTP_200_OK
    else:
        # Room not found, return a 404 error
        return jsonify({'error': 'Room not found'}), HTTP_404_NOT_FOUND

@room.put('/update-room')
@cross_origin()
def updateRoom():
    try:
        data = request.get_json()
        id = data.get('id')
        newName = data.get('name')
        trainURL = data.get('trainURL')
        email = request.args.get('email')
        if email is None:
            return jsonify({
                'error': 'Required email parameter!'
            }), HTTP_400_BAD_REQUEST
        
        room = findById(id)
        if room is None:
            return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
        
        roomId = room['roomId']
        userAdmin = findByEmail(email=email)
        if userAdmin is None:
            return jsonify({
                'error': 'User is not found!'
            }), HTTP_404_NOT_FOUND
        credentialsJs = userAdmin['credentials']
        if credentialsJs is None:
            return jsonify({
                'error': 'Created User doesnt connect drive!'
            }), HTTP_400_BAD_REQUEST
        drive = getGoogleDrive(credentialsJs=credentialsJs)
        if newName is not None:
            # Get handle to the folder to be updated
            folder = drive.CreateFile({'id': roomId})
            folder.FetchMetadata()
            # Update the folder name
            folder['title'] = newName
            folder.Upload()

        room['name'] = newName
        room['trainURL'] = trainURL
        result = update(id=id,document=room)
        result['_id'] = str(result['_id'])
        return json.loads(dumps(result)), HTTP_200_OK
    except:
        return jsonify({'error': 'Failed to update room.'}), HTTP_500_INTERNAL_SERVER_ERROR


@room.delete('/delete-room/<string:room_id>')
@cross_origin()
def deleteRoom(room_id):
    email = request.args.get('email')
    if email is None:
        return jsonify({
            'error': 'Required email parameter!'
        }), HTTP_400_BAD_REQUEST
    room = findById(room_id)
    if room is None:
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
    roomId = room['roomId']

    userAdmin = findByEmail(email=email)
    if userAdmin is None:
        return jsonify({
            'error': 'User is not found!'
        }), HTTP_404_NOT_FOUND
    credentialsJs = userAdmin['credentials']
    if credentialsJs is None:
        return jsonify({
            'error': 'Created User doesnt connect drive!'
        }), HTTP_400_BAD_REQUEST
    drive = getGoogleDrive(credentialsJs=credentialsJs)
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
