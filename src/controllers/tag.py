from os import access
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, app, request, jsonify
from firebase_admin import auth as authenticator
from werkzeug.security import check_password_hash, generate_password_hash
import json
from bson.json_util import dumps
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from src.dtos.tag import Tag
from src.services.tag import getAll, create
tag = Blueprint("tag", __name__, url_prefix="/api/v1/tag")


@tag.get("/")
@jwt_required()
def getAllTag():
    return json.loads(dumps(getAll())), HTTP_200_OK


@tag.post("/")
def createTag():
    req = request.get_json()
    tag = Tag(**req)
    result = create(tag.to_bson())
    return jsonify({"id": result}), HTTP_201_CREATED
