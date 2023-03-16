from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from flask import Blueprint, request, jsonify
from firebase_admin import auth as authenticator
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from src.dtos.account import Account
from src.services.account import findByEmail, create, update
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json
from flask_cors import cross_origin
auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.get('/authorize')
@cross_origin()
def authorize():
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
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # This will open a new browser tab for authorization
    drive = GoogleDrive(gauth) 
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and title='yololaso1'"
    folders = drive.ListFile({'q': query}).GetList()

    if len(folders) == 0:
        # No folder with the given name exists, create a new folder
        folder_metadata = {'title': 'yololaso1', 'mimeType': 'application/vnd.google-apps.folder'}
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()

        # Get the folder ID of the newly created folder
        folder_parent_id = folder['id']
    else:
        # A folder with the given name already exists, get its ID
        folder_parent_id = folders[0]['id']
    credentials_json = gauth.credentials.to_json()
    userAdmin['credentials'] = json.loads(credentials_json)
    result = update(email=email,document=userAdmin)
    result["_id"] = None
    return jsonify(result), HTTP_200_OK

@auth.post("/login")
def login():
    accessToken = request.json["accessToken"]
    decodedToken = authenticator.verify_id_token(accessToken)
    email = decodedToken["email"]

    account = findByEmail(email)

    if account:
        access = create_access_token(identity=email)
        return jsonify({
            "email": email,
            "accessToken": access,
            "name": account['name']
        }), HTTP_200_OK

    return jsonify({
        "status": "NEW"
    }), HTTP_404_NOT_FOUND


@ auth.post("/register")
def register():
    req = request.get_json()
    accessToken = request.json["accessToken"]
    decodedToken = authenticator.verify_id_token(accessToken)
    email = decodedToken["email"]

    isExist = findByEmail(email)
    if isExist:
        return jsonify({
            "status": "EXIST"
        }), HTTP_400_BAD_REQUEST
    account = Account(**req)
    account.email = email
    create(account.to_bson())
    access = create_access_token(identity=account.email)
    return jsonify({
        "email": account.email,
        "accessToken": access,
        "name": account.name
    }), HTTP_201_CREATED


@ auth.get("/profile")
@jwt_required()
def getProfile():
    email = get_jwt_identity()
    result = findByEmail(email)
    if result is None:
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
    return jsonify(result), HTTP_200_OK

@ auth.put("/")
@jwt_required()
def updateProfile():
    email = get_jwt_identity()
    isExist = findByEmail(email)
    if isExist is None:
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
    req = request.get_json()
    account = Account(**req)
    account.email = email
    result = update(email=email,document=account.to_bson())
    result["_id"] = None
    return jsonify(result), HTTP_200_OK
