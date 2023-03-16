from bson.objectid import ObjectId
from pymongo import ReturnDocument
from src.services.db import db

rooms = db.rooms


def findById(id: str):
    return rooms.find_one({
        "_id": ObjectId(id)
    })

def getList(email: str):
    return rooms.find({
        'email': email
    })


def create(document):
    result = rooms.insert_one(document)
    return str(result.inserted_id)

def delete(id: str):
    return rooms.delete_one({
        "_id": id
    })

def update(id, document):
    result = rooms.find_one_and_update({
        "_id": ObjectId(id)
    }, {
        "$set": document
    }, return_document=ReturnDocument.AFTER,)
    return result