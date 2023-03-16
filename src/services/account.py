from bson.objectid import ObjectId
from pymongo import ReturnDocument
from src.services.db import db

accounts = db.accounts


def findByEmail(email: str):
    return accounts.find_one({
        "email": email
    },
        {'_id': False}
    )

def findById(id: str):
    return accounts.find_one({
        "_id": ObjectId(id)
    })


def create(document):
    result = accounts.insert_one(document)
    return str(result.inserted_id)


def update(email, document):
    result = accounts.find_one_and_update({
        "email": email
    }, {
        "$set": document
    }, return_document=ReturnDocument.AFTER,)
    return result
