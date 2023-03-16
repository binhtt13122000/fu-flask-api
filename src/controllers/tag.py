from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED
from flask import Blueprint, request, jsonify
import json
from bson.json_util import dumps
from src.dtos.tag import Tag
from src.services.tag import getAll, create
tag = Blueprint("tag", __name__, url_prefix="/api/v1/tag")

@tag.get("/hello")
# @jwt_required()
def getAllTag1():
    return jsonify({
        'status': 'ok'
    })


@tag.get("/")
# @jwt_required()
def getAllTag():
    return json.loads(dumps(getAll())), HTTP_200_OK


@tag.post("/")
def createTag():
    req = request.get_json()
    tag = Tag(**req)
    result = create(tag.to_bson())
    return jsonify({"id": result}), HTTP_201_CREATED
