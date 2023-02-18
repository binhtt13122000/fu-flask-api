from os import access
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, app, request, jsonify
from firebase_admin import auth as authenticator
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.dtos.account import Account
from src.services.account import findByEmail, create, update
import json
from bson.json_util import dumps
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


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
    print(result)
    result["_id"] = None
    return jsonify(result), HTTP_200_OK
