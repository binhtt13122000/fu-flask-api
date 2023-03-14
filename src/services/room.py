from pymongo import ReturnDocument
from src.services.db import db

rooms = db.rooms


def findById(id: str):
    return rooms.find_one({
        "_id": id
    })


def create(document):
    result = rooms.insert_one(document)
    return str(result.inserted_id)
