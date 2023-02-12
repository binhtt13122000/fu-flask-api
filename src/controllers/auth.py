from os import access
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from flask import Blueprint, app, request, jsonify
from firebase_admin import auth as authenticator
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.dtos.account import Account
from src.services.account import findByEmail, create
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
    account = Account(**req)
    result = create(account.to_bson())
    return jsonify({"id": result}), HTTP_201_CREATED


@ auth.get("/")
@jwt_required()
def getC():
    result = findByEmail("binh")
    if result is None:
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND
    return jsonify(result), HTTP_200_OK
# @auth.post("/login")
# @swag_from("./docs/auth/login.yaml")
# def login():
#     email = request.json.get("email", "")
#     password = request.json.get("password", "")

#     user = User.query.filter_by(email=email).first()

#     if user:
#         is_pass_correct = check_password_hash(user.password, password)

#         if is_pass_correct:
#             refresh = create_refresh_token(identity=user.id)
#             access = create_access_token(identity=user.id)

#             return jsonify({
#                 "user": {
#                     "refresh": refresh,
#                     "access": access,
#                     "username": user.username,
#                     "email": user.email
#                 }

#             }), HTTP_200_OK

#     return jsonify({"error": "Wrong credentials"}), HTTP_401_UNAUTHORIZED


# @auth.get("/me")
# @jwt_required()
# def me():
#     user_id = get_jwt_identity()
#     user = User.query.filter_by(id=user_id).first()
#     return jsonify({
#         "username": user.username,
#         "email": user.email
#     }), HTTP_200_OK


# @auth.get("/token/refresh")
# @jwt_required(refresh=True)
# def refresh_users_token():
#     identity = get_jwt_identity()
#     access = create_access_token(identity=identity)

#     return jsonify({
#         "access": access
#     }), HTTP_200_OK
